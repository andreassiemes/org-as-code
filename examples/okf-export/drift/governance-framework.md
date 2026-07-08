---
type: Drift
title: Governance framework drift
description: DACI is defined but two of three recent reprioritizations happened without contributor review.
tags: [drift, warning, improving, governance]
timestamp: 2026-07-04T09:00:00Z
x-opi-field: governance.framework
x-opi-severity: warning
x-opi-trend: improving
x-opi-since: 2025-11-01
---

# Drift: governance.framework

**Expected:** DACI (driver prepares, approver decides with contributor input).
**Actual:** 2 of 3 recent reprioritizations happened without contributor review.
**Delta:** Framework not followed in practice.

**Severity:** warning. **Trend:** improving (since 2025-11-01).

Decision log mandated by [dec-s002](/decisions/dec-s002.md) (2026-03-11); first review
completed 2026-06-10. Affects the [Steering Committee](/gremien/steering-committee.md)
and the [Delivery Organization](/units/delivery.md).

# Schema (source fragment)

```yaml
field: governance.framework
expected: "DACI (driver prepares, approver decides with contributor input)"
actual: "2 of 3 recent reprioritizations happened without contributor review"
delta: "Framework not followed in practice"
severity: warning
since: 2025-11-01
trend: improving
note: "Decision log mandated by dec-s002 (2026-03-11); first review completed 2026-06-10."
```
