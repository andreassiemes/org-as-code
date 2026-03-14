---
tags: [org-as-code, opi, spec]
status: draft
date: 2026-03-14
---

# OPI Specification v0.5 — Addendum

> Decision Graph & Agent Context — OPI for Governance Intelligence
>
> Extends: OPI Spec v0.4 (2026-03-13)
> Status: Draft — v0.5 (March 2026)

---

## Abstract

OPI v0.5 extends the Specification with two features that connect governance structure to runtime intelligence:

1. **Decision Graph** (`decisions[]`) — A top-level array of recorded decisions, linked across time through triggers and consequences, enabling governance audit trails, impact analysis, and decision-aware drift detection
2. **Agent Context API** (`agents[].context_api`) — Extensions to the existing `agents[]` block that define how AI agents consume their governance context at runtime, including escalation paths, refined scope, and a structured endpoint configuration

Both features are **fully additive**. OPI v0.4 documents work without modification.

---

## What's New in v0.5

| Feature | Location | Description | Use Case |
|---------|----------|-------------|----------|
| **Decision Graph** | `decisions[]` (top-level) | Structured decision records linked via triggers/consequences forming a directed acyclic graph | Governance audit trail, impact analysis, drift enrichment |
| **Decision Revision** | `decisions[].revises` | Links a superseding decision back to the one it replaces | Decision lifecycle tracking, compliance |
| **Escalation Path** | `agents[].escalation_path` | Ordered list of escalation targets for an agent instance | Agent runtime escalation, on-call chains |
| **Refined Agent Scope** | `agents[].scope` (extended) | Adds `org_units`, `gremien`, and `decision_types` to agent scope definition | Fine-grained governance context scoping |
| **Context Endpoint** | `agents[].context_endpoint` | API configuration for delivering governance context to agents at runtime | MCP server integration, JSON/YAML context delivery |

---

## 1. Schema Reference: `decisions[]` — Decision Graph

Top-level array alongside `gremien[]` and `agents[]`. Each entry is a structured record of one organizational decision, with optional links to related decisions forming a directed acyclic graph.

### Structure

```yaml
decisions:
  - id: string              # Unique ID, e.g. "dec-001" (required)
    date: string            # ISO 8601 date of decision (required)
    gremium: string         # Reference to gremium ID where decision was made (required)
    title: string           # One-sentence description of the decision (required)
    driver: string          # Person or role who drove this decision (required)
    approver: string        # Person or role who formally approved (required)
    status: enum            # active | planned | revoked | superseded (required)
    rationale: string       # Why this decision was made (required)
    triggers: [string]      # Decision IDs that led to this decision (optional, default [])
    consequences: [string]  # Decision IDs that resulted from this decision (optional, default [])
    revises: string         # ID of the decision this one supersedes (optional)
    scope: string           # Organizational scope affected (optional)
    review_date: string     # ISO 8601 date when this decision should be reviewed (optional)
    x-*: any                # Extension fields
```

### Field Documentation

| Field | Type | Required | Description | Example |
|-------|------|:--------:|-------------|---------|
| `id` | string | **Yes** | Unique identifier within the document. Recommended: sequential slug `dec-NNN` or semantic `dec-<topic>-NNN`. MUST be unique across all `decisions[]`. | `"dec-001"`, `"dec-budget-2026-01"` |
| `date` | string (ISO 8601) | **Yes** | Date on which the decision was formally made (not drafted, not announced — decided). | `"2026-03-01"` |
| `gremium` | string | **Yes** | Reference to the ID of the gremium (`gremien[].id`) where the decision was made. Establishes who owns the decision. | `"steering-committee"` |
| `title` | string | **Yes** | One-sentence description of the decision. Should be a complete declarative sentence. | `"Adopt OPI v0.4 as the standard for all organizational units by Q3 2026"` |
| `driver` | string | **Yes** | Person or role who owned the decision process (equivalent to DACI Driver). May be a `members[]` name or `components.roles` key. | `"coo"`, `"Maria Schmidt"` |
| `approver` | string | **Yes** | Person or role who formally approved the decision. In DACI: the Approver. Must be a member or role reference. | `"ceo"`, `"steering-committee-chair"` |
| `status` | enum | **Yes** | Lifecycle state. `active` = in force. `planned` = decided but not yet enacted. `revoked` = cancelled without replacement. `superseded` = replaced by another decision (see `revises`). | `"active"` |
| `rationale` | string | **Yes** | Explanation of why this decision was made. Include context, alternatives considered, and key reasoning. 2-5 sentences recommended. | `"Standardizing on OPI v0.4 reduces tooling fragmentation across 8 units and enables automated drift detection."` |
| `triggers` | [string] | No | IDs of decisions that caused or necessitated this decision. Backward links in the graph. Default: `[]`. | `["dec-001", "dec-003"]` |
| `consequences` | [string] | No | IDs of decisions that were directly caused by this one. Forward links in the graph. Default: `[]`. Tooling may compute these automatically from `triggers` cross-references. | `["dec-005"]` |
| `revises` | string | No | ID of the decision this one supersedes. The referenced decision MUST be updated to `status: superseded`. Required when this decision replaces an earlier one. | `"dec-002"` |
| `scope` | string | No | Free-text description of the organizational scope affected (units, regions, domains). | `"All engineering and product units"`, `"EU region only"` |
| `review_date` | string (ISO 8601) | No | When should this decision be reviewed for continued validity? Tooling may alert if review_date passes without revisit. | `"2026-09-01"` |
| `x-*` | any | No | Extension fields for org-specific metadata (e.g., `x-jira-issue`, `x-confluence-page`). | `x-jira: "ARCH-42"` |

