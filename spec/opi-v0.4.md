---
tags: [org-as-code, opi, spec]
status: draft
date: 2026-03-13
---

# OPI Specification v0.4 — Addendum

> Roles, Agents & Drift — OPI for the Living Org Model
>
> Extends: OPI Spec v0.3 (2026-02-27)
> Status: Draft — v0.4 (March 2026)

---

## Abstract

OPI v0.4 extends the Specification with three major capabilities, driven by real-world needs from HR tooling and AI agent governance:

1. **Roles as First-Class Entity** (`components.roles`) — Structured role definitions that HR tools can consume and extend
2. **Agents as Organizational Citizens** (`agents[]` block) — AI agents with explicit scope, governance, and constraints, treated like human team members
3. **Drift Detection** (`status.drift[]`) — Mechanism for capturing and tracking spec-vs-status deviations over time

All features are **backward compatible** with v0.3. Existing documents require no changes.

---

## What's New in v0.4

| Feature | Location | Description | Use Case |
|---------|----------|-------------|----------|
| **Roles Definition** | `components.roles` | Reusable role definitions with skills, qualifications, decision authority | HR tool integration, job evaluation, career ladders |
| **Role Reference** | `members[].role_ref` | Reference existing roles instead of inline strings | DRY role management, consistency across units |
| **Agent Types** | `components.agents` | Agent definitions with capabilities, constraints, governance | AI agent registry, reusable agent types |
| **Agent Scoping** | `agents[]` (unit-level) | Instantiate agents per unit with specific scope and schedule | Agent deployment, permission scoping |
| **Drift Detection** | `status.drift[]` | Track spec-vs-status deviations with trend and severity | Anomaly detection, alerting, reconciliation |

---

## 1. Schema Reference: `components.roles` — Roles as First-Class Entity

New optional section within `components`. Contains reusable role definitions that can be referenced across units via `role_ref`.

### Structure

```yaml
components:
  roles:
    <role-key>:
      title: string                    # Human-readable role title (required)
      level: string                    # Seniority level enum (optional)
      job_family: string               # Job family for HR mapping (optional)
      purpose: string                  # Role purpose statement (required)
      accountabilities: [string]       # Key accountabilities (required)
      skills:
        required: [string]             # Required skills (optional)
        preferred: [string]            # Preferred skills (optional)
      qualifications: [string]         # Education/experience requirements (optional)
      decision_authority:
        - scope: string                # Decision scope
          framework: string            # Governance framework
          daci: string                 # DACI role (optional)
      reports_to: string               # Reference to other role or unit (optional)
      x-*: any                         # Extension fields
```

### Field Documentation

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `title` | string | Yes | Human-readable role name | `"Product Lead"` |
| `level` | enum | No | Seniority band: `junior`, `mid`, `senior`, `lead`, `principal`, `executive` | `"senior"` |
| `job_family` | string | No | Job family identifier for HR-tool mapping. Links to compensation bands, career ladders. | `"product"`, `"engineering-backend"` |
| `purpose` | string | Yes | Single-sentence purpose statement. Why does this role exist? | `"Owns product roadmap, stakeholder alignment, and success metrics"` |
| `accountabilities` | [string] | Yes | List of key responsibilities. 2-5 bullets. Actionable verbs. | `["Define and prioritize product roadmap", "Align stakeholders on direction"]` |
| `skills.required` | [string] | No | Skills non-negotiable for role success. Prioritized list. | `["Product management", "Stakeholder management", "Data analysis"]` |
| `skills.preferred` | [string] | No | Nice-to-have skills. Second-order competencies. | `["Technical background", "Agile/Scrum certification"]` |
| `qualifications` | [string] | No | Formal requirements: years of experience, degrees, certifications. | `["5+ years product management", "MBA or equivalent", "PSPO certification"]` |
| `decision_authority` | [object] | No | Explicit decision rights. Array of decision scopes with governance mapping. | See example below. |
| `decision_authority[].scope` | string | Yes | What domain of decisions? | `"Product roadmap priorities"`, `"Budget > 10k"` |
| `decision_authority[].framework` | string | Yes | Governance framework applied to this decision. Must exist in org's governance frameworks. | `"DACI"`, `"consent"`, `"autocratic"` |
| `decision_authority[].daci` | string | No | Explicit DACI role in context of this decision. If framework is DACI, maps to: `driver`, `approver`, `contributor`, `informed`. Overridable per unit. | `"approver"`, `"driver"` |
| `reports_to` | string | No | Reporting structure: reference to another role key OR a unit id. Enables org chart generation. | `"head-of-product"` (role ref) or `"board"` (unit ref). |

### Full Example

```yaml
components:
  roles:
    # --- Product Domain ---

    product-lead:
      title: "Product Lead"
      level: senior
      job_family: product
      purpose: "Owns product roadmap, stakeholder alignment, and success metrics"
      accountabilities:
        - "Define and prioritize product roadmap with quarterly planning"
        - "Align stakeholders (engineering, design, sales, support) on direction"
        - "Own product KPIs: adoption, retention, NPS, feature usage"
        - "Conduct user research and competitive analysis"
      skills:
        required:
          - "Product management (feature discovery, roadmapping)"
          - "Stakeholder management and alignment"
          - "Data-driven decision making"
          - "Communication and influence without authority"
        preferred:
          - "Technical background or technical literacy"
          - "Agile/Scrum certification (PSPO, CSPO)"
          - "Jobs to be Done framework experience"
      qualifications:
        - "5+ years product management experience"
        - "Shipped 3+ products or major features to market"
        - "Experience working across engineering, design, and go-to-market teams"
      decision_authority:
        - scope: "Product roadmap priorities (quarterly)"
          framework: DACI
          daci: driver
        - scope: "Feature scope and acceptance criteria"
          framework: DACI
          daci: approver
        - scope: "Product spending (tools, research, prototyping) < 10k"
          framework: DACI
          daci: approver
        - scope: "Product spending > 10k"
          framework: DACI
          daci: contributor
      reports_to: head-of-product

    head-of-product:
      title: "Head of Product"
      level: executive
      job_family: product
      purpose: "Sets product strategy, leads product team, represents product at executive level"
      accountabilities:
        - "Define product vision and multi-year strategy"
        - "Build and lead product team (hiring, performance, development)"
        - "Own product P&L: revenue, unit economics, customer satisfaction"
        - "Represent product at board/executive leadership meetings"
      skills:
        required:
          - "Product leadership and team management"
          - "Strategic thinking and long-term planning"
          - "Business acumen (unit economics, market dynamics)"
          - "Executive presence and communication"
        preferred:
          - "Experience scaling product teams from 1 to 20+ people"
          - "Venture capital or strategic M&A experience"
      qualifications:
        - "8+ years product management, 3+ in leadership role"
        - "Led product team through market expansion or pivot"
      decision_authority:
        - scope: "Product vision and strategy"
          framework: DACI
          daci: driver
        - scope: "Product team structure and hiring"
          framework: DACI
          daci: approver
        - scope: "Product budgets (all amounts)"
          framework: DACI
          daci: approver
      reports_to: ceo

    # --- Engineering Domain (example) ---

    backend-engineer:
      title: "Backend Engineer"
      level: mid
      job_family: engineering-backend
      purpose: "Designs, builds, and maintains backend services and data systems"
      accountabilities:
        - "Design and implement backend features with high code quality"
        - "Collaborate with product and frontend on API contracts"
        - "Maintain on-call rotation for production services"
        - "Mentor junior engineers"
      skills:
        required:
          - "Backend programming (Python, Go, Java, or similar)"
          - "SQL and database design"
          - "RESTful API design and HTTP fundamentals"
          - "Testing (unit, integration, contract)"
        preferred:
          - "Kubernetes / Docker container orchestration"
          - "Message queues (RabbitMQ, Kafka, SQS)"
          - "Event-driven architecture"
      qualifications:
        - "3+ years backend engineering experience"
        - "Shipped 2+ production systems with 10k+ daily active users"
      decision_authority:
        - scope: "Backend architecture decisions"
          framework: consent
          daci: contributor
        - scope: "Library/framework choices"
          framework: DACI
          daci: contributor
      reports_to: engineering-manager
```

