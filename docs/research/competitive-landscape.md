---
type: research
project: "[[2026__Code-Driven-OrgDesign]]"
date: 2026-02-19
tags:
  - org-design
  - competitive-intelligence
  - opi
  - market-analysis
---

# OPI Competitive Landscape — February 2026

```toc
```

## Executive Summary

The "organization as code" space is **fragmented and early-stage**. No single tool or framework does what OPI proposes. The closest competitors operate in adjacent niches — Team Topologies tooling, developer portals, enterprise org design platforms, and governance-as-code for infrastructure. The **OPI sweet spot** (YAML-defined org units + governance + inter-unit interfaces + AI-native + Git-versioned) is genuinely unoccupied.

The biggest validation: **"Company as Code"** by Daniel Rothmann (42futures, Feb 2025) independently proposes a nearly identical thesis — but with no implementation, no spec, and no community. The term `organizationascode.com` was registered in Sep 2025 — someone else sees the same opportunity.

---

## Competitive Landscape Map

### Tier 1: Direct Competitors (Same Problem Space)

These aim to represent organizational structure as machine-readable, version-controlled code.

---

#### TeamAPI-As-Code
- **URL:** https://github.com/TeamTopologies/TeamAPI-As-Code
- **What it does:** YAML/JSON specification for machine-readable Team API definitions. Documents team info, focus, type, communication channels, services, meetings, interactions, and dependencies.
- **Maturity:** Very low. 27 stars, 3 forks, 1 commit visible, essentially dormant since Jan 2022.
- **Relation to OPI:** Most directly comparable. Both use YAML to define team/unit interfaces. TeamAPI-As-Code is specifically about Team Topologies vocabulary (stream-aligned, enabling, platform, complicated subsystem).
- **What OPI does better:**
  - OPI includes **governance** (DACI, decision rights, Gremien) — TeamAPI-As-Code does not
  - OPI defines **inter-unit data flows** (inputs/outputs with format, frequency) — TeamAPI-As-Code only has loose "interactions"
  - OPI includes **mandates** (purpose, authority, accountability) — TeamAPI-As-Code has "focus" but no governance
  - OPI has **validation/CI** concept (.ci/ directory) — TeamAPI-As-Code has no tooling
- **What OPI can learn:**
  - TeamAPI-As-Code's fields for **communication channels**, **meetings**, and **ways of working** are useful additions
  - The concept of **interaction modes** (collaboration, X-as-a-Service, facilitating) is a good vocabulary to adopt
  - Schema validation approach (JSON Schema) is a proven pattern

---

#### "Company as Code" (Daniel Rothmann, 42futures)
- **URL:** https://blog.42futures.com/p/company-as-code
- **What it does:** Blog post (Feb 2025) proposing treating organizational structure as executable code — a "company manifest" as single source of truth. Proposes declarative DSL, graph model (undirected cyclic), and plugin architecture for system integration.
- **Maturity:** Concept only. No implementation, no repo, no spec, no community.
- **Relation to OPI:** Nearly identical thesis. Rothmann identifies the same problems (compliance documentation overhead, disconnected HRIS/GRC tools, static org documents).
- **What OPI does better:**
  - OPI has a **concrete architecture** (units/, governance/, processes/, knowledge/) — Rothmann is theoretical
  - OPI uses **established formats** (YAML + Markdown + Git) — Rothmann proposes a custom DSL
  - OPI has a **PoC context** (ORAYLIS Gremienstruktur) — Rothmann has no implementation
  - OPI's **PARA adaptation for orgs** is a concrete knowledge architecture — Rothmann has none
- **What OPI can learn:**
  - Rothmann frames the **compliance/audit use case** powerfully — this is a strong enterprise selling point
  - The **"staging environment for org changes"** metaphor is brilliant marketing
  - His framing of the **graph model** (undirected cyclic vs. DAG) is technically more precise than OPI's current architecture sketch
  - The **integration framework** concept (plugging into production systems) is missing from OPI

---

