"""`orgspec serve` — MCP context endpoint over an OPI repository (stdlib only).

Implements the streamable-HTTP MCP transport (JSON-RPC 2.0 over POST /mcp,
plain-JSON responses) with the Serving Profile's enforcement rules:

* auth via `X-API-Key` (Rule 95 — enforcement lives here, not in the client)
* tools take no caller-identity parameters (Rule 97)
* read-only by design (§4.5) — the write path is the repository's change process
* `--watch`: mtime check per request; a merged PR is visible on the next call

One key, one tier ceiling (--ceiling). Everything above it is redacted or
omitted on the way out — see tools.enforce_tier.
"""

from __future__ import annotations

import json
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import __version__
from .loader import LoadError, load
from .tools import Catalog, TIER_ORDER

PROTOCOL_VERSION = "2025-03-26"


class _State:
    """Model + catalog with watch-aware reload."""

    def __init__(self, root: str, watch: bool, ceiling: str = "internal"):
        self.root, self.watch, self.ceiling = root, watch, ceiling
        self._lock = threading.Lock()
        self.model = load(root)
        self.catalog = Catalog(self.model, ceiling)

    def fresh_catalog(self) -> Catalog:
        with self._lock:
            if self.watch and self.model.stale():
                try:
                    self.model = load(self.root)
                    self.catalog = Catalog(self.model, self.ceiling)
                    print(f"[watch] reloaded: {self.model.counts()}")
                except LoadError as exc:
                    # keep serving the last good state; a broken tree never 500s the agent
                    print(f"[watch] reload failed, serving last good state: {exc}")
            return self.catalog


def _handler(state: _State, api_key: str):
    class Handler(BaseHTTPRequestHandler):
        server_version = f"orgspec-serve/{__version__}"

        def log_message(self, fmt, *args):  # quieter default log line
            print(f"[http] {args[0]} {args[1]}" if len(args) > 1 else fmt % args)

        def _json(self, code: int, payload: dict | None):
            body = b"" if payload is None else json.dumps(payload).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)

        def do_GET(self):
            # no SSE stream in the MVP; streamable-HTTP clients fall back to POST
            self._json(405, {"error": "POST JSON-RPC to /mcp"})

        def do_POST(self):
            if self.path.rstrip("/") not in ("/mcp", ""):
                return self._json(404, {"error": "unknown path, use /mcp"})
            if self.headers.get("X-API-Key", "") != api_key:
                return self._json(401, {"error": "missing or invalid X-API-Key"})
            try:
                length = int(self.headers.get("Content-Length", 0))
                msg = json.loads(self.rfile.read(length) or b"{}")
            except (ValueError, json.JSONDecodeError):
                return self._json(400, _rpc_error(None, -32700, "parse error"))
            if "id" not in msg:  # notification (e.g. notifications/initialized)
                return self._json(202, None)
            self._json(200, self._dispatch(msg))

        # -- JSON-RPC dispatch ------------------------------------------------
        def _dispatch(self, msg: dict) -> dict:
            mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
            try:
                if method == "initialize":
                    return _rpc_result(mid, {
                        "protocolVersion": params.get("protocolVersion", PROTOCOL_VERSION),
                        "capabilities": {"tools": {"listChanged": False}},
                        "serverInfo": {
                            "name": "orgspec-serve",
                            "version": __version__,
                            "title": "OPI Serving Profile reference implementation",
                        },
                        "instructions": (
                            "Tools are derived from the OPI schema of this organization "
                            "repository. Naming grammar: get_<entity>_by_id, "
                            "filter_<entities>_by_<field>, search_<entities>_by_text. "
                            "Composite governance tools: who_decides(topic), "
                            "get_decision_chain(id), get_agent_mandate(ref). "
                            "The endpoint is read-only: changes travel through the "
                            "repository's change process (pull requests)."
                        ),
                    })
                if method == "ping":
                    return _rpc_result(mid, {})
                if method == "tools/list":
                    return _rpc_result(mid, {"tools": state.fresh_catalog().describe()})
                if method == "tools/call":
                    catalog = state.fresh_catalog()
                    name = params.get("name", "")
                    try:
                        result = catalog.call(name, params.get("arguments") or {})
                    except KeyError:
                        return _rpc_error(mid, -32602, f"unknown tool: {name}")
                    except TypeError as exc:
                        return _rpc_error(mid, -32602, f"bad arguments for {name}: {exc}")
                    return _rpc_result(mid, {
                        "content": [{"type": "text",
                                     "text": json.dumps(result, indent=2, default=str)}],
                        "isError": False,
                    })
                return _rpc_error(mid, -32601, f"method not found: {method}")
            except Exception as exc:  # noqa: BLE001 — one bad call never kills the server
                return _rpc_error(mid, -32603, f"internal error: {exc}")

    return Handler


def _rpc_result(mid, result):
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def _rpc_error(mid, code, message):
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}


def serve(root: str, host: str = "127.0.0.1", port: int = 8484,
          key: str | None = None, watch: bool = False,
          ceiling: str = "internal") -> None:
    if ceiling not in TIER_ORDER:
        raise SystemExit(f"--ceiling must be one of {', '.join(TIER_ORDER)} (got {ceiling!r})")
    state = _State(root, watch, ceiling)
    api_key = key or secrets.token_urlsafe(24)
    httpd = ThreadingHTTPServer((host, port), _handler(state, api_key))
    counts = ", ".join(f"{v} {k}" for k, v in state.model.counts().items())
    print(f"orgspec serve {__version__} — OPI Serving Profile (read-only)")
    print(f"  repo:   {state.model.root}  ({counts})")
    print(f"  tools:  {len(state.catalog.tools)} generated")
    print(f"  mcp:    http://{host}:{port}/mcp   (X-API-Key required)")
    print(f"  tier:   {ceiling} — entities above this tier are redacted or omitted (spec §1.1)")
    if key is None:
        print(f"  key:    {api_key}   (generated — pass --key to pin one)")
    print(f"  watch:  {'on — merged changes are visible on the next call' if watch else 'off'}")
    print(f'  client: claude mcp add --transport http org "http://{host}:{port}/mcp" '
          f'--header "X-API-Key: {api_key}"')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