---

## 2. Updated `members[]` — Role Reference in v0.4

Extends the existing `members[]` array from v0.2/v0.3. Backward compatible: old syntax still works.

### Option A: Inline Role (v0.2/v0.3 — still supported)

```yaml
members:
  - name: "Maria Schmidt"
    role: "Product Lead"                # Inline string
    start_date: 2025-06-01
    daci: driver
```

### Option B: Reference via `role_ref` (new in v0.4)

```yaml
members:
  - role_ref: product-lead              # Reference to components.roles
    name: "Maria Schmidt"                # Optional: concrete person's name
    start_date: 2025-06-01
    daci: driver                         # Optional: override role's decision_authority
```

### Option C: Mixed (both inline and reference)

```yaml
members:
  # Using role_ref (recommended for standardized roles)
  - role_ref: product-lead
    name: "Maria Schmidt"
    start_date: 2025-06-01

  # Using inline role (for ad-hoc, one-off roles)
  - role: "Technical Writer (Contractor)"
    name: "John Doe"
    start_date: 2025-09-01
    daci: informed
```

### Members Schema (extended for v0.4)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role_ref` | string | No* | Reference to key in `components.roles`. Mutually exclusive with inline `role`. |
| `role` | string | No* | Inline role description (v0.2 style). Mutually exclusive with `role_ref`. |
| `name` | string | No | Concrete person's name if member is a human. |
| `start_date` | string (ISO 8601) | No | When did person/role start in this unit? |
| `end_date` | string (ISO 8601) | No | When did person leave? Enables retention tracking. |
| `daci` | enum | No | DACI role override for this member in this unit's context. Values: `driver`, `approver`, `contributor`, `informed`. |
| `capacity` | number | No | FTE or percentage allocation to this unit. Range 0.0-1.0 or 0-100. |
| `reports_to` | string | No | Direct manager reference (member name or role_ref). |
| `x-*` | any | No | Extension fields. |

**Note:** `role` and `role_ref` are mutually exclusive. At least one must be present. If both are present, validator MUST reject (error).

### Full Member Example

```yaml
members:
  # Full-time Product Lead with role reference
  - role_ref: product-lead
    name: "Maria Schmidt"
    start_date: 2025-06-01
    daci: driver
    capacity: 1.0
    reports_to: head-of-product
    x-employee-id: "EMP-1234"

  # Part-time Engineering Manager (50% split between two units)
  - role_ref: engineering-manager
    name: "Bob Chen"
    start_date: 2024-01-15
    daci: approver
    capacity: 0.5
    reports_to: vp-engineering

  # Contractor with inline role (not in standard role library)
  - role: "UI/UX Designer (Contract, through Q2 2026)"
    name: "Sarah O'Connor"
    start_date: 2026-01-15
    end_date: 2026-06-30
    daci: contributor
    capacity: 0.8
    reports_to: design-lead

  # Agent member (new in v0.4 — see agents block)
  - role_ref: delivery-analyst-agent
    name: "Delivery Analytics Bot"
    daci: informed
    x-agent: true
```

---

## 3. Schema Reference: `components.agents` — Agent Type Definition

Agents are defined once as reusable types in `components.agents`, then scoped to specific units via the `agents[]` block.

### Agent Type Definition Fields

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `name` | string | **Yes** | Human-readable name of the agent |
| `type` | enum | **Yes** | Agent classification: `analytical` \| `operational` \| `advisory` \| `orchestrator` |
| `purpose` | string | **Yes** | Why this agent exists — what problem does it solve? |
| `capabilities` | string[] | **Yes** | What this agent can do (e.g. "Read delivery metrics", "Generate reports") |
| `constraints` | string[] | **Yes** | Hard boundaries — what this agent CANNOT do. Never empty. |
| `governance` | object | **Yes** | Permission model: `may_read`, `may_write`, `may_decide`, `audit_trail`, `framework` |
| `model` | string | No | Optional hint for the AI runtime (e.g. `claude-haiku`, `gpt-4-turbo`, `local-llm`) |
| `owner` | string | **Yes** | Human accountable for this agent's behavior — must be a `members[]` entry or `components.roles` reference |

### `governance` Object (Agent-Level)

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `may_read` | boolean | **Yes** | Can this agent read data and documentation? |
| `may_write` | boolean | **Yes** | Can this agent create/modify artifacts (reports, summaries)? Note: does NOT mean modifying OPI spec or org data. |
| `may_decide` | boolean | **Yes** | Can this agent make decisions, or only prepare recommendations? |
| `audit_trail` | enum | **Yes** | How are agent actions logged: `git` \| `database` \| `event-log` \| `combined` |
| `framework` | string | No | Required if `may_decide: true` — which governance framework does this agent follow? (must match org `governance.framework`) |

**Important:** `may_write` refers to artifact creation (reports, analysis documents), NOT modification of OPI spec/status files. OPI document changes always require human review via Git PR.

### Agent Type Enum Values

| Value | Use Case | Can Make Decisions? | Example |
|-------|----------|:------------------:|---------|
| `analytical` | Read-only analysis, reporting, anomaly detection | No | Delivery Analytics Agent, KPI Monitor |
| `operational` | Execute processes, create artifacts, minor automations | No | Report Generator, Task Creator |
| `advisory` | Recommend courses of action, prepare decisions | No | Strategy Assistant, Risk Analyzer |
| `orchestrator` | Coordinate workflows across units, potentially escalate/delegate | Conditional (rarely) | Workflow Orchestrator, Incident Commander |

---

## 4. Schema Reference: Unit-Level `agents[]` — Agent Scoping

Each unit can instantiate agents from the global agent registry via the `agents[]` block.

### Scoped Agent Instance Fields

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `ref` | string | **Yes** | Reference to `components.agents.<agent-id>` |
| `scope` | object | **Yes** | Defines visibility and data access for this agent instance |
| `schedule` | object | No | When/how often this agent runs (cadence, day, time) |
| `disabled` | boolean | No | If `true`, this agent instance is inactive (default: `false`) |