### Full Example

```yaml
decisions:
  # Foundation decision — established the OPI program
  - id: dec-001
    date: 2026-01-15
    gremium: steering-committee
    title: "Adopt OPI as the standard organizational specification format across all business units"
    driver: coo
    approver: ceo
    status: active
    rationale: |
      Fragmented unit documentation (wikis, slide decks, verbal agreements) makes it impossible
      to run automated compliance checks or onboard AI agents with reliable governance context.
      OPI provides a machine-readable, version-controlled format that all our tooling can consume.
      Alternatives considered: custom YAML schema (rejected: reinventing solved problem),
      off-the-shelf HRIS (rejected: no agent governance model).
    scope: "All business units (15 active as of 2026-Q1)"
    review_date: 2026-07-01

  # Consequence of dec-001: specific tooling decision
  - id: dec-002
    date: 2026-01-28
    gremium: architecture-board
    title: "Use orgspec CLI as the reference implementation for OPI linting and visualization"
    driver: head-of-engineering
    approver: cto
    status: superseded
    rationale: |
      After adopting OPI (dec-001), we needed a reference toolchain. orgspec CLI was the most
      mature open-source option with existing DACI and drift validation support.
    triggers:
      - dec-001
    revises: null
    scope: "DevOps and Platform Engineering"
    review_date: 2026-06-01

  # Revision of dec-002: upgraded to v0.5-aware tooling
  - id: dec-004
    date: 2026-03-14
    gremium: architecture-board
    title: "Upgrade orgspec CLI to v0.5 and enable Decision Graph validation and Agent Context API"
    driver: head-of-engineering
    approver: cto
    status: active
    rationale: |
      OPI v0.5 introduces Decision Graph (dec-003) and Agent Context API. The existing orgspec
      v0.4 toolchain cannot validate decision cycles or serve agent context endpoints.
      Upgrading enables governance-aware agent deployment across all units.
    triggers:
      - dec-002
      - dec-003
    revises: dec-002
    scope: "Platform Engineering, all CI/CD pipelines"
    review_date: 2026-09-14

  # Parallel decision — OPI v0.5 adoption
  - id: dec-003
    date: 2026-03-10
    gremium: steering-committee
    title: "Extend OPI to v0.5 with Decision Graph and Agent Context API features"
    driver: coo
    approver: ceo
    status: active
    rationale: |
      Operational governance is increasingly agent-assisted. Agents need structured access to
      active decisions in scope to avoid acting against current governance. The Decision Graph
      provides the traceability needed for compliance audits. Both features are additive;
      v0.4 compatibility is preserved.
    triggers:
      - dec-001
    consequences:
      - dec-004
    scope: "OPI specification, orgspec CLI, all units deploying agents"
    review_date: 2026-09-10
```

### Use Cases

**Governance Audit Trail**
Every significant decision is recorded with date, gremium, driver, approver, and rationale. Auditors can query the `decisions[]` array to reconstruct who decided what, when, and why — without interviewing people or searching meeting notes.

**Impact Analysis**
The `triggers` and `consequences` links form a traversable graph. Tools can answer: "If we revoke dec-001, which subsequent decisions are affected?" Walking the consequence chain surfaces downstream dependencies before a reversal is enacted.

**Drift Detection Enrichment**
Drift entries (`status.drift[]`) can reference decision IDs in their `note` field to explain why a deviation was intentionally accepted. Tooling can correlate: "This drift has been `stable` since dec-003 was enacted — is the spec now out of date, or is the drift expected?"

---

## 2. Schema Reference: `agents[].context_api` — Agent Context API

Extensions to the existing unit-level `agents[]` block introduced in v0.4. These fields define how an agent discovers its governance context at runtime: its escalation chain, refined scope, and the endpoint configuration for consuming a structured context payload.

### Extended Agent Instance Fields

Full `agents[]` entry with v0.5 additions:

