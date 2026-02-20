# OPI Specification v0.2

**Organizational Programming Interface — A machine-readable format for organizational design.**

---

## Abstract

The OPI Specification defines a standard, language-agnostic format for describing organizational units and their interfaces. An OPI document describes: what a unit is responsible for, how it makes decisions, what it produces and consumes, and how it connects to other units.

OPI is to organizational design what OpenAPI is to software APIs — a contract that makes the invisible visible.

## Status

Draft — v0.2 (February 2026)

## Design Principles

| # | Principle | Rationale |
|---|-----------|-----------|
| 1 | **Human-readable, machine-parseable** | YAML as primary format. Any person should understand it; any tool should parse it. |
| 2 | **One file per unit** | Each organizational unit owns its OPI document (`opi.yaml`). Distributed authorship. |
| 3 | **Schema-first** | Reusable definitions in `components`. Reference via `$ref` (JSON Pointer). |
| 4 | **Governance as first-class citizen** | Decision rights, authority levels, escalation paths are not metadata — they are core. |
| 5 | **Interfaces over hierarchy** | Explicit inputs/outputs/events between units matter more than reporting lines. |
| 6 | **Extensible** | Custom fields via `x-` prefix. Organizations can extend without forking the spec. |
| 7 | **Versionable** | Every document carries a version. Changes are tracked via Git, reviewed via PR. |

## Prior Art & Differentiation

