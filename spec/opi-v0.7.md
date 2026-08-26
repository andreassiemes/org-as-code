# OPI Specification v0.7 (Addendum)

**Status:** STABLE — tagged `v0.7.1`. Under the project's stability policy
([VERSIONING.md](../VERSIONING.md)) the spec text, schema, and validation rules of this
minor version do not change anymore; fixes ship as PATCH and never alter semantics. The
version was published as a public draft on 2026-07-09 and stabilized after implementation
feedback (no formal RFC round; see §8, DD-1).

**Baseline:** OPI v0.6 (rules 1–86). Everything in this addendum is **fully additive** —
v0.6, v0.5, and v0.4 documents work without modification.

---

## Abstract

OPI v0.7 makes decisions *live* and organizations *servable*. It introduces six features:

1. **Visibility Tiers** (`visibility:`, core attribute) — A data-classification attribute
   on entities and fields, independent of any consumer. One declaration governs rendering,
   exports, and serving alike. Enforcement is a consumer obligation with one hard rule:
   it happens in the serving layer, never in the client.
2. **Decision Lifecycle** — Decisions gain calibrated reversibility (`decision_type`),
   provisionality (`hypothesis` + `validate`/`validate_by`), honest history (`reopen_log`,
   supersede-not-edit), carried minority positions (`dissent`), strings attached
   (`conditions`), and first-class contradictions (`conflicts_with`). The fields are
   production-proven: they were extracted from a client decision system built on this
   model, not designed on a whiteboard.
3. **`ai:` Block** — RAG governance: which parts of the organization may enter LLM
   contexts, under which redaction and caching rules. Deliberately narrow — tool-level
   access semantics live in the Serving Profile, not here.
4. **Serving Profile** — The normative answer to what `context_endpoint: {format: mcp}`
   (declared since v0.5) actually serves: a deterministic field-type → tool-type
   derivation, three composite tools (`who_decides`, `get_decision_chain`,
   `get_agent_mandate`, SHOULD), and server-side visibility enforcement.
5. **Agent Mandate Provenance** (`mandate_source`, `valid_until`) — An `agents[]` entry
   already declares *what* an agent may touch and *where it escalates*. It could not
   declare *from whom that authority derives* — and therefore not what happens when the
   source of that authority goes away.
6. **Adoption Staircase** (non-normative) — Two lanes for OPI adoption: the personal
   repo-and-agent lane (L0/L1) and the served context-layer lane (L2). The boundary
   between them is the number of people, not the amount of data.

**Positioning.** v0.6 connected OPI to the open knowledge ecosystem (OKF). v0.7 connects
it to the *agent runtime*: an OPI repository remains the strict, versioned source of
truth — the Serving Profile defines how that truth is exposed to agents at scale without
ever leaving the repository's governance (PRs, history, drift detection).

## Maturity

| ✅ Normative and implemented | 🚧 Specified, implementation pending | ❌ Specified but unimplementable |
|---|---|---|
| Entity-level visibility tiers (rules 87–88, all entity types) · decision lifecycle (rules 90–93) · `ai:` block (rule 94) · Access Enforcement (§4.4, `--ceiling`) · agent mandate provenance (rules 99–100) | Serving Profile composite tools — SHOULD in v0.7, MUST from v1.0 (rules 95–98) | Field-level tiers (rule 89): no declaration syntax was ever specified — see §1.4 |

Dates promise; buckets describe. The third column exists because a specification that
quietly carries an unenforceable rule teaches readers to distrust the enforceable ones.

---

## What's New in v0.7

