# Org as Code

> Making organizational design reviewable, testable, deployable.

**Org as Code** is an open framework for defining organizational structures, governance, and decision flows in version-controlled, AI-readable formats — so they can be treated like software: reviewed, tested, and deployed.

At its core: **OPI (Organizational Programming Interfaces)** — a YAML-based specification for encoding how organizations make decisions, assign responsibilities, and coordinate work.

## Why?

Organizations spend enormous effort on governance, compliance, and coordination — and most of it is invisible, undocumented, or stuck in slide decks. Meanwhile, software engineering solved this decades ago: version control, code review, automated testing, continuous deployment.

**Org as Code** bridges this gap. It brings engineering practices to organizational design — not to replace human judgment, but to make structures visible, discussable, and evolvable.

## 6 Principles

| # | Principle | Core Idea |
|---|-----------|-----------|
| 1 | **Org as Code** | Structures are versioned, reviewable, deployable — like software |
| 2 | **Human-First Automation** | AI handles the tedious; humans make the decisions |
| 3 | **Decision Flow Visibility** | Make visible where decisions get stuck |
| 4 | **Interface over Hierarchy** | OPIs over rigid org charts |
| 5 | **Adaptive by Design** | The framework adapts to the organization's developmental stage |
| 6 | **High-Performing Humanity** | Performance AND humanity — enabling entrepreneurial thinking without losing the human |

## What's Inside

```
org-as-code/
├── spec/                           # OPI Specification
│   ├── opi-v0.1.md                 #   Foundation spec (669 lines)
│   ├── opi-v0.2.md                 #   Full spec (1500+ lines, 36 validation rules)
│   └── opi-v0.2.schema.json        #   JSON Schema for validation
├── examples/
│   ├── governance/                 # Unit definitions
│   │   ├── committee-structure.yaml
│   │   ├── steering-committee.yaml #   Committee with DACI, schedule, interfaces
│   │   └── delivery-lead-sync.yaml #   Meeting with facilitator, weekly cadence
│   └── flows/                      # Cross-unit decision flows
│       ├── budget-approval.yaml    #   Decision flow with conditional routing
│       └── escalation.yaml         #   Escalation path with time-based triggers
├── templates/                      # Reusable org templates
│   ├── consulting-firm.yaml        #   7 custom types for consulting orgs
│   └── spotify-model.yaml          #   Squad, Tribe, Chapter, Guild types
└── docs/
    └── research/                   # Background research
        ├── competitive-landscape.md
        └── opi-spec-research-report.md
```

## Quick Example

A Steering Committee defined as OPI — with members, schedule, governance, and interfaces:

```yaml
opi: "0.2.0"

unit:
  name: "Steering Committee"
  id: steering-committee
  type: committee
  purpose: "Strategic decisions for the delivery organization"
  mandate: "Budget approval >10k EUR, headcount changes, unit restructuring"
  owner: "COO"

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

schedule:
  cadence: biweekly
  duration: 60
  rrule: "FREQ=WEEKLY;INTERVAL=2;BYDAY=TU;BYHOUR=10;BYMINUTE=0"

governance:
  framework: daci
  decisions:
    - type: budget-approval
      authority: approve
      quorum: 3
      escalation: board

interfaces:
  inputs:
    - from: delivery-lead-sync
      artifact: decision-proposals
      format: markdown
  outputs:
    - to: all-hands
      artifact: decision-log
      format: markdown
      cadence: monthly
```

## OPI Spec v0.2 Highlights

The specification defines 15 sections for modeling organizational units:

| Section | Purpose |
|---------|---------|
| `unit` | Identity, type, purpose, mandate |
| `members` | Roles with DACI/RAPID accountability |
| `schedule` | Cadence with iCalendar RRULE support |
| `governance` | Decision frameworks and authority |
| `interfaces` | Inputs/outputs between units |
| `flows` | Cross-unit decision and escalation paths |
| `components` | Type inheritance and custom unit types |
| `capabilities` | What the unit can do |
| `channels` | Communication (async, meetings, wikis) |
| `dependencies` | Unit relationships and SLAs |

**Unit types:** `team` · `department` · `committee` · `meeting` · `working-group` · `circle` · `board` · `custom`

**Governance models:** DACI · RAPID · OVIS · consent · consensus · autocratic

→ Full spec: [`spec/opi-v0.2.md`](spec/opi-v0.2.md) | JSON Schema: [`spec/opi-v0.2.schema.json`](spec/opi-v0.2.schema.json)

## Templates

Pre-built organizational templates with custom unit types:

- **[Consulting Firm](templates/consulting-firm.yaml)** — Practice, Delivery Unit, Steering, Staffing Board, Client Board, All-Hands, Leadership Team
- **[Spotify Model](templates/spotify-model.yaml)** — Squad, Tribe, Chapter, Guild

Templates use OPI's type inheritance (`components.types`) so you can define your organization's building blocks once and instantiate them consistently.

## Status

🚧 **Active Development** — Spec v0.2 is feature-complete. Tooling (validation, visualization) coming next.

## Learn More

- 🌐 [org-as-code.com](https://org-as-code.com) — Concept, principles, and visual guides
- 📖 [OPI Spec v0.2](spec/opi-v0.2.md) — The full specification
- 📖 [OPI Spec v0.1](spec/opi-v0.1.md) — Foundation version
- 💡 [Examples](examples/) — Real-world configurations
- 📐 [Templates](templates/) — Reusable organizational templates

## Author

**Andreas Siemes** — Principal Consultant Strategy & Transformation. Building the bridge between organizational design and software engineering.

- [LinkedIn](https://www.linkedin.com/in/andreassiemes/)
- [andreassiemes.de](https://andreassiemes.de)

## License

MIT