#### DCgov Organizational Chart (YAML)
- **URL:** https://github.com/DCgov/organizational-chart
- **What it does:** YAML-based parsable organizational chart of DC government agencies. Includes agency name, abbreviation, budget code, homepage, parent entity, social media links.
- **Maturity:** Minimal. 1 star, 11 commits since 2015, essentially archived.
- **Relation to OPI:** Proof of concept that government saw value in YAML org charts. Limited to hierarchy (no governance, no interfaces, no processes).
- **What OPI does better:** Everything. DCgov is a flat hierarchy file, not a framework.
- **What OPI can learn:** Government/public sector is a potential early adopter — they have compliance mandates that reward machine-readable org structures.

---

### Tier 2: Adjacent Tools (Solve Part of the Problem)

These solve a subset of what OPI addresses but from a different angle.

---

#### Spotify Backstage (Software Catalog)
- **URL:** https://backstage.io
- **What it does:** Open-source internal developer portal. YAML-based `catalog-info.yaml` files define services, teams (Groups), ownership, APIs, and dependencies. Teams own their metadata via Git workflow.
- **Maturity:** Very high. 29k+ GitHub stars, CNCF Incubating, hundreds of enterprise adopters.
- **Relation to OPI:** Backstage already models teams-own-services in YAML. Its Group entity type can represent organizational hierarchy. But it is **software-catalog-first**, not org-design-first.
- **What OPI does better:**
  - OPI is **org-design-native** — governance, mandates, decision rights, DACI
  - OPI models **inter-unit information flows** — Backstage models service dependencies
  - OPI includes **processes and policies** as first-class citizens — Backstage does not
  - OPI is **AI-native** (designed for LLM context consumption) — Backstage is for developer self-service
- **What OPI can learn:**
  - **catalog-info.yaml** is the most successful "structure as YAML in Git" pattern in the world — study its adoption mechanics
  - Backstage's **entity model** (Component, API, Group, User, System, Domain, Resource) is well-designed
  - The **provider pattern** (sync from external sources) solves the "single source of truth" problem
  - OPI could position itself as **"Backstage for organizational design"** — this metaphor would resonate with CTOs

---

#### Cortex
- **URL:** https://www.cortex.io
- **What it does:** Commercial internal developer portal. YAML entity descriptors for services, teams, infrastructure. Customizable catalog types. Integrates with identity providers for auto-ownership.
- **Maturity:** High. Commercial product, venture-funded, enterprise customers.
- **Relation to OPI:** Like Backstage but commercial. Custom entity types can model org structures beyond just services. YAML-in-Git approach.
- **What OPI does better:** Same as Backstage — OPI is governance-native, not software-catalog-first.
- **What OPI can learn:**
  - Cortex's **custom entity types** ("design catalog and entity types for all kinds of components") shows the demand for flexible organizational modeling
  - Their integration with **Okta/Google/Workday** for automatic ownership is a pattern OPI needs

---

#### Port
- **URL:** https://www.port.io
- **What it does:** "Agentic" internal developer portal. Blueprints (custom entity definitions) for modeling any organizational asset. Team/User blueprints for org structure.
- **Maturity:** High. Commercial, Gartner-recognized, growing adoption.
- **Relation to OPI:** Port's "Blueprints" allow modeling arbitrary org entities — potentially even OPI-like structures. But it's still a developer portal, not an org design tool.
- **What OPI does better:** OPI has an **opinionated structure** for org design. Port is a generic canvas.
- **What OPI can learn:**
  - Port's **Blueprint system** (custom entity definitions) is a good abstraction to study
  - Their insight that 53% of engineers use portals for metadata reliability shows the market for "org truth as code"

---

#### GlassFrog (Holacracy)
- **URL:** https://www.glassfrog.com + https://github.com/holacracyone/glassfrog-api
- **What it does:** Software platform for Holacracy governance. Manages roles, circles, accountabilities, policies, and governance meetings. Has a REST API for programmatic access to org structure.
- **Maturity:** Medium. Production product used by Holacracy practitioners. API available but documentation sparse.
- **Relation to OPI:** GlassFrog is the closest **production example** of governance-as-code for organizations. Roles have purposes, domains, and accountabilities — similar to OPI mandates. Circles are nested units.
- **What OPI does better:**
  - OPI is **framework-agnostic** — GlassFrog requires Holacracy adoption
  - OPI uses **open formats** (YAML/Markdown/Git) — GlassFrog is a proprietary SaaS
  - OPI includes **inter-unit interfaces** (OPIs) — GlassFrog focuses on intra-circle governance
  - OPI is **AI-native** — GlassFrog predates the LLM era
