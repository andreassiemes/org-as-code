---
type: Agent
title: Governance Advisor Agent
description: Answers governance queries against the decision log and flags stale decisions before each Steering Committee.
tags: [analytical, governance, read-only]
timestamp: 2026-07-04T09:00:00Z
x-opi-id: governance-advisor
x-opi-type: analytical
x-opi-governance: read-only
---

# Agent: Governance Advisor Agent

Analytical agent. Answers governance queries against the
[Steering Decision Log](/knowledge/decision-log.md) and flags stale decisions 48h before
each [Steering Committee](/gremien/steering-committee.md). Governance access is
**read-only**, scoped to the [Delivery Organization](/units/delivery.md) and decision
types *budget-allocation* and *governance*.

**Escalation path:** [Head of Delivery](/roles/head-of-delivery.md) →
[COO](/roles/coo.md).

**Capabilities:**

* Read decisions and drift from the OPI document set
* Prepare pre-read summaries for the Steering Committee

# Schema (source fragment)

```yaml
ref: governance-advisor
scope:
  units: [delivery]
  data: [decisions, governance, status]
  governance: read-only
  gremien: [steering-committee]
  decision_types: [budget-allocation, governance]
schedule:
  cadence: biweekly
  condition: "48h before each Steering Committee"
escalation_path:
  - head-of-delivery
  - coo
```
