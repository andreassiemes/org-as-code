# OPI Specification v0.8 (Addendum): Effect and Legitimacy

**Status:** STABLE — tagged `v0.8.0`, 2026-08-26. Published as a public draft on
2026-08-22 and stabilized after the reference implementation ran against it. Under the
project's stability policy ([VERSIONING.md](../VERSIONING.md)) the text, schema and rules
of this minor version do not change anymore; fixes ship as PATCH. There was no formal RFC
round (see §8, DD-1).

What a stable label does *not* claim here is stated in Maturity below: no organisation has
kept `enforcement` and `approval` current across a year of decisions yet. That is an
evidence gap, not a specification gap, and this project's policy does not let it hold a
version back.

**Baseline:** OPI v0.6 (rules 1–86) plus OPI v0.7 (rules 87–100, including Agent Mandate
Provenance) — **stable since 2026-08-01**, released as `v0.7.0`/`v0.7.1`. Everything in this
addendum is **fully additive** — v0.7, v0.6, v0.5 and v0.4 documents validate without
modification.

**Rule range:** 101–103. **Design decisions:** DD-12, DD-13, DD-14 (v0.7.0 occupies DD-11,
the implementation note on Rule 99). v0.9 begins at Rule 104 and DD-15; no numbers are
reserved for deferred material.

---

## Abstract

Up to v0.7, OPI records that something **was decided** — by whom, in which body, with which
reversibility, under which condition. v0.8 adds the two facts that surround the same
decision: whether it was **entitled to bind**, and whether it **took effect**. Both are
recorded as dated facts with an external anchor, never as an implication of the decision
itself.

1. **Decision effect** (`decisions[].enforcement`) — the effect of a decision as a separate
   dated fact with an external anchor, so the record never claims that something happened
   because it was decided.
2. **Approval and quorum** (`decisions[].approval`) — how many consents a decision needed and
   which ones exist, each anchored to evidence that already lives in the repository.
3. **One read path** (`get_undelivered_decisions`, v0.7 §4.3 amended) — the question "what did
   we decide and never carry?" as traffic rather than as an audit.
4. **A bounded derivation** (Rule 103, v0.7 §4.2 amended) — v0.8 places nested blocks on a
   served entity, so the rule that stops a catalog from growing with the schema is this
   version's own cleanup, not a general opinion.
5. **One withdrawal** (Rule 89, field-level tiers, §3.4) — v0.7.1 marked the rule
   unimplementable as written; v0.8 honours the published commitment by withdrawing it,
   together with the two sentences in v0.7 §1.1/§1.2 that promise the feature. No document
   is affected: a syntax for field tiers never existed.

**Positioning.** v0.7 made an organisation servable. v0.8 makes a decided organisation
answerable for its own record: an effect that either happened or visibly did not, and a
quorum that either holds or is a false record. All three of the version's failure modes are
one failure mode — a record that claims more than it knows (DD-7): a decision read as its
effect, a quorum asserted without its consents, an empty answer read as "nothing open".

Exactly one mechanism in v0.8 asks nobody to be diligent: `get_undelivered_decisions`
answers Rule 101's question continuously, for whoever asks, without a follow-up ritual. The
two fields it reads are written by people, weeks after the decision, and the coverage line is
the only counter-pressure the version has — v0.8 does not remove the diligence, it makes its
absence countable.

---

## Maturity

| Bucket | What it covers |
|---|---|
| ✅ **Implemented in the reference implementation** | **Rules 101 and 102** in `tools/validate.py` (with the warning severity and `--as-of` clock of §7), the **v0.8 JSON Schema** (`spec/opi-v0.8.schema.json`, additive on v0.7), **`get_undelivered_decisions`** in `orgspec serve` with key-bounded coverage (§3.2), and **Rule 103 in full** — the server derives no tool from a field no served document populates and nothing over nested lists and objects, which is what §3.1 needs so that v0.7 §4.2 can no longer be read as licence to serve the whole schema. `examples/serve-demo/org.yaml` carries both blocks; the fixtures of §7 run under `tests/` |
| 🚧 **Open, not blocking** | **Use over time.** Every rule of this version runs, and the specification text is settled. What is still missing is longevity: no organisation has kept `enforcement` and `approval` current across a year of decisions. That is a gap in evidence, not in the specification, and under this project's stability policy it does not hold a version back — a stable label promises that the text stops moving, not that the world has caught up with it (see [VERSIONING.md](../VERSIONING.md), *Note on enforcement*). Of the two numbers in §1.5, effect latency is computable today on `examples/org-as-code-self`; relapse rate is not, because no decision there has lapsed yet |

v0.8 is the first version since v0.6 that ships with its rules implemented on the day the
draft is published: nothing in it waits for git access, visibility tiers or a conformance
suite. What it still waits for is use — and use is what a specification earns after it
settles, not a condition it must satisfy before. The Rule 89
withdrawal (§3.4) has no implementation dimension: it strikes text whose subject could
never be written down.

---

## 1. Schema Reference: Decision Enforcement (`decisions[].enforcement`)

### 1.1 The separate fact

A decision and its effect are two facts with two timestamps. `decisions[].date` records when
a body decided. `decisions[].enforcement` records what happened afterwards in the world. OPI
keeps them apart so that the record never claims more than it knows (DD-7). For the same
reason `enforced` is deliberately absent from the `decisions[].status` enum: folding effect
into the decision's own status is one field for two facts, and no way to say "decided in
February, effective in May".

`enforcement` is an OPTIONAL object on any `decisions[]` entry. **Its absence asserts
nothing** — an absent block does not mean "not enforced", it means the model is silent about
effect. Silence is a legitimate state; a wrong claim is not. Because silence is the block's
absence and not an empty block, `status` is REQUIRED as soon as `enforcement` is present: an
`enforcement: {}` would raise the coverage count without stating a fact (Rule 101).

`enforcement` is deliberately **not** a workflow state. It carries no transitions, no step
history, no assignees and no reminder state. The field carries dates; whether anyone is
reminded of them is a tooling question — Rule 101's overdue finding and
`get_undelivered_decisions` (§3.2) are exactly that, and they live in the tool, not in the
record (DD-5, DD-12).

The key is called `status` and not `state` although the word now occurs three times in one
specification (top-level `status`, `decisions[].status`, `enforcement.status`): each is the
standing of the object that carries it, the objects are distinct, and one word for one
concept across three scopes is better vocabulary than two words for it.

**Two clocks, and which one may be self-written.** DD-9 requires an external anchor for
self-reported values, and this block contains both kinds of value, so the distinction is
stated once here and holds for the whole specification. An **observation** about one's own
state — that an effect occurred, on which day, that a consent was given — needs an anchor in
a system the document does not own (a commit, a ticket, minutes); that is what `ref` is for,
and why a date without one is self-report. The anchor is outside the document, not necessarily
outside the organisation. An **expectation** about one's own future — `expected_by`, and likewise
`review_date` and `validate_by` from earlier versions — can only come from the organisation
itself; nothing external could author it. What must lie outside the document for an
expectation is not the bound but the **clock** it is judged by, which is why Rule 101's
overdue finding takes its date from a parameter and not from the file. Observations are
anchored; expectations are timed.

**Backfilling is not a lesser record.** A `first_effect_at` entered months after the fact,
with an anchor, is formally equivalent to one maintained as it happened: the day of the
effect is in the document, the day of the entry is in the repository's history. OPI does not
distinguish the two and does not try to — the first latency measurement of any adopting
organisation is a backfill, and a specification that graded backfills would make its own
first measurement impossible.

**Example 1 — a decision that took effect, with an external anchor:**

```yaml
decisions:
  - id: dec-001
    date: 2026-05-04
    title: "Platform team owns the shared event schema"
    status: active
    decision_type: one-way
    gremium: exec-board
    driver: head-of-platform
    approver: exec-board
    scope: program
    rationale: "Three teams shipped incompatible event names in one quarter"
    enforcement:
      status: in_effect
      first_effect_at: 2026-05-27          # T3 — the first action that implemented it
      ref: "pr:platform-1284"              # external anchor (DD-9), not a signature
```