### `scope` Object (Agent Instance)

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `units` | string[] | **Yes** | Which organizational units are visible to this agent (e.g. `[delivery, engineering]`). Use `["*"]` for org-wide visibility only with explicit governance approval. |
| `data` | string[] | **Yes** | What data types can this agent access (e.g. `[metrics, reports, decisions]`) |
| `governance` | string | No | Governance data access mode: `none` (cannot read governance), `read-only` (can read decisions but not modify), `full` (rare, requires approval). Default: `none`. |

### `schedule` Object (Agent Instance)

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `cadence` | enum | No | Execution frequency: `on-demand` \| `hourly` \| `daily` \| `weekly` \| `monthly` \| `quarterly` |
| `day` | string | No | Day of week (for weekly/monthly) or date (for monthly) — e.g. `Monday`, `15` |
| `time` | string | No | Time in 24h format (UTC) — e.g. `"06:00"` |
| `condition` | string | No | Optional trigger condition (e.g. `"when metrics available"`) |

---

## 5. Core Principle: Governance as the Permission Model

**Traditional Stack Model:**
```
Roles → Groups → Permissions → Access Control Lists
```

**OPI Agent Model:**
```
Governance Framework → Agent Scoping → Constraints → Action Validation
```

The difference: In OPI, an agent's **constraints are enforced at decision time**, not at infrastructure time. An analytical agent doesn't have database write permission — it's explicitly prevented by its constraints and governance rules.

This allows:
1. **Human-readable policies** ("cannot modify data sources", "must escalate anomalies")
2. **Runtime validation** (Agent checks governance rules before acting)
3. **Audit trail** (Every constraint violation is logged)

---

## 6. Complete Examples: Agents

### Example 1: Analytical Agent (Read-Only)

**Definition in `components.agents`:**

```yaml
components:
  agents:
    delivery-analyst:
      name: "Delivery Analytics Agent"
      type: analytical
      purpose: |
        Monitors delivery KPIs and prepares weekly status reports.
        Flags anomalies to delivery-lead for escalation.
      capabilities:
        - "Read delivery metrics from BI pipeline"
        - "Aggregate metrics by team and sprint"
        - "Generate weekly status reports"
        - "Flag KPI anomalies against thresholds (automated)"
        - "Recommend corrective actions"
      constraints:
        - "Cannot modify any data sources or org data"
        - "Cannot approve decisions — only prepares analysis for human review"
        - "Must escalate anomalies (severity > warning) to unit-lead within 24h"
        - "Cannot access confidential financial data (salary, headcount planning)"
      governance:
        may_read: true
        may_write: false          # Can create reports/artifacts, not modify OPI
        may_decide: false
        audit_trail: git          # All artifact creation logged as Git commits
      model: claude-haiku         # Suggests smaller, cost-efficient model
      owner: head-of-delivery     # Human accountable for this agent
```

**Scoping in `delivery/opi.yaml`:**

```yaml
agents:
  - ref: delivery-analyst
    scope:
      units: [delivery, engineering]       # Can see these units' metrics
      data: [metrics, reports, status]     # Can read these data types
      governance: none                     # Cannot read governance decisions
    schedule:
      cadence: weekly
      day: Monday
      time: "06:00"
      condition: "when metrics pipeline runs successfully"
    disabled: false
```

**Runtime Behavior:**
- Agent runs every Monday at 06:00 UTC
- Reads delivery metrics from BI pipeline (scoped to delivery + engineering units)
- Generates weekly report (creates Git commit with analysis)
- If anomaly detected (delta > threshold), sends escalation message to `head-of-delivery`
- **Cannot:** modify metrics, approve any decisions, modify org structure, access HR data
- **Audit trail:** All artifacts and escalations are Git commits with agent signature

---

### Example 2: Orchestrator Agent (Decision Preparation + Escalation)

**Definition in `org.yaml` or shared `components.agents`:**

```yaml
components:
  agents:
    budget-orchestrator:
      name: "Budget Cycle Orchestrator"
      type: orchestrator
      purpose: |
        Automates budget cycle workflows: kicks off unit proposals,
        consolidates submissions, prepares recommendation for approval.
        Escalates threshold breaches to steering-committee.
      capabilities:
        - "Send budget-cycle-start event to all units"
        - "Consolidate unit budget submissions"
        - "Check budget requests against authorization limits"
        - "Flag threshold breaches (>50k EUR requires board approval)"
        - "Prepare budget recommendation document"
        - "Schedule steering-committee meeting if escalation needed"
      constraints:
        - "Cannot approve budget requests — only prepares recommendation"
        - "Must escalate decisions above 50k EUR to steering-committee"
        - "Cannot override governance thresholds"
        - "Cannot modify member allocations (HR data is off-limits)"
        - "Must maintain decision audit trail (all escalations documented)"
      governance:
        may_read: true
        may_write: true          # Can create budget documents, send events
        may_decide: false        # Prepares decisions, humans approve
        audit_trail: combined    # Git + event log for full traceability
        framework: DACI          # Uses org's DACI framework for escalation
      model: claude-opus-4
      owner: cfo
```

**Scoping in `steering-committee/opi.yaml`:**

```yaml
agents:
  - ref: budget-orchestrator
    scope:
      units: ["*"]                        # Org-wide visibility (requires approval — noted in governance)
      data: [metrics, budgets, decisions] # Can read budget data + decisions
      governance: read-only               # Can READ governance/approval thresholds, not modify
    schedule:
      cadence: quarterly
      day: "1"                            # First day of quarter
      time: "09:00"
      condition: "when CFO approves budget cycle start"
    disabled: false
```

**Runtime Behavior:**
- Triggers on CFO approval (condition: `when CFO approves budget cycle start`)
- Reads DACI governance framework from org (escalation rules)
- For requests > 50k EUR: sends escalation to `steering-committee` with recommendation
- Creates audit trail: every decision point is logged
- **Cannot:** approve budgets, modify org data, override decision thresholds
- **Must:** escalate within defined governance framework

---

### Example 3: Advisory Agent (Limited Scope, No Data Write)

**Definition:**

```yaml
components:
  agents:
    risk-advisor:
      name: "Risk Analysis Agent"
      type: advisory
      purpose: |
        Analyzes risk registers and project status across units.
        Prepares risk recommendations and escalation notices for PMO.
      capabilities:
        - "Read risk registers from all projects"
        - "Aggregate and categorize risks (technical, resource, scope)"
        - "Analyze risk trends month-over-month"
        - "Generate risk briefing documents"
        - "Flag new high-severity risks for escalation"
      constraints:
        - "Cannot modify risk registers"
        - "Cannot approve risk mitigation strategies"
        - "Cannot access financial or salary data"
        - "Escalations must include both risk and recommended owner"
      governance:
        may_read: true
        may_write: false
        may_decide: false
        audit_trail: git
      owner: pmo-lead
```

**Scoping:**

