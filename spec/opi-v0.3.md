# OPI Specification v0.3

**Organizational Programming Interface — A machine-readable format for organizational design.**

---

## Abstract

The OPI Specification defines a standard, language-agnostic format for describing organizational units and their interfaces. An OPI document describes: what a unit is responsible for, how it makes decisions, what it produces and consumes, and how it connects to other units.

OPI is to organizational design what OpenAPI is to software APIs — a contract that makes the invisible visible.

## Status

Draft — v0.3 (February 2026)

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

### Unit Document

An OPI unit document is a YAML file with the following top-level structure:

```yaml
opi: "0.3.0"          # REQUIRED — Spec version

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
status: {}             # Actual state (Complete conformance level)
```

All top-level fields except `opi` and `unit` are OPTIONAL.

### Org Document (`org.yaml`) — v0.3

A new optional organization-level document that defines org-wide metadata and defaults. This is NOT an OPI unit — it is a configuration document that tooling uses to understand the organizational context.

```yaml
opi: "0.3.0"          # REQUIRED — Spec version

org:                   # REQUIRED in org.yaml
  name: "Acme Corp"   # REQUIRED — Organization name
  id: acme-corp        # OPTIONAL — Machine-readable slug
  version: "2026-Q1"  # OPTIONAL — Structural version (updates with org redesigns)
  website: https://acme.com   # OPTIONAL
  description: "Technology consulting firm"    # OPTIONAL

defaults:              # OPTIONAL — Org-wide defaults applied to all units
  timezone: Europe/Berlin
  locale: de-DE
  governance:
    framework: DACI    # Default framework when unit doesn't specify one
  schedule:
    timezone: Europe/Berlin   # Default timezone for schedules

schema:                # OPTIONAL — Declares spec versions in use
  opi_version: "0.3.0"
  bp_version: "1.0"   # If Business Primitives is used (see BP Integration)
```

#### `org.defaults` — Inheritance

Values in `org.defaults` are applied to all unit documents in the organization when the corresponding field is absent. Explicit values in unit documents always override org-level defaults. This enables consistent governance configuration without repeating it in every file.

```yaml
# If org.yaml has:
defaults:
  governance:
    framework: DACI

# Then a unit without governance.framework inherits:
governance:
  framework: DACI
```

---

## Schema Reference

### `opi` (string, REQUIRED)

The OPI Specification version this document conforms to. Semantic versioning.

```yaml
opi: "0.3.0"
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
| `start_date` | date | No | When this person/role began in this unit (YYYY-MM-DD). **v0.3** |
| `end_date` | date | No | When this person/role leaves this unit (YYYY-MM-DD). If absent, current. **v0.3** |

The `daci` field (v0.2) maps a member's **governance role** within this specific unit, separate from their organizational `role`. A person can be `lead` (organizational role) and `approver` (DACI role) in the same unit.

The `start_date` / `end_date` fields (v0.3) enable **temporal role tracking**: organizational history, rotation planning, and compliance queries ("who was approver for budget decisions in Q1 2025?"). A member without `end_date` is currently active.

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

**Meeting-type unit (committee) with temporal roles:**

```yaml
members:
  - role: chair
    position: "COO"
    daci: approver
    attendance: permanent
    start_date: 2025-01-01

  - role: member
    position: "Head of Delivery"
    daci: driver
    attendance: permanent
    start_date: 2025-01-01

  - role: member
    position: "Head of Sales"
    daci: contributor
    attendance: permanent
    start_date: 2026-01-01    # New member since Q1 2026

  - role: guest
    position: "CFO"
    daci: informed
    attendance: on-demand
    end_date: 2026-06-30      # Rotating off mid-2026
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
| `method` | enum | No | Interaction pattern: `unary` / `stream` / `batch` / `collaborative`. Default: `unary`. **v0.3** |
| `bp_type` | string | No | Business Primitives atom type this artifact corresponds to (e.g. `decision`, `metric`, `action`). **v0.3** |