| Feature | Location | Description | Use Case |
|---------|----------|-------------|----------|
| **Visibility Tiers** | `visibility:` on entities/fields | `public \| internal \| restricted \| confidential` + mandatory `classification_reason` from `restricted` up | One classification, all consumers (render, export, serve) |
| **Decision Type** | `decisions[].decision_type` | `two-way \| one-way \| big-bet \| delegated` — calibrates required decision substance | Reversible decisions decided fast; irreversible ones decided well |
| **Hypothesis Decisions** | `decisions[].status: hypothesis` + `validate`, `validate_by` | Provisional decisions with an explicit validation criterion and deadline | Evidence before lock-in; overdue validations surface in tooling |
| **Reopen Log** | `decisions[].reopen_log[]` | Dated, reasoned reopen entries; re-deciding happens via supersede, never silent edit | Honest decision history; audit of evolved reasoning |
| **Dissent & Conditions** | `decisions[].dissent[]`, `decisions[].conditions` | Minority positions carried forward; decisions with strings attached | Disagreement is recorded, not erased |
| **Conflicts** | `decisions[].conflicts_with[]` | First-class contradiction edges that demand a resolution | Contradicting decisions become visible work, not folklore |
| **`ai:` Block** | `ai:` (top-level) | RAG governance: tier ceiling, redaction, embedding/caching rules | "How do I feed my org into LLMs safely" as declared policy |
| **Serving Profile** | §4 (+ `context_endpoint`) | Normative semantics for `format: mcp`: tool derivation, composite tools, enforcement | An org repo served to agents; `orgspec serve` is the reference implementation |
| **Adoption Staircase** | §5 (non-normative) | L0/L1 (personal lane) → L2 (served lane) | Honest guidance on when the context layer is needed — and when not |

---

## 1. Schema Reference: Visibility Tiers (`visibility:`)

### 1.1 The attribute

`visibility` is an OPTIONAL attribute on any entity (unit, member, gremium, decision,
agent, knowledge concept) and on individual fields of `decisions[]` entries.

```yaml
visibility: internal        # public | internal | restricted | confidential
classification_reason:      # REQUIRED for restricted and confidential
```

| Tier | Meaning | Consumer obligation |
|------|---------|---------------------|
| `public` | May appear anywhere, including public exports | none |
| `internal` | **Default.** Visible to the organization/program | exclude from public exports |
| `restricted` | Visible to a named circle | redact content; keep the entity's *existence* visible as a redacted card so graph topology stays honest |
| `confidential` | Kept out of the open repository entirely | never serialize; reference by id only |

**Design intent:** `visibility` is data classification, not an AI feature. The same
declaration governs a rendered HTML view, an OKF export (v0.6 §1), and a served MCP
endpoint (§4). Consumers differ in *mechanism*, never in *classification*.

### 1.2 Defaulting and inheritance

An entity without `visibility` is `internal`. A field-level `visibility` MAY only
*raise* the tier relative to its entity (an `internal` decision may have a `restricted`
field; a `restricted` decision cannot contain a `public` field).

### 1.3 Example

```yaml
decisions:
  - id: D-2026-014
    title: "Consolidate the two platform teams"
    visibility: restricted
    classification_reason: "restructuring — personnel impact"
    status: active
    driver: coo
    approver: exec-board
```

A conformant renderer shows D-2026-014 to non-circle readers as a redacted card
(id, date, tier — no title, no substance). A conformant server (§4) omits its content
from tool results for keys below `restricted` — and does not advertise field-filter
tools that would leak its values.

### 1.4 Enforcement status of the tier model

Entity-level classification is specified and enforced as of v0.7.1:

- **Rules 87 and 88 apply to every entity** — units, members, gremien, agents, knowledge
  concepts, and decisions. The reference validator checks all of them.
- **§4.4 Access Enforcement is implemented.** `orgspec serve --ceiling <tier>` redacts
  entities above the ceiling to a card (id, date, tier) and never serializes
  `confidential` at any ceiling — that tier means *kept out of the open repository
  entirely*, not *needs a higher key*.

**One gap remains, and it is a specification defect rather than an implementation one.**
§1.1 and §1.2 describe `visibility` on *individual fields* of `decisions[]` entries, and
Rule 89 constrains such field tiers — but **no syntax for declaring a field-level tier
was ever specified**: there is no schema construct for it and no example. A rule whose
subject cannot be expressed cannot be implemented, and defining that syntax would be new
semantics, not a patch.

