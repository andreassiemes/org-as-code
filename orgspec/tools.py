"""Tool catalog for the OPI Serving Profile (spec/opi-v0.7.md §4.2–§4.3).

The catalog is derived deterministically from the entity field table below — one
row per servable field, mirroring the v0.6 JSON Schema. Field kinds map to tool
shapes exactly as the Serving Profile specifies:

    key      -> get_<entity>_by_id
    tag/enum -> filter_<entity>_by_<field>
    text     -> search_<entity>_by_text   (one tool per entity, pooled fields)
    relation -> traversal tools

Composite tools (§4.3, SHOULD): who_decides, get_decision_chain, get_agent_mandate,
and since v0.8 get_undelivered_decisions (spec/opi-v0.8.md §3.2).

Rule 103 (v0.8): derivation is bounded by the instance (a field no served document
populates yields no tool) and by nesting (nested lists and objects such as
`decisions[].enforcement` and `approval.records[]` travel with their record and
derive no tools of their own). Both bounds are structural here: only the fields in
ENTITIES are ever considered, and only when at least one record carries them.
"""

from __future__ import annotations

import json

from .loader import Model

# --- field table (mirrors spec/opi-v0.6.schema.json for the MVP entities) -------
# entity -> (singular, plural-key, tag fields, text fields)
ENTITIES = {
    "decision": {
        "list_key": "decisions",
        "tags": ["status", "gremium", "driver", "approver", "scope", "decision_type"],
        "text": ["title", "rationale"],
    },
    "unit": {
        "list_key": "units",
        "tags": ["type", "owner", "parent"],
        "text": ["name", "purpose", "mandate"],
    },
    "gremium": {
        "list_key": "gremien",
        "tags": ["cadence"],
        "text": ["name", "purpose"],
    },
}


def _match(entity: dict, field: str, value: str) -> bool:
    return str(entity.get(field, "")).lower() == str(value).lower()


def _text_hit(entity: dict, fields: list[str], query: str) -> bool:
    q = query.lower()
    return any(q in str(entity.get(f, "")).lower() for f in fields)


def _slim(e: dict, keep=("id", "title", "name", "status", "type", "purpose")) -> dict:
    """Headline projection. `visibility` and `date` always travel with it: every
    tool result passes through `enforce_tier` on the way out (Rule 95, v0.7 §4.4
    point 1), and a projection that dropped the tier first would serve a
    restricted entity as internal."""
    return {k: e[k] for k in (*keep, "date", "visibility") if k in e}


TIER_ORDER = {"public": 0, "internal": 1, "restricted": 2, "confidential": 3}
REDACTED_KEEP = ("id", "ref", "date", "visibility")


class Envelope(dict):
    """A composite tool's result wrapper — not an entity.

    §1.2's default ("absent `visibility` means internal") classifies *entities*:
    the records that live in the entity lists and carry a tier, declared or
    implied. A composite's answer wrapper carries none, because it is not a
    thing the organisation classified — it is the shape of a reply, built from
    entities that were each classified on their own.

    Without this distinction the default swallows the wrapper whole: served to a
    `public` key, an unmarked `{"as_of": …, "undelivered": […], "coverage": {…}}`
    is read as an internal entity above the ceiling and redacted to the fields of
    REDACTED_KEEP, none of which a wrapper has — so every composite returns `{}`
    and an empty answer becomes indistinguishable from "nothing open". That is
    the reading v0.8 §3.2 forbids in its own tool description.

    Marking the wrapper keeps the single gate of `Catalog.call` intact: the
    contents still pass through `enforce_tier` entity by entity, and a redacted
    card inside a wrapper stays a redacted card. Only the wrapper itself is
    spared a classification it never had.
    """


def _envelope(value: dict) -> Envelope:
    return value if isinstance(value, Envelope) else Envelope(value)


def tier_of(entity) -> int:
    """Classification of an entity; absent means internal (spec §1.2)."""
    if not isinstance(entity, dict):
        return TIER_ORDER["internal"]
    return TIER_ORDER.get(entity.get("visibility"), TIER_ORDER["internal"])


