# orgspec — OPI reference tooling

Reference CLI for the OPI spec. Two commands in this MVP:

```bash
python3 -m orgspec validate <org.yaml | repo-dir>   # delegates to tools/validate.py
python3 -m orgspec validate <path> --as-of 2026-06-30  # fixed clock for Rule 101 (v0.8)
python3 -m orgspec serve <repo-dir> [--watch] [--key K] [--port 8484]
```

## `orgspec serve` — the Serving Profile, running

Reference implementation of the **OPI v0.7 Serving Profile**
(`spec/opi-v0.7.md` §4): exposes an OPI repository to AI agents as an MCP
context endpoint — **without moving the source of truth**. The repo (files, PRs,
history) stays canonical; the server is a stateless projection of the working tree.

```bash
python3 -m orgspec serve examples/serve-demo --watch
# prints the endpoint, the generated tool count, the API key, and the
# ready-to-paste `claude mcp add` line
```

- **Tool derivation:** the catalog is generated deterministically from the entity
  field table (`get_<entity>_by_id`, `filter_*_by_<field>` with known values in the
  description, `search_*_by_text`, relation traversals). 5 entities in the demo org
  yield ~22 tools; nothing is hand-curated per deployment.
- **Composite tools (§4.3, SHOULD):** `who_decides(topic)`,
  `get_decision_chain(id)`, `get_agent_mandate(ref)`, and since the v0.8 draft
  `get_undelivered_decisions(as_of?)` — "what did we decide and never carry?",
  always with the enforcement coverage of the set it examined, bounded to what the
  key may see (spec/opi-v0.8.md §3.2). The v0.8 blocks `decisions[].enforcement`
  and `decisions[].approval` derive no tools of their own (Rule 103).
- **Enforcement (§4.4):** `X-API-Key` checked server-side; tools accept no
  caller-identity parameters. MVP ships ONE key without visibility tiers — tier
  enforcement lands with the v0.7 schema.
- **Read-only (§4.5):** by design. Changes travel through the repository's change
  process (pull requests), not through the endpoint.
- **`--watch`:** mtime-based reload per request — a merged PR is visible on the
  agent's next tool call. A broken working tree never breaks the server; it keeps
  serving the last good state and logs the parse error.

**Transport:** streamable-HTTP MCP (JSON-RPC 2.0 over `POST /mcp`, plain-JSON
responses; notifications get `202`). Tested end-to-end with the standard client
handshake (`initialize` → `notifications/initialized` → `tools/list` → `tools/call`).

**Dependency:** PyYAML (parsing). Like `tools/validate.py`, there is deliberately
no fallback YAML parser — a server that guesses at YAML would defeat its purpose.