```yaml
agents:
  - ref: string                     # Reference to components.agents (v0.4, required)
    scope:                          # Extended in v0.5
      units: [string]               # (v0.4) Organizational units visible to agent
      data: [string]                # (v0.4) Data types accessible
      governance: string            # (v0.4) none | read-only | full
      org_units: [string]           # (NEW) Org unit names (human-readable aliases)
      gremien: [string]             # (NEW) Gremium IDs whose decisions are in scope
      decision_types: [string]      # (NEW) Categories of decisions agent may reference
    schedule:                       # (v0.4, unchanged)
      cadence: enum
      day: string
      time: string
      condition: string
    disabled: boolean               # (v0.4, unchanged)
    escalation_path: [string]       # (NEW) Ordered escalation targets
    context_endpoint:               # (NEW) API endpoint configuration
      format: enum                  # json | yaml | mcp (default: json)
      include_decisions: boolean    # Include active decisions in scope (default: true)
      include_integral: boolean     # Include AQAL/maturity context (default: false)
```

### Field Documentation: `escalation_path`

| Field | Type | Required | Description | Example |
|-------|------|:--------:|-------------|---------|
| `escalation_path` | [string] | No | Ordered list of escalation targets. When the agent must escalate, it contacts targets in order until acknowledged. Each entry SHOULD be a `members[]` name, `components.roles` key, or gremium ID. First entry is primary escalation target. | `["unit-lead", "head-of-engineering", "cto"]` |

### Field Documentation: `scope` Extensions

| Field | Type | Required | Description | Example |
|-------|------|:--------:|-------------|---------|
| `scope.org_units` | [string] | No | Human-readable organizational unit names (complements `scope.units` which uses machine IDs). Useful when agent context payload needs display-friendly labels. | `["Product", "Engineering", "Data"]` |
| `scope.gremien` | [string] | No | Gremium IDs whose decisions are in scope for this agent. Agent's context payload will include `active` decisions from these gremien. MUST reference existing `gremien[].id` values. | `["architecture-board", "steering-committee"]` |
| `scope.decision_types` | [string] | No | Categories of decisions the agent is permitted to reference in its reasoning. Tooling may use this to filter the `decisions[]` payload. | `["architecture", "budget", "governance"]` |

### Field Documentation: `context_endpoint`

| Field | Type | Required | Description | Example |
|-------|------|:--------:|-------------|---------|
| `context_endpoint` | object | No | Configuration for the agent's governance context endpoint. Defines the format and content of the context payload delivered to the agent at runtime. | — |
| `context_endpoint.format` | enum | No | Serialization format for the context payload. `json` = standard JSON (default). `yaml` = YAML. `mcp` = Model Context Protocol tool-call format. Default: `json`. | `"mcp"` |
| `context_endpoint.include_decisions` | boolean | No | Whether to include `active` decisions from `scope.gremien` in the context payload. Default: `true`. Set `false` to reduce payload size for agents that don't need decision context. | `true` |
| `context_endpoint.include_integral` | boolean | No | Whether to include AQAL quadrant / maturity assessment context (Integral OE layer). Default: `false`. Only relevant for orgs using the Integral OE extension. | `false` |

### Full Example: Agent with Context API

```yaml
agents:
  - ref: governance-advisor
    scope:
      units: [product, engineering, data]
      data: [decisions, metrics, governance, status]
      governance: read-only
      org_units: ["Product", "Engineering", "Data Analytics"]
      gremien: [steering-committee, architecture-board]
      decision_types: [architecture, governance, budget]
    schedule:
      cadence: on-demand
      condition: "when agent receives governance query"
    escalation_path:
      - product-lead           # Primary: unit lead
      - head-of-product        # Secondary: domain head
      - coo                    # Tertiary: executive
    context_endpoint:
      format: mcp
      include_decisions: true
      include_integral: false
```

### Context API Response Schema

When an agent runtime queries its governance context, the endpoint returns a structured payload. Below is the JSON schema for the `json` format response. The `mcp` format wraps this in a Model Context Protocol tool-call response.