**Example 2 — decided, not yet carried, and overdue (Rule 101 WARNING):**

```yaml
decisions:
  - id: dec-002
    date: 2026-02-10
    title: "Every incident review names a single accountable owner"
    status: active
    decision_type: two-way
    gremium: ops-council
    driver: coo
    approver: ops-council
    scope: unit
    rationale: "Reviews kept ending with a team name instead of a person"
    conditions: "Incident template must gain an owner field first"
    enforcement:
      status: pending
      expected_by: 2026-04-30              # judged by a clock outside the document
```

**Example 3 — an effect that happened and did not hold:**

```yaml
decisions:
  - id: dec-003
    date: 2026-01-15
    title: "Weekly release train replaces on-demand deploys"
    status: active
    decision_type: two-way
    gremium: ops-council
    driver: head-of-delivery
    approver: ops-council
    scope: unit
    rationale: "Unbatched deploys caused four rollbacks in December"
    enforcement:
      status: lapsed
      first_effect_at: 2026-01-29          # it did happen once
      lapsed_at: 2026-03-16                # and stopped on a day, like every other fact
      ref: "commit:8f1c2ad"                # and the anchor stays
```

| Key | Semantics |
|---|---|
| `status` | REQUIRED where `enforcement` is present. Enum: `pending` (effect expected, none observed yet), `in_effect` (a first effect happened and holds — this is T3), `lapsed` (an effect happened and no longer holds; the reversal of an effect that occurred). The enum is closed for documents declaring opi 0.8.x: a v0.8 validator reports any other value as an ERROR (Rule 101). A later minor version that adds a value does so under its own version gate; a v0.8 validator that rejects such a document is conformant, not broken (§7). There is no `superseded` value: superseding changes the standing of the *decision*, never the fact that its effect did or did not occur |
| `first_effect_at` | OPTIONAL date (`YYYY-MM-DD`). The first action that implemented the decision. REQUIRED when `status` is `in_effect` or `lapsed` — both assert that an effect occurred. MUST NOT be present when `status: pending`, and MUST NOT precede `decisions[].date`: an effect cannot precede its cause |
| `lapsed_at` | OPTIONAL date (`YYYY-MM-DD`). The day the effect stopped holding. REQUIRED when `status: lapsed`, MUST NOT be present for `pending` or `in_effect`, and MUST NOT precede `first_effect_at`. Every other asserted fact in this block carries its day; a lapse without one would be the one exception, and it would make the relapse rate (§1.5) uncomputable |
| `expected_by` | OPTIONAL date (`YYYY-MM-DD`). The date by which a first effect was expected — a declared expectation, not a promise the repository can keep. It becomes a finding only when a clock outside the document passes it (Rule 101). Where it is absent, no overdue finding is raised at all, and the coverage line counts the omission separately: an expectation OPI does not have is one it must not invent from another field |
| `ref` | OPTIONAL string. External anchor for the asserted effect — a commit, pull request, ticket or minutes id. RECOMMENDED shape `<kind>:<value>`, the same shape as `approval.records[].ref` (§2). It is an **anchor, not a signature** (DD-6): nothing verifies it, but a date without one is self-report (DD-9). MAY be present on `pending` (e.g. a ticket tracking the expected effect); no finding |

`x-*` extension keys are permitted, as everywhere in OPI.

**Design intent — one anchor, and it stays one.** `ref` is a single string. Where two
artifacts evidence one effect, the document names the one that is canonical for the fact and
leaves the other to prose or an `x-` field. If a real corpus ever demands more, the additive
answer is a new `refs[]` key, never a re-typing of `ref` — a `string | [string]` union would
force every consumer into two code paths for the ordinary case, and re-typing a published
key is closed to us (R1).

**Design intent — the block records enforcement, and the version is called Effect.** The
alternative name `decisions[].effect` was considered and rejected. What the block records is
whether a decision was *carried* — enforcement in the organisational sense, the sense in
which people honour a rule (DD-6) — while "effect" stays free as the abstract noun the
specification needs in prose, in DD-7 ("a decision is not its effect") and in the metric
names of §1.5. The price is one word naming two things in one specification, and it is paid
in §3.3 by retitling the serving section rather than by renaming the field.

**Coverage, not silence.** A validator SHOULD report, once per run, two numbers:
`enforcement: N/M active decisions carry a block, K/N of those state an expectation`. Rule 101
never flags an absent block and never flags a missing `expected_by`, so this line is the only
thing that keeps either omission from being the cheapest route to a clean report. The second
half is not decoration: a document whose every active decision carries
`enforcement: {status: pending}` and no `expected_by` produces no finding at all and would
otherwise report perfect coverage. The line is normative-adjacent on purpose — a note, never
a finding. The validator SHOULD report approval coverage the same way (`approval: N/M active
decisions carry a quorum`), see §7.

### 1.2 Which decisions expect an effect

`enforcement` MAY appear on a decision in any `status`; a hypothesis is often put into effect
precisely in order to test it. Only `status: active` decisions are *expected* to produce an
effect, and only they can produce the Rule 101 overdue WARNING. `planned`, `hypothesis`,
`revoked` and `superseded` decisions never do.

### 1.3 Supersede, reopen, lapse

**An `enforcement` block is never rewritten because the decision's standing changed.** When a
decision moves to `superseded`, its recorded effect stays as it was: if it took effect, it
took effect, and the record must keep saying so. The successor decision carries its own
`enforcement` block and its own T3. This is what makes effect latency computable across a
decision chain instead of collapsing on every re-decision.

A `reopen_log` entry on a decision whose enforcement is `in_effect` is a **relapse**: a
decision that was carried and is being negotiated again. Both facts then stand in the same
record, which is exactly the point.

If the effect itself was rolled back, set `status: lapsed`, **keep** `first_effect_at` and
`ref`, and add `lapsed_at`. This is why the enum has a third value rather than two: the
reversal is a second fact about the same event, not a reason to delete the first, and
`pending` asserts no effect the anchor could evidence. A `ref` MAY still be present on
`pending` (e.g. a ticket tracking the expected effect); Rule 101 raises no finding for it.
Each value therefore states exactly one dated fact — an
effect is awaited, holds, or held and stopped. The case "never happened at all" is not a
fourth value: it is `pending` with an `expected_by` that has passed, where Rule 101 already
makes it visible and where no anchor exists that a validator could check.

**The block carries one episode.** `enforcement` records the first effect of a decision and
whether that effect still holds. Once written, `first_effect_at`, `lapsed_at` and `ref` MUST
NOT be removed or altered; only `status` moves, and it moves forward
(`pending` → `in_effect` → `lapsed`). A second episode — an effect that lapsed and later
returned — is deliberately not representable in one block, because representing it would make
the block a process (DD-12). Where an organisation re-established the effect, it did so by
deciding again, and that decision carries its own block and its own T3 in the chain; where
nothing was decided again, the return is not a fact this record can hold, and `lapsed` with
its date stands. As with an inflated quorum (DD-14), no file-based check observes a producer
who deletes a date instead; the obligation is stated, not enforced.

### 1.4 `conditions` and `enforcement` are different statements

`conditions` (v0.7) states what must hold for a decision to bind. `enforcement` states what
happened in the world. An unmet condition typically leaves `enforcement.status: pending`, but
the two are not substitutes: a condition can be met while nothing happens, and an effect can
occur while a condition is still open. Neither field implies the other and neither is derived
from the other.

### 1.5 What this measures

With `date` and `enforcement.first_effect_at` in the same record, **effect latency** is a
computation over the repository rather than a reconstruction from minutes. With `lapsed_at`
and `reopen_log` beside them, the **relapse rate** is computable over a window: decisions that
reached `in_effect` and were either reverted or negotiated again within it. Both numbers need
a day on every asserted fact, which is why the block has no undated value. Neither number is
part of the schema; both become available because the facts are kept apart and dated.