- **What OPI can learn:**
  - Holacracy's **data model** (Role: purpose + domains + accountabilities) is battle-tested and should inform OPI's mandate.yaml schema
  - The **governance meeting process** (propose → react → amend → integrate) could inspire OPI's change management workflow
  - Circle nesting (circles contain roles which can be sub-circles) is a proven org hierarchy model

---

#### Holacracy Constitution (GitHub)
- **URL:** https://github.com/holacracyone/Holacracy-Constitution
- **What it does:** The Holacracy Constitution as Markdown on GitHub. Version-controlled organizational operating system.
- **Maturity:** Established. v5.0, actively maintained.
- **Relation to OPI:** Proof that a governance framework can live in Git as Markdown. The Constitution defines roles, circles, governance processes, and operational practices.
- **What OPI does better:** OPI operationalizes the structure (machine-readable YAML), not just documents it (prose Markdown).
- **What OPI can learn:** The Constitution's **modular adoption** approach (you can adopt parts, not the whole thing) is a crucial adoption strategy OPI should copy.

---

### Tier 3: Enterprise Org Design Platforms (Different Approach, Same Problem)

These are commercial platforms that solve org design visually/interactively, not as code.

---

#### Orgvue
- **URL:** https://www.orgvue.com
- **What it does:** Enterprise organizational design and workforce planning platform. Model change before committing, scenario planning, evidence-based decisions. Connects to HRIS.
- **Maturity:** Very high. Enterprise-grade, used by large organizations.
- **Relation to OPI:** Solves the same "design your org" problem but through a visual GUI, not code. Proprietary, not version-controlled.
- **What OPI does better:** Open formats, Git-versioned, AI-native, no vendor lock-in, developer-friendly.
- **What OPI can learn:**
  - **Scenario planning** ("model change before you commit") is a killer feature. OPI should support branch-based scenario planning (Git branches = org design variants)
  - Orgvue's **HRIS integration** is essential for enterprise adoption

---

#### Nakisa
- **URL:** https://nakisa.com
- **What it does:** Org design + workforce planning with agentic AI. Two tiers: Strategic (C-level restructuring) and Operational (manager-level team building). Real-time visualization.
- **Maturity:** Very high. Enterprise customers, AI features, regular releases (2025.R4).
- **Relation to OPI:** Direct competitor in the org design problem space, but polar opposite approach (SaaS GUI vs. code-first).
- **What OPI does better:** Open formats, transparency, no vendor lock-in, Git history, AI-as-reader not AI-as-black-box.
- **What OPI can learn:**
  - Nakisa's **two-tier model** (Strategic vs. Operational) maps well to OPI's potential user base — C-level uses governance/strategy, managers use unit definitions
  - Their **agentic AI for org design** is a direct validation of OPI's "AI-native" principle

---

#### ChartHop
- **URL:** https://www.charthop.com
- **What it does:** People analytics + org visualization. Dynamic org charts, compensation reviews, headcount planning, performance management in one platform.
- **Maturity:** High. Venture-funded, growing enterprise adoption.
- **Relation to OPI:** Overlaps on org visualization but is fundamentally an HR/people analytics tool, not an org design framework.
- **What OPI does better:** OPI models **governance and interfaces**, not just people and positions.
- **What OPI can learn:** ChartHop shows that org charts alone are not enough — the market wants **analytics on top of structure**.

---

#### Functionly
- **URL:** https://www.functionly.com
- **What it does:** Interactive org design for operational leaders. Scenario planning, headcount modeling, org chart editing, team collaboration.
- **Maturity:** Medium. Smaller than Orgvue/Nakisa but modern and accessible.
- **Relation to OPI:** Closest to OPI's "operational leaders want to design their org" thesis, but visual-first, not code-first.
- **What OPI does better:** Open formats, version control, governance layer.
- **What OPI can learn:**
  - Functionly's **unlimited scenario creation** is powerful — OPI should emphasize Git branches as unlimited org design scenarios
  - Their focus on **operational leaders** (not just C-suite) aligns with OPI's target audience