```yaml
agents:
  - ref: risk-advisor
    scope:
      units: [all-projects]    # Can access all project-type units
      data: [risks, status, metrics]
      governance: none         # Cannot read decisions
    schedule:
      cadence: daily
      time: "08:00"
```

---

## 7. Schema Reference: `status.drift[]` — Drift Detection

The `drift` field is an optional array within the `status` block. Each entry describes one specific deviation.

### Conceptual Framework: Conditions vs. Drift

| Aspect | `conditions[]` | `drift[]` |
|--------|---|---|
| **What** | Current state snapshot | Historical deviation pattern |
| **Question answered** | "Is the system healthy right now?" | "How far and how long has the system deviated from desired?" |
| **Temporal nature** | Point-in-time (since date) | Trend (improving/stable/worsening) |
| **Use case** | Status dashboards, health checks | Root cause analysis, pattern detection, alerting |
| **Scope** | Org-wide state categories (Staffed, InterfacesHealthy, etc.) | Specific field-level deviations (expected vs. actual) |

**Example:**
- A condition `Staffed: False` tells you the team *is* under-staffed right now.
- A drift entry tells you the team has been 2 positions short *for 6 weeks* and the trend is *worsening* (no candidates in pipeline).

Drift is conditions-enriched: it captures **what changed, by how much, when it started, and whether it's improving**.

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `field` | string | **Yes** | The spec field this drift refers to (e.g., `members`, `interfaces.outputs.monthly-report`, `governance.framework`). MUST match a valid OPI field path. |
| `expected` | any | **Yes** | The desired value according to `spec`. Can be string, number, boolean, date, or complex object. |
| `actual` | any | **Yes** | The observed value from `status`. Same type as `expected` where possible. |
| `delta` | string \| number | No | Quantified difference between expected and actual. For numeric fields: `-2`, `+5`, `180%`. For non-numeric: text description (`"2 cycles overdue"`, `"de facto autocratic"`). |
| `severity` | enum | **Yes** | Impact level: `info`, `warning`, `critical`. Tooling may use this to trigger alerts or suppress low-severity drifts. |
| `since` | date (YYYY-MM-DD) | **Yes** | Start date of this drift. When the deviation was first observed. |
| `trend` | enum | **Yes** | Direction of change: `improving`, `stable`, `worsening`. Computed from historical drift entries or from observable indicators. |
| `note` | string | No | Human-readable explanation of the drift and context. Max 200 chars recommended. |

### Type Constraints

**`field`:** Uses JSON Pointer syntax (RFC 6901) for nested paths:
- Top-level: `members`, `governance`, `capabilities`
- Nested: `interfaces.outputs.monthly-report`, `members.count`, `governance.framework`
- Array indices: `channels.0.slack` (first Slack channel)

**`expected` / `actual`:** MUST be serializable to YAML. Objects/arrays permitted.

**`delta`:**
- For numeric comparisons: Use signed integers or percentages (`-2`, `+150%`)
- For temporal: Use ISO 8601 durations (`P1W` = 1 week overdue) or prose (`"8 weeks overdue"`)
- For qualitative: Descriptive string explaining the gap

**`severity`:** Single-select enum:
- `info`: Acknowledged drift, no action needed (e.g., "intentional pilot program runs 2 weeks longer than planned")
- `warning`: Requires monitoring and likely action (e.g., "budget 15% over target; reviewing discretionary spend")
- `critical`: Immediate action required (e.g., "escalation SLA missed for 3 consecutive decisions")

**`trend`:** Single-select enum:
- `improving`: Drift is narrowing over time (e.g., vacancies being filled, compliance improving)
- `stable`: Drift has not materially changed for 2+ periods (e.g., chronic understaffing with no hiring plan)
- `worsening`: Drift is growing (e.g., customer feedback backlog increasing, team morale declining)

---

## 8. Complete Examples: Drift Detection

### Example 1: Staffing Drift (Numeric)

```yaml
status:
  observed_version: "2026-Q1"
  conditions:
    - type: Staffed
      status: "False"
      reason: "10 of 12 positions filled"
      since: 2026-01-15

  drift:
    - field: members
      expected: 12
      actual: 10
      delta: -2
      severity: warning
      since: 2026-01-15
      trend: improving
      note: "2 Senior Engineers departed (UK office closure). Recruiting: 4 candidates in final round, first hire target 2026-04-15."
```

**Why improving?** The drift was `worsening` 6 weeks ago (uncertain timeline, vague candidates). Now it's `improving` because there's a concrete hiring plan with named candidates and a target date.

---

### Example 2: Interface Delivery Drift (Temporal)

```yaml
unit:
  name: "Data Analytics"
  interfaces:
    outputs:
      - name: "monthly-report"
        audience: "Executive Team"
        frequency: "monthly"
        sla: "15th of each month"

status:
  conditions:
    - type: InterfacesHealthy
      status: "False"
      reason: "Monthly report delivery SLA missed 2 consecutive cycles"
      since: 2026-02-01

  drift:
    - field: interfaces.outputs[0].frequency
      expected: "monthly"
      actual: "last delivered 2026-01-05 (delivery gap: 9 weeks)"
      delta: "P9W"  # ISO 8601: 9 weeks overdue
      severity: critical
      since: 2026-02-01
      trend: worsening
      note: "Analytics platform migration (data quality issues). Root cause: 3 ETL pipelines still unstable. Estimated resolution: 2026-04-01 (8 weeks)."
```

**Why critical?** This is a contractual interface. Executives depend on monthly data for board decisions. 9 weeks overdue is unacceptable.

---

### Example 3: Governance Drift (Qualitative)

```yaml
unit:
  name: "Product Team"
  governance:
    framework: DACI
    decisions:
      - scope: "Product roadmap prioritization"
        daci:
          driver: "Product Lead"
          approver: "Head of Product"
          contributor: ["Engineering Lead", "Design Lead", "Data Analytics"]
          informed: ["Executive Team"]

status:
  drift:
    - field: governance.framework
      expected: "DACI (driver: Product Lead, approver explicitly decides with contributor input)"
      actual: "De facto autocratic (Head of Product unilaterally reorders roadmap without contributor review)"
      delta: "Framework not followed in practice"
      severity: warning
      since: 2025-11-01
      trend: stable
      note: "Governance drift: formal DACI defined but 2 of 3 recent reprioritizations happened without contributor sync. Root cause: tooling gap (no decision logging). Action: implement decision log by 2026-04-01."
```

**Why stable?** This pattern has repeated consistently for 4 months with no corrective action taken yet. It's not improving (no decision log implemented) but not actively worsening (no escalation).

---

### Example 4: Capability Drift (Skill-Based)

```yaml
unit:
  name: "DevOps Team"
  capabilities:
    - name: "Kubernetes Orchestration"
      level: "Advanced"
      required_for: ["platform-reliability", "deployment-automation"]
      maturity: "mature"

status:
  drift:
    - field: capabilities[0].level
      expected: "Advanced"
      actual: "Intermediate (2 of 4 engineers lack Kubernetes certification)"
      delta: "50% skill gap"
      severity: warning
      since: 2025-10-01
      trend: improving
      note: "2 engineers onboarded. Certification training in progress (ends 2026-04-30). Meanwhile, cluster maintenance handled by contract with external vendor (overhead: $15k/month)."
```