---

## 2. Schema Reference: Approval and Quorum (`decisions[].approval`)

Until v0.7 a decision records **who was accountable** (`driver`, `approver`) and **where it
was taken** (`gremium`). It does not record **how many consents were required** and **which
ones exist**. `approval` closes that gap: the quorum becomes data, and every consent carries
an anchor to evidence that already exists in the repository.

`approval` is OPTIONAL. Its absence means *no quorum was recorded* — never *no quorum was
required*.

**Example — a big bet ratified by a board, and a delegated decision needing one consent:**

```yaml
decisions:
  - id: dec-004
    date: 2026-06-20
    title: "Usage-based pricing for the public API"
    status: active
    decision_type: big-bet
    gremium: exec-board
    driver: product-lead
    approver: exec-board
    scope: program
    rationale: "Seat pricing stalled two enterprise deals; usage aligns price with value"
    approval:
      quorum: 3
      records:
        - by: coo
          at: 2026-06-20
          ref: "minutes:exec-board-2026-06-20"
        - by: product-lead
          at: 2026-06-20
          ref: "minutes:exec-board-2026-06-20"
        - by: head-of-sales
          at: 2026-06-24                   # written consent after the meeting
          ref: "commit:a1b2c3d"
    dissent:
      - "payments lead: usage pricing shifts revenue risk into a single billing path"
  - id: dec-005
    date: 2026-07-08
    title: "Adopt the shared release checklist for all delivery teams"
    status: active
    decision_type: delegated
    gremium: platform-council
    driver: platform-engineer
    approver: tech-lead
    scope: unit
    rationale: "Two teams shipped without the smoke pass; the checklist already existed"
    approval:
      quorum: 1
      records:
        - by: tech-lead
          at: 2026-07-08
          ref: "commit:9f4e1aa"
```

| Key | Semantics |
|---|---|
| `approval` | OPTIONAL object. The legitimacy record of one decision. Refines `gremium`; replaces neither `gremium` nor `approver` |
| `approval.quorum` | integer ≥ 1, REQUIRED when `approval` is present. How many consents this decision needed. The key deliberately reuses the word `governance.change_process.approval[].quorum` (v0.6) already uses for the same concept, rather than introducing a second name for it |
| `approval.records[]` | OPTIONAL list. One entry per **consent given**. Its complete absence is a recorded quorum with no consents captured yet — a WARNING, never an error (Rule 102) |
| `approval.records[].by` | REQUIRED string. Flat id of the consenting role or member — same reference style as `driver` / `approver`, no prefixes |
| `approval.records[].at` | REQUIRED date (`YYYY-MM-DD`). The day the consent was given. It MAY fall before or after `decisions[].date`; neither is a finding |
| `approval.records[].ref` | OPTIONAL string. Anchor to the evidence. RECOMMENDED shape `<kind>:<value>` with `commit:`, `pr:`, `minutes:`, `doc:`. Free text — validators MUST NOT attempt to resolve it. Its absence on a decision in force is a WARNING for the same reason as in §1.1: a consent date without an anchor is self-report (DD-9) |

**Design intent — one record per consent, consents only.** `records[]` counts **agreement**,
nothing else. There is no `stance` key and no abstention marker: an entry is a consent by
definition. Objections stay where v0.7 put them — in `dissent[]`, which is prose and
deliberately not countable. A single list with mixed stances would make the quorum arithmetic
ambiguous for the sake of one field.

**Design intent — the anchor belongs to the consent, not to the block.** An `approval.ref`
at object level was considered and rejected. Two consents given in the same meeting then
repeat the same `minutes:` id, as `dec-004` shows, and that repetition is intended: a consent
is evidenced individually or not at all, and a shared anchor at block level would let one
minutes reference stand in for consents that were never recorded there. This is one of the
few decisions in v0.8 that a later version could revisit additively; it is written down so
that revisiting it is a decision rather than a rediscovery.

**Design intent — the entitled set is not a third list.** An `eligible[]` key was specified
and cut. The entitled set is `gremien[<decision.gremium>].members[]`, which exists, is
maintained for its own reasons, and is not written in the same act as the consents it would
qualify. A per-decision `eligible[]` is written by the same hand as `records[]`, so anyone
wanting to silence a finding would simply add the name to it — a check whose subject defines
its own criterion is exactly the DD-9 failure this version rejects elsewhere. The narrower
mechanism is kept: Rule 102 compares against `members[]` where the comparison is meaningful,
and reports nothing where it is not.

**Design intent — `approval` refines, it does not duplicate.** `gremium` remains the venue,
`approver` remains the single accountable point, both REQUIRED and unchanged.

**Design intent — two `approval` keys, two subjects, no inheritance.**
`governance.change_process.approval[]` (v0.6) governs changes **to the document**: who
approves or ratifies a modification of the model, with its own `quorum`.
`decisions[].approval` describes a decision **recorded in** the document. Neither derives from
nor defaults into the other, and a document-wide `governance.approval_policy` with
per-`decision_type` quorum defaults is deliberately not in v0.8: it would introduce default
inheritance (policy says three, the decision says two — which wins?) into a place where the
existing change-process quorum already answers a different question. Quorum height per
decision is the organisation's call; the correlation with `decision_type` is a convention
tooling MAY report and no rule enforces. What that leaves unclosed, and on what condition it
returns, is stated in §4.1.

**Design intent — anchors, not signatures.** `ref` is a pointer, never a proof. A file-based
specification cannot enforce cryptographic consent, and an unenforced MUST is security
theatre (DD-6). Whoever needs proof verifies the anchor in the system that owns it. A missing
anchor is not a violation; it is a visible self-report, and Rule 102 says so at WARNING level
rather than pretending otherwise.

**What happens when the quorum is not met.** Nothing in the lifecycle. There is no new
`status` value, no `rejected`, no `pending` — the shortfall is a **validation finding** whose
severity follows the state the decision claims (Rule 102). What the rule catches is an
internal contradiction in a legitimacy record: a decision in force whose own record shows
fewer consents than it says it needed. It does not catch an inflated quorum — whoever needs
three consents and has two can write `quorum: 2`, and no file-based check can see that. The
claim is inner consistency, not enforcement (DD-14).

**Adoption.** Both blocks are designed to be entered one line at a time, and nothing in v0.8
needs a server. `approval: {quorum: 3}` is the single line an adopter can transcribe from an
existing governance policy on day one; `enforcement: {status: pending, expected_by: …}` is the
single line a decision produces the moment it is taken. Both are plain YAML at L0, both rules
run in `tools/validate.py` — the tool the CI template already offers for copying — and an L1
agent answers "what did we decide and never carry?" by filtering two keys in the file it
already reads. The composite of §3.2 is an L2 convenience for whoever serves the model, not
the entry price for recording the facts.

---

## 3. Serving Profile Amendments

### 3.1 §4.2 Tool derivation (deterministic) — AMENDED

A conformant server derives its tool catalog from the **entities present in the served
document set** — never hand-curated per deployment, and never from the schema alone:

| Schema shape | Generated tool | Example |
|---|---|---|
| entity with `id` | `get_<entity>_by_id` | `get_unit_by_id` |
| enum / tag field | `filter_<entity>_by_<field>` | `filter_decisions_by_status` |
| free-text field | `search_<entity>_by_text` | `search_decisions_by_text` (title + rationale) |
| date / numeric field | `find_<entity>_by_<field>_range` | `find_decisions_by_review_date_range` |
| declared relation | traversal tool | `get_unit_children` (from `parent`) |

Derivation is bounded on two sides, and Rule 103 states both as prohibitions:

1. **By the instance.** A field the served documents never populate produces no tool. A
   schema grows monotonically; a catalog must not.
2. **By nesting.** Derivation applies to top-level entity lists whose items carry `id`.
   Nested lists (`approval.records[]`, `status.drift[]`) and nested objects
   (`decisions[].enforcement`) travel **with** their record and derive no tools of their own.
   Where such a statement needs its own read path, it is a named composite (§4.3 below).