def enforce_tier(value, ceiling: int, _inherited: bool = False):
    """Apply the serving obligations of spec §1.1 to a tool result.

    At or below the ceiling the entity passes through untouched. Above it,
    content is redacted while existence stays visible as a card (id, date,
    tier), so graph topology remains honest.

    `confidential` is not a higher access level and no ceiling unlocks it: the
    tier means "kept out of the open repository entirely — never serialize,
    reference by id only" (§1.1). An entity carrying it is already a spec
    violation of the document; the server does not compound it by serving it.

    Absence, not access-denied (§4.4): a caller cannot tell a filtered entity
    from one that does not exist.

    `_inherited` marks the contents of an entity that has already cleared the
    ceiling. Rule 103 (v0.8): nested lists and objects such as
    `decisions[].enforcement` and `approval.records[]` *travel with their
    record* — they are parts of it, not entities in their own right, and they
    carry no tier of their own. Classifying them independently would apply
    §1.2's entity default ("absent means internal") to a sub-object that was
    never classified, and strip `enforcement`, `approval` and `scope` out of a
    decision the caller is entitled to read in full. The tier decision belongs
    to the record; once it is made, it holds for everything inside it.
    """
    if isinstance(value, list):
        out = [enforce_tier(v, ceiling, _inherited) for v in value]
        return [v for v in out if v is not None]
    if isinstance(value, Envelope):
        # A wrapper is not an entity and has no tier of its own: recurse into its
        # contents, never classify the wrapper. See Envelope's docstring.
        #
        # Inside a wrapper, a *list* holds entities (`undelivered[]`, `nodes[]`,
        # `bodies[]`, `precedents[]`) and each item is classified on its own. A
        # plain *object* is a part of the answer, not an entity — `coverage`,
        # `scope` — and is no more classifiable than the wrapper around it. No
        # composite returns a bare entity as an object-valued key; where one
        # would, it enforces the entity's tier itself before wrapping.
        return Envelope({
            k: enforce_tier(v, ceiling, _inherited=isinstance(v, dict))
            for k, v in value.items()
        })
    if not isinstance(value, dict):
        return value
    if _inherited:
        # Part of a record that already cleared the ceiling (Rule 103).
        return value
    tier = tier_of(value)
    if tier >= TIER_ORDER["confidential"]:
        return None
    if tier > ceiling:
        return {k: value[k] for k in REDACTED_KEEP if k in value}
    return {k: enforce_tier(v, ceiling, _inherited=True) for k, v in value.items()}