**Why improving?** There's a concrete training plan and end date. The interim risk is mitigated with vendor support.

---

### Example 5: Budget Drift (Financial)

```yaml
unit:
  name: "Engineering"
spec:
  budget:
    annual: 2500000  # EUR
    discretionary: 500000

status:
  drift:
    - field: budget.discretionary
      expected: 500000
      actual: 650000
      delta: "+150000 (+30%)"
      severity: critical
      since: 2026-01-01
      trend: worsening
      note: "Overrun driven by emergency contractor support (platform migration). CFO approval obtained 2026-02-15. Revised forecast: $2.65M for FY2026 (6% overspend). Mitigation: defer non-critical hiring."
```

**Why critical?** Budget overruns at 6% threaten the annual plan. But the approval note prevents escalation.

---

## 9. Validation Rules (v0.4)

### Rules 48–52: Role Validation

#### Rule 48: `role_ref` Resolution

**Assertion:** Every `members[].role_ref` MUST reference an existing key in `components.roles` (within the same document or a referenced document).

**Rationale:** Role references enable reuse and consistency. Dangling references create ambiguity.

**Level:** ERROR

**Example:**

```yaml
members:
  - role_ref: product-manager     # ✓ PASS if exists in components.roles
    name: "Alice"

  - role_ref: ghost-role          # ✗ FAIL if ghost-role not in components.roles
    name: "Bob"
```

---

#### Rule 49: Required Skills Non-Empty

**Assertion:** If `components.roles[].skills.required` is present, it MUST contain at least one item. An empty `required` array is an error.

**Rationale:** Required skills define the bar for role success. Empty requirements indicate incomplete role definition.

**Level:** WARNING (can override with comment)

**Example:**

```yaml
roles:
  good-role:
    skills:
      required:
        - "Product management"           # ✓ PASS
        - "Stakeholder management"

  bad-role:
    skills:
      required: []                       # ✗ WARN: empty required skills
```

---

#### Rule 50: Decision Authority Framework Validity

**Assertion:** If `components.roles[].decision_authority` is present, every entry's `framework` field MUST match an existing governance framework in the org.

**Rationale:** Decision authority must map to actual org governance mechanisms. Unknown frameworks are useless.

**Level:** WARNING

**Valid frameworks:** `DACI`, `consent`, `RAPID`, `autocratic`, `democratic`, `sociocratic`, or org-custom (via `x-` extension).

**Example:**

```yaml
roles:
  product-lead:
    decision_authority:
      - scope: "Roadmap"
        framework: DACI               # ✓ PASS if DACI is org's framework
      - scope: "Budget"
        framework: FancyUnknownMethod  # ✗ WARN: unknown framework
```

---

#### Rule 51: Reports_to Reference Validity

**Assertion:** If `components.roles[].reports_to` is present, it MUST reference either:
1. An existing role key in `components.roles`, OR
2. An existing unit id in the org

**Rationale:** Reporting structure must be resolvable. Enables org chart generation and management chain validation.

**Level:** ERROR

**Example:**

```yaml
roles:
  backend-engineer:
    reports_to: engineering-manager    # ✓ PASS if role exists

  engineering-manager:
    reports_to: vp-engineering         # ✓ PASS if unit "vp-engineering" exists

  lonely-role:
    reports_to: nonexistent-boss       # ✗ FAIL: no such role or unit
```

---

#### Rule 52: Level Enum Constraint

**Assertion:** If `components.roles[].level` is present, it MUST be one of the standard levels: `junior`, `mid`, `senior`, `lead`, `principal`, `executive`.

Organizations MAY extend this via `x-custom-levels` in `org.yaml`. If org defines custom levels, those are also valid.

**Rationale:** Standard levels enable career ladder mapping, compensation band alignment, and HR tool integration.

**Level:** WARNING (can use `x-level` for org-specific values)

**Standard levels:**

| Level | Typical Experience | Example Role |
|-------|-------------------|--------------|
| `junior` | 0-2 years | Junior Engineer, Associate Product Manager |
| `mid` | 2-5 years | Software Engineer, Product Manager |
| `senior` | 5+ years | Senior Engineer, Senior Product Manager |
| `lead` | 7+ years, manages team | Engineering Lead, Product Lead |
| `principal` | 10+ years, strategic influence | Principal Engineer, Principal Designer |
| `executive` | Leadership across org | VP, Director, Head of Function |

**Example:**

```yaml
components:
  roles:
    engineer:
      level: senior                     # ✓ PASS: standard level

    designer:
      level: t-shaped-wizard            # ✗ WARN: unknown level
      x-level: t-shaped-wizard          # ✓ PASS: use x-extension for custom
```

---

### Rules 53–58: Agent Validation

#### Rule 53: `agents[].ref` Must Exist

**Assertion:** Every agent instance reference in `agents[].ref` must point to a defined agent in `components.agents` or imported from a shared registry.

**Rationale:** Prevents orphaned agent references.

**Level:** ERROR

**Example:**

```yaml
agents:
  - ref: delivery-analyst              # ✓ PASS if exists in components.agents
    scope:
      units: [delivery]

  - ref: nonexistent-agent             # ✗ FAIL
    scope:
      units: [sales]
```

---

#### Rule 54: `agents[].scope.units[]` Must Be Valid

**Assertion:** Each unit in the scope must be a valid organizational unit (resolvable in the unit graph). Use `["*"]` only with explicit approval in governance notes.

**Rationale:** Scope must reference real units. Org-wide scope (`["*"]`) is a security-sensitive decision.

**Level:** ERROR

**Example:**

```yaml
agents:
  - ref: delivery-analyst
    scope:
      units: [delivery, engineering]    # ✓ PASS: valid units

  - ref: budget-analyzer
    scope:
      units: [unknown-unit]             # ✗ FAIL: unit doesn't exist
```

---

#### Rule 55: `constraints[]` Cannot Be Empty

**Assertion:** Every agent MUST have at least one constraint. An empty `constraints[]` is a security violation.

**Rationale:** Agents without constraints are ungovernance. This rule enforces that governance IS the permission model.

**Level:** ERROR

**Example:**

```yaml
# INVALID — no constraints
constraints: []

# VALID — even one constraint is better than none
constraints:
  - "Cannot access customer PII"
```

---

#### Rule 56: `owner` Must Be Valid

**Assertion:** Agent owner must be a `members[]` entry or a valid `components.roles` reference in the same org.

**Rationale:** Owner is accountable for agent behavior. Owner must be resolvable.

**Level:** ERROR

**Example:**

```yaml
# ✓ PASS: owner is a valid role reference
agents:
  - ref: delivery-analyst
    scope: ...

  # In components.agents definition:
  owner: head-of-delivery              # Valid role in components.roles

# ✗ FAIL: owner doesn't exist
agents:
  - ref: delivery-analyst
    scope: ...
    owner: nonexistent-person          # Invalid — no such person or role
```