```json
{
  "agent": {
    "ref": "governance-advisor",
    "type": "advisory",
    "purpose": "Analyze governance decisions and recommend actions for in-scope units",
    "constraints": [
      "Cannot modify OPI documents or governance records",
      "Cannot approve decisions — only prepares recommendations",
      "Must escalate ambiguous governance conflicts to unit-lead"
    ],
    "governance": {
      "may_read": true,
      "may_write": false,
      "may_decide": false,
      "audit_trail": "git"
    }
  },
  "scope": {
    "units": ["product", "engineering", "data"],
    "org_units": ["Product", "Engineering", "Data Analytics"],
    "gremien": ["steering-committee", "architecture-board"],
    "decision_types": ["architecture", "governance", "budget"],
    "governance_access": "read-only"
  },
  "escalation_path": [
    "product-lead",
    "head-of-product",
    "coo"
  ],
  "decisions": [
    {
      "id": "dec-001",
      "date": "2026-01-15",
      "gremium": "steering-committee",
      "title": "Adopt OPI as the standard organizational specification format across all business units",
      "status": "active",
      "driver": "coo",
      "approver": "ceo",
      "scope": "All business units",
      "review_date": "2026-07-01"
    },
    {
      "id": "dec-003",
      "date": "2026-03-10",
      "gremium": "steering-committee",
      "title": "Extend OPI to v0.5 with Decision Graph and Agent Context API features",
      "status": "active",
      "driver": "coo",
      "approver": "ceo",
      "scope": "OPI specification, orgspec CLI, all units deploying agents",
      "review_date": "2026-09-10"
    }
  ],
  "as_of": "2026-03-14T09:00:00Z"
}
```

**Notes:**
- `rationale` is excluded from the default context payload to keep it concise. Agents may request full decision records via a separate lookup.
- `decisions` array contains only `active` decisions from gremien in `scope.gremien`. `planned`, `revoked`, and `superseded` decisions are excluded unless explicitly requested.
- `as_of` timestamp enables agents to detect stale context (e.g., if cache TTL is exceeded).

### Use Case: How an AI Agent Consumes its Governance Context at Runtime

At agent startup or on-demand invocation, the agent runtime executes the following flow:

```
Agent Startup Flow (with Context API):
1. Agent runtime loads agent definition from components.agents
2. Runtime reads context_endpoint config from agents[] instance
3. Runtime calls: orgspec context <agent-id> --format <format>
4. orgspec resolves:
   a. Agent constraints and governance flags
   b. Scope: units, gremien, decision_types
   c. Active decisions from scope.gremien
   d. Escalation path for this instance
5. Runtime injects context payload into agent system prompt or tool context
6. Agent reasons within governance bounds:
   - "I may only reference decisions from: steering-committee, architecture-board"
   - "Active decisions in scope: dec-001, dec-003, dec-004"
   - "If I need to escalate: product-lead → head-of-product → coo"
7. Agent executes task, logs reasoning and constraints validated
8. If constraint triggered → escalate to escalation_path[0]
```

This prevents the common failure mode of agents acting against current governance: an agent that knows `dec-003` is active will not recommend rolling back to OPI v0.4.

### MCP Server Integration

When `context_endpoint.format: mcp`, the orgspec CLI exposes an **MCP server** that AI agent hosts (Claude, OpenAI Assistants, etc.) can connect to as a tool provider.

The MCP server exposes two tools:

| Tool | Description | Arguments |
|------|-------------|-----------|
| `get_governance_context` | Returns the full context payload for the requesting agent | `agent_id: string`, `as_of: string (ISO 8601, optional)` |
| `lookup_decision` | Returns full decision record including rationale | `decision_id: string` |

**Integration example (Claude system prompt injection via MCP):**

```
Available tools:
- get_governance_context(agent_id) → Returns active decisions, constraints, escalation path
- lookup_decision(decision_id) → Returns full decision record

Before answering governance questions, call get_governance_context to load
current decisions in scope. Do not reason about governance without current context.
```

This enables Claude (or any MCP-compatible agent host) to fetch live governance context before reasoning, ensuring answers reflect the current org state rather than training data.

---

## 3. Validation Rules (v0.5)

Rules continue numbering from v0.4 (last rule: 62).

### Rules 63–68: Decision Graph Validation

#### Rule 63: `decisions[].gremium` Must Reference Existing Gremium

**Assertion:** Every `decisions[].gremium` MUST reference an ID that exists in `gremien[]` within the same document or a referenced document.

**Rationale:** Decisions are owned by gremien. Dangling gremium references prevent accountability tracking.

**Level:** ERROR

**Example:**

```yaml
gremien:
  - id: steering-committee
    name: "Steering Committee"

decisions:
  - id: dec-001
    gremium: steering-committee    # ✓ PASS: exists in gremien[]
    ...

  - id: dec-002
    gremium: ghost-committee       # ✗ FAIL: no such gremium
    ...
```

---

#### Rule 64: `decisions[].triggers[]` Must Reference Existing Decision IDs

**Assertion:** Each entry in `decisions[i].triggers[]` MUST reference an ID that exists in `decisions[]`.

**Rationale:** Trigger links form the backward edges of the decision graph. Dangling triggers break graph traversal and audit trail reconstruction.

**Level:** ERROR

**Example:**

```yaml
decisions:
  - id: dec-001
    triggers: []                   # ✓ PASS: root decision, no triggers

  - id: dec-002
    triggers: [dec-001]            # ✓ PASS: dec-001 exists

  - id: dec-003
    triggers: [dec-999]            # ✗ FAIL: dec-999 not in decisions[]
```