class Catalog:
    """Generated tools over a loaded Model. `describe()` feeds MCP tools/list."""

    def __init__(self, model: Model, ceiling: str = "internal"):
        self.model = model
        self.ceiling = TIER_ORDER.get(ceiling, TIER_ORDER["internal"])
        self.tools: dict[str, dict] = {}
        self._build()

    # -- catalog construction -------------------------------------------------
    def _add(self, name: str, description: str, params: dict, fn, required=None):
        self.tools[name] = {
            "description": description,
            "inputSchema": {
                "type": "object",
                "properties": params,
                "required": list(params.keys()) if required is None else list(required),
            },
            "fn": fn,
        }

    def _build(self):
        m = self.model
        for singular, cfg in ENTITIES.items():
            items = m.entities.get(cfg["list_key"], [])
            if not items:
                continue
            lk = cfg["list_key"]

            self._add(
                f"list_{lk}",
                f"List all {lk} (id + headline fields).",
                {},
                lambda items=items: [_slim(e) for e in items],
            )
            self._add(
                f"get_{singular}_by_id",
                f"Fetch one {singular} record by its id.",
                {"id": {"type": "string", "description": f"the {singular} id"}},
                lambda id, items=items: next(
                    (e for e in items if str(e.get("id")) == str(id)),
                    {"error": f"no {singular} with id {id}"},
                ),
            )
            for field in cfg["tags"]:
                if not any(field in e for e in items):
                    continue  # field unused in this document set -> no tool
                self._add(
                    f"filter_{lk}_by_{field}",
                    f"Filter {lk} by exact {field} value. "
                    f"Known values: {sorted({str(e.get(field)) for e in items if e.get(field)})}",
                    {field: {"type": "string"}},
                    lambda items=items, field=field, **kw: [
                        e for e in items if _match(e, field, kw[field])
                    ],
                )
            self._add(
                f"search_{lk}_by_text",
                f"Full-text keyword search over {lk} ({', '.join(cfg['text'])}).",
                {"query": {"type": "string"}},
                lambda query, items=items, cfg=cfg: [
                    e for e in items if _text_hit(e, cfg["text"], query)
                ],
            )

        if m.entities.get("units"):
            self._add(
                "get_unit_children",
                "Units whose `parent` is the given unit id (structure traversal).",
                {"id": {"type": "string"}},
                lambda id: [
                    _slim(u) for u in m.entities["units"] if str(u.get("parent")) == str(id)
                ],
            )

        # --- composite tools (Serving Profile §4.3, SHOULD) ---
        if m.entities.get("decisions") or m.entities.get("gremien"):
            self._add(
                "who_decides",
                "Who can decide on a topic? Resolves via gremien (purpose match) and "
                "decisions (driver/approver of matching precedents). The governance "
                "answer, with mandate context.",
                {"topic": {"type": "string"}},
                self._who_decides,
            )
        if m.entities.get("decisions"):
            self._add(
                "get_decision_chain",
                "Trace a decision's history and blast radius: follows revises, "
                "supersedes/superseded_by, triggers, consequences, conflicts_with.",
                {"id": {"type": "string"}},
                self._decision_chain,
            )
        if m.entities.get("decisions"):
            self._add(
                "get_undelivered_decisions",
                "What did we decide and never carry? Active decisions whose enforcement "
                "is pending and whose expected_by has passed as of the given date "
                "(default: today). Always returns the enforcement coverage of the set it "
                "examined, so an empty answer cannot be read as 'nothing open' "
                "(v0.8 §3.2).",
                {"as_of": {"type": "string",
                           "description": "YYYY-MM-DD clock to judge expected_by against; "
                                          "default: today"}},
                self._undelivered_decisions,
                required=[],
            )
        if m.entities.get("agents"):
            self._add(
                "get_agent_mandate",
                "What may this AI agent decide, and where does it escalate? Reads the "
                "agent's scope and escalation_path (v0.5 Agent Context API).",
                {"ref": {"type": "string"}},
                self._agent_mandate,
            )

    # -- composite implementations --------------------------------------------
    def _who_decides(self, topic: str):
        m, q = self.model, topic.lower()
        bodies = [
            {
                "gremium": g.get("id"),
                "name": g.get("name"),
                "purpose": g.get("purpose"),
                "cadence": g.get("cadence"),
                "members": g.get("members", []),
                "visibility": g.get("visibility"),
            }
            for g in m.entities.get("gremien", [])
            if q in json.dumps(g, default=str).lower()
        ]
        precedents = [
            {
                "id": d.get("id"),
                "title": d.get("title"),
                "status": d.get("status"),
                "driver": d.get("driver"),
                "approver": d.get("approver"),
                "gremium": d.get("gremium"),
                "date": d.get("date"),
                "visibility": d.get("visibility"),
            }
            for d in m.entities.get("decisions", [])
            if _text_hit(d, ["title", "rationale", "scope"], topic)
        ]
        answer = {"topic": topic, "bodies": bodies, "precedents": precedents}
        if not bodies and not precedents:
            answer["note"] = (
                "No gremium purpose or decision precedent matches this topic. "
                "Escalate via the org's change process (governance.change_process)."
            )
        return _envelope(answer)

    def _decision_chain(self, id: str):
        m = self.model
        edges, seen, frontier = [], set(), [str(id)]
        rel_fields = ("revises", "supersedes", "superseded_by", "triggers",
                      "consequences", "conflicts_with", "depends_on", "blocks")
        while frontier:
            cur = frontier.pop()
            if cur in seen:
                continue
            seen.add(cur)
            d = m.by_id("decisions", cur)
            if not d:
                continue
            for field in rel_fields:
                val = d.get(field)
                refs = val if isinstance(val, list) else ([val] if val else [])
                for ref in refs:
                    ref = str(ref)
                    edges.append({"from": cur, field: ref})
                    frontier.append(ref)
            # reverse edges: anyone pointing at cur
            for other in m.entities["decisions"]:
                oid = str(other.get("id"))
                if oid in seen:
                    continue
                for field in rel_fields:
                    val = other.get(field)
                    refs = val if isinstance(val, list) else ([val] if val else [])
                    if cur in [str(r) for r in refs]:
                        frontier.append(oid)
        nodes = [
            _slim(m.by_id("decisions", n) or {"id": n, "error": "unresolved ref"})
            for n in sorted(seen)
        ]
        return Envelope({"root": id, "nodes": nodes, "edges": edges})

    def _undelivered_decisions(self, as_of: str | None = None):
        import datetime

        def to_date(v):
            if isinstance(v, datetime.datetime):
                return v.date()
            if isinstance(v, datetime.date):
                return v
            try:
                return datetime.date.fromisoformat(str(v))
            except (TypeError, ValueError):
                return None

        clock = to_date(as_of) if as_of else datetime.date.today()
        if clock is None:
            return Envelope({"error": f"as_of {as_of!r} is not a YYYY-MM-DD date"})
        # Coverage is bounded to what the requesting key may see (§3.2): count over the
        # same tier-enforced view the result itself passes through, so a redacted card
        # (no `status`) is neither "active" nor "annotated" here.
        visible = enforce_tier(list(self.model.entities.get("decisions", [])), self.ceiling)
        active = [d for d in visible if isinstance(d, dict) and d.get("status") == "active"]
        with_block = [d for d in active if isinstance(d.get("enforcement"), dict)]
        with_expect = [d for d in with_block if d["enforcement"].get("expected_by")]
        hits = []
        for d in with_expect:
            enf = d["enforcement"]
            exp = to_date(enf.get("expected_by"))
            if enf.get("status") == "pending" and exp and exp < clock:
                hits.append({
                    "id": d.get("id"), "title": d.get("title"), "date": d.get("date"),
                    "gremium": d.get("gremium"), "driver": d.get("driver"),
                    "expected_by": enf.get("expected_by"),
                    "overdue_days": (clock - exp).days,
                    # The tier travels with the projection, for the reason _slim
                    # states: this list is classified again on the way out, and a
                    # hit that dropped its tier first would be re-read as internal
                    # and redacted down to a bare id — turning a named overdue
                    # decision into an anonymous one for every public caller.
                    "visibility": d.get("visibility"),
                })
        return Envelope({
            "as_of": clock.isoformat(),
            "undelivered": hits,
            "coverage": {
                "active": len(active),
                "with_enforcement": len(with_block),
                "with_expected_by": len(with_expect),
                "line": (f"{len(with_block)} of {len(active)} active decisions carry an "
                         f"enforcement block, {len(with_expect)} of {len(with_block)} state "
                         f"an expectation"),
            },
        })

    def _agent_mandate(self, ref: str):
        for a in self.model.entities.get("agents", []):
            if str(a.get("ref")) == str(ref):
                # The wrapper is built from the agent's fields, so it does not
                # inherit the agent's tier the way a returned record would: the
                # gate in `call` sees a wrapper, not the entity. Enforce the
                # agent's own classification here, before wrapping — otherwise a
                # restricted agent's mandate is served in full to any ceiling
                # (the composite-versus-tier gap Rule 95 closed for the others).
                if tier_of(a) > self.ceiling:
                    return Envelope(
                        {k: a[k] for k in REDACTED_KEEP if k in a}
                    )
                return Envelope({
                    "ref": a.get("ref"),
                    "scope": a.get("scope"),
                    "escalation_path": a.get("escalation_path"),
                    "disabled": a.get("disabled", False),
                    "context_endpoint": a.get("context_endpoint"),
                })
        return Envelope({"error": f"no agent with ref {ref}",
                         "known": [a.get("ref") for a in self.model.entities.get("agents", [])]})

    # -- MCP surface -----------------------------------------------------------
    def describe(self) -> list[dict]:
        return [
            {"name": n, "description": t["description"], "inputSchema": t["inputSchema"]}
            for n, t in sorted(self.tools.items())
        ]

    def call(self, name: str, arguments: dict):
        tool = self.tools.get(name)
        if not tool:
            raise KeyError(name)
        # Rule 95 / §4.4: enforcement happens here, on the way out — one gate
        # every tool result passes through, rather than per-tool filtering that
        # a new tool could forget.
        return enforce_tier(tool["fn"](**(arguments or {})), self.ceiling)
