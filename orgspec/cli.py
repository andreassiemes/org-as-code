"""orgspec CLI — `validate` and `serve`."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from . import __version__
from .loader import LoadError, load


def _cmd_validate(args) -> int:
    """Delegate to tools/validate.py (the canonical validator) when available."""
    repo_validator = Path(__file__).resolve().parent.parent / "tools" / "validate.py"
    targets = []
    root = Path(args.path)
    if root.is_dir():
        try:
            targets = [str(p) for p in load(root).docs]
        except LoadError as exc:
            print(f"✗ {exc}")
            return 1
    else:
        targets = [str(root)]
    if repo_validator.exists():
        return subprocess.call([sys.executable, str(repo_validator), *targets])
    # fallback: structural load only
    try:
        model = load(args.path)
    except LoadError as exc:
        print(f"✗ {exc}")
        return 1
    print(f"✓ parsed {len(model.docs)} document(s): {model.counts()}")
    print("  (tools/validate.py not found — structural load only, no rule checks)")
    return 0


def _cmd_serve(args) -> int:
    from .server import serve  # imported lazily: stdlib-only, but keep startup honest

    try:
        serve(args.path, host=args.host, port=args.port, key=args.key, watch=args.watch)
    except LoadError as exc:
        print(f"✗ {exc}")
        return 1
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="orgspec", description="OPI reference tooling")
    ap.add_argument("--version", action="version", version=f"orgspec {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="validate OPI documents (file or repo dir)")
    v.add_argument("path")
    v.set_defaults(fn=_cmd_validate)

    s = sub.add_parser("serve", help="serve an OPI repo as an MCP context endpoint")
    s.add_argument("path", help="org.yaml or a repository directory")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8484)
    s.add_argument("--key", help="API key (default: generated and printed)")
    s.add_argument("--watch", action="store_true",
                   help="reload on file changes — a merged PR is visible on the next call")
    s.set_defaults(fn=_cmd_serve)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
