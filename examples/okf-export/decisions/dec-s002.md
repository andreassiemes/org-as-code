---
type: Decision
title: Introduce a mandatory decision log for all steering decisions
description: A mandatory decision log makes the DACI framework auditable and closes the observed governance drift.
tags: [governance, decision]
timestamp: 2026-07-04T09:00:00Z
x-opi-id: dec-s002
x-opi-status: active
x-opi-date: 2026-03-11
x-opi-driver: head-of-delivery
x-opi-approver: coo
x-opi-decision-type: governance
x-opi-review-date: 2026-06-01
---

# Decision: Introduce a mandatory decision log for all steering decisions

**Owned by** [Steering Committee](/gremien/steering-committee.md).
**Driver:** [Head of Delivery](/roles/head-of-delivery.md).
**Approver:** [COO](/roles/coo.md).

Two of three recent reprioritizations happened without contributor review. Root cause is
a tooling gap: DACI is defined but decisions are not logged. A mandatory decision log
makes the framework auditable and closes the
[governance drift](/drift/governance-framework.md).

**Scope:** Steering Committee. **Review date:** 2026-06-01 (review completed 2026-06-10,
see [log](/log.md) — satisfies the freshness rule, OPI Rule 80).

# References

* [DACI Decision Framework](/knowledge/daci-framework.md)
* [Steering Decision Log](/knowledge/decision-log.md)

# Schema (source fragment)

```yaml
id: dec-s002
date: 2026-03-11
gremium: steering-committee
status: active
decision_type: governance
driver: head-of-delivery
approver: coo
review_date: 2026-06-01
knowledge_refs:
  - daci-framework
  - decision-log
```