Rule 89 therefore stands unimplementable until v0.8 resolves it in one of two ways:
by specifying the syntax, or by withdrawing the rule and the two sentences that promise
it. Until then, treat field-level classification as absent: classify the whole decision.
*(Resolved in the v0.8 draft: withdrawn — see [opi-v0.8.md §3.4](opi-v0.8.md).)*

**Consequence for adopters.** Entity tiers are enforced end to end — declaration,
validation, serving. Field tiers are not, because they cannot be written down.

---

## 2. Schema Reference: Decision Lifecycle

### 2.1 New fields on `decisions[]`

**Example 1 — a commitment with carried dissent and a condition (one-way door):**

```yaml
decisions:
  - id: D-2026-002
    title: "Every recorded decision names a single accountable decider"
    status: active
    decision_type: one-way        # irreversible — requires rationale (Rule 90)
    driver: coo
    approver: exec-board
    rationale: "Post-mortems kept ending at 'the board decided' with no one able to reopen"
    conditions: "Mandate registry must exist before enforcement"
    dissent:
      - "People lead: group accountability protects juniors; revisit at Q4 review"
    review_date: 2026-10-01
```

**Example 2 — a hypothesis with its test, later superseded (honest history):**

```yaml
decisions:
  - id: D-2026-009
    title: "Usage-based pricing for the API product"
    status: hypothesis            # additive enum value (see 2.2)
    decision_type: big-bet
    validate: "3 design partners convert AND billing tickets stay under 5/month"
    validate_by: 2026-09-30
    conflicts_with: [D-2026-004]  # contradicts the seat-based GA decision — needs a resolution

  - id: D-2026-004
    title: "Seat-based pricing at general availability"
    status: superseded            # re-decided via supersede, never silent edit (Rule 92)
    decision_type: two-way
    reopen_log:
      - "2026-06-03 — two enterprise deals stalled where usage concentrated in few power users"
```

| Field | Type | Semantics |
|-------|------|-----------|
| `decision_type` | enum | `two-way` (reversible), `one-way` (irreversible), `big-bet` (high stakes), `delegated`. Calibrates the required decision substance: `one-way`/`big-bet` decisions SHOULD carry rationale and risks; `two-way` decisions are allowed to be fast |
| `validate` | string | The criterion that turns a hypothesis into a commitment |
| `validate_by` | date | Deadline for validation; overdue hypotheses surface in tooling |
| `reopen_log[]` | list | `"YYYY-MM-DD — reason"` entries. The *quality of the reason* is the point, not the count |
| `dissent[]` | list | Minority positions carried forward beyond `consulted` |
| `conditions` | string | For "decided with a condition" (Auflage) |
| `conflicts_with[]` | list | Ids of contradicting decisions — a declared conflict demands a resolution slot |

### 2.2 `status: hypothesis` (additive enum value)

The `status` enum gains `hypothesis`: a decision taken provisionally, with an explicit
validation criterion. Per the v0.6 Permissive Consumer Model (rules 82–84), v0.6
consumers encountering the unknown value degrade gracefully; v0.7 validators enforce
that hypotheses carry `validate` + `validate_by` (Rule 91).

**Lifecycle:** `hypothesis → active` (validated) or `hypothesis → revoked` (falsified),
each via a dated update. Re-deciding an `active` decision happens by creating a new
decision that `revises` the old one and setting the old one to `superseded` — never by
silently editing the record (Rule 92).

### 2.3 Provenance

These fields were extracted from a production decision-capture system (35+ real program
decisions, June 2026) and generalized. `decision_type` calibrating required substance,
`reopen_log` over silent edits, and carried `dissent` are the three mechanics that
proved themselves in practice.

---

## 3. Schema Reference: The `ai:` Block

