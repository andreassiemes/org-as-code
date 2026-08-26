# Versioning & Stability Policy

OPI uses semantic-style spec versions (`MAJOR.MINOR.PATCH`, declared per document via
the `opi:` field). This file states what a version label promises.

## Stability labels

| Label | Promise |
|-------|---------|
| **stable** | The spec text, schema, and validation rules of this minor version do not change anymore. Fixes ship as PATCH (clarifications, typos — never semantics). Breaking anything here costs a new MINOR version. |
| **draft** | Public and implementable, but fields, rules, and semantics may still change based on implementation feedback. Drafts live on a `vX.Y-draft` branch until they stabilize. |

## Current versions

| Version | Status | Scope |
|---------|--------|-------|
| **v0.8** | **stable** (tagged `v0.8.0`, 2026-08-26) | Effect and Legitimacy: `decisions[].enforcement` (effect as a separate dated fact), `decisions[].approval` (quorum and consents), `get_undelivered_decisions` composite, bounded catalog derivation. Rules 101–103. Withdraws Rule 89 (field-level tiers; no syntax was ever specified). Published as a public draft 2026-08-22, stabilized once the reference implementation ran against it. Backward-compatible with v0.7: every v0.4–v0.7 document validates unchanged. |
| **v0.7** | **stable** (tagged `v0.7.2`, 2026-08-24) | Visibility tiers, decision lifecycle, `ai:` block, Serving Profile, agent mandate provenance. Rules 87–100. Published as a public draft 2026-07-09, stabilized after implementation feedback. `v0.7.1` closed the tier enforcement gap without changing any specification text. `v0.7.2` fixed the composite tools serving `restricted` entities in full below their tier (behaviour only, regression-tested). `v0.7.3` closed a disclosure in `get_agent_mandate`, which never checked the agent's own tier, and stopped composite result wrappers from being classified as entities (behaviour only, regression-tested — see the note below). |
| **v0.6** | **stable** (tagged `v0.6.0`, 2026-07-09) | OKF interoperability, knowledge graph, `log.md` provenance, permissive consumer model. Rules 1–86. |
| v0.5 and older | superseded | Kept in `spec/` for reference; documents remain valid (see below). |

### v0.7.3 — disclosure in `get_agent_mandate` (2026-08-26)

Anyone running `orgspec serve` from v0.7.0–v0.7.2 with an agent classified above the
serving ceiling should update.

`get_agent_mandate` assembled its answer from an agent's fields and returned it without
ever consulting that agent's `visibility`. Every other tool was tier-enforced on the way
out (Rule 95), but the enforcement gate saw a result *wrapper*, not the agent entity — so
the wrapper's own (absent, therefore `internal`) classification was applied instead of the
agent's. A `restricted` agent's mandate, including its `scope`, was served in full to any
caller at ceiling `internal` or above.

Two details are worth stating plainly, because they explain why this survived two patch
releases:

* **The default ceiling is the exposed one.** At ceiling `public` the answer looked
  correct — but only because a second defect, fixed in the same patch, redacted the whole
  wrapper to `{}`. One bug masked the other. The disclosure is visible at `internal`, which
  is what `orgspec serve` runs at unless told otherwise.
* **No test covered a ceiling other than the default**, and none covered an agent above the
  ceiling. `tests/test_serving_public_ceiling.py` now does both, in both directions.

The same patch stops composite result wrappers (`who_decides`, `get_decision_chain`,
`get_agent_mandate`) from being read as entities, which had made them return `{}` at
ceiling `public`, and stops a record's own sub-objects (such as `agents[].scope`) from
being classified separately from the record they belong to.

Found while describing this project in its own specification — the self-description is
served at ceiling `public`, which is the case the suite had never exercised.

No specification text changes. Documents valid under v0.7.2 remain valid.

**Note on enforcement.** A stable label promises that the *specification* does not change
anymore — not that every rule is implemented. Where the reference implementation lags the
text, the specification says so: see v0.7 §1.4 for the tier model. Closing such a gap is
PATCH work, never a new minor version.

## Compatibility rules

1. **Additive by default.** A MINOR version MUST NOT remove or re-type existing fields.
   Every document valid under vX.Y stays valid under vX.(Y+1).
2. **Enums may grow, not shrink.** New enum values are additive; consumers tolerate
   unknown values (Permissive Consumer Model, rules 82–84).
3. **Rules are append-only.** Validation rules keep their numbers forever; a withdrawn
   rule is marked deprecated, never renumbered.
4. **Deprecation before removal.** Anything scheduled for removal is marked deprecated
   for at least one MINOR version and listed in the migration guide.

## Release flow

Draft branch → implementation feedback (the reference implementation must run against
the draft before it stabilizes) → merge to `main` → tag `vX.Y.0` → status flips to
stable here and in the README → the website facts (`index.html`, `llms.txt` on
org-as-code.com) are updated in the same release step, never later.