#### `interfaces.outputs` (array)

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `to` | string | **Yes** | Target unit (id or name) |
| `artifact` | string | **Yes** | What is delivered |
| `format` | string | No | Format |
| `cadence` | string | No | Delivery frequency |
| `method` | enum | No | Interaction pattern: `unary` / `stream` / `batch` / `collaborative`. Default: `unary`. **v0.3** |
| `bp_type` | string | No | Business Primitives atom type this artifact corresponds to. **v0.3** |

#### Interface Method Types — v0.3

The `method` field (inspired by gRPC's four communication patterns) describes how the interface operates over time:

| Method | Meaning | Org Pattern |
|--------|---------|-------------|
| `unary` | Single request-response (default) | Ad-hoc budget request |
| `stream` | Continuous, ongoing feed | Weekly sales dashboard metrics |
| `batch` | Aggregated, periodic delivery | Monthly consolidated report |
| `collaborative` | Bidirectional, ongoing joint process | Co-design workshop series |

**When to use:** Use `unary` for most artifacts (any discrete deliverable). Use `stream` for continuous metric feeds or monitoring outputs. Use `batch` for roll-up reports. Use `collaborative` for workstreams that span multiple back-and-forth interactions.

#### Example

```yaml
interfaces:
  inputs:
    - from: sales
      artifact: customer-feedback
      format: markdown
      cadence: weekly
      required: true
      method: stream            # Continuous feed, not one-off requests
      bp_type: metric           # Each feedback entry follows BP Metric structure

    - from: board
      artifact: strategic-direction
      format: decision-record
      cadence: quarterly
      bp_type: decision         # Follows BP Decision structure

  outputs:
    - to: sales
      artifact: product-roadmap
      format: markdown
      cadence: monthly
      method: unary             # Delivered as a single document per cycle

    - to: board
      artifact: product-metrics
      format: yaml
      cadence: monthly
      method: batch             # Aggregated from sprint-level data
      bp_type: metric
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

#### `governance.change_process` — Structural Change Governance (v0.2)

How changes to the org structure itself (this OPI document) are proposed, reviewed, and approved. Inspired by [Holacracy governance meetings](https://www.holacracy.org/constitution/5-0/) (propose → react → amend → integrate) and Git-based workflows.

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `proposal` | string | No | How changes are proposed (e.g. `"Pull Request on GitHub"`, `"Governance Meeting"`) |
| `review` | array | No | Review steps before approval |
| `approval` | array | No | Approval steps |
| `communication` | array | No | How approved changes are communicated |
| `cadence` | string | No | How often structural reviews happen (e.g. `quarterly`) |

---

### `schedule` (object) — v0.2

When a unit meets — time, cadence, recurrence. Primarily used for meeting-type units (`committee`, `meeting`, `working-group`, `circle`) but also valid for any unit with regular sync meetings.

The `schedule` block provides enough structured data to generate **calendar views** (timetables) and **ICS calendar exports**.

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `cadence` | string | **Yes** | Frequency: `daily` / `weekly` / `biweekly` / `monthly` / `quarterly` / `biannual` / `annual` / `on-demand` |
| `day` | string | No | Scheduled day(s) (e.g. `Monday`, `"Monday,Wednesday"`) |
| `time` | string | No | Start time in 24h format (e.g. `"10:00"`) |
| `duration` | string | No | Expected length as string with unit: `"30min"`, `"90min"`, `"2h"`. **v0.3: always string format** |
| `location` | string | No | Physical or virtual location |
| `timezone` | string | No | IANA timezone (e.g. `Europe/Berlin`). Default: `org.defaults.timezone` or `UTC`. |
| `recurrence` | object | No | Machine-readable recurrence for calendar export |
| `exceptions` | string[] | No | Dates when the meeting does NOT occur (e.g. holidays) |

> **v0.3 Change:** `schedule.duration` MUST be a string with an explicit unit suffix: `"30min"`, `"90min"`, `"2h"`, `"4h"`. Integer values (e.g. `60`) are deprecated and SHOULD be migrated to string format.

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
  duration: "90min"
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
  duration: "4h"
  location: "Headquarters, Board Room"
  timezone: Europe/Berlin
  recurrence:
    type: rrule
    value: "FREQ=MONTHLY;INTERVAL=3;BYDAY=3FR"
  exceptions:
    - "2026-12-27"   # Holiday break
```

---

### `channels` (object)

How people communicate within and with this unit. Analogous to OpenAPI's `servers`.

#### `channels.sync` (array) — Meetings and rituals

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `type` | string | **Yes** | `meeting` / `workshop` / `standup` / `review` |
| `name` | string | **Yes** | Meeting name |
| `cadence` | string | No | Frequency |
| `duration` | string | No | Expected length (string format: `"30min"`, `"2h"`) |
| `day` | string | No | Scheduled day(s) |
| `rituals` | object | No | Pre/during/post protocols |
| `$ref` | string | No | Reference to a meeting-type unit (v0.2) |

#### `channels.async` (array) — Digital channels

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `type` | string | **Yes** | `slack` / `email` / `teams` / `wiki` / `ticket-system` |
| `name` | string | **Yes** | Channel identifier |
| `purpose` | string | No | What this channel is for |

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
| `escalation_flow` | string | No | ID of the flow that handles escalation when health becomes `blocked`. **v0.3** |

The `escalation_flow` field (v0.3) closes the gap between dependency health and escalation flows. When `health` becomes `blocked`, tooling can automatically surface the referenced flow as the resolution path.

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
    health: blocked
    note: "No response in 8 days. SLA is 3 days."
    escalation_flow: cross-unit-blocker    # v0.3: explicit link to resolution flow
```

---

### `flows` (array) — v0.2

Cross-unit decision and information flows. **This is what makes org-as-code actionable** — not just static structure, but visible movement of decisions, escalations, and information through the organization.

A flow describes a **path** that a decision, request, or piece of information takes across multiple units. Each station in the path defines: who receives it, what action they take, under what conditions, and where it goes next.

Flows can be defined inline (in a unit's OPI document) or as **standalone flow documents** in a `flows/` directory. Standalone flow documents are recommended for flows that span 3+ units.

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

#### `components.artifacts` — Artifact Definitions with BP Integration (v0.3)

Artifacts now support a `bp_type` field that links the artifact to a [Business Primitives](https://businessprimitives.com) atom type. This makes the information model of each artifact explicit and machine-readable.

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `type` | string | No | High-level artifact class (e.g. `document`, `plan`, `report`) |
| `format` | string | No | File format (e.g. `yaml`, `markdown`, `spreadsheet`) |
| `description` | string | No | What this artifact contains |
| `bp_type` | string | No | Business Primitives atom type (`decision`, `metric`, `risk`, `action`, `timeline`, `status`, `stakeholder`). **v0.3** |
| `schema` | object | No | Inline schema for required fields |

```yaml
components:
  artifacts:
    decision-record:
      type: document
      format: yaml
      description: "Structured record of a governance decision"
      bp_type: decision        # Links to BP Decision atom (decided_by, title, rationale, ...)

    unit-metrics:
      type: report
      format: yaml
      description: "Monthly unit performance metrics"
      bp_type: metric          # Links to BP Metric atom (name, value, unit, trend, ...)

    budget-request:
      type: document
      format: markdown
      description: "Formal budget request with justification"
      bp_type: action          # Links to BP Action atom (owner, title, due_date, ...)

    risk-register:
      type: document
      format: yaml
      description: "Identified risks with probability, impact, and mitigations"
      bp_type: risk            # Links to BP Risk atom (threat, probability, impact, owner, ...)
```

#### `components.unit-types` — Type Inheritance (v0.2)

Custom unit type definitions that units can inherit from via `unit.derived_from`.

Each unit type defines:

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | What this unit type represents |
| `base_type` | string | Built-in OPI type this extends |
| `derived_from` | string | Parent custom type (for type hierarchies) |
| `required_members` | string[] | Roles that MUST be present in any unit of this type |
| `required_fields` | string[] | Top-level fields that MUST be present |
| `defaults` | object | Default values applied when not explicitly set |
| `template` | object | Partial OPI document merged into instances |

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

## Connection to Business Primitives

> **OPI + BP = Clarity Engineering**

OPI defines **structural clarity**: who exists, what they own, how they interact, how decisions flow. [Business Primitives](https://businessprimitives.com) defines **informational clarity**: what decisions look like, how metrics are structured, what a risk record contains.

Together they address the complete organizational clarity problem:

- **OPI** answers: "How is the org structured? Where do decisions get made? How does information flow?"
- **BP** answers: "What does that decision look like? What fields does that metric have? How is this risk documented?"

### Concept Mapping

| OPI Concept | BP Concept | Relationship |
|-------------|-----------|-------------|
| `interfaces.outputs[].artifact` | BP Atom type (via `bp_type`) | OPI declares the artifact; BP defines its schema |
| `governance.decisions[]` | `primitive: decision` | OPI models who/where; BP models what/when/why |
| `dependencies[].health` | `primitive: status` | OPI tracks org health; BP provides the status format |
| `flows[].path[].output` | BP Atom (via artifact `bp_type`) | Flow outputs can be BP-typed artifacts |
| `status.conditions[]` | `primitive: status` (RAG) | OPI conditions map to BP Status atoms |
| `members[].accountabilities` | `primitive: action` | Accountabilities can be expressed as BP Actions |
| Unit KPIs (via capabilities) | `primitive: metric` | Capability SLAs can reference BP Metrics |

### Cross-Reference Convention

Documents may reference across specs using prefixed IDs:

```yaml
# In an OPI document — reference a BP primitive
refs:
  - id: "bp:dec-budget-q2-2026"
    rel: informs

# In a BP document — reference an OPI unit
refs:
  - id: "opi:steering-committee"
    rel: part-of
```

Prefix convention:
- `opi:` — References an OPI unit, meeting, or flow by `unit.id`
- `bp:` — References a Business Primitives document by its `id` field

### Integration Example

An OPI interface output annotated with `bp_type`, paired with a BP decision document:

```yaml
# In steering-committee/opi.yaml
interfaces:
  outputs:
    - to: all-hands
      artifact: quarterly-budget-decision
      format: yaml
      cadence: quarterly
      bp_type: decision         # This artifact follows BP Decision structure
```

```yaml
# In decisions/dec-budget-q2-2026.yaml
bp: "1.0"
primitive: decision
id: dec-budget-q2-2026
decided_by: "COO"
title: "Approved Q2 2026 delivery budget: 850k EUR"
decided_date: 2026-04-15
status: approved
rationale: "On track vs. Q1; capacity plan requires additional senior hire"
refs:
  - id: "opi:steering-committee"
    rel: part-of
```

---

## File Organization

### Recommended: One file per unit

```
org/
├── org.yaml                       # Organization-level metadata (v0.3)
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
├── templates/                     # Org-model templates (v0.2)
│   ├── spotify-model/
│   ├── holacracy/
│   ├── consulting-firm/
│   └── traditional/
└── README.md
```

> **Three content directories = three views:**
> - `units/` → **Org Chart** (who exists, what they own)
> - `meetings/` → **Calendar / Timetable** (when things happen, who attends)
> - `flows/` → **Decision Flow Dashboard** (how decisions/information move)
>
> `org.yaml` is the fourth view: **Org Context** (name, defaults, declared spec versions).

### Alternative: Single file

For small organizations or getting started, a single file is valid:

```yaml
opi: "0.3.0"
unit:
  name: "My Team"
  purpose: "We do things"
# ... all sections in one file
```

---

## Tooling Specification — v0.3

This section defines the interface contract for OPI-conformant tooling. It describes what a **Validator** and a **Visualizer** must do, so that any implementation can be drop-in compatible.

### Validator

A conformant OPI Validator:

**Input:**
- A single OPI YAML file, OR
- A directory (scans `*.yaml` files recursively)

**Output:**
- Structured list of results, each with:
  - `severity`: `ERROR` / `WARN` / `INFO` / `PASS`
  - `rule`: Rule ID (e.g. `R02`, `R19`)
  - `file`: Source file path
  - `line`: Line number (when available)
  - `message`: Human-readable description

**Minimum implementation (Structural Rules 1-13):**

A validator claiming "OPI conformance" MUST implement Validation Rules 1–13 (structural + schedule). These rules require only single-document analysis.

**Recommended (cross-unit validation):**

A validator that receives a full repository SHOULD implement cross-unit validation rules 14–18 (interface matching, SLA consistency). This requires resolving unit references across files.

**Example output format (human-readable):**

```
PASS  R02  units/product-team/opi.yaml       unit.name present and non-empty
WARN  R15  units/product-team/opi.yaml:42    Orphaned output: artifact 'sprint-demos' has no matching input in 'stakeholders'
WARN  R16  units/product-team/opi.yaml:48    SLA mismatch: expects customer-feedback weekly, sales delivers monthly
ERROR R23  flows/budget-approval.yaml:31     Dangling flow: station 'approvals-committee' does not exist
INFO       flows/cross-unit-blocker.yaml     Circular flow detected: A→B→C→A (review if intentional)
```

**Example output format (machine-readable):**

```json
[
  { "severity": "WARN", "rule": "R15", "file": "units/product-team/opi.yaml", "line": 42,
    "message": "Orphaned output: artifact 'sprint-demos' has no matching input in 'stakeholders'" }
]
```

### Visualizer

A conformant OPI Visualizer SHOULD support at least one of the following views:

**Calendar View** (requires `schedule` blocks):
- Input: All OPI documents with `schedule` fields in a repository
- Output: Week-view or month-view table (HTML, Markdown, or ICS)
- Columns: Days of week
- Rows: Time slots
- Cell content: Unit name, duration, attendee count
- ICS export: One `.ics` file per unit with `schedule.recurrence`

**Flow View** (requires `flows` documents):
- Input: One or more flow YAML files
- Output: Directed graph (Mermaid, Graphviz DOT, or SVG)
- Nodes: `path[].station` entries
- Edges: Directional arrows from station to station
- Edge labels: `action` values
- Conditional edges: `condition` shown as gate diamond

**Org Chart View** (requires `unit.parent` fields):
- Input: All OPI unit documents
- Output: Hierarchical tree (Mermaid, HTML, or SVG)
- Nodes: Unit names
- Edges: `parent` references
- Node annotation: `unit.type` (color-coded)

**Swimlane View** (requires `capabilities.*.process.lanes`):
- Input: A single OPI document with swimlane capabilities
- Output: Horizontal swimlane diagram
- Rows: One per `lanes[].unit`
- Cells: Step names in sequence

---

## Validation Rules

### Structural Rules (v0.1)

1. `opi` field MUST be present and set to a valid version string (e.g. `"0.3.0"`)
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
12. If `unit.type` is `committee`, then `unit.mandate` SHOULD be present
13. If `members[].daci` is used, `governance.framework` SHOULD be `DACI` (or mapped via `x-` extensions)

### Capability-Requirement Matching (cross-unit)

14. **Requirement satisfaction:** Every `interfaces.inputs[]` entry SHOULD have a corresponding `interfaces.outputs[]` entry in the referenced source unit
15. **Orphaned outputs:** An `interfaces.outputs[]` with no matching `interfaces.inputs[]` in the target is a WARNING
16. **Cadence mismatch:** Input expects `weekly` but source delivers `monthly` → WARNING
17. **Circular dependencies:** A→B→C→A is a WARNING (organizations have legitimate circular flows)
18. **Schedule overlap:** Two meeting-type units sharing members with overlapping schedules → WARNING

### Flow Validation (v0.2)

19. `flows[].path[]` stations SHOULD reference existing unit or meeting ids
20. `flows[].path[]` MUST contain at least 2 stations
21. `flows[].communication[].to` SHOULD reference existing unit ids
22. If `flows[].path[].governance` is present, it SHOULD be consistent with the referenced unit's governance framework
23. **Dangling flow:** A flow where intermediate stations don't exist is an ERROR
24. **SLA chain consistency:** If station B depends on A's output and A's SLA is longer than B's expected input cadence → WARNING
25. **Flow completeness:** Every `governance.decisions[].escalation` reference SHOULD have a corresponding flow

### Swimlane Validation (v0.2)

26. `capabilities.*.process.lanes[].unit` SHOULD reference existing unit or meeting ids
27. If `capabilities.*.process.lanes[]` is present, `steps` (simple list) SHOULD NOT be used in the same process
28. `capabilities.*.process.lanes[].steps[].gate` conditions SHOULD be verifiable

### Schema Validation (v0.2)

29. An OPI document SHOULD validate against the OPI JSON Schema when available
30. Tooling SHOULD ignore unknown `x-` prefixed fields during schema validation

### Type Inheritance Validation (v0.2)

31. `unit.derived_from` MUST reference an existing key in `components.unit-types`
32. If a unit type defines `required_members`, every derived unit MUST include those roles
33. If a unit type defines `required_fields`, the unit MUST include those top-level sections
34. `components.unit-types[].base_type` MUST be a valid built-in OPI unit type
35. Type inheritance chains MUST NOT form cycles
36. If `governance.change_process` is present, `change_process.review[].role` SHOULD reference roles in `members[]`

### Interface Method Validation (v0.3)

37. `interfaces.inputs[].method` and `interfaces.outputs[].method` values MUST be one of: `unary`, `stream`, `batch`, `collaborative`
38. If `interfaces.inputs[].method` is `stream`, `cadence` SHOULD be `weekly` or shorter (streams have high frequency)
39. If `interfaces.inputs[].method` is `batch`, `cadence` SHOULD be `monthly` or longer (batches aggregate over time)

### Temporal Role Validation (v0.3)

40. `members[].start_date` and `members[].end_date` MUST use YYYY-MM-DD format
41. If both `start_date` and `end_date` are present, `end_date` MUST be after `start_date`
42. A member with `end_date` in the past SHOULD be considered historical (tooling MAY filter from current views)

### Duration Format Validation (v0.3)

43. `schedule.duration` and `channels.sync[].duration` MUST be a string with format `"<N>min"` or `"<N>h"` (e.g. `"30min"`, `"90min"`, `"2h"`)
44. Integer duration values (e.g. `duration: 60`) are deprecated and MUST produce a WARNING

### BP Integration Validation (v0.3)

45. `interfaces.inputs[].bp_type` and `interfaces.outputs[].bp_type` values, if present, MUST be one of the defined BP atom types: `decision`, `metric`, `risk`, `action`, `timeline`, `status`, `stakeholder`
46. `components.artifacts[*].bp_type`, if present, MUST be a valid BP atom type
47. Cross-spec `refs` entries using `opi:` or `bp:` prefix SHOULD reference existing documents (WARNING if unresolvable)

---

## Conformance Levels

| Level | Requirements | Use Case |
|-------|-------------|----------|
| **Minimal** | `opi` + `unit` (name only) | Quick start, experimentation |
| **Basic** | + `members` + `interfaces` | Team documentation |
| **Standard** | + `governance` + `channels` + `schedule` | Full organizational modeling, calendar-ready |
| **Complete** | + `events` + `dependencies` + `flows` + `components` + `status` | Enterprise-grade, decision flow modeling, tooling-ready |

### Spec/Status Pattern (Complete level)

Inspired by [Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/), Complete-level OPI documents MAY include a `status` section that captures the **actual state** alongside the **desired state** (spec).

```yaml
opi: "0.3.0"

unit:
  name: "Product Team"

# Everything above = DESIRED state.
# status below = ACTUAL state.

status:
  observed_version: "2026-Q1"
  conditions:
    - type: Staffed
      status: "False"
      reason: "2 of 12 positions unfilled"
      since: 2026-01-15

    - type: InterfacesHealthy
      status: "False"
      reason: "Customer feedback not received for 6 weeks (SLA: monthly)"
      since: 2026-02-01

    - type: GovernanceCompliant
      status: "True"
      since: 2025-12-01
```

**Standard condition types:** `Staffed`, `MandateClear`, `InterfacesHealthy`, `GovernanceCompliant`, `BudgetWithin`, `DependenciesOk`

---

## Org-Model Templates

Pre-built templates for known organizational frameworks. Each template provides `components.unit-types` definitions plus example structures.

```
templates/
├── spotify-model/
│   ├── types.yaml             # squad, tribe, chapter, guild
│   ├── example-tribe.yaml
│   └── README.md
├── holacracy/
│   ├── types.yaml             # circle, role, governance-meeting
│   ├── example-circle.yaml
│   └── README.md
├── consulting-firm/
│   ├── types.yaml             # practice, steering, staffing
│   ├── example-org.yaml
│   └── README.md
└── traditional/               # v0.3: now available
    ├── types.yaml             # department, division, board, supervisory-board
    ├── example-org.yaml
    └── README.md
```

### Traditional Org Template (v0.3)

The `traditional/` template defines unit types for hierarchical organizations:

```yaml
components:
  unit-types:
    traditional-department:
      description: "Functional department (e.g. Finance, HR, Marketing)"
      base_type: support
      required_members: [department-head]
      required_fields: [governance, interfaces]
      defaults:
        governance:
          framework: autocratic
        schedule:
          cadence: monthly

    traditional-division:
      description: "Business division grouping multiple departments"
      base_type: leadership
      required_members: [division-head]
      defaults:
        governance:
          framework: DACI
        schedule:
          cadence: monthly

    traditional-management-board:
      description: "Executive management board (Geschäftsführung / Vorstand)"
      base_type: committee
      required_members: [ceo, cfo]
      required_fields: [governance, schedule, interfaces]
      defaults:
        governance:
          framework: consensus
        schedule:
          cadence: weekly

    traditional-supervisory-board:
      description: "Supervisory board (Aufsichtsrat) — oversight, not management"
      base_type: committee
      required_members: [chair]
      required_fields: [governance, schedule]
      defaults:
        governance:
          framework: consensus
        schedule:
          cadence: quarterly
```

---

## Migration Guide

### v0.1 → v0.2

**Meetings:** If you have sync meetings in `channels.sync[]`, consider migrating them to standalone unit documents of type `committee` or `meeting`. Add a `schedule` block with `cadence`, `day`, `time`, and `duration`.

**Decision flows:** If `governance.decisions[].escalation` references other units, consider modeling those as `flows[]` documents for richer path modeling.

**DACI roles:** If members have implicit governance roles, add explicit `members[].daci` fields.

### v0.2 → v0.3

**Duration format (required):** Change integer `duration` values to string format:

```yaml
# Before (v0.2 — deprecated)
schedule:
  duration: 90

# After (v0.3 — required)
schedule:
  duration: "90min"
```

**New optional fields (additive, no action required):**
- `members[].start_date` / `end_date` — add for temporal tracking
- `interfaces.inputs/outputs[].method` — add for interaction pattern clarity
- `interfaces.inputs/outputs[].bp_type` — add if using Business Primitives
- `components.artifacts[*].bp_type` — add to link artifacts to BP types
- `dependencies[].escalation_flow` — add to link blocked dependencies to resolution flows
- `org.yaml` — create as organization-level context document

---

## JSON Schema

A machine-readable JSON Schema for v0.3 will be published as `opi-v0.3.schema.json`. It validates all top-level sections plus the new v0.3 fields.

**Usage with IDE (VS Code + YAML extension):**

```yaml
# yaml-language-server: $schema=./opi-v0.3.schema.json
opi: "0.3.0"
unit:
  name: "My Team"
```

**Usage with CI validation:**

```bash
# Using ajv-cli
npx ajv validate -s opi-v0.3.schema.json -d "units/**/*.yaml"

# Using Python jsonschema
python3 -c "
import json, yaml
from jsonschema import validate
schema = json.load(open('opi-v0.3.schema.json'))
doc = yaml.safe_load(open('meetings/steering-committee.yaml'))
validate(doc, schema)
print('Valid OPI document')
"
```

---

## Changelog

### v0.3.0 (2026-02-22)

**Theme: Integration, temporal modeling, and tooling contracts**

**v0.3 — OPI-BP Integration:**
- **`org.yaml` spec:** New optional organization-level document with `org` (metadata), `defaults` (org-wide fallbacks), and `schema` (declared spec versions). Enables consistent timezone, locale, and governance defaults across all unit documents.
- **`bp_type` field:** New optional field on `interfaces.inputs[]`, `interfaces.outputs[]`, and `components.artifacts[]`. Links OPI artifacts to [Business Primitives](https://businessprimitives.com) atom types (`decision`, `metric`, `risk`, `action`, `timeline`, `status`, `stakeholder`). Makes information schemas explicit without requiring BP adoption.
- **OPI-BP section:** New spec section "Connection to Business Primitives" — concept mapping table, cross-reference convention (`opi:` / `bp:` prefixes), and integration example.
- **`opi:` / `bp:` cross-reference prefix:** Formalized in OPI spec (previously only in BP spec). Enables bidirectional references between OPI units and BP primitives.
- **Validation rules 45–47:** BP type validation, cross-spec reference resolution.

**v0.3 — Interface Method Types (R8, deferred from v0.2):**
- **`method` field on `interfaces.inputs[]` and `interfaces.outputs[]`:** Enum: `unary` (default, ad-hoc), `stream` (continuous), `batch` (aggregated periodic), `collaborative` (bidirectional joint process). Inspired by gRPC communication patterns adapted to org context.
- **Guidance:** When to use each method type, with org-world examples.
- **Validation rules 37–39:** Method enum validation, stream/batch cadence consistency.

**v0.3 — Temporal Roles (R9, deferred from v0.2):**
- **`members[].start_date` / `end_date`:** New optional date fields (YYYY-MM-DD). Enable organizational history, rotation planning, and compliance queries. Members without `end_date` are currently active.
- **Validation rules 40–42:** Date format, end-after-start, historical member filtering.

**v0.3 — Tooling Specification:**
- **Tooling Specification section:** New spec section defining the interface contract for OPI-conformant Validators and Visualizers. Covers: input formats, output formats, minimum required rules, and four visualization types (Calendar, Flow, Org Chart, Swimlane).
- **Validator output format:** Structured (severity + rule + file + line + message) in both human-readable and machine-readable (JSON) form.

**v0.3 — Structural improvements:**
- **`dependencies[].escalation_flow`:** New optional field linking a blocking dependency to the flow that resolves it. Closes the gap between `health: blocked` and escalation path.
- **Traditional org template:** New `templates/traditional/` with four unit types: `traditional-department`, `traditional-division`, `traditional-management-board`, `traditional-supervisory-board`. Completes the template library promised in v0.2d.
- **Duration format standardization:** `schedule.duration` and `channels.sync[].duration` MUST be string format (`"30min"`, `"2h"`). Integer values deprecated with WARNING. Validation rule 43–44.
- **Migration guide:** New section with step-by-step upgrade paths: v0.1→v0.2 and v0.2→v0.3.
- **Inconsistency fixes:** Version strings in all examples updated to `"0.3.0"`. README unit types aligned with spec. `flows[].path[]` field consistently named `station`.

### v0.2.0 (2026-02-19)

**Theme: Meeting-type units, decision flows & calendar-ready data**

**v0.2a — Meeting-type units & schedule:**
- Meeting-type units: `committee`, `meeting`, `working-group`, `circle` as first-class OPI entities
- `schedule` block with cadence, day, time, duration, location, timezone, RRULE, exceptions
- `members[].daci` and `members[].attendance` fields
- Validation rules 8–13 and 18

**v0.2b — Decision Flow Graph:**
- `flows` section: cross-unit decision and information flows
- Flow types: `decision`, `information`, `escalation`, `change-request`
- Station model with action vocabulary, conditions, governance, SLAs
- Standalone flow documents in `flows/` directory
- Validation rules 19–25

**v0.2c — JSON Schema & Process Swimlanes:**
- `opi-v0.2.schema.json`
- Process swimlanes: `capabilities.*.process.lanes[]`
- Validation rules 26–30

**v0.2d — Type Inheritance, Change Management & Templates:**
- `unit.derived_from` and `components.unit-types` with full type definition schema
- `governance.change_process`
- Org-Model Templates: Spotify Model, Consulting Firm (YAML files)
- Validation rules 31–36

### v0.1.0 (2026-02-19)

- Initial draft
- Core sections: unit, members, capabilities, interfaces, events, governance, channels, dependencies, references, components
- Extension mechanism (`x-` prefix), file organization patterns
- Validation rules including capability-requirement matching
- Conformance levels (Minimal → Basic → Standard → Complete)
- Multiple governance frameworks: DACI, RAPID, OVIS, consent, consensus, autocratic
- Spec/Status pattern for desired vs. actual state
- Prior art analysis

---

## License

This specification is licensed under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0).

---

*OPI is developed by [Andreas Siemes](https://andreassiemes.de). Contributions welcome at [github.com/andreassiemes/org-as-code](https://github.com/andreassiemes/org-as-code).*