The second bound is what v0.8 owes the serving profile: this version puts two nested blocks on
an entity that is already served, and v0.7 §4.2 read literally could be taken as licence to
derive over them.

**The catalog is a budget, and the budget is currently small.** Tool definitions are spent
before the first user message (DD-13). Measured against the reference implementation on branch
`v0.8-draft` (commit `7d23415`, 2026-08-22) over `examples/serve-demo/org.yaml` (4 units,
2 gremien, 7 decisions, 1 agent), `Catalog.describe()` yields 23 tools and roughly 5.6 kB of
`tools/list` payload (`json.dumps`, default separators); the composite added in §3.2 is one
definition of about 520 bytes, roughly nine per cent of that catalog. The tool count is bounded
by the entity table (`ENTITIES` in `orgspec/tools.py`) and does not grow with record count. The
payload is not bounded that way: `filter_*` descriptions enumerate the known values of each
tag field, so catalog size grows with the number of distinct tag values, not with record count;
no cap on that enumeration is specified in v0.8. A per-key report of catalog size
is deliberately **not** required here: it would need per-key catalogs, which no implementation
has (per-key access enforcement, v0.7 §4.4 points 2–3, is unimplemented — only `--ceiling`
exists), and a named tokenizer, which the specification does not name (§4.1).

Tool descriptions carry the schema field descriptions — the agent learns the org's query
surface from the tool catalog alone; no schema documents travel into prompts.

### 3.2 §4.3 Composite tools (SHOULD) — ONE ROW ADDED

| Tool | Question it answers | Resolution |
|---|---|---|
| `who_decides(topic)` | "Who can decide this?" | resolves via units → gremien → decisions (driver/approver + mandate) |
| `get_decision_chain(id)` | "How did we get here?" | traverses `revises`, `triggers`, `consequences`, `supersedes`, `conflicts_with` |
| `get_agent_mandate(ref)` | "What may this AI agent decide, and where does it escalate?" | reads `agents[]` scope + `escalation_path` |
| `get_undelivered_decisions(as_of?)` | "What did we decide and never carry?" | `status: active` ∧ `enforcement.status: pending` ∧ `expected_by` strictly before `as_of` (default: today). The result MUST carry `as_of`, `undelivered[]` with at least `id` and `expected_by` per hit, and `coverage` with the integers `active`, `with_enforcement`, `with_expected_by`; the sentence form is RECOMMENDED beside them, never instead. MUST additionally return the enforcement coverage of the set it examined, in both halves — `N of M active decisions carry an enforcement block, K of N state an expectation` |

The new row exists for the reason given in §3.1: what v0.8 adds to `decisions[]` is nested, so
nothing is derived over it, and the one question worth asking gets one composite instead of a
family of filters. It is also the single place where this version's working assumption becomes
a mechanism: Rule 101 raises "what did we decide and never carry?" in the lint, once per run,
for whoever runs the lint; `get_undelivered_decisions` is the same question in traffic, for
whoever asks — and asking needs no follow-up discipline.

**The coverage obligation is not decoration.** Without it the tool answers over the subset of
decisions someone bothered to annotate, and an empty result would read as "nothing open" when
it may mean "nothing recorded" or "nothing dated". A result that cannot distinguish "none
outstanding" from "none observed" claims more than it knows, which is the failure this whole
version exists to prevent (DD-7).

**The coverage numbers are bounded by the requesting key.** `M` and `N` are counted over the
tier-enforced view the result itself passes through (v0.7 §4.4 point 1). A decision redacted
to a card carries neither `status` nor `enforcement` and is therefore neither active nor
annotated for this count. They MUST NOT aggregate across a visibility boundary: a count that
includes what the caller cannot read would say more than the served view does, against v0.7
§4.4 point 3 (absence over access-denied), the only access promise the specification makes. The validator's coverage line of §1.1 is a different number with the same
shape — a local run over a document set, with no key involved — and reports over everything it
was given.

**The same question at L1.** An agent reading the document directly answers it by filtering
two keys, with no server, no catalog and no key. The composite is a convenience for whoever
already serves the model; it is not the price of recording the facts.

### 3.3 §4.4 **Access Enforcement** — the name v0.8 relies on

§4.4 governs server-side access enforcement: tier ceilings, absence over access-denied, key
binding. With `decisions[].enforcement` in the core, the single word "Enforcement" would have
named two unrelated things in one specification — access control and effect in the world.
v0.7.0 therefore renamed §4.4 to **Access Enforcement**; v0.8 relies on that published name
and changes no normative content of §4.4.

**Rule 98 enumeration.** Since v0.7.0, the enumeration of composite tools in Rule 98 is
non-exhaustive; the table in §4.3 is the authoritative list. v0.8 adds its composite under
that already-published amendment, so a rule naming three composites next to a table listing
four is not a discrepancy a reader can find.

### 3.4 Rule 89 (Field-Level Tiers): **Withdrawn**

v0.7.1 marked Rule 89 — "a field-level `visibility` MUST be equal to or stricter than its
entity's tier" — **unimplementable as written**: no syntax for declaring a field-level tier
was ever specified, no schema construct, no example, and no line of the validator or the
server touches one (v0.7 §1.4). The published text commits v0.8 to either specifying the
syntax or withdrawing the rule. v0.8 withdraws it. *(Maintainer decision, 2026-08-01.)*