---

#### BCG OrgBuilder
- **URL:** https://www.bcg.com/x/product-library/orgbuilder
- **What it does:** BCG's patented platform for distributed organization redesign. Used in 3,000+ projects, restructuring 4M+ roles since 2010. Manages data flows, permissions, talent selection during reorganizations.
- **Maturity:** Very high. But proprietary to BCG consulting engagements.
- **Relation to OPI:** BCG OrgBuilder proves the **massive enterprise demand** for org design tooling. But it is consulting-locked — you can only use it with BCG.
- **What OPI does better:** Open, self-service, no consulting dependency, AI-native.
- **What OPI can learn:**
  - The **scale** (4M roles) proves the market exists
  - Their focus on **permissions and talent selection during reorgs** is a feature OPI could address
  - The **change management** focus (track progress, steer projects) is important

---

### Tier 4: Frameworks and Patterns (Conceptual, Not Tools)

---

#### Org Topologies (Krivitsky & Flemm)
- **URL:** https://www.orgtopologies.com
- **What it does:** Strategic org design framework with 16 archetypes and 4 distinctive topologies. Visual map tool + MADE change method. Certification program. Claims to be "first People + AI management system."
- **Maturity:** Medium. Active training business, Miro templates, LeSS community integration.
- **Relation to OPI:** Complementary framework. Org Topologies provides the **diagnostic and design vocabulary**; OPI could provide the **implementation format**.
- **What OPI does better:** OPI is implementation-level (actual YAML files), not just diagnostic.
- **What OPI can learn:**
  - The **16 archetypes** could become pre-built OPI templates
  - Their Miro integration shows the importance of visual tooling alongside code

---

#### Team Topologies (Skelton & Pais)
- **URL:** https://teamtopologies.com + https://github.com/TeamTopologies
- **What it does:** Framework defining 4 team types and 3 interaction modes. Miro plugin, templates, Team API concept.
- **Maturity:** High. Industry standard for tech org design. Books, training, consulting.
- **Relation to OPI:** OPI could be positioned as the **implementation layer** for Team Topologies patterns.
- **What OPI does better:** OPI goes beyond team types to governance, decision rights, and information flows.
- **What OPI can learn:**
  - **Team API** as a concept is powerful and widely adopted — OPI should explicitly support it
  - The **Miro plugin** strategy shows the importance of meeting users where they are

---