RAG governance — the declared policy for feeding organizational content into LLM
contexts. Deliberately narrow: the `ai:` block governs *content flow into models*;
tool-level access semantics are the Serving Profile's job (§4).

```yaml
ai:
  context_ceiling: internal      # highest visibility tier that may enter LLM contexts
  redact:                        # patterns/fields stripped before any model call
    - "members[].name"           # e.g. serve roles, not persons
  embeddings:
    allowed: true
    ceiling: internal            # tier ceiling for vector stores (may be stricter)
    store: local                 # local | private-cloud | none
  caching:
    allowed: true
    ttl_days: 30                 # cached completions/context expire
  provenance: required           # model-facing exports carry source refs (v0.6 log.md)
```

| Key | Semantics |
|-----|-----------|
| `context_ceiling` | No content above this tier enters a prompt, context window, or fine-tune. Default: `internal` |
| `redact[]` | Field paths/patterns stripped before model exposure, regardless of tier |
| `embeddings.ceiling` | Vector stores persist; their ceiling MAY be stricter than the context ceiling, never looser |
| `caching` | Whether and how long model-side caches may retain org content |
| `provenance` | Whether model-facing exports must carry source references |

**Relationship to §1 and §4:** The `ai:` block *consumes* the visibility classification
(§1); it never redefines it. A serving implementation (§4) MUST apply the `ai:` block's
ceiling and redaction on top of key-tier enforcement.

---

## 3a. Schema Reference: Agent Mandate Provenance

An `agents[]` entry already declares *what* an agent may touch (`scope`) and *where it
escalates* (`escalation_path`). What it cannot express is *from whom that authority is
derived* — and therefore what happens when the source of that authority goes away.

### 3a.1 The attributes

```yaml
agents:
  - ref: support-triage-agent
    mandate_source: platform-council    # role_ref or gremium the authority derives from
    valid_until: 2026-10-31             # optional; the derivation expires
    scope:                              # unchanged (v0.5)
      units: [payments]
      data: [tickets, order-state]
    escalation_path: [payments, platform-council]
```

| Key | Semantics |
|-----|-----------|
| `mandate_source` | OPTIONAL. A `role_ref` (from `components.roles`) or a gremium id from which this agent's authority is derived. When absent, the agent is an independent actor and its `scope` stands on its own — it must then be justified wherever an independent actor would be |
| `valid_until` | OPTIONAL. ISO date after which the derivation no longer holds. Consumers MUST evaluate it against an external timestamp — a commit date, a CI run, a ratification reference — never against a value the agent itself writes |

**Design intent.** `mandate_source` is provenance, not delegation: the agent remains the
actor of its own operations, and nothing in this section reassigns authorship. The
declaration answers a governance question — *who is answerable for this agent being
allowed to do this* — that neither `scope` nor `escalation_path` answers.

**Revocation is not a field.** An agent's derived mandate ends when its source ceases to
exist. That is referential integrity (Rule 100), not a lifecycle flag: remove the role or
the gremium, and every mandate derived from it fails validation on the next run. A
dedicated `on_revoked` key would imply a state in which revocation does *not* propagate.

---

## 4. Serving Profile (normative for serving implementations)

> Fills the declaration that has existed since v0.5: an agent's `context_endpoint` with
> `format: mcp`. This chapter defines what a conformant MCP context endpoint serves.
> Reference implementation: `orgspec serve`.

### 4.1 Principle: the repository never leaves

A serving implementation exposes an OPI document set to agents **without moving the
source of truth**. The repository (files, PRs, history, drift detection) remains
canonical; the server is a stateless projection of the working tree (or a named ref).
This is the deliberate divergence from database-backed context layers: retrieval and
access control are added *on top of* the versioned truth, not instead of it.

### 4.2 Tool derivation (deterministic)

A conformant server derives its tool catalog from the schema — never hand-curated per
deployment:

| Schema shape | Generated tool | Example |
|---|---|---|
| entity with `id` | `get_<entity>_by_id` | `get_unit_by_id` |
| enum / tag field | `filter_<entity>_by_<field>` | `filter_decisions_by_status` |
| free-text field | `search_<entity>_by_text` | `search_decisions_by_text` (title + rationale) |
| date / numeric field | `find_<entity>_by_<field>_range` | `filter_decisions_by_review_date_range` |
| declared relation | traversal tool | `get_unit_children` (from `parent`) |

Tool descriptions carry the schema field descriptions — the agent learns the org's
query surface from the tool catalog alone; no schema documents travel into prompts.

### 4.3 Composite tools (SHOULD)

Three tools encode organizational semantics beyond generic schema serving. A conformant
server **SHOULD** provide them in v0.7; they become **MUST** in v1.0 alongside the
conformance suite:

| Tool | Question it answers | Resolution |
|------|--------------------|-----------|
| `who_decides(topic)` | "Who can decide this?" | resolves via units → gremien → decisions (driver/approver + mandate) |
| `get_decision_chain(id)` | "How did we get here?" | traverses `revises`, `triggers`, `consequences`, `supersedes`, `conflicts_with` |
| `get_agent_mandate(ref)` | "What may this AI agent decide, and where does it escalate?" | reads `agents[]` scope + `escalation_path` — the governance answer for agent oversight |

### 4.4 Access Enforcement (MUST)

1. **Server-side, never client-side.** Visibility enforcement (§1) happens in the
   serving layer. A conformant server MUST NOT rely on the client or the model to
   filter.
2. **Keys carry tiers.** Every agent key binds a maximum visibility tier (and MAY bind
   a unit scope). Results above the key's tier are redacted per §1.1.
3. **The catalog is filtered too.** Fields above the key's tier generate **no tools**
   for that key — absence over access-denied. A key must not be able to enumerate what
   it cannot see.
4. **Identity never travels through the model.** The key/identity binding lives in the
   serving layer; tools take no caller-identity parameters. A model cannot escalate a
   tier by asking.
5. **`ai:` ceiling applies on top.** Key tier and `ai.context_ceiling` compose; the
   stricter one wins.

### 4.5 Write path (deliberately absent)

The Serving Profile is **read-only**. Changes to the organization travel through the
repository's change process (PRs, reviews — `governance.change_process`). A future
`propose_change` tool MAY create a branch/PR; it will never write to the working tree.

---

## 5. Adoption Staircase (non-normative)

Two architectures, both legitimate — the boundary is the number of people, not the
amount of data:

| Level | Lane | Setup | Fits |
|-------|------|-------|------|
| **L0** | Personal | An org repo + a human reading it | Solo founders, consultants, small teams documenting |
| **L1** | Personal + agent | The repo + a local coding agent (Claude Code etc.) reading YAML directly | One operator with full visibility. **No server needed — deliberately.** |
| **L2** | Served | `orgspec serve` + agent keys with tiers | Multiple people/agents, partial visibility, live queries |

**The breaking point** between L1 and L2 is not scale of data — a repo handles thousands
of decisions — but the moment *other people* (or their agents) consume the model: they
need retrieval without full-file reads, and they must not see everything. That is a
context-layer problem, not a memory problem. Moving to L2 changes the access
architecture; it does not change the source of truth.

Do not start at L2. Every OPI adoption begins as a repo one person can read.

---

## 6. Validation Rules (v0.7)

Rules continue numbering from v0.6 (last rule: 86). Rules 87–89 cover Visibility;
90–93 cover the Decision Lifecycle; 94 covers the `ai:` block; 95–98 cover the Serving
Profile (conformance rules for serving implementations, not document lint); 99–100 cover
Agent Mandate Provenance.

### Rules 87–89: Visibility

#### Rule 87: Valid Tier Values