**What is withdrawn.** Rule 89's assertion no longer applies; the number is not reused.
The two sentences that promise the feature (v0.7 §1.1's "and on individual fields of
`decisions[]` entries" and the field-level sentence in §1.2) and the word "fields" in §4.4
point 3 ("fields above the key's tier") are to be read as "entities", which is what the
implementation enforces and all it ever could enforce. The v0.7 text is left as published
under the stability policy; each affected place (§1.1, §1.2, §1.4, §4.4) carries a pointer
here, and the withdrawal is normative from this section.

**Why withdraw rather than specify.** Three weeks of public draft produced no consumer and
no request for field tiers; entity-level classification covers what every consumer —
renderer, OKF export, serving layer — actually does (§1.3's own example redacts the whole
decision). Inventing a syntax with no consumer is the pattern on which `components.scopes`
failed review round 1: a structural schema change bought for a feature its own section
called optional. If a real case arrives — one field of an otherwise visible decision —
v0.9+ can introduce the syntax under a new number, designed against the case instead of
ahead of it.

**Compatibility.** No document can be affected: since the syntax never existed, no document
expresses a field-level tier. The withdrawal invalidates nothing and changes no validator or
server behaviour — there was no behaviour. It is nevertheless a semantic change to a stable
line — published text loses a promise — which is why it ships in v0.8, not in a v0.7.2
patch.

---

## 4. What v0.8 Defers, and What It Does Not Add

### 4.1 Deferred, each on a condition

v0.8 began as a version with six additions and ten rules, under the theme "Effect and
Traffic". It ships with two additions and three rules, and the traffic half is v0.9's title,
not this version's. Each deferral is bound to a prerequisite rather than to a date (DD-10);
none is bound to a release month.

| Deferred | Returns when |
|---|---|
| `components.roles.<key>.authority_over` (authority over authority) | Agent Mandate Provenance (Rules 99/100) is published — met since 2026-08-01 — **and** the evaluation of mixed role/unit edges over `reports_to` is decided; the second half is the one still open. When it returns it takes the next free rule number of the version that carries it, never a number behind v0.8 inserted into earlier text: 99 and 100 are taken, and a back-numbered rule would break the numbering contract |
| Served query-miss telemetry (a new §4.7) | A conformance test exists **and** per-key access enforcement (v0.7 §4.4 points 2–3) is implemented. A specification cannot regulate a channel at ERROR level that no implementation emits |
| `status.query_coverage[]` and its vocabulary list | Telemetry emits, so that a declared model boundary is designed against observed misses rather than assumed ones. Its only consumer was the telemetry |
| The answer envelope (a new §4.6) | The conformance suite exists. Its main purpose was carrying freshness, which is deferred with the entry below |
| `components.scopes` and `agents[].scope.ref` | A second consumer needs the shared scope definition. It was the only structural schema change in the version, bought for one consumer the section itself described as optional |
| `knowledge[].max_age_days` (freshness bounds) | The anchor module exists (`--anchor git\|log\|none`). Rule 80 has required it since v0.6 and nobody has built it; the second rule on a missing module is not the way to get one. A commit on the containing document is not an acceptable anchor — it is anticorrelated with the quantity being measured |
| A per-key report of catalog token size | Per-key catalogs exist (v0.7 §4.4 points 2–3) **and** the specification names a tokenizer, so that two implementations report comparable numbers. Until then §3.1 states the measured size in tools and bytes |
| Quorum defaults per `decision_type` | A corpus maintains `approval` at scale — the question is whether a `big-bet` should be held to a higher quorum than a `two-way`, and it is answerable from a real distribution, not from a schema. v0.8 records the quorum a decision claims and checks it against itself; it does not check the quorum against the decision's type |

**What v0.8 therefore does not close.** A decision taken and never carried is now visible; a
question asked of the model and never answered is not. Both are latency, both were invisible
in v0.7, and the second needs served traffic, a declared model boundary and a conformance test
before a rule about it means anything.

### 4.2 Deliberately not added, in any version

These are settled, not pending. They are listed so the question does not return.

| Not in OPI | Why |
|---|---|
| Mandatory signatures on consents or effects | Not enforceable without a relay, and an unenforced MUST is security theatre (DD-6). The substitute is the anchor |
| A write path in the serving profile | The write path *is* the repository's change process (DD-4). An endpoint that mutates the org bypasses the governance OPI exists to provide |
| Web-of-trust reputation | The wrong layer for an organisational model |
| A transport protocol | OPI is file-based; portability comes from git, not from a protocol |
| Channel membership as an access model | Structurally too poor for an org model — precisely the gap OPI exists to fill |
| `on_revoked` / `on_source_revoked` as fields | Revocation is referential integrity (Rule 100), not a lifecycle flag. A field would suggest a state in which the cascade does not apply |
| Implementation details of a retrieval layer | Ranking constants, chunking, bursting: minimal spec, powerful tooling |
| An enforcement value in the `decisions[].status` enum | Exactly the conflation this version exists to prevent. Effect stays a separate block with its own timestamps (DD-7) |

---

## 5. Validation Rules (v0.8)

Rules 101 and 102 bind documents and are checked by the canonical validator
(`tools/validate.py`, invoked as `orgspec validate`). Rule 103 binds serving implementations,
not documents — like Rules 95–98, the validator does not check it. Its `**Level:** ERROR` is a
**conformance class for the v1.0 suite**, not a finding severity: no document can violate it,
and nothing in a lint run reports it. Unlike Rules 95–98 it is testable today, with two
`tools/list` calls against the reference server (§7).

**Severity architecture.** The two document rules take opposite severities for a reason, and
the reason holds for every future rule on this pair of fields: **ERROR for a contradiction in
the document, WARNING for a state in the organisation.** A shortfall in `approval` is a false
record — the document contradicts itself, and that is a defect the repository owns. An absent
or overdue effect is a fact about the organisation, and a validator that failed CI over an
organisation's inaction would be lying about its own reach (DD-6). Note that the two rules
read two different `status` fields: Rule 101 takes its severities from `enforcement.status`,
Rule 102 from `decisions[].status`.

Both document rules are **presence-gated**: they have no input where their field is absent, so
the finding count of every existing document is unchanged at zero. Where a v0.8 field appears
in a document declaring an earlier version, its presence is reported as a note, never as an
error — the validator once narrowed `decision_type` version-independently and failed a valid
v0.6 document (repaired in `c33280f`, see §6); new checks follow the repaired idiom.

### Rules 101–102: Decision Effect and Legitimacy

#### Rule 101: Effect Is Recorded, Never Assumed

**Assertion:** Where `decisions[].enforcement` is present, `enforcement.status` MUST be
present and MUST be one of `pending | in_effect | lapsed`; an empty `enforcement` object is a
violation. `status: in_effect` and `status: lapsed` MUST each carry a `first_effect_at`;
`status: pending` MUST NOT carry one. `status: lapsed` MUST carry a `lapsed_at`; `pending` and
`in_effect` MUST NOT carry one. `first_effect_at`, `lapsed_at` and `expected_by` MUST be valid
ISO 8601 dates (`YYYY-MM-DD`) where present; `first_effect_at` MUST NOT be earlier than the
decision's `date`, and `lapsed_at` MUST NOT be earlier than `first_effect_at`. Once written,
`first_effect_at`, `lapsed_at` and `ref` MUST NOT be removed or altered — a producer obligation in the sense of Rule 92 (no silent edit), observable only in repository history; the validator raises no finding for it (§1.3). A history-aware tool MAY report a changed `first_effect_at`, `lapsed_at` or `ref`. — `in_effect` or
`lapsed` without `ref` is a WARNING: an effect date without an external anchor is
self-report. — A decision with `status: active` and `enforcement.status: pending` whose
`expected_by` has passed relative to a timestamp outside the document is a WARNING — passed
means strictly earlier than the as-of date; on the expected day itself no finding is raised. Where
`expected_by` is absent, no overdue finding is raised; no other field substitutes for it. — An
`active` decision with no `enforcement` block MUST NOT be flagged; absence asserts nothing
(§1.1). Tooling SHOULD instead report enforcement coverage in both halves — blocks present,
and expectations stated among them — so that neither omission is the cheaper way to avoid a
warning.
**Rationale:** A decision record that cannot distinguish "decided" from "happened" claims more
than it knows (DD-7). The coherence checks make the distinction trustworthy: an effect cannot
precede its cause, a lapse cannot precede the effect it ends, a pending effect cannot have a
date, and every value that asserts a fact must name its day — which is also what makes effect
latency and relapse rate computable (§1.5). The anchor WARNING follows DD-9. The overdue
WARNING is the only lint-side mechanism by which a decision nobody carried becomes visible
work rather than folklore; it is a WARNING and not an ERROR because a repository cannot enforce
effect (DD-6), and a validator that failed CI over an organisation's inaction would be lying
about its own reach. It rests on `expected_by` alone: `review_date` answers when a decision is
looked at again, not when it should bite, and a mechanism that fires on the wrong clock gets
switched off rather than read. The no-flag-on-absence clause exists because a rule that fires
only when a field is present otherwise rewards leaving it out — which is why the counter-
pressure is a two-part count and not a single one.
**Level:** ERROR (`status` present and in enum; date validity; `in_effect`/`lapsed` require
`first_effect_at`; `lapsed` requires `lapsed_at`; `pending` and `in_effect` exclude
`lapsed_at`; `pending` excludes `first_effect_at`; `first_effect_at` not before `date`;
`lapsed_at` not before `first_effect_at`) / WARNING (`in_effect`/`lapsed` without `ref`;
overdue `pending` on an `active` decision)

#### Rule 102: A Recorded Quorum Must Be Met

**Assertion:** Where `decisions[].approval` is present it MUST carry `quorum` as an integer
≥ 1, and every `records[]` entry MUST carry a non-empty `by` and an ISO 8601 `at`. — Where
`records[]` is absent entirely, the finding is a WARNING (`quorum declared, no consents
recorded`) regardless of the decision's status, never an ERROR. — Where `records[]` is
present, the quorum is counted over **distinct** `by` values; if that count is lower than
`quorum`, the decision does not carry the legitimacy it claims: ERROR for `status: active`,
WARNING for `status: planned` and `status: hypothesis`, no finding for `status: revoked` and
`status: superseded`, and no finding for any `decisions[].status` value not named here. —
Every `records[].by` SHOULD appear in `gremien[<decision.gremium>].members[]`; a `by` outside
that list is a WARNING. The comparison is made only where both the `by` value and at least one
entry of that `members[]` list resolve to a declared role in `components.roles`; where the
gremium declares no members, or where neither side is resolvably role-formed, no finding is
reported. — A `records[]` entry without `ref` on a decision with `status: active` is a
WARNING.
**Rationale:** A quorum that is written down and contradicted by its own record lends a
decision authority it never had. What the rule establishes is the **inner consistency of a
legitimacy record**, not quorum enforcement (DD-14) — `quorum` and `records[]` are written by
the same hand, so an inflated quorum is invisible to any file-based check, and the rule should
not be read as catching it. Missing capture and false capture are therefore separated: a bare
`quorum: 3` is the one line an adopter can transcribe from an existing governance policy on
day one, and making that break CI would push adopters towards omitting the block — the exact
incentive Rule 101 is built to avoid. Historical records (`revoked`, `superseded`) are exempt
so that honest, incomplete history stays representable. Count and entitlement are one
statement about one quorum, which is why they are one rule: a consent from outside the
entitled set is the most common way a quorum is inflated, and checking the arithmetic without
checking the set would certify the inflation. The entitlement clause stays a WARNING, and is
narrowed to comparable forms, because `members[]` may hold plain person names while a record
holds a role key — the same tolerance as Rule 69, extended to the form mismatch OPI cannot
today resolve. It compares against `members[]` rather than a per-decision list precisely so
that the checked party does not author its own criterion. The anchor WARNING is the same DD-9
clause Rule 101 carries; a version that demanded an anchor for an effect date and not for a
consent date would apply its own principle unevenly.
**Level:** ERROR (structure; shortfall while in force) / WARNING (quorum declared with no
records; shortfall while not yet in force; consent from outside the declared membership;
consent without an anchor)

### Serving Profile Rules

#### Rule 103: Catalog Derivation Is Bounded

**Assertion:** A conformant server MUST NOT derive a tool from a field that is present in the
schema and absent from every instance in the served document set. It MUST NOT expand nested
lists or nested objects into tools of their own; these travel with their parent record, and a
read path for them is a named composite (§4.3). Which tools a server is obliged to *generate*
is not settled here and belongs to the v1.0 conformance suite.
**Rationale:** Tool definitions are spent before the first user message; MCP servers have been
reported to occupy tens of thousands of tokens of context on definitions alone. A catalog that
grows with the schema makes declaring an organisation more expensive than not declaring it,
which is the only competitor OPI has (DD-13). The rule is stated purely as a prohibition for
two reasons: a positive derivation obligation is untestable without the conformance suite and
would make the reference implementation non-conformant on the day it ships, which is the
DD-3 failure this version otherwise avoids; and the prohibition is what §4.2 needs, because
read as a licence it would let a server derive over the nested blocks v0.8 introduces. This is
also why the two additions of this version cost zero catalog entries.
**Level:** ERROR (conformance class, see the preamble above)

---

## 6. Backward Compatibility

All v0.8 features are additive. No field is renamed, removed, or re-typed; no key becomes
required; no existing enum is extended — the one new enum (`enforcement.status`) lives on a
new field. `decisions[].status` is unchanged and in particular gains no `enforced` value.
**No existing constraint is touched at all:** this version makes no structural schema change,
so R1 holds without a guarding fixture. v0.7, v0.6, v0.5 and v0.4 documents validate unchanged
under v0.8. There is no migration script, no document change and no announcement any adopter
must act on.

**Consumer tolerance, stated on the ground that carries it.** Both additions are valid against
`spec/opi-v0.7.schema.json` today, because `$defs/Decision.additionalProperties` is
`{"description": "x-* extension fields permitted"}` — a subschema without constraints, so an
unknown nested key passes. That is the whole basis of the claim. It is *not* Rules 82–84: Rule
82 covers unknown **top-level** keys and Rule 84 unknown **values of known enums**, and both
v0.8 additions are nested keys, so a v0.7 consumer's tolerance for them is not normed
anywhere. The gap is real and is left open on purpose.

| Addition | Compatibility finding |
|---|---|
| `decisions[].enforcement` | New OPTIONAL nested object with five keys. `grep` over `spec/`, `examples/`, `tools/`, `orgspec/` before the patch (`main` at `c33280f`): no `enforcement`, `first_effect_at`, `lapsed_at` or `expected_by` as a **key** anywhere. The word "enforcement" occurs only as prose in v0.7 §4.4 and in `orgspec/server.py` comments — resolved by renaming that section title, not the field (§3.3) |
| `decisions[].approval` | New OPTIONAL nested object. `quorum`/`by`/`at` are required only *inside* it. `$defs/Decision.required` (`id, date, gremium, title, driver, approver, status, rationale`) unchanged. `governance.change_process.approval[]` (v0.6) is a different subject and is untouched; the shared word `quorum` is deliberate (§2). A document that already keeps an `x-approval` now has two places for one statement — the usual price of consolidating an `x-` field, and the validator notes the co-presence (§7) |
| Rule 103 | Binds implementations, exactly like Rules 95–98. No document can violate it; effect on `validate.py`: none. Stated as a prohibition, it is satisfied by the reference implementation on day one |

**The one existing behaviour that would have broken v0.8 — repaired.** `tools/validate.py`
gated on `version.startswith("0.7")` and selected the decision-status enum from that gate, so
a document declaring `opi: "0.8.0"` fell out of the gate and its `status: hypothesis` was
reported as an **error** — in a version whose Rule 102 grades `hypothesis` explicitly and
whose §1.2 exempts it from the overdue WARNING. That forward break is fixed on `main`
(`c33280f`): a numeric `(major, minor)` comparison replaced the prefix test before any v0.8
work began, so no validator-gate work item remains. The schema half ships with this draft:
`properties.opi.pattern` in `spec/opi-v0.8.schema.json` is `^0\.[678]\.\d+$`, widened narrowly so
the v0.8 schema does not silently accept v0.5 documents (fixture in `tests/test_validate_v08.py`).

**One genuine caveat: Rule 101 introduces a clock into the validator.** The same unchanged
document can produce a warning tomorrow that it does not produce today. That is not an R1
violation — no document becomes invalid, and a warning does not fail CI — but it is new tool
behaviour and is stated here, in this addendum's own compatibility section: the published
v0.7 §7 carries no clock sentence to extend, and editing published text produces retro-edits.
The clock MUST be a parameter
(`--as-of YYYY-MM-DD`, default today), both for reproducible fixtures and because an
expectation must be judged by a clock outside the document (§1.1). The report header MUST name
the `as-of` date it used, so that a finding can be reconstructed from the report alone.

---

## 7. Implementation Notes and Fixture Obligations

> **Implementation status (draft, 2026-08-22).** The notes below were written before the
> patch and are kept as the record of what had to be decided. Everything they call for
> exists on the `v0.8-draft` branch: the warning channel and three-count summary line, the
> `--as-of` parameter (passed through by `orgspec validate`), Rules 101–102, the three
> coverage/co-presence notes, the v0.8 schema with its `if/then` dependencies, the composite
> with `as_of` optional, and the fixture list as `tests/test_validate_v08.py` and
> `tests/test_serving_v08.py` (stdlib `unittest`, run by `.github/workflows/tests.yml`).
> Regression was measured on `main` before and on the branch after the patch: identical
> counts on every committed example, serve-demo in its v0.7 form included.

**Order of work.** The rule code is the smallest part of this patch, not the first. Two pieces
of local infrastructure come before it:

1. **A warning severity in the report.** `tools/validate.py` has exactly three channels
   today — `ok()`, `fail()`, `note()` — and no warning level; the one existing WARNING in the
   specification (Rule 90) is a note with a ⚠ prefix. v0.8 brings five distinct warning
   conditions plus two coverage notes, and Rule 102's severity ladder is meaningless if
   warnings and notes print identically. **Decision: add a third count.** The summary line
   becomes `PASS: N passed, M failed, K warnings`; the exit code is unchanged, so
   `.github/workflows/validate.yml` — an advertised copy-paste template running in other
   people's repositories — keeps working. This is the first change to land, because every
   fixture assertion depends on it.
2. **A fixture runner.** There is no `tests/` directory, no pytest configuration and no
   fixture directory; CI is one `validate.py` call over three example files, judged by exit
   code. Four of the expected outcomes below are *silence*, and silence is exactly what an
   exit code cannot see — and those four fixtures are the ones guarding the deletions this
   version made. A runner that asserts ERROR / WARNING-only / silent / note per fixture is a
   named work item, not an implied one.

Then: rule code, schema, serving. **The former v0.7 dependency is closed.** *Publishing* v0.8
was gated on the two amendments in §3.3 — the Rule 98 enumeration and the §4.4 title — being
in the v0.7 text before it stabilised, because v0.8 references them and editing published text
afterwards produces retro-edits. Both shipped in v0.7.0, so v0.8 is no longer editorially
blocked. *Implementing* v0.8 was never gated: no v0.8 rule depends on Rules 99/100, and
reserved numbers do not need to be occupied to stay reserved.

**Schema.** New `$defs`: `Enforcement`, `Approval`, `ApprovalRecord`. All use the house
`additionalProperties: {"description": "x-* extension fields permitted"}`, never
`additionalProperties: false` — the one exception in OPI is `ai:`, and it is not touched here.
`format: date` is strict on `first_effect_at`, `lapsed_at`, `expected_by` and `records[].at`,
deliberately unlike `validate_by`, which is lax by design: a consent falls on a day, and Rule
101 has to be able to compute a bound. Whoever means a fuzzy expectation omits `expected_by`.
`enforcement` requires `status`; the `in_effect`/`lapsed` ⇒ `first_effect_at` and `lapsed` ⇒
`lapsed_at` dependencies are expressible as `if/then`, the date comparisons are not (below).
Widen `properties.opi.pattern` to `^0\.[678]\.\d+$`. **Copy checklist** — the schema is a full
copy per version (1283 → 1953 → ~2025 lines), and the three places that must move each time
are `$id`, `title` and `properties.opi.pattern`. The wrong `$id` in the v0.7 schema came from
skipping exactly this. A schema refactor is out of scope for this patch.

**Validator.** One change touches existing logic and it is a repair, not an addition: there is
exactly **one** version gate (`validate.py:158`) feeding exactly **one** enum selection
(`:262`), and it is replaced by a `version_tuple()` / `at_least()` helper (§6) — the same idiom
Rules 101 and 102 use for their version notes. The cross-field conditions of Rule 101
(`in_effect`/`lapsed` ⇒ `first_effect_at`; `lapsed` ⇒ `lapsed_at`; `pending` ⇒ neither;
`first_effect_at >= date`; `lapsed_at >= first_effect_at`) belong in `validate.py`, the same
division of labour as Rule 91. **The most likely bug in the whole patch:** PyYAML parses
unquoted dates to `datetime.date`, so every date field can arrive as `date` *or* `str`;
compare via `date.fromisoformat(str(v))`, never as raw strings on mixed types. Add
`--as-of YYYY-MM-DD` (default today) and print it in the report header — and note that
`orgspec validate` delegates to `validate.py` by subprocess passing **file paths only, no
flags** (`orgspec/cli.py:14-37`, which is also why `--schema` is unreachable that way); three
lines of pass-through are part of this patch, or the parameter promise is unkeepable. Report
three coverage numbers as notes, not checks: `enforcement: N/M active decisions carry a block,
K/N of those state an expectation` and `approval: N/M`. Add one further note where
`x-enforcement` or `x-approval` is present alongside the adopted key — the expected
intermediate state of every adoption, and silent double maintenance otherwise.

**Serving.** `get_undelivered_decisions` needs the decision loader only, plus the two-part
coverage count over the same examined set, bounded to what the requesting key may see (§3.2).
One piece of shared catalog code is touched: `tools.py:64-73` marks every generated parameter
as required (`"required": list(params.keys())`), so the optional `as_of` needs a `required=`
argument on `_add` — five lines, but not zero. Rule 103 is testable in process with two
`tools/list` calls. **Name the varied field:** because derivation runs off a hardcoded entity
table, a field outside that table can never produce a tool and an assertion over it would pass
against a server that ignores Rule 103 entirely. `scope` is the honest candidate — it is in
the whitelist, populated in the serve-demo document set and absent from the older examples —
so varying it exercises the real skip at `tools.py:99-100`. A second call asserts that
`enforcement` and `approval.records[]` produce no tools of their own. This is the first
serving-side test in the project and it needs no HTTP conformance harness.

**Fixtures that must exist.** Rule 101: `enforcement.status: bogus` (ERROR), `enforcement: {}`
(ERROR, missing `status`), `in_effect` without `first_effect_at` (ERROR), `lapsed` without
`first_effect_at` (ERROR), `lapsed` without `lapsed_at` (ERROR), `in_effect` with `lapsed_at`
(ERROR), `lapsed_at` before `first_effect_at` (ERROR), `first_effect_at` before `date`
(ERROR), `pending` with `first_effect_at` (ERROR), `in_effect` without `ref` (WARNING only),
`active` + `pending` + past `expected_by` under a fixed `--as-of` (WARNING), the same with a
future date (silent), the same with `expected_by` equal to `--as-of` (silent — the boundary is strict), `active` + `pending` with no `expected_by` and a stale `review_date`
(**silent — guards the removed fallback**), `hypothesis` + overdue (silent, §1.2),
`superseded` + `in_effect` (silent, §1.3). Rule 102: `quorum: 3` with no `records[]` (WARNING,
not ERROR — guards partial adoption), `quorum: 3` with two records on `active` (ERROR) and on
`planned` (WARNING), `quorum: 2` with two records carrying the **same** `by` (ERROR — distinct
counting; two identical `by` values are not themselves an error, only the resulting shortfall
is), a role-formed `by` outside a role-formed `members[]` (WARNING), the same where the
gremium declares no `members[]` (silent), the same where `members[]` holds unresolvable person
names (**silent — guards the form-mismatch narrowing**), an active decision whose record has
no `ref` (WARNING). Coverage: a document with no `enforcement` anywhere (`0/M`, note only) and
one where every active decision carries a block without `expected_by` (`M/M, 0/M` — the case
the second half exists for). Co-presence: `x-enforcement` beside `enforcement` (note).
Version behaviour: `opi: "0.8.0"` with `status: hypothesis` MUST PASS (guards the forward
break, §6); an `enforcement` block in a document declaring `opi: "0.7.0"` yields a note, not
an error.

**Regression.** The promise is: no new findings from Rules 1–100 on the same inputs, before
and after the patch, under a fixed `--as-of`. It is anchored on
`examples/okf-export/source/opi.yaml` and `examples/serve-demo/org.yaml` — both committed on
`main` (serve-demo since `a988fde`) — plus a committed fixture, run as a golden-output test in
the runner above. The starting picture is clean: the version-independent `decision_type`
narrowing that used to fail okf-export with two errors was fixed in its own commit
(`c33280f`, before any v0.8 work) and the baseline was re-measured afterwards — okf-export
**PASS 10/0**, serve-demo **PASS 7/0**, pilot-starter **PASS 9/0**, governance
steering-committee and delivery-lead-sync **PASS 4/0**. The only failing files under
`examples/` are pre-v0.4 fragments without a root unit (`flows/*`, `governance/
committee-structure.yaml`, opi 0.2 or none) and the deliberately broken teaching aid plus the
three placeholder templates; none of them is a regression subject. Note that neither anchor
file is in the CI workflow today, which checks three other examples; adding okf-export to CI
is now possible and is listed as a work item. The wording matters in one more place: Rule 80
is **not** activated by this patch — it needs the anchor module that was deferred together
with `knowledge[].max_age_days` (§4.1), and okf-export carries a passed
`review_date: 2026-06-01` that would light up the moment Rule 80 runs.

**Two further implementation findings, recorded here so §6 stays a compatibility statement.**
A v0.7 **validator** that rejects a v0.8 document is conformant, not broken — D11 ("strict
producer, permissive consumer") makes strictness the point, and Rules 82–84 are
`WARNING (consumer-side)`. And cross-version *schema* validation is expected to fail on
`properties.opi` (`^0\.[67]\.\d+$` in the v0.7 schema) before any new key is reached; that is
not a compatibility claim in either direction. Relevant to sequencing: a missing
`spec/opi-v0.8.schema.json` degrades to a note (`validate.py:379`), so schema and validator
may land in either order, and `VERSION_PATTERN` already accepts `0.8.0`.

---

## 8. Design Decisions

| # | Decision | Rationale |
|---|---|---|
| DD-1 | **Public draft, no formal RFC round** | An RFC with a comment deadline and no audience is documented silence. The draft ships under the release process with open Discussions; design-partner review runs on dedicated issues. The formal RFC process is defined in GOVERNANCE.md and debuts at v1.0-RC, when implementers exist to comment |
| DD-2 | **`visibility` in the core, not in `ai:`** | Classification is consumer-independent; renderers, exporters, and servers all need it. Binding it to AI would force a second mechanism for every other consumer |
| DD-3 | **Composite tools SHOULD, not MUST** | A MUST nobody can test weakens the spec; the conformance suite arrives with v1.0. Naming and specifying the tools now claims the semantics |
| DD-4 | **Serving is read-only** | The write path *is* the repository's change process. An endpoint that mutates the org bypasses the governance OPI exists to provide |
| DD-5 | **Lifecycle fields over a state machine** | A full workflow engine in the schema would be premature; dated logs (`reopen_log`), explicit tests (`validate_by`), and supersede edges express the lifecycle without prescribing tooling |
| DD-6 | **Declare what people must honour, not what machines can enforce** | Systems that couple declaration to enforcement can only express rules with an enforcement point. An organisation's binding rules mostly have none: a mandate holds because people honour it. OPI declares that class of rule; it does not pretend to enforce it |
| DD-7 | **A decision is not its effect** | Recording that something was decided must never imply that it happened. The two are separate facts with separate timestamps, and conflating them makes the record claim more than it knows |
| DD-8 | **A derivation never exceeds its source** | Applies to `ai:` ceilings (Rule 94), to agent mandates (Rule 99), and to any future authority-over-authority relation. Where a derived thing would need more than its origin, the model is wrong, not the ceiling |
| DD-9 | **Self-reported values need an external anchor** | A time bound set by the party it constrains is not a bound. Anything an entity writes about its own rights, validity, or freshness MUST be evaluated against a timestamp outside its control |
| DD-10 | **State maturity in three buckets, not as a roadmap** | Implemented / specified-but-unimplemented / opinion-without-text. Dates promise; buckets describe. A reader deciding whether to build against the spec needs the second, not the first |
| DD-11 | **A rule fires only where the document can answer it** *(v0.7.0, restated here for readability)* | Rule 99 checks the dimensions `components.roles` and the entity graph actually carry, and stays silent on the rest. A rule that demands information the schema does not hold is not strict — it is unimplementable, and an unimplementable ERROR trains readers to ignore the validator |
| DD-12 | **First effect, not a workflow** | Effect is recorded as dated facts with one anchor, never as a process. A repository can observe that something became real; it cannot manage the becoming. Each enum value therefore states exactly one dated fact, one block carries one episode, and reminding is a tooling question, not a field (extends DD-5) |
| DD-13 | **The catalog is a budget** | Tool definitions are spent before the first user message. A catalog that grows with the schema makes declaring an organisation more expensive than not declaring it. Derivation is therefore bounded by the instance and by nesting, stated as prohibitions so the bound is satisfiable before a conformance suite exists — and nested statements get named composites instead of derived families |
| DD-14 | **A legitimacy record is checked against itself, not enforced** | Quorum and consents are written by the same hand, so no file-based check can see a quorum set too low. What a repository can check is whether a record contradicts its own claim, and whether a consent comes from outside the body that was entitled to give it. Declaring the narrower claim is what keeps the check honest and the field adoptable — the alternative is a rule that pretends to certify legitimacy and instead certifies its inflation (extends DD-6) |

**Predecessor series D1–D13** (v0.4–v0.6) is unchanged and continues to apply.

---

## 9. Changelog

- **2026-07-30** — Initial internal draft (r1). Theme: Effect and Traffic. Six additions,
  Rules 101–110, DD-11…DD-14.
- **2026-07-30 (same day)** — Internal r2 after review round 1 (four lenses). Theme narrowed
  to Effect. Adds `decisions[].enforcement` and `decisions[].approval`, amends §4.2 (bounded
  derivation), adds one composite `get_undelivered_decisions` to §4.3, and refers to §4.4 as
  Access Enforcement. Rules 101–103; Rule 98's enumeration declared non-exhaustive.
  `approval.required` renamed to `approval.quorum`; `enforcement.status: failed` replaced by
  `lapsed`; `approval.eligible[]` and Rule 101's `review_date` fallback dropped. Four
  additions, the answer envelope and query-miss telemetry deferred to v0.9, each bound to a
  condition.
- **2026-07-30 (same day)** — Internal r3 after review round 2 (coherence, completeness,
  adoption cost). Title widened to **Effect and Legitimacy**, and the framing raised from
  "what happened after the decision" to the two facts surrounding it; DD-13 added so the
  legitimacy half carries a principle. `enforcement.lapsed_at` added (REQUIRED with `lapsed`),
  making the relapse rate computable and leaving no asserted fact undated; the block is stated
  to carry one episode. The enforcement coverage line becomes two-part, in the validator and in
  `get_undelivered_decisions`, and that tool's coverage is bounded to the requesting key. Rule
  103 restated purely as a prohibition and reduced to two bounds; the per-key token report
  deferred. New §4 carries the deferrals with their conditions and the list of what OPI
  deliberately does not add. Rule 102's entitlement clause narrowed to comparable reference
  forms. "How the Sections Depend on Each Other" dissolved into §5's severity architecture and
  §4. Two design intents recorded rather than left implicit: `decisions[].effect` as an
  alternative field name, and an object-level `approval.ref`. Rules 101–103 unchanged in
  number; v0.9 begins at Rule 104 and DD-14.
- **2026-08-01** — Editorial reconciliation (r4) after the v0.7.0/v0.7.1 stable releases.
  No normative change to the v0.8 additions. Stale claims removed: §4.4 rename and Rule 98
  amendment are published fact, not v0.8 work; the `startswith("0.7")` forward break is fixed
  on `main` (`c33280f`); the publishing gate on the §3.3 amendments has fallen; the §4.1
  `authority_over` condition restated without a version name (review decision 1). Design
  decisions renumbered **DD-12…DD-14** because v0.7.0 occupied DD-11 (implementation note on
  Rule 99); v0.9 now begins at Rule 104 and **DD-15**. Earlier changelog and revision-log
  entries keep their historical numbering.
- **2026-08-01 (same day)** — **Rule 89 withdrawn** (maintainer decision): new §3.4 carries
  the withdrawal, rationale and the consequential strikes in v0.7 §1.1/§1.2/§1.4/§4.4.
  Abstract gains item 5. The two §4.1 conditions and the §3.1 aside that used "Rule 89" as
  shorthand for per-key enforcement now name v0.7 §4.4 points 2–3 directly.
- **2026-08-22** — Public draft on `v0.8-draft`. Editorial close of the internal drafting
  series; no normative change against r4. The `authority_over` deferral in §4.1 names its
  condition only, no target version. §7's regression baseline re-measured on `main` after
  `c33280f`: every committed v0.4–v0.7 example passes; the only failing files under
  `examples/` are pre-v0.4 fragments, placeholder templates and the deliberate teaching aid.
  Ships with the reference implementation of Rules 101–102 (`tools/validate.py`, warning
  severity, `--as-of`), the v0.8 JSON Schema, the `get_undelivered_decisions` composite and
  a fixture runner under `tests/`.
