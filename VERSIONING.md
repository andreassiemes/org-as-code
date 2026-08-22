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
| **v0.8** | **draft** (branch `v0.8-draft`, public draft 2026-08-22) | Effect and Legitimacy: `decisions[].enforcement` (effect as a separate dated fact), `decisions[].approval` (quorum and consents), `get_undelivered_decisions` composite, bounded catalog derivation. Rules 101–103. Withdraws Rule 89 (field-level tiers; no syntax was ever specified). Stabilizes once a consumer maintains both blocks on real decisions. |
| **v0.7** | **stable** (tagged `v0.7.1`, 2026-08-01) | Visibility tiers, decision lifecycle, `ai:` block, Serving Profile, agent mandate provenance. Rules 87–100. Published as a public draft 2026-07-09, stabilized after implementation feedback ([discussion](../../discussions/1)). `v0.7.1` closed the tier enforcement gap without changing any specification text. |
| **v0.6** | **stable** (tagged `v0.6.0`, 2026-07-09) | OKF interoperability, knowledge graph, `log.md` provenance, permissive consumer model. Rules 1–86. |
| v0.5 and older | superseded | Kept in `spec/` for reference; documents remain valid (see below). |

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