---

#### Rule 65: `decisions[].consequences[]` Must Reference Existing Decision IDs

**Assertion:** Each entry in `decisions[i].consequences[]` MUST reference an ID that exists in `decisions[]`.

**Rationale:** Consequence links form the forward edges of the decision graph. Dangling consequence links prevent impact analysis.

**Level:** ERROR

**Example:**

```yaml
decisions:
  - id: dec-001
    consequences: [dec-002]        # ✓ PASS: dec-002 exists

  - id: dec-002
    consequences: [dec-999]        # ✗ FAIL: dec-999 not in decisions[]
```

---

#### Rule 66: `decisions[].revises` Must Reference Existing Decision ID

**Assertion:** If `decisions[i].revises` is present, it MUST reference an ID that exists in `decisions[]`.

**Rationale:** Revision links are critical for lifecycle tracking. A revision that doesn't point to a real decision cannot be traced.

**Level:** ERROR

**Example:**

```yaml
decisions:
  - id: dec-001
    status: superseded
    ...

  - id: dec-002
    revises: dec-001               # ✓ PASS: dec-001 exists

  - id: dec-003
    revises: dec-ghost             # ✗ FAIL: dec-ghost not in decisions[]
```

---

#### Rule 67: Revoked Decision Must Have Rationale or `revises`

**Assertion:** A decision with `status: revoked` MUST satisfy at least one of:
1. `revises` points to the superseded decision, OR
2. `rationale` explicitly states why it was revoked (rationale is already required, but content must address revocation)

**Rationale:** Revocation without explanation creates governance blind spots. Auditors must be able to understand why a decision was cancelled.

**Level:** WARNING

**Example:**

```yaml
# ✓ PASS: revocation with explicit revises link
- id: dec-004
  status: revoked
  revises: dec-001
  rationale: "dec-001 was revoked after strategy pivot in Q2 2026."

# ✓ PASS: revocation with clear rationale (no replacement decision)
- id: dec-005
  status: revoked
  rationale: "Initiative cancelled due to budget constraints in 2026-Q1 planning."

# ✗ WARN: revocation rationale too vague
- id: dec-006
  status: revoked
  rationale: "No longer relevant."   # Insufficient — why? when? who decided?
```

---

#### Rule 68: Decision Graph Must Not Contain Cycles

**Assertion:** The directed graph formed by `triggers` and `consequences` links MUST be a DAG (directed acyclic graph). Cycles are not permitted.

**Rationale:** Decision causality is directional in time. A cycle (A triggered B, B triggered A) is logically impossible and indicates data error. Cycles break graph traversal and audit trail reconstruction.

**Level:** ERROR

**Detection:** Run topological sort on the decision graph. If sort fails (cycle detected), report the cycle members.

**Example:**

```yaml
decisions:
  - id: dec-A
    triggers: [dec-C]              # ✗ FAIL: A ← C, but C ← B ← A → cycle
    consequences: [dec-B]

  - id: dec-B
    triggers: [dec-A]
    consequences: [dec-C]

  - id: dec-C
    triggers: [dec-B]
    consequences: [dec-A]          # cycle: A → B → C → A
```

---

### Rules 69–71: Agent Context API Validation

#### Rule 69: `escalation_path[]` Entries Should Reference Valid Targets

**Assertion:** Each entry in `agents[].escalation_path[]` SHOULD reference a valid `members[]` name, `components.roles` key, or `gremien[].id`. Unresolvable entries are not an error but generate a warning.

**Rationale:** An escalation path with dangling references fails silently at runtime. Warnings surface this before deployment.

**Level:** WARNING

**Example:**

```yaml
agents:
  - ref: governance-advisor
    escalation_path:
      - product-lead           # ✓ PASS: valid role ref
      - head-of-product        # ✓ PASS: valid role ref
      - ghost-person           # ✗ WARN: not resolvable
```

---

#### Rule 70: `scope.gremien[]` Must Reference Existing Gremium IDs

**Assertion:** Each entry in `agents[].scope.gremien[]` MUST reference an ID that exists in `gremien[]`.

**Rationale:** The agent context payload filters decisions by gremium. A reference to a non-existent gremium silently produces an empty decisions list — a security-relevant failure mode.

**Level:** ERROR

**Example:**

```yaml
gremien:
  - id: steering-committee
    name: "Steering Committee"

agents:
  - ref: governance-advisor
    scope:
      gremien:
        - steering-committee   # ✓ PASS: exists in gremien[]
        - fake-board           # ✗ FAIL: no such gremium
```

---

#### Rule 71: `context_endpoint.format` Must Be Valid Enum

**Assertion:** If `agents[].context_endpoint.format` is present, it MUST be one of: `json`, `yaml`, `mcp`.