#### RAPID / DACI / RACI / OVIS Frameworks
- **URLs:** [Bain RAPID](https://www.bain.com/insights/management-tools-decision-rights-tools/), [Atlassian DACI](https://www.atlassian.com/team-playbook/plays/daci), [BCG OVIS](https://www.bcg.com/industries/public-sector/decision-rights-using-ovis-framework)
- **What they do:** Decision rights frameworks that clarify who Recommends, Agrees, Performs, Inputs, Decides (or Drives, Approves, Contributes, Informed).
- **Maturity:** Very high conceptually. Zero machine-readable implementations.
- **Relation to OPI:** OPI's `governance.daci` section is a **direct operationalization** of these frameworks.
- **What OPI does better:** OPI makes DACI/RAPID **machine-readable and version-controlled** — currently they exist only as spreadsheets or Confluence pages.
- **What OPI can learn:**
  - Include **RAPID and OVIS** as alternative governance schema options (not just DACI)
  - BCG's OVIS (Own, Veto, Influence, Support) is particularly good for hierarchical orgs

---

### Tier 5: Governance-as-Code (Infrastructure Pattern, Org Inspiration)

---

#### Open Policy Agent (OPA) / Rego
- **URL:** https://www.openpolicyagent.org
- **What it does:** Industry-standard policy-as-code engine. Policies written in Rego language, evaluated at deployment time. Used for infrastructure, Kubernetes, API gateways.
- **Maturity:** Very high. CNCF Graduated, massive adoption.
- **Relation to OPI:** OPA proves that "governance as code" works at scale — but only for infrastructure. OPI extends this pattern to organizational governance.
- **What OPI does better:** OPI applies the pattern to **human organizational decisions**, not just infrastructure policies.
- **What OPI can learn:**
  - OPA's **decoupled architecture** (policy decision separate from enforcement) is a good pattern
  - The **Rego language** shows that domain-specific policy languages work — OPI could define validation rules in a similar DSL
  - OPA's **testing framework** for policies is directly applicable to OPI validation (.ci/)

---

#### HashiCorp Sentinel / Spacelift
- **URL:** https://www.hashicorp.com/en/blog/policy-as-code-explained + https://spacelift.io/blog/policy-as-code-tools
- **What they do:** Policy-as-code tools for infrastructure governance. Define rules that infrastructure must follow.
- **Maturity:** High. Enterprise-grade.
- **Relation to OPI:** Same pattern (rules as code, validation, enforcement) but for infrastructure.
- **What OPI can learn:** The **"policy as code" narrative** is well-established and OPI can draft behind it — "We did policy-as-code for infrastructure. Now we do it for organizations."

---

## Gap Analysis: What Nobody Does

| Capability | TeamAPI-As-Code | Backstage | GlassFrog | Orgvue/Nakisa | **OPI** |
|------------|:-:|:-:|:-:|:-:|:-:|
| Units/Teams as YAML | Yes | Partial | No (API) | No (GUI) | **Yes** |
| Inter-unit interfaces (inputs/outputs) | Weak | No | No | No | **Yes** |
| Governance (DACI/decision rights) | No | No | Yes (Holacracy) | No | **Yes** |
| Mandates (purpose, authority) | Weak ("focus") | No | Yes (Holacracy) | Partial | **Yes** |
| Git version control | Yes | Yes | No | No | **Yes** |
| Processes as code | No | No | Yes (meetings) | No | **Yes** |
| CI/CD validation | No | No | No | No | **Yes** |
| AI-native (LLM-readable) | No | No | No | AI features | **Yes** |
| Scenario planning | No | No | No | Yes | **Git branches** |
| HRIS integration | No | Partial | No | Yes | **Not yet** |
| Visual output | No | Partial | Yes | Yes | **Generate from code** |

**OPI's unique combination:** The intersection of governance + interfaces + version control + AI-native is **completely unoccupied**.

---

## Strategic Positioning

### Narrative Options

1. **"Backstage for Org Design"** — Resonates with CTOs, implies YAML-in-Git maturity
2. **"Infrastructure as Code, but for Organizations"** — Drafts behind the IaC movement
3. **"Policy as Code for Human Decisions"** — Extends OPA/Sentinel narrative to org governance
4. **"The missing layer between Team Topologies and your Git repository"** — Very specific, high-signal

**Recommendation:** Lead with #2 in broad audiences, #4 in technical/Team Topologies communities.

### Positioning Against Each Tier

| Tier | OPI's Message |
|------|--------------|
| TeamAPI-As-Code | "We include governance, not just team descriptions" |
| Backstage/Cortex/Port | "We model the organization, not just the software catalog" |
| GlassFrog | "We're framework-agnostic and open-format" |
| Orgvue/Nakisa/ChartHop | "We're code-first — version-controlled, reviewable, AI-native" |
| OPA/Sentinel | "We extend governance-as-code from infrastructure to organizations" |

---

## Key Takeaways for OPI Spec

### Must-Have (Validated by Market)
1. **JSON Schema for validation** — TeamAPI-As-Code, Backstage both do this
2. **Entity model with types** — Backstage's Component/Group/API/System/Domain pattern works
3. **Interaction modes vocabulary** — Team Topologies' collaboration/X-as-a-Service/facilitating
4. **Multiple governance frameworks** — Support DACI, RAPID, OVIS (not just DACI)
5. **Modular adoption** — Holacracy Constitution v5.0's lesson: let people adopt parts, not the whole thing

### Should-Have (Differentiation)
1. **Compliance/audit automation** — Rothmann's "Company as Code" thesis; strong enterprise hook
2. **Scenario planning via Git branches** — OPI-unique, powerful metaphor
3. **Generated visualizations** — Every competitor has visuals; OPI needs generate-from-code output
4. **Integration points** — Provider pattern from Backstage for HRIS/identity sync

### Nice-to-Have (Future)
1. **Custom DSL** — If YAML becomes limiting (Rothmann's point about graph models)
2. **Validation rules as OPA/Rego** — Composable policy engine for org governance
3. **Change management workflow** — Inspired by GlassFrog's governance meeting process

---

## Competitive Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Team Topologies builds out TeamAPI-As-Code | Medium | OPI is broader (governance, processes, interfaces). Move fast. |
| Backstage adds org design features | Low-Medium | Backstage stays software-focused. OPI could be a Backstage plugin. |
| Enterprise vendors (Orgvue/Nakisa) add "as code" mode | Medium | They won't open-source. OPI's moat is open formats + community. |
| Someone else builds "Company as Code" first | High | Rothmann has no implementation. **Speed matters now.** |
| `organizationascode.com` domain owner launches something | Medium | OPI has `org-as-code.com` + unique OPI term. Different enough. |

### Timing Window

- Daniel Rothmann published "Company as Code" in Feb 2025 — **1 year ago, no follow-up**
- `organizationascode.com` registered Sep 2025 — **5 months ago, nothing visible**
- TeamAPI-As-Code dormant since 2022 — **no momentum**
- The window is **open but closing**. Every month increases the chance someone else ships first.

---

## Sources

- [TeamAPI-As-Code](https://github.com/TeamTopologies/TeamAPI-As-Code)
- [Team API Template](https://github.com/TeamTopologies/Team-API-template)
- [Company as Code — Daniel Rothmann (42futures)](https://blog.42futures.com/p/company-as-code)
- [DCgov Organizational Chart](https://github.com/DCgov/organizational-chart)
- [Backstage Software Catalog](https://backstage.io/docs/features/software-catalog/)
- [Backstage Descriptor Format](https://backstage.io/docs/features/software-catalog/descriptor-format/)
- [Cortex Internal Developer Portal](https://www.cortex.io/)
- [Port Internal Developer Portal](https://www.port.io/)
- [GlassFrog](https://www.glassfrog.com/) + [GlassFrog API](https://github.com/holacracyone/glassfrog-api)
- [Holacracy Constitution v5.0](https://www.holacracy.org/constitution/5-0/)
- [Holacracy Constitution on GitHub](https://github.com/holacracyone/Holacracy-Constitution)
- [Orgvue](https://www.orgvue.com/)
- [Nakisa Org Design](https://nakisa.com/products/org-design-software/)
- [ChartHop](https://slashdot.org/software/comparison/ChartHop-vs-Orgvue/)
- [Functionly](https://www.functionly.com/)
- [BCG OrgBuilder](https://www.bcg.com/x/product-library/orgbuilder)
- [Org Topologies](https://www.orgtopologies.com/)
- [Team Topologies](https://teamtopologies.com/)
- [Miro Team Topologies Plugin](https://miro.com/marketplace/team-topologies/)
- [Miro Org Topologies 2025 Template](https://miro.com/miroverse/org-topologies-2025/)
- [Open Policy Agent](https://platformengineering.org/blog/policy-as-code)
- [Policy-as-Code Tools 2026 (Spacelift)](https://spacelift.io/blog/policy-as-code-tools)
- [Pactflow](https://pactflow.io/)
- [RAPID Framework](https://umbrex.com/resources/frameworks/strategy-frameworks/rapid-decision-rights-framework/)
- [DACI Framework (Atlassian)](https://www.atlassian.com/team-playbook/plays/daci)
- [BCG OVIS Framework](https://www.bcg.com/industries/public-sector/decision-rights-using-ovis-framework)
- [Operations as Code (DevOps.com)](https://devops.com/operations-as-code-transforming-operational-excellence/)
- [GitHub-as-Code (Terraform)](https://medium.com/@yurinnick/github-organization-as-a-code-29da7efe3086)
- [Ingentis Org Design Software](https://www.ingentis.com/en/platform/org-design-software/)