| Spec | Focus | Governance? | Interfaces? | Decision Modeling? | Status |
|------|-------|:-----------:|:-----------:|:------------------:|--------|
| [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0.html) | Software APIs | — | Yes | — | Industry standard |
| [AsyncAPI 3.0](https://www.asyncapi.com/docs/reference/specification/v3.0.0) | Event-driven APIs | — | Yes | — | CNCF |
| [TeamAPI-As-Code](https://github.com/TeamTopologies/TeamAPI-As-Code) | Team interfaces | — | Partial | — | Dormant (since 2022) |
| [Backstage Catalog](https://backstage.io/docs/features/software-catalog/) | Software ownership | — | Partial | — | CNCF, 29k stars |
| [GlassFrog / Holacracy](https://www.glassfrog.com/) | Circle governance | Yes (Holacracy only) | — | Yes (Holacracy only) | Production, proprietary |
| [Company as Code](https://blog.42futures.com/p/company-as-code) | Org as executable code | Concept | Concept | Concept | Blog post only (Feb 2025) |
| [TOSCA 2.0](https://docs.oasis-open.org/tosca/TOSCA/v2.0/TOSCA-v2.0.html) | Cloud topology | — | Yes (capabilities/requirements) | — | OASIS standard |
| [Kubernetes CRDs](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) | Desired vs. actual state | — | — | — | Industry standard |
| **OPI** | **Org unit interfaces** | **Yes** | **Yes** | **Yes** | **This spec** |

**The gap OPI fills:** No existing spec combines organizational structure, decision governance, and interface definitions in a single, machine-readable format. TeamAPI-As-Code lacks governance entirely. GlassFrog is Holacracy-locked and proprietary. "Company as Code" has no implementation. Enterprise platforms (Orgvue, Nakisa, ChartHop) are GUI-first with no open formats.

**Key inspirations:** OpenAPI (document structure, `$ref`, extensions), TOSCA (capability-requirement matching), Kubernetes (spec/status separation), Team Topologies (interaction types), Holacracy (role reification).

---

## Document Structure

An OPI document is a YAML file with the following top-level structure:

```yaml
opi: "0.2.0"          # REQUIRED — Spec version

unit: {}               # REQUIRED — Identity & metadata
members: []            # Roles & accountabilities
capabilities: {}       # What this unit provides
interfaces: {}         # Inputs & outputs
events: {}             # Async notifications (pub/sub)
governance: {}         # Decision framework
schedule: {}           # When this unit meets (time, cadence, recurrence)
channels: {}           # Communication endpoints
dependencies: []       # Explicit unit dependencies
flows: []              # Decision & information flows across units (v0.2)
references: []         # External documentation
components: {}         # Reusable definitions
```

All top-level fields except `opi` and `unit` are OPTIONAL.

---

## Schema Reference

### `opi` (string, REQUIRED)

The OPI Specification version this document conforms to. Semantic versioning.

```yaml
opi: "0.1.0"
```

---

### `unit` (object, REQUIRED)

Identity and metadata of the organizational unit. Analogous to OpenAPI's `info` object.

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `name` | string | **Yes** | Human-readable name |
| `id` | string | No | Machine-readable identifier (slug). Defaults to slugified `name`. |
| `type` | enum | No | Unit classification (see Unit Types) |
| `purpose` | string | No | Why this unit exists (1-2 sentences) |
| `mandate` | string | No | What this unit is responsible for |
| `owner` | string | No | Accountable person (role or name) |
| `parent` | string | No | Parent unit reference (hierarchy) |
| `tags` | string[] | No | Discovery and categorization |
| `version` | string | No | Structural version (e.g. `"2026-Q1"`) |
| `derived_from` | string | No | Base unit type from `components.unit-types` (v0.2). Inherits defaults and required fields. |

#### Unit Types

```yaml
# Organizational units (Team Topologies + extensions)
type: stream-aligned     # Aligned to a business domain flow
     | platform           # Enables other units to deliver autonomously
     | enabling           # Helps units overcome obstacles, learn skills
     | leadership         # Executive and management units
     | support            # Shared services (HR, Finance, Legal)

# Meeting-type units (v0.2) — units that primarily exist as recurring interactions
     | committee          # Standing body with mandate & decision authority (Gremium)
     | meeting            # Recurring meeting without formal mandate
     | working-group      # Temporary, goal-oriented group (disbands when done)
     | circle             # Self-governing group (Holacracy/S3 pattern)
```

**Organizational units** (top group) are inspired by [Team Topologies](https://teamtopologies.com/key-concepts), extended with `leadership` and `support`.

**Meeting-type units** (v0.2) model committees, meetings, and groups as first-class OPI entities. A committee IS an organizational unit — it has a mandate, members with governance roles, scheduled interactions, and defined inputs/outputs. This enables calendar views, decision flow modeling, and meeting-specific I/O tracking.

> **When to use which type:**
> - `committee` — Has a formal mandate and decision authority (e.g. Steering Committee, Board)
> - `meeting` — Recurring without formal authority (e.g. All-Hands, Team Sync)
> - `working-group` — Temporary, created for a specific goal (e.g. Migration Task Force)
> - `circle` — Self-governing per Holacracy/S3 rules (e.g. Product Circle)

#### Examples

**Organizational unit:**

```yaml
unit:
  name: "Product Team"
  id: product-team
  type: stream-aligned
  purpose: "End-to-end product development and delivery"
  mandate: "Own product roadmap, feature delivery, and customer feedback loop"
  owner: "Head of Product"
  parent: engineering-division
  tags: [product, delivery, customer-facing]
  version: "2026-Q1"
```

**Meeting-type unit (v0.2):**

```yaml
unit:
  name: "Steering Committee"
  id: steering-committee
  type: committee
  purpose: "Strategic decisions for delivery organization"
  mandate: "Budget approval >10k EUR, headcount changes, unit restructuring"
  owner: "COO"
  parent: leadership
  tags: [governance, strategy, delivery]
  version: "2026-Q1"
```

---

### `members` (array)

People, roles, and their accountabilities within the unit. Each member is defined by their role, not by name — making the structure portable and privacy-safe.

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `role` | string | **Yes** | Role identifier (e.g. `lead`, `contributor`, `driver`, `approver`) |
| `position` | string | No | Position title or function |
| `name` | string | No | Person name (optional, for internal use) |
| `count` | integer | No | Number of people in this role (default: 1) |
| `accountabilities` | string[] | No | What this role is responsible for |
| `daci` | enum | No | Governance role in this unit's context: `driver` / `approver` / `contributor` / `informed` |
| `attendance` | enum | No | `permanent` / `optional` / `on-demand` (default: `permanent`) |

The `daci` field (v0.2) maps a member's **governance role** within this specific unit, separate from their organizational `role`. A person can be `lead` (organizational role) and `approver` (DACI role) in the same unit. For non-DACI frameworks, use the equivalent role mapping via `x-` extensions.

#### Examples

**Organizational unit:**

```yaml
members:
  - role: lead
    position: "Head of Product"
    accountabilities:
      - roadmap-ownership
      - stakeholder-alignment

  - role: contributor
    position: "Product Manager"
    count: 3

  - role: informed
    position: "COO"
```

**Meeting-type unit (committee):**

```yaml
members:
  - role: chair
    position: "COO"
    daci: approver
    attendance: permanent

  - role: member
    position: "Head of Delivery"
    daci: driver
    attendance: permanent

  - role: member
    position: "Head of Sales"
    daci: contributor
    attendance: permanent

  - role: guest
    position: "CFO"
    daci: informed
    attendance: on-demand
```

---

### `capabilities` (object)

What this unit provides to the organization. Analogous to OpenAPI's `paths` — the "endpoints" other units can consume.

Each capability is a named key with the following fields:

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `description` | string | **Yes** | What this capability does |
| `type` | enum | No | `core` / `support` / `advisory` |
| `cadence` | string | No | How often (e.g. `weekly`, `quarterly`, `on-demand`) |
| `sla` | object | No | Expected response time and quality level |
| `process` | object | No | How this capability is executed (trigger, steps, inputs, output, lanes) |

#### `capabilities.*.process` (object)

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `trigger` | string | No | What starts this process |
| `steps` | string[] | No | Simple ordered step list (single-unit process) |
| `lanes` | array | No | Multi-unit process with swimlanes (v0.2). Each lane defines which unit handles which steps. |
| `input` | object | No | What goes into this process |
| `output` | object | No | What comes out of this process |

#### `capabilities.*.process.lanes[]` — Swimlanes (v0.2)

Inspired by [BPMN swimlanes](https://www.omg.org/spec/BPMN/2.0/About-BPMN/) — visualize which unit handles which part of a cross-unit process. Each lane is one unit's responsibility within the larger process.

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `unit` | string | **Yes** | Unit or meeting responsible for this lane |
| `steps` | array | **Yes** | Ordered steps this unit performs |
| `handoff` | string | No | What is passed to the next lane |

Each step can be a simple string or a detailed object:

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `name` | string | **Yes** | Step name |
| `action` | string | No | Standard action (reuses flow action vocabulary) |
| `duration` | string | No | Expected duration |
| `gate` | string | No | Condition to proceed (decision gateway) |

> **Flows vs. Swimlanes:** `flows[]` model how a single item (decision, request) travels through the org. Swimlanes model how a **recurring process** is divided across units. A quarterly planning process has swimlanes; a budget approval has a flow. Use both when needed — they complement each other.

#### Examples

**Single-unit process (v0.1 style, still valid):**

```yaml
capabilities:
  feature-delivery:
    description: "Prioritize, build, and ship product features"
    type: core
    cadence: per-sprint
    sla:
      response_time: "sprint-aligned (2 weeks)"
      quality: "Definition of Done met"
    process:
      trigger: "Feature request submitted"
      steps:
        - "Triage & prioritize"
        - "Design & spec"
        - "Implementation"
        - "Review & deploy"
      output:
        artifact: shipped-feature
        format: release-notes
```

**Multi-unit process with swimlanes (v0.2):**

```yaml
capabilities:
  quarterly-planning:
    description: "Cross-unit quarterly planning cycle"
    type: core
    cadence: quarterly
    sla:
      response_time: "Completed within first 2 weeks of quarter"
    process:
      trigger: "Quarter start"
      lanes:
        - unit: unit-leads
          steps:
            - name: "Submit unit proposals"
              action: propose
              duration: "3 business days"
              handoff: unit-proposals

        - unit: delivery-lead-sync
          steps:
            - name: "Consolidate proposals"
              action: review
              duration: "2 business days"
            - name: "Resolve conflicts & dependencies"
              action: review
              gate: "All cross-unit dependencies resolved"
              handoff: consolidated-plan

        - unit: steering-committee
          steps:
            - name: "Review consolidated plan"
              action: review
              duration: "1 meeting"
            - name: "Approve budget allocation"
              action: approve
              gate: "Budget within approved limits"
              handoff: approved-plan

        - unit: unit-leads
          steps:
            - name: "Break down into sprint goals"
              action: execute
              duration: "3 business days"
            - name: "Commit to quarterly deliverables"
              action: report

      output:
        artifact: quarterly-plan
        format: markdown
```

**How this renders as a swimlane diagram:**

```
┌─────────────────┬─────────────────────────────────────────────────────────────────┐
│   Unit Leads    │ [Submit proposals] ─────────────────────── [Break down] → [Commit] │
├─────────────────┼────────────────────┐                          ▲               │
│ Delivery Leads  │    [Consolidate] → [Resolve conflicts] ───────┘               │
├─────────────────┼─────────────────────────────┐                                 │
│ Steering        │            [Review plan] → [Approve budget] ──────────────────┘ │
└─────────────────┴─────────────────────────────────────────────────────────────────┘
```

---

### `interfaces` (object)

Explicit inputs and outputs between this unit and others. The core of OPI — making information flow visible and contractual.

#### `interfaces.inputs` (array)

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `from` | string | **Yes** | Source unit (id or name) |
| `artifact` | string | **Yes** | What is received |
| `format` | string | No | Format (e.g. `yaml`, `markdown`, `spreadsheet`) |
| `cadence` | string | No | Expected frequency |
| `required` | boolean | No | Whether this input is mandatory (default: `false`) |

#### `interfaces.outputs` (array)

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `to` | string | **Yes** | Target unit (id or name) |
| `artifact` | string | **Yes** | What is delivered |
| `format` | string | No | Format |
| `cadence` | string | No | Delivery frequency |

#### Example

```yaml
interfaces:
  inputs:
    - from: sales
      artifact: customer-feedback
      format: markdown
      cadence: weekly
      required: true

    - from: board
      artifact: strategic-direction
      format: decision-record
      cadence: quarterly

  outputs:
    - to: sales
      artifact: product-roadmap
      format: markdown
      cadence: monthly

    - to: board
      artifact: product-metrics
      format: yaml
      cadence: monthly
```

---

### `events` (object)

Asynchronous notifications — what a unit broadcasts and subscribes to. Inspired by [AsyncAPI](https://www.asyncapi.com/).

#### `events.publishes` (array)

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `name` | string | **Yes** | Event identifier |
| `description` | string | No | What triggers this event |
| `subscribers` | string[] | No | Units that should receive this |

#### `events.subscribes` (array)

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `name` | string | **Yes** | Event identifier |
| `source` | string | **Yes** | Publishing unit |
| `triggers` | string | No | What action this event triggers internally |

#### Example

```yaml
events:
  publishes:
    - name: roadmap-updated
      description: "Quarterly roadmap was revised"
      subscribers: [sales, engineering, board]

  subscribes:
    - name: budget-approved
      source: finance
      triggers: "Unlock hiring pipeline"
```

---

### `governance` (object)

Decision-making framework. **This is OPI's key differentiator** — no other spec models organizational decision rights.

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `framework` | enum | No | Default decision framework (see Governance Frameworks) |
| `decisions` | array | No | Decision types with authority mapping |
| `change_process` | object | No | How structural changes to this unit are governed (v0.2) |

#### Governance Frameworks

OPI supports multiple decision-making frameworks. Each unit chooses what fits its culture:

```yaml
framework: DACI         # Driver, Approver, Contributor, Informed (Atlassian)
         | RAPID        # Recommend, Agree, Perform, Input, Decide (Bain)
         | OVIS         # Own, Veto, Influence, Support (BCG, public sector)
         | consent      # No objections = approved (Sociocracy 3.0)
         | consensus    # All agree (traditional)
         | autocratic   # Single decision maker
```

The `decisions[]` entry fields (`driver`, `approver`, `contributors`, `informed`) map to DACI. For other frameworks, use `x-` extensions or the generic `authority` field:

```yaml
# RAPID example
governance:
  framework: RAPID
  decisions:
    - type: hiring
      x-recommend: recruiter
      x-agree: legal
      x-perform: hiring-manager
      x-input: [team-lead, hr-business-partner]
      x-decide: department-head
```

#### Decision Entry

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `type` | string | **Yes** | Decision category (e.g. `hiring`, `budget`, `strategic`) |
| `driver` | string | No | Person/role driving the decision (DACI: D) |
| `approver` | string | No | Person/role with final authority (DACI: A) |
| `contributors` | string[] | No | People/roles consulted (DACI: C) |
| `informed` | string[] | No | People/roles notified after (DACI: I) |
| `authority` | enum | No | `decide` / `approve` / `delegate` / `escalate` |
| `quorum` | integer | No | Minimum participants for valid decision |
| `threshold` | string | No | Condition that triggers this decision type (e.g. `">50k EUR"`) |
| `escalation` | string | No | Where unresolved decisions go |
| `documentation` | string | No | How decisions are recorded |

#### Example

```yaml
governance:
  framework: DACI
  decisions:
    - type: feature-prioritization
      driver: head-of-product
      approver: cto
      contributors: [sales, engineering]
      informed: [board]
      authority: decide
      escalation: steering-committee

    - type: budget
      driver: head-of-product
      approver: cfo
      authority: approve
      threshold: ">10k EUR"
      escalation: board
      documentation: decision-log
```

#### `governance.change_process` — Structural Change Governance (v0.2)

How changes to the org structure itself (this OPI document) are proposed, reviewed, and approved. Inspired by [Holacracy governance meetings](https://www.holacracy.org/constitution/5-0/) (propose → react → amend → integrate) and Git-based workflows.

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `proposal` | string | No | How changes are proposed (e.g. `"Pull Request on GitHub"`, `"Governance Meeting"`) |
| `review` | array | No | Review steps before approval |
| `approval` | array | No | Approval steps |
| `communication` | array | No | How approved changes are communicated |
| `cadence` | string | No | How often structural reviews happen (e.g. `quarterly`) |

Each `review[]` and `approval[]` entry:

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `role` | string | **Yes** | Who reviews or approves |
| `action` | string | No | `review` / `approve` / `consent` / `veto` |
| `deadline` | string | No | Expected turnaround |
| `quorum` | integer | No | Minimum participants for valid decision |

> **Why this matters:** Without explicit change governance, org structures drift silently. With `change_process`, every structural change (new unit, mandate shift, role change) follows a defined path — just like code changes follow a PR process.

#### Example

```yaml
governance:
  framework: DACI
  change_process:
    proposal: "Pull Request on org-as-code repository"
    review:
      - role: affected-unit-leads
        action: review
        deadline: "5 business days"
      - role: people-culture
        action: review
        deadline: "5 business days"
    approval:
      - role: steering-committee
        action: approve
        quorum: 3
    communication:
      - to: all-units
        trigger: merged
        format: changelog
        channel: email
      - to: affected-unit-leads
        trigger: merged
        format: decision-record
        channel: teams
    cadence: quarterly

  decisions:
    - type: feature-prioritization
      # ... (as before)
```

---

### `schedule` (object) — v0.2

When a unit meets — time, cadence, recurrence. Primarily used for meeting-type units (`committee`, `meeting`, `working-group`, `circle`) but also valid for any unit with regular sync meetings.

The `schedule` block provides enough structured data to generate **calendar views** (timetables) and **ICS calendar exports**.

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `cadence` | string | **Yes** | Frequency: `daily` / `weekly` / `biweekly` / `monthly` / `quarterly` / `biannual` / `annual` / `on-demand` |
| `day` | string | No | Scheduled day(s) (e.g. `Monday`, `"Monday,Wednesday"`) |
| `time` | string | No | Start time in 24h format (e.g. `"10:00"`) |
| `duration` | string | No | Expected length (e.g. `30min`, `90min`, `2h`) |
| `location` | string | No | Physical or virtual location |
| `timezone` | string | No | IANA timezone (e.g. `Europe/Berlin`). Default: organization-wide setting. |
| `recurrence` | object | No | Machine-readable recurrence for calendar export |
| `exceptions` | string[] | No | Dates when the meeting does NOT occur (e.g. holidays) |

#### `schedule.recurrence` (object)

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `type` | string | **Yes** | `rrule` (iCalendar RFC 5545) |
| `value` | string | **Yes** | RRULE string (e.g. `"FREQ=WEEKLY;INTERVAL=2;BYDAY=WE"`) |

The `recurrence` field uses [iCalendar RRULE](https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.10) syntax. This enables direct ICS export: tooling combines `unit.name` + `schedule` + `members` to generate calendar invitations.

#### Examples

**Biweekly committee:**

```yaml
schedule:
  cadence: biweekly
  day: Wednesday
  time: "10:00"
  duration: 90min
  location: "Room A / Microsoft Teams"
  timezone: Europe/Berlin
  recurrence:
    type: rrule
    value: "FREQ=WEEKLY;INTERVAL=2;BYDAY=WE"
```

**Quarterly board meeting:**

```yaml
schedule:
  cadence: quarterly
  day: Friday
  time: "09:00"
  duration: 4h
  location: "Headquarters, Board Room"
  timezone: Europe/Berlin
  recurrence:
    type: rrule
    value: "FREQ=MONTHLY;INTERVAL=3;BYDAY=3FR"
  exceptions:
    - "2026-12-27"   # Holiday break
```

**Weekly team sync (on a regular unit):**

```yaml
schedule:
  cadence: weekly
  day: Tuesday
  time: "09:30"
  duration: 30min
  location: "Microsoft Teams"
```

---

### `channels` (object)

How people communicate within and with this unit. Analogous to OpenAPI's `servers`.

> **v0.2 note:** For meeting-type units (`committee`, `meeting`, etc.), prefer using the top-level `schedule` block instead of `channels.sync`. Use `channels.sync` for regular units that want to list their internal meetings inline, or to reference meeting-type units via `$ref`.

#### `channels.sync` (array) — Meetings and rituals

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `type` | string | **Yes** | `meeting` / `workshop` / `standup` / `review` |
| `name` | string | **Yes** | Meeting name |
| `cadence` | string | No | Frequency |
| `duration` | string | No | Expected length |
| `day` | string | No | Scheduled day(s) |
| `rituals` | object | No | Pre/during/post protocols |
| `$ref` | string | No | Reference to a meeting-type unit (v0.2) |

#### `channels.async` (array) — Digital channels

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `type` | string | **Yes** | `slack` / `email` / `teams` / `wiki` / `ticket-system` |
| `name` | string | **Yes** | Channel identifier |
| `purpose` | string | No | What this channel is for |

#### Example

```yaml
channels:
  sync:
    - type: meeting
      name: "Product Weekly"
      cadence: weekly
      duration: 30min
      day: Tuesday
      rituals:
        pre: ["Agenda shared 24h before"]
        during: ["Timeboxed (max 10min/topic)", "Decisions logged"]
        post: ["Action items published same day"]

  async:
    - type: slack
      name: "#product-team"
      purpose: "Internal coordination"
    - type: email
      name: "product@acme.com"
      purpose: "External requests"
```

---

### `dependencies` (array)

Explicit dependencies on other units. Makes organizational coupling visible.

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `unit` | string | **Yes** | Referenced unit |
| `type` | enum | No | `collaboration` / `x-as-a-service` / `facilitating` / `blocking` |
| `description` | string | No | Nature of the dependency |
| `health` | enum | No | `ok` / `at-risk` / `blocked` |
| `note` | string | No | Details if health is not `ok` |

Interaction types follow [Team Topologies](https://teamtopologies.com/key-concepts):
- **collaboration** — Joint work, high bandwidth, temporary
- **x-as-a-service** — Consume with minimal coordination
- **facilitating** — One unit helps another grow a capability
- **blocking** — Hard dependency, work stops without resolution

#### Example

```yaml
dependencies:
  - unit: platform-team
    type: x-as-a-service
    description: "CI/CD, monitoring, infrastructure"
    health: ok

  - unit: legal
    type: x-as-a-service
    description: "Contract review for enterprise deals"
    health: at-risk
    note: "Average response >5 days, SLA is 3 days"
```

---

### `flows` (array) — v0.2

Cross-unit decision and information flows. **This is what makes org-as-code actionable** — not just static structure, but visible movement of decisions, escalations, and information through the organization.

A flow describes a **path** that a decision, request, or piece of information takes across multiple units. Each station in the path defines: who receives it, what action they take, under what conditions, and where it goes next.

Flows can be defined inline (in a unit's OPI document) or as **standalone flow documents** in a `flows/` directory. Standalone flow documents are recommended for flows that span 3+ units.

> **Design inspiration:** BPMN decision gateways (conditions at each station), gRPC method types (unary/stream/batch/collaborative), ArchiMate message flows.

#### Flow Object

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `name` | string | **Yes** | Human-readable flow name |
| `id` | string | No | Machine-readable identifier (slug) |
| `type` | enum | No | `decision` / `information` / `escalation` / `change-request` |
| `description` | string | No | What this flow does |
| `trigger` | string | No | What initiates this flow |
| `path` | array | **Yes** | Ordered sequence of stations |
| `communication` | array | No | Notifications triggered by outcomes |
| `fallback` | object | No | Default behavior on timeout or unresolved state |

#### Flow Types

```yaml
type: decision          # A decision traveling through approval levels
     | information       # Information being distributed or aggregated
     | escalation        # A problem being escalated up the hierarchy
     | change-request    # A structural change to the organization itself
```

#### `flows[].path[]` — Stations

Each station is a stop in the flow where a unit acts on the item.

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `station` | string | **Yes** | Unit id or meeting id that handles this step |
| `action` | string | **Yes** | What happens here (e.g. `identify`, `review`, `approve`, `ratify`, `inform`) |
| `description` | string | No | Detail on what this station does |
| `condition` | string | No | When this station activates (e.g. `"amount > 10k EUR"`) |
| `input` | string | No | Artifact received at this station |
| `output` | string | No | Artifact produced at this station |
| `governance` | object | No | Inline DACI/governance for this specific step |
| `sla` | string | No | Expected turnaround time (e.g. `"5 business days"`) |

#### Station Actions

Standard action vocabulary:

| Action | Meaning |
|--------|---------|
| `identify` | Recognize a need or problem |
| `propose` | Create a formal proposal |
| `review` | Evaluate without decision authority |
| `approve` | Grant approval (with potential conditions) |
| `ratify` | Confirm a decision made elsewhere |
| `reject` | Decline with feedback |
| `escalate` | Forward to a higher authority |
| `inform` | Distribute information (no action required) |
| `execute` | Carry out an approved decision |
| `report` | Deliver a status update |

#### `flows[].communication[]` — Notifications

Triggered when a flow reaches a specific outcome.

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `trigger` | string | **Yes** | Outcome that activates this notification (e.g. `approved`, `rejected`, `escalated`, `completed`) |
| `to` | string[] | **Yes** | Target units or meetings |
| `artifact` | string | No | What is communicated |
| `format` | string | No | Format of the communication |
| `channel` | string | No | Delivery channel (e.g. `email`, `teams`, `wiki`) |

#### `flows[].fallback` (object)

Default behavior when a flow stalls.

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `timeout` | string | **Yes** | Duration before fallback activates (e.g. `"14d"`, `"5 business days"`) |
| `action` | enum | **Yes** | `escalate` / `auto-approve` / `reject` / `notify` |
| `to` | string | No | Target unit for escalation |
| `notify` | string[] | No | Who gets notified about the stall |

#### Examples

**Decision flow: Budget approval across 3 levels**

```yaml
flows:
  - name: "Budget Approval"
    id: budget-approval
    type: decision
    description: "Budget requests travel through up to 3 approval levels depending on amount"
    trigger: "Unit lead identifies budget need"

    path:
      - station: delivery-lead-sync
        action: identify
        description: "Delivery Lead identifies budget need during weekly sync"
        output: budget-request

      - station: steering-committee
        action: approve
        condition: "amount > 10k EUR"
        input: budget-request
        output: budget-decision
        governance:
          framework: DACI
          driver: head-of-delivery
          approver: coo
        sla: "Next scheduled meeting (max 14d)"

      - station: board
        action: ratify
        condition: "amount > 50k EUR"
        input: budget-decision
        output: ratified-budget
        governance:
          framework: DACI
          driver: coo
          approver: board-chair
        sla: "Next board meeting (max 90d)"

    communication:
      - trigger: approved
        to: [delivery-lead-sync, finance, all-hands]
        artifact: budget-announcement
        format: decision-record
        channel: teams

      - trigger: rejected
        to: [delivery-lead-sync]
        artifact: rejection-with-feedback
        format: markdown

      - trigger: escalated
        to: [board, coo]
        artifact: escalation-notice
        format: decision-record

    fallback:
      timeout: "14d"
      action: escalate
      to: board
      notify: [coo, head-of-delivery]
```

**Information flow: Monthly reporting (bottom-up aggregation)**

```yaml
flows:
  - name: "Monthly Delivery Report"
    id: monthly-delivery-report
    type: information
    description: "Unit metrics aggregate upward into steering and board reports"
    trigger: "Month end"

    path:
      - station: unit-leads
        action: report
        description: "Each unit lead submits unit metrics"
        output: unit-metrics
        sla: "By 3rd business day"

      - station: delivery-lead-sync
        action: review
        description: "Head of Delivery consolidates into delivery report"
        input: unit-metrics
        output: delivery-report
        sla: "By 5th business day"

      - station: steering-committee
        action: review
        description: "Steering reviews delivery performance"
        input: delivery-report
        output: steering-summary
        sla: "Next scheduled meeting"

      - station: board
        action: inform
        description: "Board receives executive summary"
        input: steering-summary

    communication:
      - trigger: completed
        to: [all-hands]
        artifact: monthly-highlights
        format: markdown
        channel: email
```

**Escalation flow: Cross-unit blocker resolution**

```yaml
flows:
  - name: "Cross-Unit Blocker"
    id: cross-unit-blocker
    type: escalation
    description: "When one unit blocks another, escalate through defined path"
    trigger: "Unit dependency health becomes 'blocked'"

    path:
      - station: affected-unit
        action: identify
        description: "Affected unit raises blocker"
        output: blocker-report

      - station: delivery-lead-sync
        action: review
        description: "Delivery Leads attempt to resolve peer-to-peer"
        input: blocker-report
        condition: "blocker not resolved in 5d"
        output: escalation-report
        sla: "5 business days"

      - station: steering-committee
        action: approve
        description: "Steering decides resource reallocation or priority change"
        input: escalation-report
        output: resolution-decision
        governance:
          driver: head-of-delivery
          approver: coo

    communication:
      - trigger: resolved
        to: [affected-unit, blocking-unit]
        artifact: resolution-decision
        format: decision-record

    fallback:
      timeout: "10d"
      action: escalate
      to: coo
      notify: [affected-unit, blocking-unit, head-of-delivery]
```

#### Standalone Flow Documents

For flows spanning 3+ units, use standalone files in `flows/`:

```
org/
├── units/
├── meetings/
├── flows/                         # Cross-unit flows (v0.2)
│   ├── budget-approval.yaml
│   ├── monthly-reporting.yaml
│   ├── cross-unit-blocker.yaml
│   └── hiring-process.yaml
├── governance/
├── components/
└── README.md
```

A standalone flow document uses the same `opi` header and wraps the flow in a `flow` key:

```yaml
opi: "0.2.0"
flow:
  name: "Budget Approval"
  id: budget-approval
  type: decision
  path: [...]
  communication: [...]
  fallback: {}
```

When defined inline (within a unit document), flows are nested in the `flows` array. Tooling SHOULD support both locations.

---

### `references` (array)

Links to external documentation, policies, and handbooks. Analogous to OpenAPI's `externalDocs`.

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `name` | string | **Yes** | Reference title |
| `url` | string | **Yes** | Link |

---

### `components` (object)

Reusable definitions, referenced via `$ref`. Analogous to OpenAPI's `components`.

| Field | Type | Description |
|-------|------|-------------|
| `artifacts` | object | Document/deliverable type definitions |
| `authority-levels` | object | Decision authority definitions |
| `unit-types` | object | Custom unit type definitions with inheritance (v0.2) |

Components have no effect until referenced. Use JSON Pointer syntax:

```yaml
# Reference within same file
output:
  $ref: "#/components/artifacts/product-roadmap"

# Reference to another file
from:
  $ref: "units/sales/opi.yaml#/unit"
```

#### `components.unit-types` — Type Inheritance (v0.2)

Custom unit type definitions that units can inherit from via `unit.derived_from`. Inspired by [TOSCA](https://docs.oasis-open.org/tosca/TOSCA/v2.0/TOSCA-v2.0.html) type inheritance.

Each unit type defines:

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | What this unit type represents |
| `base_type` | string | Built-in OPI type this extends (e.g. `committee`, `stream-aligned`) |
| `derived_from` | string | Parent custom type (for type hierarchies) |
| `required_members` | string[] | Roles that MUST be present in any unit of this type |
| `required_fields` | string[] | Top-level fields that MUST be present (e.g. `schedule`, `governance`) |
| `defaults` | object | Default values applied when not explicitly set |
| `template` | object | Partial OPI document merged into instances |

**Inheritance rule:** Fields from the type definition are merged into the unit instance. Explicit values in the unit always override inherited defaults. `required_members` and `required_fields` are additive (child types add requirements, never remove them).

**Usage:** A unit references a custom type via `unit.derived_from`:

```yaml
unit:
  name: "Payments Squad"
  derived_from: spotify-squad     # inherits from components.unit-types.spotify-squad
  purpose: "Handle all payment processing"
```

The tooling resolves `derived_from`, merges defaults, and validates required fields/members.

#### Examples

**Artifact components:**

```yaml
components:
  artifacts:
    product-roadmap:
      type: plan
      format: markdown
      description: "Quarterly product roadmap with priorities and timelines"

    decision-record:
      type: document
      format: yaml
      description: "Structured record of a governance decision"
      schema:
        required: [date, type, decision, rationale]
        properties:
          date: { type: string }
          type: { type: string }
          decision: { type: string }
          rationale: { type: string }
          alternatives: { type: array, items: { type: string } }
```

**Unit type components (v0.2):**

```yaml
components:
  unit-types:
    # --- Spotify Model types ---
    spotify-squad:
      description: "Cross-functional team aligned to a mission (Spotify Model)"
      base_type: stream-aligned
      required_members: [product-owner, scrum-master]
      required_fields: [schedule, interfaces]
      defaults:
        schedule:
          cadence: biweekly
        governance:
          framework: consent

    spotify-tribe:
      description: "Collection of squads with shared domain (Spotify Model)"
      base_type: leadership
      required_members: [tribe-lead]
      defaults:
        schedule:
          cadence: monthly

    spotify-chapter:
      description: "Functional group across squads for skill development (Spotify Model)"
      base_type: enabling
      required_members: [chapter-lead]
      defaults:
        schedule:
          cadence: biweekly

    # --- Holacracy types ---
    holacracy-circle:
      description: "Self-governing circle with defined roles and accountabilities (Holacracy)"
      base_type: circle
      required_members: [lead-link, rep-link, facilitator, secretary]
      required_fields: [governance, schedule]
      defaults:
        governance:
          framework: consent
        schedule:
          cadence: weekly
      template:
        channels:
          sync:
            - type: meeting
              name: "Governance Meeting"
              cadence: monthly
            - type: meeting
              name: "Tactical Meeting"
              cadence: weekly

    # --- Consulting firm types ---
    consulting-practice:
      description: "Skill-based unit that staffs into client projects"
      base_type: stream-aligned
      required_members: [practice-lead]
      required_fields: [capabilities, interfaces]

    consulting-steering:
      description: "Strategic committee for a consulting organization"
      base_type: committee
      required_members: [chair, managing-directors]
      required_fields: [governance, schedule, interfaces]
      defaults:
        governance:
          framework: DACI
        schedule:
          cadence: biweekly
          duration: 90min
```

---

### Extensions (`x-` prefix)

Any object in an OPI document MAY include fields prefixed with `x-` for organization-specific extensions. Tools MUST ignore unknown `x-` fields.

```yaml
unit:
  name: "Product Team"
  x-cost-center: "CC-4200"
  x-office-location: "Building A, Floor 3"
```

---

## File Organization

### Recommended: One file per unit

```
org/
├── org.yaml                       # Organization-level metadata
├── units/
│   ├── board/opi.yaml
│   ├── product-team/opi.yaml
│   ├── engineering/opi.yaml
│   └── sales/opi.yaml
├── meetings/                      # Meeting-type units (v0.2)
│   ├── steering-committee.yaml
│   ├── delivery-lead-sync.yaml
│   ├── all-hands.yaml
│   └── quarterly-review.yaml
├── flows/                         # Cross-unit flows (v0.2)
│   ├── budget-approval.yaml
│   ├── monthly-reporting.yaml
│   └── cross-unit-blocker.yaml
├── governance/
│   └── policies/
│       └── spending-authority.yaml
├── components/
│   ├── artifacts.yaml
│   └── authority-levels.yaml
└── README.md
```

> **v0.2 note:** Three content directories map to three views:
> - `units/` → **Org Chart** (who exists, what they own)
> - `meetings/` → **Calendar / Timetable** (when things happen, who attends)
> - `flows/` → **Decision Flow Dashboard** (how decisions/information move through the org)

### Org-Model Templates (v0.2)

Pre-built templates for known organizational frameworks. Each template provides `components.unit-types` definitions plus example structures that can be scaffolded via tooling.

```
org/
├── ...
└── templates/                     # Pre-built org model templates (v0.2)
    ├── spotify-model/
    │   ├── types.yaml             # unit-types: squad, tribe, chapter, guild
    │   ├── example-tribe.yaml     # Full tribe with squads
    │   └── README.md
    ├── holacracy/
    │   ├── types.yaml             # unit-types: circle, role, governance-meeting
    │   ├── example-circle.yaml
    │   └── README.md
    ├── consulting-firm/
    │   ├── types.yaml             # unit-types: practice, steering, staffing
    │   ├── example-org.yaml
    │   └── README.md
    └── traditional/
        ├── types.yaml             # unit-types: department, division, board
        ├── example-org.yaml
        └── README.md
```

**How templates work:**

1. **Choose a template:** `opi init --template spotify-model`
2. **Scaffold:** Tooling creates `components/unit-types.yaml` from the template's `types.yaml`
3. **Customize:** Modify scaffolded units with your actual team names, members, schedules
4. **Validate:** Schema validation ensures inherited required fields are present

Templates are a **starting point**, not a constraint. Organizations typically mix patterns (e.g. Spotify squads for delivery + traditional departments for support). The type system supports this via `derived_from` chains.

### Alternative: Single file

For small organizations or getting started, a single file is valid:

```yaml
opi: "0.1.0"
unit:
  name: "My Team"
  purpose: "We do things"
# ... all sections in one file
```

---

## Validation Rules (v0.1)

### Structural Rules

1. `opi` field MUST be present and set to `"0.1.0"`
2. `unit.name` MUST be present and non-empty
3. All `$ref` pointers MUST resolve to existing definitions
4. `governance.decisions[].type` MUST be unique within a unit
5. `interfaces.inputs[].from` and `interfaces.outputs[].to` SHOULD reference existing unit ids
6. `dependencies[].health` values MUST be one of: `ok`, `at-risk`, `blocked`
7. `members[].role` SHOULD follow a consistent vocabulary within the organization

### Schedule Validation (v0.2)

8. Meeting-type units (`committee`, `meeting`, `working-group`, `circle`) SHOULD have a `schedule` block
9. If `schedule.recurrence` is present, `schedule.recurrence.type` MUST be `rrule`
10. If `schedule.time` is present, it MUST be in 24h format (`HH:MM`)
11. `members[].daci` values MUST be one of: `driver`, `approver`, `contributor`, `informed`
12. If `unit.type` is `committee`, then `unit.mandate` SHOULD be present (committees need defined authority)
13. If `members[].daci` is used, `governance.framework` SHOULD be `DACI` (or explicitly mapped via `x-` extensions)

### Capability-Requirement Matching (cross-unit validation)

When validating a multi-unit OPI repository, tooling SHOULD verify interface consistency across units. Inspired by [TOSCA](https://docs.oasis-open.org/tosca/TOSCA/v2.0/TOSCA-v2.0.html) capability-requirement matching:

14. **Requirement satisfaction:** Every `interfaces.inputs[]` entry SHOULD have a corresponding `interfaces.outputs[]` entry in the referenced source unit with a matching `artifact` name
15. **Orphaned outputs:** An `interfaces.outputs[]` entry with no matching `interfaces.inputs[]` in the target unit is a WARNING (potential waste)
16. **Cadence mismatch:** If unit A expects input `weekly` but unit B delivers `monthly`, this is a WARNING (SLA mismatch)
17. **Circular dependencies:** A dependency cycle (A→B→C→A) is a WARNING, not an error (organizations have legitimate circular flows)
18. **Schedule overlap:** If two meeting-type units share members and have overlapping `schedule` entries, this is a WARNING (calendar conflict)

### Flow Validation (v0.2)

19. `flows[].path[]` stations SHOULD reference existing unit or meeting ids
20. `flows[].path[]` MUST contain at least 2 stations (a flow with 1 station is not a flow)
21. `flows[].communication[].to` SHOULD reference existing unit ids
22. If `flows[].path[].governance` is present, it SHOULD be consistent with the referenced unit's `governance.framework`
23. **Dangling flow:** A flow where intermediate stations don't exist is an ERROR
24. **SLA chain consistency:** If station B depends on station A's output, and A's SLA is longer than B's expected input cadence, this is a WARNING
25. **Flow completeness:** Every `governance.decisions[].escalation` reference SHOULD have a corresponding flow that models the escalation path

### Swimlane Validation (v0.2)

26. `capabilities.*.process.lanes[].unit` SHOULD reference existing unit or meeting ids
27. If `capabilities.*.process.lanes[]` is present, `steps` (simple list) SHOULD NOT be used in the same process (use one or the other)
28. `capabilities.*.process.lanes[].steps[].gate` conditions SHOULD be verifiable (references existing artifacts or states)

### Schema Validation (v0.2)

29. An OPI document SHOULD validate against the OPI JSON Schema (`opi-v0.2.schema.json`) when available
30. Tooling SHOULD ignore unknown `x-` prefixed fields during schema validation

### Type Inheritance Validation (v0.2)

31. `unit.derived_from` MUST reference an existing key in `components.unit-types` (within the same document or a referenced template)
32. If a unit type defines `required_members`, every unit with `derived_from` that type MUST include those roles in its `members[]`
33. If a unit type defines `required_fields`, the unit MUST include those top-level sections (e.g. `schedule`, `governance`, `interfaces`)
34. `components.unit-types[].base_type` MUST be a valid built-in OPI unit type (`stream-aligned`, `platform`, `enabling`, `leadership`, `support`, `committee`, `meeting`, `working-group`, `circle`)
35. Type inheritance chains (`derived_from` → parent `derived_from`) MUST NOT form cycles
36. If `governance.change_process` is present, `change_process.review[].role` SHOULD reference roles present in the unit's `members[]` or a recognizable organizational role

Example validation output:

```
PASS  product-team requires customer-feedback from sales → sales outputs customer-feedback to product-team
WARN  product-team outputs sprint-demos to stakeholders → no unit "stakeholders" has matching input
WARN  SLA mismatch: product-team expects customer-feedback weekly, sales delivers monthly
INFO  Circular flow detected: product-team → sales → product-team (review if intentional)
```

---

## Conformance Levels

| Level | Requirements | Use Case |
|-------|-------------|----------|
| **Minimal** | `opi` + `unit` (name only) | Quick start, experimentation |
| **Basic** | + `members` + `interfaces` | Team documentation |
| **Standard** | + `governance` + `channels` + `schedule` | Full organizational modeling, calendar-ready |
| **Complete** | + `events` + `dependencies` + `flows` + `components` + `status` | Enterprise-grade, decision flow modeling, tooling-ready |

### Spec/Status Pattern (Complete level)

Inspired by [Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/), Complete-level OPI documents MAY include a `status` section that captures the **actual state** alongside the **desired state** (`spec`). The delta between both is the organizational debt.

```yaml
opi: "0.1.0"

unit:
  name: "Product Team"
  # ... desired structure

# Everything above defines the DESIRED state (spec).
# The status section below reflects ACTUAL state.

status:
  observed_version: "2026-Q1"       # Last version reviewed by leadership
  conditions:
    - type: Staffed
      status: "False"
      reason: "2 of 12 positions unfilled (Senior Dev, UX Designer)"
      since: 2026-01-15

    - type: InterfacesHealthy
      status: "False"
      reason: "Customer feedback not received for 6 weeks (SLA: monthly)"
      since: 2026-02-01

    - type: GovernanceCompliant
      status: "True"
      since: 2025-12-01

    - type: MandateClear
      status: "True"
      since: 2026-01-10
```

**Standard condition types:** `Staffed`, `MandateClear`, `InterfacesHealthy`, `GovernanceCompliant`, `BudgetWithin`, `DependenciesOk`

**Reconciliation:** Organizations review status periodically (weekly standups, monthly reviews, quarterly planning). Each review is a reconciliation loop — compare actual state to desired state, take action to close the gap. The `status.conditions` array makes this queryable across all units.

---

## JSON Schema (v0.2)

A machine-readable JSON Schema is available at `opi-v0.2.schema.json`. It validates OPI documents against the structure defined in this spec.

**Usage with IDE (VS Code + YAML extension):**

```yaml
# yaml-language-server: $schema=./opi-v0.2.schema.json
opi: "0.2.0"
unit:
  name: "My Team"
  # IDE now provides autocomplete, validation, hover docs
```

**Usage with CI validation:**

```bash
# Using ajv-cli
npx ajv validate -s opi-v0.2.schema.json -d "units/**/*.yaml"

# Using Python jsonschema
python3 -c "
import json, yaml
from jsonschema import validate
schema = json.load(open('opi-v0.2.schema.json'))
doc = yaml.safe_load(open('meetings/steering-committee.yaml'))
validate(doc, schema)
print('Valid OPI document')
"
```

**Coverage:** The schema validates all top-level sections (`unit`, `members`, `capabilities`, `interfaces`, `events`, `governance`, `schedule`, `channels`, `dependencies`, `flows`, `references`, `components`, `status`) plus standalone flow documents (`flow`). Extension fields (`x-*`) are permitted and ignored during validation.

---

## Changelog

### v0.2.0 (2026-02-19)

**Theme: Meeting-type units, decision flows & calendar-ready data**

**v0.2a — Meeting-type units & schedule:**
- **Meeting-type units:** New unit types `committee`, `meeting`, `working-group`, `circle` — meetings and committees are now first-class OPI entities with their own members, governance, interfaces, and schedule
- **`schedule` block:** New top-level section with `cadence`, `day`, `time`, `duration`, `location`, `timezone`, `recurrence` (iCalendar RRULE), `exceptions` — enables calendar views and ICS export
- **`members[].daci`:** Explicit governance role mapping per member (driver/approver/contributor/informed), separate from organizational `role`
- **`members[].attendance`:** Member attendance type (permanent/optional/on-demand)
- **`channels.sync[].$ref`:** Reference meeting-type units from regular units
- **File organization:** `meetings/` directory for meeting-type units alongside `units/`
- **Validation rules 8-13:** Schedule validation, DACI consistency, committee mandate requirement
- **Validation rule 18:** Cross-unit schedule overlap warning

**v0.2c — JSON Schema & Process Swimlanes:**
- **JSON Schema:** `opi-v0.2.schema.json` — validates all 15 OPI properties, enables IDE autocomplete and CI validation
- **Process swimlanes:** `capabilities.*.process.lanes[]` for multi-unit processes — each lane defines which unit handles which steps
- **Swimlane steps:** Can be simple strings or detailed objects with `name`, `action`, `duration`, `gate` (decision gateway)
- **`handoff` field:** Explicit artifact handoff between lanes
- **ASCII swimlane rendering:** Spec includes example of how lanes render as a diagram
- **Guidance:** Flows vs. Swimlanes — when to use which (single item traveling vs. recurring process divided across units)
- **Validation rules 26-30:** Lane unit references, steps/lanes exclusivity, gate verifiability, schema validation

**v0.2d — Type Inheritance, Change Management & Org-Model Templates:**
- **`unit.derived_from`:** Units can inherit from custom type definitions in `components.unit-types` — inspired by TOSCA type inheritance
- **`components.unit-types` expansion:** Full type definition schema with `base_type`, `derived_from` (type hierarchies), `required_members`, `required_fields`, `defaults`, `template`
- **Inheritance rule:** Explicit values override defaults; `required_members` and `required_fields` are additive across type chains
- **`governance.change_process`:** Structural change governance — how changes to the org structure itself are proposed, reviewed, and approved (Holacracy governance + Git PR workflow)
- **Org-Model Templates:** Pre-built `templates/` directory with unit type definitions for known organizational models (Spotify Model, Consulting Firm, Holacracy, Traditional)
- **Template files:** `template-spotify-model.yaml` (squad/tribe/chapter/guild), `template-consulting-firm.yaml` (7 unit types + 2 standard flows)
- **Validation rules 31-36:** Type inheritance validation, required members/fields, change process consistency

**v0.2b — Decision Flow Graph:**
- **`flows` section:** New top-level field for modeling cross-unit decision and information flows
- **Flow types:** `decision`, `information`, `escalation`, `change-request`
- **Station model:** Ordered path of units/meetings with `action`, `condition`, `input/output`, `governance`, `sla`
- **Standard actions:** `identify`, `propose`, `review`, `approve`, `ratify`, `reject`, `escalate`, `inform`, `execute`, `report`
- **Communication rules:** Outcome-triggered notifications to target units
- **Fallback behavior:** Timeout-based escalation, auto-approve, rejection, or notification
- **Standalone flow documents:** `flows/` directory for flows spanning 3+ units
- **File organization:** Three directories = three views (units → org chart, meetings → calendar, flows → decision dashboard)
- **Validation rules 19-25:** Station reference validation, minimum path length, SLA chain consistency, flow completeness check

### v0.1.0 (2026-02-19)

- Initial draft
- Core sections: unit, members, capabilities, interfaces, events, governance, channels, dependencies, references, components
- Extension mechanism (`x-` prefix)
- File organization patterns
- Validation rules including capability-requirement matching (cross-unit)
- Conformance levels (Minimal → Basic → Standard → Complete)
- Multiple governance frameworks: DACI, RAPID, OVIS, consent, consensus, autocratic
- Spec/Status pattern for desired vs. actual state (Complete conformance level)
- Prior art analysis: OpenAPI, AsyncAPI, TeamAPI-As-Code, Backstage, GlassFrog/Holacracy, TOSCA, Kubernetes CRDs, "Company as Code"

---

## License

This specification is licensed under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0).

---

*OPI is developed by [Andreas Siemes](https://andreassiemes.de). Contributions welcome at [github.com/andreassiemes/org-as-code](https://github.com/andreassiemes/org-as-code).*