**Rationale:** Tooling cannot generate a context payload for unknown formats.

**Level:** ERROR

**Example:**

```yaml
agents:
  - ref: governance-advisor
    context_endpoint:
      format: json               # ✓ PASS
      include_decisions: true

  - ref: bad-agent
    context_endpoint:
      format: graphql            # ✗ FAIL: not a valid format
```

---

## 4. Backward Compatibility

Both v0.5 features are fully additive. No changes to existing fields or validation rules.

| Document | v0.5 Behavior |
|----------|--------------|
| v0.4 document (no `decisions[]`) | Valid. `decisions[]` is optional. Rules 63–68 do not apply. |
| v0.4 document (no `context_endpoint`) | Valid. All new `agents[]` fields are optional. |
| v0.3 document | Valid. All v0.4 and v0.5 features are optional. |
| v0.2 / v0.1 document | Valid. Only schema version may generate a deprecation notice from tooling. |

Upgrading is incremental:
1. **No action required.** Existing documents are valid as-is.
2. **Optional: Add `decisions[]`.** Start recording key decisions. No other fields required.
3. **Optional: Add `context_endpoint` to agents.** Define how agents consume governance context.
4. **Optional: Link decisions** via `triggers`, `consequences`, `revises` to build the graph over time.

---

## 5. CLI Integration (`orgspec`)

The `orgspec` CLI is the reference implementation for OPI validation and visualization.

### New Commands (v0.5)

| Command | Description |
|---------|-------------|
| `orgspec decisions` | Visualize the decision graph (ASCII or Mermaid output). Highlights cycles, superseded nodes, and pending `review_date` entries. |
| `orgspec decisions --status active` | Filter decisions by status. |
| `orgspec decisions --gremium <id>` | Show decisions for a specific gremium. |
| `orgspec context <agent-id>` | Output the full governance context payload for a given agent (in the configured format). Useful for debugging and dry-run. |
| `orgspec context <agent-id> --format mcp` | Output context as MCP tool response format. |
| `orgspec lint` | Runs all validation rules, including v0.5 rules 63–71. Reports errors and warnings. |
| `orgspec serve --mcp` | Start MCP server exposing `get_governance_context` and `lookup_decision` tools. |

### Example Output: `orgspec decisions`

```
Decision Graph — as of 2026-03-14

dec-001 [ACTIVE] Adopt OPI as standard (2026-01-15, steering-committee)
  └─ triggered → dec-002 [SUPERSEDED] Use orgspec CLI v0.4 (2026-01-28, architecture-board)
  └─ triggered → dec-003 [ACTIVE] Extend OPI to v0.5 (2026-03-10, steering-committee)
                   └─ triggered → dec-004 [ACTIVE] Upgrade orgspec to v0.5 (2026-03-14, architecture-board)
                                    └─ revises → dec-002

⚠  dec-001 review_date 2026-07-01 approaching (109 days)
✓  No cycles detected
✓  All gremium references resolved
```

### Example Output: `orgspec context governance-advisor`

```json
{
  "agent": { "ref": "governance-advisor", ... },
  "scope": { "gremien": ["steering-committee", "architecture-board"], ... },
  "decisions": [
    { "id": "dec-001", "status": "active", "title": "Adopt OPI ...", ... },
    { "id": "dec-003", "status": "active", "title": "Extend OPI to v0.5 ...", ... },
    { "id": "dec-004", "status": "active", "title": "Upgrade orgspec to v0.5 ...", ... }
  ],
  "escalation_path": ["product-lead", "head-of-product", "coo"],
  "as_of": "2026-03-14T09:00:00Z"
}
```

---

## 6. JSON Schema Additions (v0.5)

JSON Schema fragments for both features, following the same style as `opi-v0.4.schema.json`.

### Fragment: `decisions[]`

```json
{
  "$defs": {
    "Decision": {
      "type": "object",
      "required": ["id", "date", "gremium", "title", "driver", "approver", "status", "rationale"],
      "properties": {
        "id": {
          "type": "string",
          "description": "Unique decision identifier",
          "pattern": "^[a-z0-9][a-z0-9\\-]*$"
        },
        "date": {
          "type": "string",
          "format": "date",
          "description": "ISO 8601 date of decision"
        },
        "gremium": {
          "type": "string",
          "description": "Reference to gremium ID"
        },
        "title": {
          "type": "string",
          "minLength": 10,
          "description": "One-sentence decision description"
        },
        "driver": { "type": "string" },
        "approver": { "type": "string" },
        "status": {
          "type": "string",
          "enum": ["active", "planned", "revoked", "superseded"]
        },
        "rationale": {
          "type": "string",
          "minLength": 20,
          "description": "Why this decision was made"
        },
        "triggers": {
          "type": "array",
          "items": { "type": "string" },
          "default": []
        },
        "consequences": {
          "type": "array",
          "items": { "type": "string" },
          "default": []
        },
        "revises": {
          "type": "string",
          "description": "ID of the decision this one supersedes"
        },
        "scope": { "type": "string" },
        "review_date": {
          "type": "string",
          "format": "date"
        }
      },
      "additionalProperties": {
        "description": "x-* extension fields permitted"
      }
    }
  },
  "properties": {
    "decisions": {
      "type": "array",
      "items": { "$ref": "#/$defs/Decision" },
      "description": "Top-level decision graph"
    }
  }
}
```