**Assertion:** If present, `visibility` MUST be one of `public`, `internal`,
`restricted`, `confidential`. Absent means `internal`.
**Level:** ERROR

#### Rule 88: Classification Reason from `restricted` Up

**Assertion:** An entity or field with `visibility: restricted` or
`visibility: confidential` MUST carry a non-empty `classification_reason`.
**Rationale:** Restriction without a stated reason is unaccountable secrecy; the reason
is metadata and stays visible even where content is redacted.
**Level:** ERROR

#### Rule 89: Fields May Only Raise the Tier

**Assertion:** A field-level `visibility` MUST be equal to or stricter than its
entity's tier.
**Level:** ERROR
**Status (v0.7.1): unimplementable as written.** No syntax for declaring a field-level
tier is specified anywhere in v0.7 — see §1.4. The rule is kept in place, unenforced,
rather than silently dropped; v0.8 either specifies the syntax or withdraws it together
with the two sentences in §1.1 and §1.2 that promise the feature.
**Resolution (v0.8 draft, 2026-08-22): withdrawn.** See [spec/opi-v0.8.md §3.4](opi-v0.8.md).
The number is not reused; this v0.7 text is left as published (stability policy) and the
withdrawal, with its consequential strikes in §1.1, §1.2, §1.4 and §4.4, is declared there.

### Rules 90–93: Decision Lifecycle

#### Rule 90: Valid `decision_type`

**Assertion:** If present, `decision_type` MUST be one of `two-way`, `one-way`,
`big-bet`, `delegated`. For `one-way` and `big-bet`, a missing `rationale` is a WARN.
**Level:** ERROR (enum) / WARN (substance)

#### Rule 91: Hypotheses Carry Their Test

**Assertion:** A decision with `status: hypothesis` MUST have non-empty `validate` and
`validate_by`. A `validate_by` in the past is a WARN (overdue validation).
**Level:** ERROR / WARN

#### Rule 92: Re-decide via Supersede, Never Silent Edit

**Assertion:** A decision whose substance changed (title, rationale, approver) without
a `reopen_log` entry or a superseding decision SHOULD be flagged. `reopen_log` entries
MUST be `"YYYY-MM-DD — reason"` with a non-empty reason.
**Level:** WARN (heuristic) / ERROR (format)

#### Rule 93: Conflicts Must Resolve

**Assertion:** `conflicts_with[]` entries MUST reference existing decision ids. Two
decisions in a declared conflict where both are `active` past either's `review_date`
is a WARN — a conflict is work, not decoration.
**Level:** ERROR (refs) / WARN (staleness)

### Rule 94: `ai:` Ceilings Compose Strictly

**Assertion:** `ai.embeddings.ceiling` MUST be equal to or stricter than
`ai.context_ceiling`. Redact paths MUST parse against the schema.
**Level:** ERROR

### Rules 95–98: Serving Profile (conformance)

*These rules bind serving implementations, not documents. `orgspec lint` does not check
them; the v1.0 conformance suite will.*

#### Rule 95: Server-Side Enforcement

**Assertion:** A conformant server MUST enforce visibility tiers in the serving layer.
Shipping unredacted content and instructing the client/model to filter is
non-conformant.

#### Rule 96: Filtered Catalog

**Assertion:** Tools whose result surface lies entirely above a key's tier MUST NOT
appear in that key's tool catalog.

#### Rule 97: No Model-Supplied Identity

**Assertion:** Tools MUST NOT accept caller-identity parameters. Identity and tier
bind to the key in the serving layer.

#### Rule 98: Composite Tools

**Assertion:** A conformant server SHOULD provide `who_decides`, `get_decision_chain`,
and `get_agent_mandate` with the semantics of §4.3. (MUST from v1.0.)
**Note:** This enumeration is non-exhaustive; the table in §4.3 is the authoritative list.

### Rules 99–100: Agent Mandate Provenance

#### Rule 99: Derived Mandates Compose Strictly

