# OPI Spec Research Report

**Date:** 2026-02-19
**Purpose:** Consolidated research for OPI Specification v0.1 — API standards, governance frameworks, competitive landscape.

---

## 1. API Specification Patterns

Five API/infrastructure specs were analyzed for structural patterns that translate to organizational modeling.

### 1.1 OpenAPI 3.1 (Software APIs)

**Adopted in OPI:**
- Document structure: `opi` version header, `unit` (≈ `info`), `capabilities` (≈ `paths`), `components` (reusable definitions)
- `$ref` for cross-references (JSON Pointer syntax)
- `x-` extension mechanism for organization-specific fields
- Required vs. optional fields, enums for constrained values

**Not applicable:** Runtime resolver patterns, server connectivity, authentication schemes.

### 1.2 AsyncAPI 3.0 (Event-Driven APIs)

**Adopted in OPI:**
- `events` section with `publishes` / `subscribes` pattern
- Channel-based communication model (sync meetings + async digital channels)

**Not applicable:** Binary message protocols, broker configuration.

### 1.3 GraphQL SDL (Schema Definition Language)

**Key insight:** Interface types as mandatory contracts. Every org unit implements a base `OrgUnit` interface with mandatory fields (`name`, `mandate`).

**Adopted in OPI:**
- Non-null concept → Conformance levels define which fields are mandatory at each tier
- Enum types for governance vocabularies (`DecisionRight`, `Frequency`)
- Query/Mutation/Subscription → maps to read org / change org / subscribe to changes

**New idea for v0.2:** Typed interface contracts with mandatory fields enforced via CI validation.

### 1.4 Protocol Buffers / gRPC

**Key insight:** Four communication method types map to organizational patterns:
- **Unary** → ad-hoc report request
- **Server streaming** → continuous metrics feed
- **Client streaming** → aggregated batch input
- **Bidirectional** → ongoing collaborative decision process

**Adopted in OPI:** Contract-first design philosophy (the YAML file IS the organizational contract).

**New idea for v0.2:** Classify every interface connection by method type (`unary` / `stream` / `batch` / `collaborative`).

### 1.5 TOSCA 2.0 (Cloud Topology)

**Key insight:** Capability-requirement matching — units declare what they provide and what they need. Tooling validates that every requirement is satisfied.

**Adopted in OPI v0.1:**
- Validation rules 8-11: requirement satisfaction, orphaned outputs, cadence mismatch, circular dependency detection
- Type inheritance concept (`derived_from` for unit type hierarchies)

**Not applicable:** Deployment artifacts, orchestration plans, cloud-specific node types.

### 1.6 Kubernetes CRDs

**Key insight:** `spec` vs. `status` separation — desired state vs. actual state. The delta IS the organizational debt. Conditions array as structured health indicators.

**Adopted in OPI v0.1:**
- `status` section at Complete conformance level
- Standard condition types: `Staffed`, `MandateClear`, `InterfacesHealthy`, `GovernanceCompliant`, `BudgetWithin`, `DependenciesOk`
- Reconciliation loop concept: reviews are reconciliation loops that close the spec/status gap

**New idea for v0.2:** `observed_version` tracking — has leadership reviewed the latest structural changes?

---

## 2. Governance Frameworks

Six organizational governance frameworks were analyzed for machine-readable patterns.

### 2.1 DACI / RAPID / OVIS

| Framework | Origin | Roles | Best For |
|-----------|--------|-------|----------|
| **DACI** | Atlassian | Driver, Approver, Contributor, Informed | Product/tech orgs |
| **RAPID** | Bain | Recommend, Agree, Perform, Input, Decide | Consulting/strategy |
| **OVIS** | BCG | Own, Veto, Influence, Support | Public sector, hierarchies |

**Adopted in OPI v0.1:** `governance.framework` supports all three plus consent/consensus/autocratic. Decision entry fields map to DACI; other frameworks use `x-` extensions.

**Finding:** Zero machine-readable implementations exist. DACI/RAPID/OVIS live exclusively in spreadsheets and Confluence pages. OPI is the first YAML operationalization.

### 2.2 Holacracy / GlassFrog

**Core model:** Roles with purpose + domains + accountabilities. Circles contain roles. Governance meetings (propose → react → amend → integrate).

**What OPI should steal:**
- Role as first-class object with `purpose`, `domain`, `accountabilities` (not just a label)
- Modular adoption (Holacracy v5.0 lesson: let people adopt parts, not the whole thing)
- Governance meeting as a formalized change process

**What doesn't fit:** Holacracy-specific terminology (tensions, processing, consent-based integration). OPI must be framework-agnostic.

### 2.3 Sociocracy 3.0 (S3)

**Core model:** Circles with drivers (organizational needs). Consent-based decision making (no objections = approved). Patterns as a library (not monolithic adoption).

**What OPI should steal:**
- `consent` as a governance framework option
- The concept of "drivers" (organizational needs that motivate action)
- Pattern library approach — OPI sections are independently adoptable

### 2.4 OPA / Rego (Policy as Code)

**Core model:** Policies written as code rules, evaluated at decision time. Decoupled architecture (policy separate from enforcement).

