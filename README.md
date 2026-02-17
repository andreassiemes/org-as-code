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
├── spec/                  # OPI Specification (YAML format)
│   └── opi-spec-v0.1.md
├── examples/              # Example configurations
│   └── governance/
│       └── committee-structure.yaml
├── principles/            # Detailed principle descriptions
├── docs/                  # Documentation & guides
└── website/               # Source for org-as-code.com
```

## Quick Example

```yaml
# committees/steering-committee.yaml
committee:
  name: Steering Committee
  purpose: "Strategic alignment and resource allocation"
  cadence: bi-weekly
  duration: 60min

  members:
    - role: chair
      position: CEO
      accountability: agenda, facilitation, decision-log
    - role: member
      position: VP Engineering
    - role: member
      position: VP Product
    - role: observer
      position: COO

  decision_framework: DACI
  decisions:
    - type: strategic
      authority: approve
      escalation: board
    - type: operational
      authority: delegate
      escalation: none

  interfaces:
    receives_from:
      - source: product-team
        artifact: quarterly-okrs
        format: yaml
    sends_to:
      - target: all-hands
        artifact: decision-log
        format: markdown
        cadence: monthly
```

## Status

🚧 **Early Stage** — Spec v0.1 in development. Contributions and feedback welcome.

## Learn More

- 🌐 [org-as-code.com](https://org-as-code.com) — Concept, principles, and visual guides
- 📖 [OPI Specification](spec/opi-spec-v0.1.md) — The technical format
- 💡 [Examples](examples/) — Real-world configurations

## Author

**Andreas Siemes** — Principal Consultant Strategy & Transformation. Building the bridge between organizational design and software engineering.

- [LinkedIn](https://www.linkedin.com/in/andreassiemes/)
- [andreassiemes.de](https://andreassiemes.de)

## License

MIT