**Assertion:** If an agent declares `mandate_source`, its `scope` MUST NOT exceed the
authority of that source in any dimension the document makes resolvable. Which dimensions
those are depends on what the source is:

| Source is a… | `scope.units` | `scope.gremien` |
|---|---|---|
| **role** (`components.roles`) | subset of units with `owner: <source>` | subset of gremien listing the source in `members` |
| **gremium** | not resolvable — a gremium does not own units | the source gremium itself only |

A scope entry that names an entity absent from the document is out of scope for this rule;
existing referential-integrity checks cover that case.
**Rationale:** A derived authority that exceeds its origin is not a derivation but a new
grant, and must be declared as one. Same composition principle as Rule 94, one level up.
**Level:** ERROR
**Implementation note:** `components.roles.<key>` carries `title`, `level`, `purpose`, and
`accountabilities` — it does not declare decision types, so `scope.decision_types` is not
checked. A rule that demanded information the schema does not hold would be
unimplementable, not strict (§8, DD-11).

#### Rule 100: Mandate Source Must Resolve

**Assertion:** A `mandate_source` MUST resolve to an existing `role_ref` in
`components.roles` or to an existing gremium id.
**Rationale:** This is the revocation mechanism. Remove the role, and every mandate
derived from it fails validation on the next run — no separate revocation step, no window
in which an orphaned agent keeps its authority.
**Level:** ERROR

---

## 7. Backward Compatibility

All v0.7 features are additive. `visibility` defaults preserve current behavior
(everything today is implicitly `internal`). `status: hypothesis` relies on the v0.6
Permissive Consumer Model — v0.6 consumers tolerate the unknown enum value by design
(rule 84). No field is renamed, removed, or re-typed. v0.6 documents validate unchanged
under v0.7.

`mandate_source` and `valid_until` (§3a) are OPTIONAL keys on `agents[]`; an agent without
them behaves exactly as in v0.6. Rules 99 and 100 fire only when `mandate_source` is
present, so no existing document gains a finding from them.

---

## 8. Design Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| DD-1 | **Public draft, no formal RFC round** | An RFC with a comment deadline and no audience is documented silence. The draft ships under the release process with open Discussions; design-partner review runs on dedicated issues. The formal RFC process is defined in GOVERNANCE.md and debuts at v1.0-RC, when implementers exist to comment |
| DD-2 | **`visibility` in the core, not in `ai:`** | Classification is consumer-independent; renderers, exporters, and servers all need it. Binding it to AI would force a second mechanism for every other consumer |
| DD-3 | **Composite tools SHOULD, not MUST** | A MUST nobody can test weakens the spec; the conformance suite arrives with v1.0. Naming and specifying the tools now claims the semantics |
| DD-4 | **Serving is read-only** | The write path *is* the repository's change process. An endpoint that mutates the org bypasses the governance OPI exists to provide |
| DD-5 | **Lifecycle fields over a state machine** | A full workflow engine in the schema would be premature; dated logs (`reopen_log`), explicit tests (`validate_by`), and supersede edges express the lifecycle without prescribing tooling |
| DD-6 | **Declare what people must honour, not what machines can enforce** | Systems that couple declaration to enforcement can only express rules with an enforcement point — file permissions, transport hooks, channel membership. An organisation's binding rules mostly have none: a mandate holds because people honour it. OPI declares that class of rule; it does not pretend to enforce it |
| DD-7 | **A decision is not its effect** | Recording that something was decided must never imply that it happened. The two are separate facts with separate timestamps, and conflating them makes the record claim more than it knows |
| DD-8 | **A derivation never exceeds its source** | Applies to `ai:` ceilings (Rule 94), to agent mandates (Rule 99), and to any future authority-over-authority relation. Where a derived thing would need more than its origin, the model is wrong, not the ceiling |
| DD-9 | **Self-reported values need an external anchor** | A time bound set by the party it constrains is not a bound. Anything an entity writes about its own rights, validity, or freshness MUST be evaluated against a timestamp outside its control — this is why `valid_until` (§3a) is explicitly not checked against a value the agent supplies |
| DD-10 | **State maturity in three buckets, not as a roadmap** | Implemented / specified-but-unimplemented / opinion-without-text. Dates promise; buckets describe. A reader deciding whether to build against the specification needs the second, not the first — §1.4 applies this to the specification itself |
| DD-11 | **A rule fires only where the document can answer it** | Rule 99 checks the dimensions `components.roles` and the entity graph actually carry, and stays silent on the rest. A rule that demands information the schema does not hold is not strict — it is unimplementable, and an unimplementable ERROR trains readers to ignore the validator |