### Fragment: `agents[].context_api` Extensions

```json
{
  "$defs": {
    "AgentScopeV5": {
      "allOf": [
        { "$ref": "#/$defs/AgentScope" },
        {
          "properties": {
            "org_units": {
              "type": "array",
              "items": { "type": "string" },
              "description": "Human-readable org unit names"
            },
            "gremien": {
              "type": "array",
              "items": { "type": "string" },
              "description": "Gremium IDs whose decisions are in scope"
            },
            "decision_types": {
              "type": "array",
              "items": { "type": "string" },
              "description": "Categories of decisions agent may reference"
            }
          }
        }
      ]
    },
    "ContextEndpoint": {
      "type": "object",
      "properties": {
        "format": {
          "type": "string",
          "enum": ["json", "yaml", "mcp"],
          "default": "json"
        },
        "include_decisions": {
          "type": "boolean",
          "default": true
        },
        "include_integral": {
          "type": "boolean",
          "default": false
        }
      },
      "additionalProperties": false
    },
    "AgentInstanceV5": {
      "allOf": [
        { "$ref": "#/$defs/AgentInstance" },
        {
          "properties": {
            "escalation_path": {
              "type": "array",
              "items": { "type": "string" },
              "description": "Ordered escalation targets"
            },
            "context_endpoint": {
              "$ref": "#/$defs/ContextEndpoint"
            }
          }
        }
      ]
    }
  }
}
```

---

## 7. Design Decisions

### D6: Decision Graph — Why Separate Top-Level Array (not inside `gremien[]`)

**Decision:** `decisions[]` is a top-level array alongside `gremien[]`, rather than being nested inside each `gremium` entry.

**Rationale:**
- Decisions frequently involve multiple gremien (one decides, another is informed). A flat array with a single `gremium` ownership field is simpler and avoids duplication.
- Graph traversal (triggers/consequences) works across all decisions regardless of gremium. Nesting would require cross-gremium lookups.
- Tooling (CLI, linters) treats `decisions[]` as its own graph object — flattening enables topological sort without merging nested arrays.

**Tradeoff:** Queries scoped to a single gremium require filtering. Tooling (`orgspec decisions --gremium <id>`) handles this.

---

### D7: Agent Context API — Why `context_endpoint` (not inline context payload in spec)

**Decision:** The spec defines *how* an agent fetches context (`context_endpoint` config), not the context payload itself.

**Rationale:**
- Context is dynamic (decisions are added, revoked, superseded). A static payload in the spec would be stale within days.
- The spec describes *governance structure*. Runtime context delivery is an operational concern — it belongs in tooling (`orgspec context`), not in the version-controlled spec file.
- Different agent hosts (Claude, OpenAI, local LLM) have different context injection mechanisms. The `format` enum (`json`, `yaml`, `mcp`) covers the main cases without locking into one.

**Tradeoff:** Requires a running `orgspec` process (or MCP server) to serve context. Stateless environments can fall back to `orgspec context <agent-id> --format yaml` output committed to the repo as a snapshot.

---

### D8: Escalation Path — Why Ordered List (not single escalation target)

**Decision:** `escalation_path` is an ordered array, not a single `escalation_target` string.

**Rationale:**
- A single target is a single point of failure. If the primary escalation target is unavailable, the agent has no fallback — it blocks or errors.
- Real on-call chains are ordered (primary → backup → executive). The array models this naturally.
- Tooling can validate that each entry is resolvable, and runtime can implement retry-with-fallback automatically.

**Tradeoff:** Slightly more verbose than a single field, but the operational safety improvement justifies it.

---

## 8. Relationship Between V0.5 Features and Prior Features

### Decision Graph ↔ Drift Detection (F3, v0.4)

`status.drift[]` entries can reference decision IDs in their `note` field to explain intentional deviations:

```yaml
status:
  drift:
    - field: governance.framework
      expected: "DACI"
      actual: "consent-based (pilot)"
      severity: info
      since: 2026-03-10
      trend: stable
      note: "Pilot approved by dec-003. Planned revert to DACI by 2026-09-01."
```

This connects drift to the decision that authorized it — auditors can see the full picture without searching meeting notes.