---

#### Rule 57: If `may_decide: true`, `governance.framework` Must Be Set

**Assertion:** Decision-making agents MUST declare which governance framework they follow. This prevents orphaned decision paths.

**Rationale:** Escalation must have a defined path. Without the framework, it's unclear who approves when the agent escalates.

**Level:** ERROR

**Example:**

```yaml
# INVALID — no framework
governance:
  may_decide: true                     # ✗ FAIL

# VALID — agent declared as DACI driver
governance:
  may_decide: true
  framework: DACI                      # ✓ PASS: escalation path is clear
```

---

#### Rule 58: Agent `type` Must Match Enum

**Assertion:** Valid types: `analytical`, `operational`, `advisory`, `orchestrator`. Custom types via `x-agent-types` extension.

**Rationale:** Standard types enable consistent tooling. Custom types are supported but flagged.

**Level:** ERROR

**Example:**

```yaml
agents:
  delivery-analyst:
    type: analytical                   # ✓ PASS: standard type

  custom-agent:
    type: custom-unknown               # ✗ FAIL: invalid type
    x-agent-types: custom-unknown      # ✓ PASS if org registers custom type
```

---

### Rules 59–62: Drift Validation

#### Rule 59: Drift Severity Enum

**Assertion:** If `status.drift[i].severity` is defined, it MUST be one of: `"info"`, `"warning"`, `"critical"`.

**Rationale:** Enables automated alerting and filtering without custom parsing.

**Level:** ERROR

---

#### Rule 60: Drift Trend Enum

**Assertion:** If `status.drift[i].trend` is defined, it MUST be one of: `"improving"`, `"stable"`, `"worsening"`.

**Rationale:** Makes trend queryable; enables dashboards and pattern detection.

**Level:** ERROR

---

#### Rule 61: Drift Since Date Validity

**Assertion:**
- `status.drift[i].since` MUST be a valid date in YYYY-MM-DD format
- MUST NOT be in the future
- MUST be <= today (current observation date)

**Rationale:** Prevents data quality issues and enables duration calculations.

**Level:** ERROR

---

#### Rule 62: Drift Field Reference

**Assertion:** `status.drift[i].field` MUST refer to a valid OPI field that exists in the corresponding spec section. Field references MUST use JSON Pointer syntax (RFC 6901).

**Rationale:** Ensures drift is traceable to a spec field; prevents orphaned drift entries.

**Level:** WARNING

---

## 10. Design Decisions

### D1: Roles — Why `components.roles` (Option B)

**Decision:** Roles are defined once in `components.roles` and referenced via `role_ref` in `members[]`, rather than defining roles inline in each unit's `members[]` array.

**Rationale:**

| Aspect | Inline (Option A) | Reusable (Option B) | Distributed Docs (Option C) |
|--------|---------|---------|---------|
| **DRY** | ✗ Duplicate across units | ✓ Define once, reference many | ✓ Define once, but scattered files |
| **Consistency** | ✗ Same role can vary by unit | ✓ Same role everywhere | ✓ Same role everywhere |
| **HR Tool Integration** | ✗ Hard to aggregate | ✓ Single source of truth | ~ Possible but complex |
| **Career Ladders** | ✗ No way to model | ✓ `reports_to`, `level` enable ladders | ✓ Possible but fragmented |
| **Tooling Simplicity** | ✓ No dereferencing needed | ✓ Simple $ref semantics | ✗ File system traversal |
| **Org Complexity** | ✓ Small orgs fine | ✓ Scales to 100+ roles | ✗ Scales but harder to maintain |

**Tradeoff:** Option B requires learning `role_ref` syntax and managing a `components.roles` library, but provides the core requirement for HR tooling: a structured role definition that job evaluation and workforce planning tools can consume as a standard building block.

**Backward Compatibility:** Option A (inline `role: "Title"`) remains fully supported. Migration is optional.

---

### D2: Agents — Why Definition + Scoping (Option C)

**Decision:** Agent-type is defined in `components.agents` (can be in `org.yaml` or in unit documents), and each unit instantiates agents via the `agents[]` block with specific scope.

**Rationale:**
- Agent-type is reusable (like `components.roles`); each unit declares own scope (parallel editing, distributed ownership)
- Mirrors how humans work — job descriptions are global, but placement in teams is local
- Preserves OPI Principle 2 (One file per unit) — each unit controls its own agent instances

**Tradeoff:** Requires two lookups (type → instance), but enables reusability and clarity of scope.

---

### D3: Drift — Why Minimal Spec (Option A)

**Decision:** The Spec defines only the *structure* of drift (`status.drift[]` with fields), while *thresholds, alerting, and corrections* belong in tooling.

**Rationale:**
1. **Separation of concerns:** The Spec describes organizational structure. Tooling and policies govern how the organization responds to structure-reality gaps.
2. **Flexibility:** Different orgs have different risk tolerances (startup vs. airline). Tooling can be configured per org; the Spec stays universal.
3. **Composability:** Drift data is consumed by multiple tools (dashboards, agents, compliance audits). Keeping the Spec minimal means any tool can add its own logic.
4. **Evolvability:** If we add `alerts[]` or `corrections[]` to the Spec, we lock in a specific operational model. V0.5 might introduce new concerns (e.g., auto-remediation, ML-based anomaly detection).

---

### D4: Agent Governance — Why Binary Flags

**Decision:** Use three binary flags (`may_read`, `may_write`, `may_decide`) instead of role-based (Admin, Analyst, Operator).

**Rationale:**
- Maps directly to governance concepts (Decision frameworks already define read/write/decide)
- Can be combined flexibly
- Requires validation rules to catch invalid combinations (e.g., `may_decide: true` without `framework`)

---

### D5: Agent Constraints — Why Never Empty

**Decision:** Every agent MUST have ≥1 constraint. An empty `constraints[]` is an error.

**Rationale:** Agents without constraints are ungovernance. This enforces that governance IS the permission model.

---

## 11. Security Considerations (Agents)

### Constraint Validation at Runtime

An agent should validate constraints **before** executing, not after:

```
Agent Action Flow:
1. Agent receives task
2. Agent reads governance + constraints
3. Agent checks: "Does this action violate constraints?"
4. If YES → escalate to owner, log, abort
5. If NO → execute, log result
```

**Implementation:** Constraint validation should be built into agent orchestration runtime, not assumed.

---

### Scope Creep Prevention

Agents should not be able to widen their own scope. Scope changes must go through:
1. PR to update `agents[].scope` in unit `opi.yaml`
2. Review by unit lead + owner
3. Approval (follows normal change governance)

This prevents: Agent quietly adding units to its scope, agent gradually gaining more data access.

---

### Owner Accountability

The `owner` field is critical:
- Owner is accountable for agent behavior
- Owner must approve constraint changes
- Owner gets escalations from the agent
- Owner can disable or reconfigure agent

