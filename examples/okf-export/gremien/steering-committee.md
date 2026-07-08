---
type: Committee
title: Steering Committee
description: Strategic decisions for the delivery organization; budget >10k EUR, headcount, restructuring, prioritization.
tags: [committee, biweekly, governance]
timestamp: 2026-07-04T09:00:00Z
x-opi-id: steering-committee
x-opi-cadence: biweekly
---

# Committee: Steering Committee

Strategic decisions for the delivery organization: budget >10k EUR, headcount changes,
unit restructuring, initiative prioritization. Chaired by the [COO](/roles/coo.md);
proposals are driven by the [Head of Delivery](/roles/head-of-delivery.md). Fed by the
[Delivery Lead Sync](/gremien/delivery-lead-sync.md). Decisions follow the
[DACI Decision Framework](/knowledge/daci-framework.md).

**Members:** coo, head-of-delivery, head-of-sales, head-of-people-culture.

# Decisions

* [Approve analytics platform migration budget (45k EUR)](/decisions/dec-s001.md)
* [Introduce a mandatory decision log for all steering decisions](/decisions/dec-s002.md)

# Schema (source fragment)

```yaml
id: steering-committee
name: "Steering Committee"
purpose: "Strategic decisions for the delivery organization: budget >10k EUR, headcount, restructuring, prioritization"
cadence: biweekly
members: [coo, head-of-delivery, head-of-sales, head-of-people-culture]
knowledge_refs:
  - daci-framework
```