**What OPI should steal for v0.2:**
- Policy rules for org governance: `spending > 50k → requires(board.approval)`
- Composable validation rules (like OPA's Rego but for organizational policies)
- Testing framework for policies (assert that rules work as expected)

### 2.5 BPMN (Business Process Modeling)

**Core model:** Processes with lanes (roles), decision gateways, message flows between participants.

**What OPI should steal for v0.2:**
- Swimlanes concept for multi-unit processes (which unit does what)
- Decision gateways as explicit escalation points
- Message flows = OPI interfaces (already partially covered)

### 2.6 ArchiMate (Enterprise Architecture)

**Core model:** Business Layer (actors, roles, processes, functions, services) → Application Layer → Technology Layer.

**What OPI should steal:**
- Business Actor → Business Role → Business Process triplet
- Clear separation between what IS (structure) and what DOES (behavior/process)
- Collaboration as a first-class entity (joint activities between actors)

---

## 3. Competitive Landscape

Full analysis: see [OPI Competitive Landscape — February 2026](../../02__AREAS/A5__Career/OPI%20Competitive%20Landscape%20—%20February%202026.md)

### Summary

| Tier | Players | OPI Differentiator |
|------|---------|-------------------|
| **Direct** | TeamAPI-As-Code (dormant), "Company as Code" (concept only), DCgov YAML | OPI has governance + interfaces + implementation |
| **Adjacent** | Backstage (29k stars), Cortex, Port, GlassFrog | OPI is org-design-native, not software-catalog-first |
| **Enterprise** | Orgvue, Nakisa, ChartHop, BCG OrgBuilder (4M+ roles) | OPI is open, code-first, Git-versioned, AI-native |
| **Frameworks** | Team Topologies, Org Topologies | OPI provides the implementation layer |
| **Infra Gov** | OPA/Rego, Sentinel | OPI extends governance-as-code to human organizations |

### Key Finding

**The intersection of governance + interfaces + version control + AI-native is completely unoccupied.** TeamAPI-As-Code is the closest but dormant since 2022 with no governance. "Company as Code" (Rothmann, Feb 2025) has identical thesis but zero implementation.

### Timing

The window is open but closing:
- `organizationascode.com` registered Sep 2025 (nothing visible)
- Rothmann published 1 year ago, no follow-up
- Enterprise vendors adding AI features → could add "as code" modes

---

## 4. Synthesis: OPI Design Decisions

### Adopted in v0.1

| Pattern | Source | OPI Implementation |
|---------|--------|-------------------|
| Document structure | OpenAPI | `opi`, `unit`, `capabilities`, `components`, `$ref`, `x-` |
| Event pub/sub | AsyncAPI | `events.publishes` / `events.subscribes` |
| Interaction types | Team Topologies | `dependencies[].type`: collaboration, x-as-a-service, facilitating |
| Multiple governance frameworks | DACI/RAPID/OVIS | `governance.framework` enum with 6 options |
| Capability-requirement matching | TOSCA | Validation rules 8-11 (cross-unit interface consistency) |
| Spec/Status separation | Kubernetes CRDs | `status` section with conditions array (Complete level) |

### Deferred to v0.2

| Pattern | Source | Reason for Deferral |
|---------|--------|-------------------|
| Communication method types | gRPC | Nice-to-have, adds complexity to interfaces |
| Role reification (temporal bounds) | Schema.org | Requires schema change to members section |
| Type inheritance | TOSCA | Needs `unit-types` component system first |
| Policy rules as code | OPA/Rego | Separate DSL concern, complex |
| Process swimlanes | BPMN | Capabilities.process is sufficient for v0.1 |
| JSON Schema validation file | Backstage | Needs stable spec first, then generate schema |
| Change management workflow | Holacracy | Governance meeting patterns need more design |

### Strategic Positioning

**Primary:** "Infrastructure as Code, but for Organizations"
**Technical:** "The missing layer between Team Topologies and your Git repository"
**Enterprise:** "Backstage for Org Design"

---

## 5. Sources

### API Specifications
- [OpenAPI 3.1.0](https://spec.openapis.org/oas/v3.1.0.html)
- [AsyncAPI 3.0.0](https://www.asyncapi.com/docs/reference/specification/v3.0.0)
- [GraphQL SDL](https://graphql.org/learn/schema/)
- [Protocol Buffers](https://protobuf.dev/overview/)
- [gRPC Core Concepts](https://grpc.io/docs/what-is-grpc/core-concepts/)
- [Schema.org Organization](https://schema.org/Organization)
- [Schema.org OrganizationRole](https://schema.org/OrganizationRole)
- [TOSCA 2.0 Specification](https://docs.oasis-open.org/tosca/TOSCA/v2.0/TOSCA-v2.0.html)
- [Kubernetes CRDs](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)

### Governance Frameworks
- [DACI (Atlassian)](https://www.atlassian.com/team-playbook/plays/daci)
- [RAPID (Bain)](https://www.bain.com/insights/management-tools-decision-rights-tools/)
- [OVIS (BCG)](https://www.bcg.com/industries/public-sector/decision-rights-using-ovis-framework)
- [Holacracy Constitution v5.0](https://www.holacracy.org/constitution/5-0/)
- [GlassFrog API](https://github.com/holacracyone/glassfrog-api)
- [Sociocracy 3.0](https://sociocracy30.org/)
- [Open Policy Agent](https://www.openpolicyagent.org)

### Competitive Landscape
- [TeamAPI-As-Code](https://github.com/TeamTopologies/TeamAPI-As-Code)
- [Company as Code (Rothmann)](https://blog.42futures.com/p/company-as-code)
- [Backstage](https://backstage.io)
- [Cortex](https://www.cortex.io)
- [Port](https://www.port.io)
- [GlassFrog](https://www.glassfrog.com)
- [Orgvue](https://www.orgvue.com)
- [Nakisa](https://nakisa.com)
- [ChartHop](https://www.charthop.com)
- [BCG OrgBuilder](https://www.bcg.com/x/product-library/orgbuilder)
- [Org Topologies](https://www.orgtopologies.com)
- [Team Topologies](https://teamtopologies.com)