Example escalation from agent to owner:
```
"Constraint violation detected: requested to modify metrics data.
 Constraint: 'cannot modify data sources'.
 Escalation to owner: head-of-delivery.
 Action: decision aborted, logged to audit trail."
```

---

### Audit Trail Requirements

Every agent action must be logged with:
- **What** — action attempted (e.g., "created budget report")
- **When** — timestamp (ISO 8601 UTC)
- **Who** — agent ID + owner ID
- **Why** — which capability triggered this
- **Result** — success/failure + reason if failed
- **Constraint checks** — which constraints were validated

Format example (Git commit):
```
commit a3f8e2c

Author: delivery-analyst <delivery-analyst@agents>
Date: 2026-03-13T06:00:00Z

[agent:delivery-analyst] Weekly KPI report generated

- Weekly metrics aggregated (delivery, engineering units)
- Anomalies detected: 2 critical, 1 warning
- Escalation: sent to head-of-delivery
- Constraints validated: 5/5 passed
- Report artifact: gs://org/reports/2026-W11-delivery-status.md
```

---

### Escalation Contract

When an agent constraint requires escalation, the escalation message MUST include:
- Reason for escalation (which constraint/threshold was violated)
- Recommended action (if advisory agent)
- Deadline for owner response (if blocking)
- Audit context (what triggered this)

Example:
```
ESCALATION ALERT — delivery-analyst to head-of-delivery

Constraint: "Must escalate anomalies (severity > warning) to unit-lead within 24h"
Anomaly: Engineering throughput dropped 35% (sprint-over-sprint)
Severity: critical
Detected: 2026-03-13T06:15:00Z
Recommended action: Review team capacity, investigate blockers
Deadline: 2026-03-14 EOD
Audit ID: git:a3f8e2c
```

---

## 12. Relationship Between Features

### Agents ↔ Roles (F1)

Agents and roles are separate concerns:
- **Roles** (`components.roles`) describe human jobs: skills, accountabilities, reporting lines
- **Agents** describe AI capabilities, constraints, governance

Connection:
- Agent `owner` field references a role
- Agent scope can be limited to specific role groups (e.g., "access to data reviewed by Data Steward role")

Example:
```yaml
# In a Data Governance unit:
agents:
  - ref: data-quality-auditor
    scope:
      units: [data-lake, data-warehouse]
      data: [schema, quality-metrics]
      governance: read-only
```

---

### Agents ↔ Drift Detection (F2 ↔ F3)

Drift Detection is a primary use case for **Analytical Agents**.

| Phase | Agent Capability | Human Role |
|-------|---|---|
| **Detection** | Scan spec vs. status; identify deltas; generate drift entries | Review, validate |
| **Analysis** | Compute trend from history; flag anomalies; explain root causes | Interpret; decide |
| **Reporting** | Aggregate drifts by field/severity/unit; prepare dashboards | Present to leadership |
| **Reconciliation** | Propose corrections (hiring plans, SLA adjustments); track progress | Approve, execute |

Example: Drift Monitor Agent

```yaml
# In org.yaml or components.agents:
components:
  agents:
    drift-monitor:
      name: "Drift Monitor Agent"
      type: analytical
      purpose: "Scans all units weekly for spec-vs-status drift; generates reports"
      capabilities:
        - "Load all unit OPI documents (spec section)"
        - "Query current org state from HRIS, BI, calendar systems"
        - "Compare spec vs. actual; detect deviations"
        - "Generate drift[] entries with severity and trend"
        - "Aggregate drifts into weekly report"
        - "Flag critical drifts for immediate escalation"
      constraints:
        - "Read-only access to org data; cannot modify spec"
        - "Cannot approve decisions; only proposes"
        - "Must escalate critical drifts within 4 hours"
      owner: Head of Org Development
```

---

## 13. Complete Example: Product Organization

A realistic unit definition using all three V0.4 features:

```yaml
opi: "0.4.0"

unit:
  id: product
  name: "Product Organization"
  purpose: "Define product strategy, roadmap, and user success metrics"
  type: stream-aligned
  derived_from: spotify-squad

components:
  roles:
    product-lead:
      title: "Product Lead"
      level: senior
      job_family: product
      purpose: "Owns product roadmap and stakeholder alignment"
      accountabilities:
        - "Define and prioritize product roadmap"
        - "Align stakeholders on product direction"
        - "Own product KPIs and success metrics"
      skills:
        required:
          - "Product management"
          - "Stakeholder management"
          - "Data-driven decision making"
      decision_authority:
        - scope: "Product roadmap priorities"
          framework: DACI
          daci: driver
      reports_to: head-of-product

  agents:
    delivery-analyst:
      name: "Delivery Analytics Agent"
      type: analytical
      purpose: "Weekly KPI monitoring and anomaly detection"
      capabilities:
        - "Read delivery metrics from BI pipeline"
        - "Generate status reports"
        - "Flag anomalies"
      constraints:
        - "Cannot modify data"
        - "Cannot access confidential financial data"
        - "Must escalate to product-lead within 24h"
      governance:
        may_read: true
        may_write: false
        may_decide: false
        audit_trail: git
      owner: product-lead

members:
  # Product Lead (head of unit)
  - role_ref: product-lead
    name: "Maria Schmidt"
    start_date: 2025-06-01
    capacity: 1.0
    daci: driver
    reports_to: head-of-product

agents:
  - ref: delivery-analyst
    scope:
      units: [product, engineering]
      data: [metrics, reports, status]
      governance: none
    schedule:
      cadence: weekly
      day: Monday
      time: "06:00"

interfaces:
  outputs:
    - name: "product-roadmap"
      audience: "Engineering, Design, Sales"
      frequency: "quarterly"
      format: markdown document

status:
  observed_version: "2026-Q1"
  conditions:
    - type: Staffed
      status: "True"
      reason: "All 2 positions filled"
      since: 2026-01-10

  drift:
    - field: members
      expected: 3
      actual: 2
      delta: -1
      severity: warning
      since: 2026-02-15
      trend: improving
      note: "1 vacant PM position; actively recruiting. First interview scheduled 2026-03-20."

    - field: interfaces.outputs[0].frequency
      expected: "quarterly"
      actual: "last delivered 2026-02-01 (1 week overdue)"
      delta: "P1W"
      severity: warning
      since: 2026-02-08
      trend: improving
      note: "Q1 roadmap delayed due to strategy review. Final draft ready for review by 2026-03-20."
```

---

## 14. File Organization (v0.4 extension)

Standard file layout for OPI documents with v0.4 features:

```
org-repo/
├── org.yaml                          # Org-level config + agent registry
├── components/
│   ├── roles.yaml                    # Shared role definitions
│   └── agents.yaml                   # Shared agent type definitions
├── units/
│   ├── product/
│   │   └── opi.yaml                  # Product unit + agent scoping
│   ├── engineering/
│   │   └── opi.yaml
│   └── steering-committee/
│       └── opi.yaml
└── docs/
    ├── examples/
    │   ├── roles-example.yaml
    │   ├── agents-example.yaml
    │   └── drift-example.yaml
    └── migration-v03-to-v04.md
```

