# OPI Specification v0.1

**Organizational Programming Interface — A machine-readable format for organizational design.**

---

## Abstract

The OPI Specification defines a standard, language-agnostic format for describing organizational units and their interfaces. An OPI document describes: what a unit is responsible for, how it makes decisions, what it produces and consumes, and how it connects to other units.

OPI is to organizational design what OpenAPI is to software APIs — a contract that makes the invisible visible.

## Status

Draft — v0.1 (February 2026)

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
opi: "0.1.0"          # REQUIRED — Spec version

unit: {}               # REQUIRED — Identity & metadata
members: []            # Roles & accountabilities
capabilities: {}       # What this unit provides
interfaces: {}         # Inputs & outputs
events: {}             # Async notifications (pub/sub)
governance: {}         # Decision framework
channels: {}           # Communication endpoints
dependencies: []       # Explicit unit dependencies
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

#### Unit Types

```yaml
type: stream-aligned     # Aligned to a business domain flow
     | platform           # Enables other units to deliver autonomously
     | enabling           # Helps units overcome obstacles, learn skills
     | governance         # Committees, boards, oversight bodies
     | leadership         # Executive and management units
     | support            # Shared services (HR, Finance, Legal)
```

Inspired by [Team Topologies](https://teamtopologies.com/key-concepts), extended with `governance`, `leadership`, and `support` for full organizational coverage.

#### Example

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

#### Example

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
| `process` | object | No | How this capability is executed (trigger, steps, inputs, output) |

#### Example

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

---

### `channels` (object)

How people communicate within and with this unit. Analogous to OpenAPI's `servers`.

#### `channels.sync` (array) — Meetings and rituals

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `type` | string | **Yes** | `meeting` / `workshop` / `standup` / `review` |
| `name` | string | **Yes** | Meeting name |
| `cadence` | string | No | Frequency |
| `duration` | string | No | Expected length |
| `day` | string | No | Scheduled day(s) |
| `rituals` | object | No | Pre/during/post protocols |

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
| `unit-types` | object | Custom unit type definitions |

Components have no effect until referenced. Use JSON Pointer syntax:

```yaml
# Reference within same file
output:
  $ref: "#/components/artifacts/product-roadmap"

# Reference to another file
from:
  $ref: "units/sales/opi.yaml#/unit"
```

#### Example

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
├── governance/
│   ├── committees/
│   │   ├── steering.yaml
│   │   └── product-sync.yaml
│   └── policies/
│       └── spending-authority.yaml
├── components/
│   ├── artifacts.yaml
│   └── authority-levels.yaml
└── README.md
```

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

### Capability-Requirement Matching (cross-unit validation)

When validating a multi-unit OPI repository, tooling SHOULD verify interface consistency across units. Inspired by [TOSCA](https://docs.oasis-open.org/tosca/TOSCA/v2.0/TOSCA-v2.0.html) capability-requirement matching:

8. **Requirement satisfaction:** Every `interfaces.inputs[]` entry SHOULD have a corresponding `interfaces.outputs[]` entry in the referenced source unit with a matching `artifact` name
9. **Orphaned outputs:** An `interfaces.outputs[]` entry with no matching `interfaces.inputs[]` in the target unit is a WARNING (potential waste)
10. **Cadence mismatch:** If unit A expects input `weekly` but unit B delivers `monthly`, this is a WARNING (SLA mismatch)
11. **Circular dependencies:** A dependency cycle (A→B→C→A) is a WARNING, not an error (organizations have legitimate circular flows)

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
| **Standard** | + `governance` + `channels` | Full organizational modeling |
| **Complete** | + `events` + `dependencies` + `components` + `status` | Enterprise-grade, tooling-ready |

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

## Changelog

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