---

### Agent Context API ↔ Decision Graph (F1 ↔ F2)

The Agent Context API delivers `decisions[]` data to agents at runtime. Agents with `include_decisions: true` receive the filtered decision graph as part of their governance context. This enables:

- Agents refusing to act against active decisions ("dec-001 mandates OPI v0.4+ — I cannot recommend reverting to v0.3")
- Agents flagging pending `review_date` entries ("dec-001 review is due in 109 days — recommend scheduling governance review")
- Agents explaining reasoning by citing decision IDs in audit trail entries

---

### Agent Context API ↔ Agents (F2, v0.4)

The Context API extends `agents[]` without changing the core governance model. `escalation_path` replaces ad-hoc constraint text like "must escalate to unit-lead" with a machine-readable, resolvable list. `context_endpoint` makes the agent governance context queryable by agent runtimes — closing the loop between the spec and agent execution.

---

## 9. Complete Example: Governance-Aware Agent Deployment

A full unit definition combining all v0.5 features with v0.4 capabilities:

```yaml
opi: "0.5.0"

unit:
  id: product
  name: "Product Organization"
  purpose: "Define product strategy, roadmap, and user success metrics"
  type: stream-aligned

gremien:
  - id: product-board
    name: "Product Board"
    purpose: "Quarterly product direction and prioritization"
    cadence: quarterly
    members: [product-lead, head-of-product, engineering-lead]

decisions:
  - id: dec-P001
    date: 2026-01-20
    gremium: product-board
    title: "Adopt Jobs-to-Be-Done framework as primary discovery methodology for 2026"
    driver: product-lead
    approver: head-of-product
    status: active
    rationale: |
      Customer research in Q4 2025 revealed that feature requests were driven by job stories
      rather than preference surveys. JTBD provides a more stable basis for roadmap decisions.
      Outcome-based roadmaps reduce mid-sprint scope changes by an estimated 30%.
    scope: "Product Organization, Design, User Research"
    review_date: 2026-07-01

  - id: dec-P002
    date: 2026-03-05
    gremium: product-board
    title: "Pause new feature development for one sprint to address critical UX debt"
    driver: product-lead
    approver: head-of-product
    status: active
    rationale: |
      NPS dropped 12 points in February (38 → 26). Root cause: 3 core flows have unresolved
      friction identified in Q4 UX audit. New feature velocity is masking retention risk.
      One-sprint pause approved; re-evaluation at sprint review.
    triggers:
      - dec-P001
    scope: "Product, Engineering sprint planning"
    review_date: 2026-03-31

components:
  agents:
    product-context-agent:
      name: "Product Governance Context Agent"
      type: advisory
      purpose: "Delivers current product governance context to AI-assisted planning tools"
      capabilities:
        - "Read active decisions from product-board"
        - "Summarize current governance state for planning sessions"
        - "Flag upcoming review dates"
      constraints:
        - "Cannot modify decisions or governance records"
        - "Cannot approve any product decisions"
        - "Must cite decision IDs when referencing governance in outputs"
      governance:
        may_read: true
        may_write: false
        may_decide: false
        audit_trail: git
      owner: product-lead

members:
  - role_ref: product-lead
    name: "Maria Schmidt"
    start_date: 2025-06-01
    daci: driver
    capacity: 1.0

agents:
  - ref: product-context-agent
    scope:
      units: [product]
      data: [decisions, status, metrics]
      governance: read-only
      gremien: [product-board]
      decision_types: [product-strategy, ux, planning]
    schedule:
      cadence: on-demand
    escalation_path:
      - product-lead
      - head-of-product
    context_endpoint:
      format: mcp
      include_decisions: true
      include_integral: false
```

---

## 10. File Organization (v0.5 extension)

```
org-repo/
├── org.yaml                          # Org-level config + agent registry
├── components/
│   ├── roles.yaml                    # Shared role definitions (v0.4)
│   └── agents.yaml                   # Shared agent type definitions (v0.4)
├── decisions/
│   ├── org-decisions.yaml            # Org-level decision graph (optional: split from org.yaml)
│   └── <unit>/
│       └── decisions.yaml            # Unit-scoped decisions (alternative layout)
├── units/
│   ├── product/
│   │   └── opi.yaml                  # Product unit (with decisions[], agents[]+context_api)
│   ├── engineering/
│   │   └── opi.yaml
│   └── steering-committee/
│       └── opi.yaml
└── docs/
    ├── examples/
    │   ├── decisions-example.yaml
    │   └── agent-context-example.yaml
    └── migration-v04-to-v05.md
```

**Note:** `decisions[]` may live directly in unit `opi.yaml` files (recommended for unit-scoped decisions) or in a separate `decisions/` directory for org-wide decisions. Both layouts are valid.