---

## 15. Migration Guide: v0.3 → v0.4

### Breaking Changes

**None.** OPI v0.4 is fully backward compatible with v0.3.

### Upgrading

1. **No action required.** Your v0.3 documents continue to work with `role: "inline string"` in `members[]`.

2. **Optional: Migrate to `role_ref`.** Extract repeating roles from multiple units, define them in `components.roles`, replace `role: "..."` with `role_ref: key`.

3. **Optional: Add agents.** Define analytical agents to automate drift detection and reporting.

4. **Optional: Add drift entries.** Start capturing spec-vs-status deviations in `status.drift[]`.

### Example Migration

**Before (v0.3):**
```yaml
# units/product/opi.yaml
members:
  - role: "Product Lead"
    name: "Maria"

# units/sales/opi.yaml
members:
  - role: "Product Lead"
    name: "Marcus"
```

**After (v0.4):**
```yaml
# org.yaml
components:
  roles:
    product-lead:
      title: "Product Lead"
      # ... full definition

# units/product/opi.yaml
members:
  - role_ref: product-lead
    name: "Maria"

# units/sales/opi.yaml
members:
  - role_ref: product-lead
    name: "Marcus"
```

---

## 16. Tooling Interface Requirements

### For Roles (F1)

- **Visualization:** Generate org charts from `roles[].reports_to` chains
- **HR Integration:** Export `components.roles` as input to job evaluation and workforce planning tools
- **Career Ladders:** Group roles by `job_family` and `level` to show progression paths
- **Skill Heatmaps:** Aggregate `skills.required` across roles to identify org skill gaps

### For Agents (F2)

**Agent Orchestration Runtime must:**
1. Load agent definition from `components.agents`
2. Validate against rules 53–58
3. Load scope from unit-level `agents[]` instance
4. Resolve agent owner (get contact, escalation path)
5. Prepare constraint validators
6. Execute agent task/schedule
7. Validate each output against constraints
8. Log all actions to audit trail
9. If constraint violated → escalate to owner
10. Commit audit entry (Git or event log)

### For Drift (F3)

**Drift Detection Tooling must support:**
1. **Drift Detection:** Scan spec vs. status; identify and generate drift entries
2. **Severity Assignment:** Infer from delta magnitude and context
3. **Trend Computation:** Examine historical drift entries; compute trajectory
4. **Querying & Filtering:** `drift where severity = critical`, `drift where trend = worsening`, etc.
5. **Alerting:** IF severity = critical THEN alert immediately
6. **Reconciliation:** Enable closing drift by proposing corrections

---

## 17. FAQ

**Q: Why separate roles and agents?**
A: They serve different purposes. Roles describe human jobs (skills, career paths, responsibilities). Agents describe AI capabilities (what they can do, what they cannot do, governance boundaries). Both can reference the same `governance.framework`, but they're different entities.

---

**Q: Can an agent be the "owner" of another agent?**
A: No. The `owner` field MUST be a human (member) or human role. This enforces accountability — humans are responsible for agent behavior.

---

**Q: What if my org doesn't use agents yet?**
A: You don't need them. The `agents[]` block is optional. Start with roles if you want HR tool integration, or start with drift if you want to track deviations. Adopt features incrementally.

---

**Q: How do I migrate from inline roles to role_ref?**
A: No breaking changes. Both work in v0.4. You can migrate incrementally: start with high-reuse roles (e.g., "Product Lead" used in 5 units), define those in `components.roles`, update those units to use `role_ref`. Leave low-reuse, one-off roles inline. Over time, the library grows.

---

**Q: Can drift entries be closed / archived?**
A: Yes, via Git. When drift is resolved, either:
1. Delete the entry (if using Git, it's in history anyway)
2. Update the entry with `closed: true` (optional extension)
3. Update the spec to match reality, then remove the drift entry

For audit purposes, Git provides full history.

---

**Q: What if two drift entries describe the same field?**
A: Don't. Each field should have at most one active drift entry. If the field drifts again after being resolved, remove the old entry and create a new one. Git will show both in history.

---

## 18. Changelog

### v0.4.0 (2026-03-13)

**Additions:**

- `components.roles` — Reusable role definitions with skills, qualifications, decision authority, and job family mapping
- `members[].role_ref` — Reference existing roles instead of inline strings
- `components.agents` — Agent type definitions with capabilities, constraints, governance
- `agents[]` (unit-level) — Agent instantiation with scope, schedule, and governance rules
- `status.drift[]` — Spec-vs-status deviation tracking with severity, trend, and delta
- **Validation Rules 48–62** — Coverage for roles, agents, and drift

**Principles:**

- All features backward compatible with v0.3
- Governance as the permission model (agents governed by explicit constraints, not implicit permissions)
- Minimal spec, powerful tooling (drift structure is in spec; detection, alerting, reconciliation belong to tooling)

**Migration:** No breaking changes. Adopt features incrementally.

---

## Appendix: Spotify Model Roles Example

```yaml
components:
  roles:
    squad-lead:
      title: "Squad Lead"
      level: lead
      job_family: engineering-squad
      purpose: "Leads cross-functional squad toward mission"
      accountabilities:
        - "Set squad roadmap and priorities"
        - "Manage squad budget and hiring"
        - "Represent squad at tribe sync"
      decision_authority:
        - scope: "Squad roadmap"
          framework: DACI
          daci: driver
      reports_to: tribe-lead

    chapter-lead:
      title: "Chapter Lead"
      level: lead
      job_family: engineering-chapter
      purpose: "Develops functional skill across squads"
      accountabilities:
        - "Mentor chapter members on skill development"
        - "Advocate for technical best practices"
      decision_authority:
        - scope: "Technical standards"
          framework: consent
          daci: driver
      reports_to: tribe-lead
```

---

## Appendix: Consulting Firm Roles Example

```yaml
components:
  roles:
    engagement-manager:
      title: "Engagement Manager"
      level: senior
      job_family: consulting-delivery
      purpose: "Owns client relationship and delivery success"
      accountabilities:
        - "Lead client engagement (requirements, scope, delivery)"
        - "Manage delivery team and budget"
        - "Report to client and internal stakeholders"
      decision_authority:
        - scope: "Scope changes < 10% effort"
          framework: DACI
          daci: approver
        - scope: "Scope changes > 10% effort"
          framework: DACI
          daci: contributor
      reports_to: partner

    consultant:
      title: "Consultant"
      level: mid
      job_family: consulting-delivery
      purpose: "Delivers client work and builds methodologies"
      accountabilities:
        - "Execute client deliverables"
        - "Capture and codify best practices"
      decision_authority:
        - scope: "Technical approach (within scope)"
          framework: DACI
          daci: driver
      reports_to: engagement-manager
```

---

**End of OPI Specification v0.4 Addendum**

This document extends v0.3 with production-ready capabilities for role management, agent governance, and drift detection. All features are optional and backward compatible.

For questions or feedback, refer to the main OPI repository and community.