### Relation to agentic workspaces

Agentic collaboration platforms — Block's Buzz is the most developed public example —
declare authority wherever a runtime can enforce it: who may push to a protected branch,
who may moderate, who is in which channel. Their guarantees are strong precisely because
an enforcement point exists.

An organisation's binding rules mostly have no such point. That a committee decides budget
allocation for the next two quarters, with a named escalation path, is not a question any
relay can answer — it holds because it was declared, ratified, and is honoured.

OPI declares that second class. The two are complementary rather than competing: a mandate
without an enforcement point stays paper, and an enforcement point without a mandate does
not know what it is enforcing.

---

## 9. Changelog

- **2026-07-09** — Initial public draft. Visibility tiers, decision lifecycle, `ai:`
  block, Serving Profile (rules 87–98), Adoption Staircase.
- **2026-07-09 (same day)** — Draft schema (`spec/opi-v0.7.schema.json`, additive delta
  on v0.6) and validator support shipped alongside the reference implementation
  (`orgspec serve`, see `orgspec/README.md`): `tools/validate.py` enforces rules 87,
  88, and 90–93 version-aware (`status: hypothesis` requires `opi: 0.7.x`), and
  `examples/serve-demo/` is a real v0.7 document. The implementation tested the draft
  before publication — one adjustment fed back: reopen-log format validation accepts
  both em-dash and hyphen separators.
- **2026-08-01** — **Stabilized as `v0.7.0`.** Added: Agent Mandate Provenance (§3a,
  rules 99–100); §1.4, which states plainly which parts of the tier model are enforced
  today and which are not; design decisions DD-6 to DD-11 and the relation to agentic
  workspaces (§8). Retitled §4.4 from *Enforcement* to *Access Enforcement*, so that one
  word does not name both access control and effect in the world. Rule 98's list of
  composite tools is marked non-exhaustive against the table in §4.3. Corrected the `$id`
  of `opi-v0.7.schema.json`, which carried the v0.6 URL. The specification file dropped
  its `-draft` suffix; references in `tools/`, `orgspec/`, and the examples follow.
- **2026-08-01 — `v0.7.1`.** Closes the tier gap §1.4 declared, and reclassifies what
  cannot be closed. No specification text changed its meaning; this is implementation
  plus an honest status.
  - Rules 87–88 now apply to **every** entity type, not only `decisions[]`
    (`tools/validate.py`). The spec has said so since §1.1; the validator had not.
  - **§4.4 Access Enforcement is implemented.** `orgspec serve --ceiling <tier>` redacts
    entities above the ceiling to a card and enforces absence over access-denied. A
    verification test found `confidential` passing through at the highest ceiling; that
    tier is now never serialized at any ceiling, because it means *kept out of the open
    repository entirely* rather than *needs a higher key*. `--ceiling` accepts
    `public|internal|restricted` for the same reason.
  - **Rule 89 is marked unimplementable**, not merely unimplemented: field-level tiers
    have no declaration syntax anywhere in v0.7. The rule stays in place, unenforced and
    labelled, for v0.8 to specify or withdraw (§1.4).
  - Added the Maturity table promised by DD-10, and `examples/serve-demo/dec-007` — the
    first example in the repository that actually carries a tier.
