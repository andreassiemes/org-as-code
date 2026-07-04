---
type: Org Unit
title: Delivery Organization
description: Strategic steering of the delivery organization; budget, headcount, restructuring, initiative prioritization.
tags: [stream-aligned, governance, delivery]
timestamp: 2026-07-04T09:00:00Z
x-opi-id: delivery
x-opi-type: stream-aligned
x-opi-owner: coo
---

# Org Unit: Delivery Organization

Strategic steering of the delivery organization: budget, headcount, restructuring,
initiative prioritization. Owned by the [COO](/roles/coo.md).

**Members:** [COO](/roles/coo.md), [Head of Delivery](/roles/head-of-delivery.md).

**Depends on** People & Culture (x-as-a-service, health: *at-risk*) for headcount data
and culture impact assessments.

# References

* [DACI Decision Framework](/knowledge/daci-framework.md)
* [Steering Decision Log](/knowledge/decision-log.md)

# Schema (source fragment)

```yaml
id: delivery
name: "Delivery Organization"
type: stream-aligned
owner: coo
members:
  - role_ref: coo
  - role_ref: head-of-delivery
dependencies:
  - unit: people-culture
    type: x-as-a-service
    health: at-risk
knowledge_refs:
  - daci-framework
  - decision-log
```
