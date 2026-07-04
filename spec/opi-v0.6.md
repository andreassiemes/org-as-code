---
tags: [org-as-code, opi, spec]
status: draft
date: 2026-06-17
---

# OPI Specification v0.6 — Addendum

> OKF Interoperability & the Knowledge Graph — OPI on the Open Substrate
>
> Extends: OPI Spec v0.5 (2026-03-14)
> Status: Draft — v0.6 (June 2026)

---

## Abstract

OPI v0.6 connects the strict, typed OPI governance model to the open knowledge ecosystem. It introduces five features:

1. **OKF Export Profile** — A deterministic, lossless mapping from an OPI document set to a conformant [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog) (OKF v0.1) bundle. OPI stays the strict source of truth; the OKF bundle is a portable, agent-readable projection.
2. **Knowledge Graph** (`knowledge[]` + `knowledge_refs[]`) — A first-class entity for typed knowledge concepts that live *beside* structure, with bidirectional links between the two. This is the knowledge layer of the org graph.
3. **OKF Import** (`orgspec import --okf`) — Round-trip ingestion of a conformant OKF bundle back into OPI, with an explicit preserved-vs-lossy contract.
4. **Native `log.md` Provenance** — OKF's `log.md` convention adopted natively as OPI's provenance and maintenance surface, with a freshness rule that gives the spec its first executable answer to ontology drift.
5. **Permissive Consumer Model** — A stated robustness rule: producers and the validator stay strict; *consumers* tolerate unknown keys, unknown types, broken links, and higher-minor enum values.

All five features are **fully additive**. OPI v0.5, v0.4, and v0.3 documents work without modification.

**Positioning.** OKF is a deliberately minimal, untyped *substrate* — one required field (`type`), untyped links, a permissive consumer contract, no registry. OPI is the strict, typed, validatable *governance layer* on top. The two share one instinct — organization and knowledge as versioned, agent-readable Markdown — but sit on different layers. v0.6 makes them snap together: OPI is the strict source; OKF is the lingua franca it travels in.

---

## What's New in v0.6

| Feature | Location | Description | Use Case |
|---------|----------|-------------|----------|
| **OKF Export Profile** | `orgspec export --target okf` | Lossless mapping of an OPI document set to a conformant OKF v0.1 bundle | Portable, vendor-neutral knowledge sharing; agent consumption without an OPI SDK |
| **OPI→OKF Type Vocabulary** | (export) | Controlled vocabulary mapping each OPI entity to an OKF `type` | Typed semantics on top of OKF's untyped substrate |
| **Knowledge Graph** | `knowledge[]` (top-level) | First-class typed knowledge concepts beside structure | Org memory: playbooks, definitions, references linked to units/roles/decisions |
| **Knowledge References** | `knowledge_refs[]` (on entities) | Bundle-relative or URI links from structure to knowledge concepts | Attaching context to a unit, role, gremium, decision, or agent |
| **OKF Import** | `orgspec import --okf` | Round-trip ingestion of a conformant OKF bundle into OPI | Bootstrapping OPI from existing OKF knowledge; federation |
| **Native `log.md` Provenance** | `log.md` (per bundle / per entity) | Chronological provenance + maintenance surface | Ontology-drift early warning, audit, change history |
| **Permissive Consumer Model** | (consumer contract) | Consumers tolerate unknown keys/types/links/enums; producers stay strict | Forward compatibility without weakening `orgspec lint` |

---

## 1. Schema Reference: OKF Export Profile

The OKF Export Profile defines how an OPI document set is rendered as a conformant **OKF v0.1 bundle** — a directory tree of Markdown files, each with YAML frontmatter, plus the reserved files `index.md` and `log.md`. The export is a **generated projection** (see Design Decision D9): the OPI YAML remains the single source of truth, and the bundle is regenerated on change.

### 1.1 OPI→OKF Type Vocabulary

OKF requires exactly one frontmatter field, `type`, and deliberately ships **no central type registry** — producers choose their own values. OPI's value-add is precisely this typing, so OPI defines a **controlled vocabulary** that every export MUST use (see Rule 72):

| OPI source | OKF `type` value | OKF file path pattern |
|------------|------------------|------------------------|
| `org` (org.yaml) | `Organization` | `/index.md` (root) + `/org.md` |
| `unit` | `Org Unit` | `/units/<unit.id>.md` |
| `components.roles.<key>` | `Role` | `/roles/<key>.md` |
| `gremien[]` entry | `Committee` | `/gremien/<gremium.id>.md` |
| `decisions[]` entry | `Decision` | `/decisions/<decision.id>.md` |
| `components.agents.<key>` / `agents[]` | `Agent` | `/agents/<agent.id>.md` |
| `status.drift[]` entry | `Drift` | `/drift/<field-slug>.md` |
| `knowledge[]` entry (§2) | the concept's own `type` (e.g. `Playbook`, `Reference`, `Concept`) | `/knowledge/<knowledge.id>.md` |

A future OPI entity requires a vocabulary addition (a minor-version concern — see D10).

### 1.2 Frontmatter Mapping

Each exported concept document carries OKF frontmatter populated deterministically from the OPI source:

| OKF field | Required by OKF | Populated from OPI |
|-----------|:---------------:|--------------------|
| `type` | **Yes** | The OPI→OKF vocabulary value (§1.1) |
| `title` | No (recommended) | `name` / `title` of the source entity |
| `description` | No (recommended) | First sentence of `purpose` / `rationale` / `description` |
| `resource` | No (recommended) | A canonical URI from `references[].url` or an `x-*` field, if present |
| `tags` | No (recommended) | `tags`, `decision_types`, or `type` enums of the source entity |
| `timestamp` | No (recommended) | ISO 8601 datetime of the export run |

OPI-specific fields are preserved as `x-opi-*` frontmatter keys so the export is **lossless** and importable (§3).

### 1.3 Cross-Links

Every OPI reference field becomes a directed, **bundle-relative** Markdown link (absolute form, beginning with `/`, which OKF recommends as stable):

| OPI reference | Emitted link (in the source doc's body) |
|---------------|------------------------------------------|
| `decisions[].gremium` | `[<title>](/gremien/<id>.md)` in the Decision doc |
| `decisions[].triggers[]` / `consequences[]` / `revises` | links between Decision docs |
| `agents[].owner` / `escalation_path[]` | links from the Agent doc to Role/member docs |
| `members[].role_ref` | links from the Unit doc to Role docs |
| `unit.parent` / `dependencies[].unit` | links between Unit docs |
| `knowledge_refs[]` (§2) | links from any entity doc to `/knowledge/<id>.md` |

Per OKF, links are **untyped** at the markup level — the relationship kind is conveyed by the surrounding prose (e.g. "Owned by", "Triggered by", "References"). Consumers treat them as directed edges and tolerate broken links (Rule 83).

### 1.4 Reserved Files

The export generates the two OKF reserved files:

- **`index.md`** at the bundle root and in each subdirectory. The bundle-root `index.md` carries the only permitted frontmatter — `okf_version: "0.1"` — and lists sections of entries:

  > **Note on the OKF spec itself:** OKF v0.1 §6 states that index files "contain no frontmatter", while §11 introduces the bundle-root `okf_version` frontmatter as the single exception. OPI follows §11: frontmatter on the root `index.md` only, never on subdirectory indexes. Validator implementers should not trip over §6 read in isolation.

  ```markdown
  # Organization: Product Organization

  ## Units
  * [Product Organization](/units/product.md) - Define product strategy, roadmap, and user success metrics

  ## Committees
  * [Product Board](/gremien/product-board.md) - Quarterly product direction and prioritization

  ## Decisions
  * [Adopt Jobs-to-Be-Done framework …](/decisions/dec-P001.md) - active, product-board
  ```

- **`log.md`** — the provenance file (§4).

### 1.5 Conformance Clause

> **An OPI OKF export MUST be a conformant OKF v0.1 bundle.** That is: every non-reserved `.md` file contains a parseable YAML frontmatter block with a non-empty `type`; the reserved files `index.md` and `log.md` follow OKF structure; and the bundle-root `index.md` declares `okf_version: "0.1"`.

This makes the export consumable by *any* OKF reader (the reference tooling in Google's `knowledge-catalog` repository — which now ships sample bundles and a reference enrichment agent alongside the static visualizer —, an LLM agent, another OPI instance) with no OPI-specific tooling.

**Beware the stray `.md`:** OKF reserves *only* `index.md` and `log.md`. Any other Markdown file in the bundle — a `README.md`, a `NOTES.md` — is a concept document and MUST carry frontmatter with a non-empty `type`, or the bundle as a whole is non-conformant. The exporter therefore MUST NOT emit auxiliary frontmatter-less `.md` files into the bundle (see Rule 73).

### 1.6 Body Convention

The exported concept body uses OKF's conventional headings where they apply (`# Schema`, `# Examples`, `# Citations`) and adds an OPI-native section that round-trips the source fragment:

```markdown
---
type: Decision
title: Adopt Jobs-to-Be-Done framework as primary discovery methodology for 2026
description: Outcome-based discovery replaces preference surveys for 2026 roadmap decisions.
tags: [product-strategy, decision]
timestamp: 2026-06-17T09:00:00Z
x-opi-id: dec-P001
x-opi-status: active
---

# Decision: Adopt JTBD framework

**Owned by** [Product Board](/gremien/product-board.md). **Driver:** product-lead. **Approver:** head-of-product.

Customer research in Q4 2025 revealed feature requests were driven by job stories rather than
preference surveys. JTBD provides a more stable basis for roadmap decisions.

# References
* [Jobs-to-Be-Done framework](/knowledge/jtbd-framework.md)

# Schema (source fragment)
```yaml
id: dec-P001
gremium: product-board
status: active
review_date: 2026-07-01
```
```

---

## 2. Schema Reference: `knowledge[]` — The Knowledge Graph

`knowledge[]` is a top-level array alongside `gremien[]`, `agents[]`, and `decisions[]`. Each entry is a typed unit of knowledge — a playbook, a reference, a concept definition, a metric definition — that lives *beside* the structural model. Where `decisions[]` records *what was decided*, `knowledge[]` records *what is known*. Together with `knowledge_refs[]` (§2.3) this forms a bidirectional graph between structure and knowledge (Verhelst capability-stack Layer 4: Knowledge Graph).

### 2.1 Structure

```yaml
knowledge:
  - id: string              # Unique ID, e.g. "jtbd-framework" (required)
    type: string            # Concept kind: Playbook | Reference | Concept | Metric Definition | … (required)
    title: string           # Human-readable display name (required)
    description: string     # One-sentence summary (required)
    resource: string        # Canonical URI for the underlying asset (optional)
    tags: [string]          # Cross-cutting categorization (optional, default [])
    body: string            # Markdown body of the concept (optional)
    relates_to: [string]    # Back-links to structure: unit/role/gremium/decision/agent IDs (optional, default [])
    citations: [string]     # External sources backing the body (optional, default [])
    timestamp: string       # ISO 8601 of last meaningful change (optional)
    x-*: any                # Extension fields
```

### 2.2 Field Documentation

| Field | Type | Required | Description | Example |
|-------|------|:--------:|-------------|---------|
| `id` | string | **Yes** | Unique identifier within the document. Slug form. MUST be unique across all `knowledge[]`. | `"jtbd-framework"` |
| `type` | string | **Yes** | The kind of knowledge concept. Free string (OKF-style, no central registry), but SHOULD be self-explanatory. Becomes the OKF `type` verbatim on export. | `"Playbook"`, `"Reference"`, `"Concept"`, `"Metric Definition"` |
| `title` | string | **Yes** | Human-readable display name. | `"Jobs-to-Be-Done Framework"` |
| `description` | string | **Yes** | One-sentence summary of the concept. | `"Discovery methodology that frames demand as jobs customers hire a product to do."` |
| `resource` | string | No | A URI that uniquely identifies the underlying asset (a wiki page, a paper, a dataset). | `"https://wiki.example.com/jtbd"` |
| `tags` | [string] | No | Cross-cutting categorization. Default `[]`. | `["discovery", "product"]` |
| `body` | string | No | Markdown body. Exported as the concept document body, may use `# Schema` / `# Examples` / `# Citations`. | — |
| `relates_to` | [string] | No | Back-links to structural entities (`unit`, `components.roles` key, `gremien[].id`, `decisions[].id`, `agents[]` ref). Forms the structure↔knowledge edges. Default `[]`. | `["product", "dec-P001"]` |
| `citations` | [string] | No | External sources backing claims in `body`. URIs or bundle-relative paths. Default `[]`. | `["https://hbr.org/…"]` |
| `timestamp` | string (ISO 8601) | No | Last meaningful change. | `"2026-06-10T12:00:00Z"` |
| `x-*` | any | No | Extension fields. | `x-confluence: "PROD-12"` |

### 2.3 `knowledge_refs[]` on Structural Entities

Any structural entity — `unit`, a `components.roles` entry, a `gremien[]` entry, a `decisions[]` entry, an `agents[]` instance — MAY carry a `knowledge_refs[]` array pointing at knowledge concepts. Each entry is either a local `knowledge[].id`, a bundle-relative path (`/knowledge/<id>.md`), or an external URI:

```yaml
decisions:
  - id: dec-P001
    # … existing v0.5 fields …
    knowledge_refs:
      - jtbd-framework                       # local knowledge[].id
      - /knowledge/nps-definition.md          # bundle-relative (e.g. an imported concept)
      - https://wiki.example.com/okf/roadmap  # external resource URI
```

`knowledge_refs[]` (structure → knowledge) and `knowledge[].relates_to[]` (knowledge → structure) are the two directions of the same edge. Tooling SHOULD reconcile them (Rule 78).

### 2.4 Full Example

```yaml
knowledge:
  - id: jtbd-framework
    type: Playbook
    title: "Jobs-to-Be-Done Framework"
    description: "Discovery methodology framing demand as the jobs customers hire a product to do."
    tags: [discovery, product, methodology]
    relates_to:
      - product            # the unit that adopted it
      - dec-P001           # the decision that mandated it
    body: |
      # Examples
      A "job story" follows the form: *When [situation], I want to [motivation], so I can [outcome].*

      # Citations
      Christensen et al., "Competing Against Luck" (2016).
    citations:
      - "https://www.christenseninstitute.org/jobs-to-be-done/"
    timestamp: 2026-06-10T12:00:00Z
```

---

## 3. Schema Reference: OKF Import (`orgspec import --okf`)

Import is the inverse of the Export Profile: it reads a **conformant OKF v0.1 bundle** and produces OPI documents. Import is intentionally narrower than export — it is **lossless out, best-effort in** (Design Decision D9).

### 3.1 Mapping

| OKF document `type` | Imported as |
|---------------------|-------------|
| A value in the OPI→OKF vocabulary (§1.1) — `Org Unit`, `Role`, `Committee`, `Decision`, `Agent`, `Drift`, `Organization` | The corresponding typed OPI entity, reconstructed from `x-opi-*` frontmatter where present, else from recommended fields |
| Any other `type` (e.g. `Playbook`, `Reference`, an unknown producer's type) | A `knowledge[]` concept (its `type` preserved verbatim) |

### 3.2 Preserved vs. Lossy

| Source of the bundle | Round-trip fidelity |
|----------------------|---------------------|
| Bundle produced by OPI export (carries `x-opi-*`) | **Lossless** — typed entities and all OPI fields are reconstructed. |
| Third-party OKF bundle (no `x-opi-*`) | **Best-effort** — recognized types map to typed entities using recommended fields only; unrecognized types become `knowledge[]` concepts; markdown `body` and links are preserved; OPI-specific structure (validation-relevant fields) is **not** inferred and is flagged in the import report. |

Import MUST refuse a non-conformant bundle (Rule 86) and MUST report every document it down-mapped to a generic `knowledge[]` concept (Rule 85).

---

## 4. Schema Reference: Native `log.md` Provenance

OPI adopts OKF's `log.md` convention **natively** as its provenance and maintenance surface (Verhelst capability-stack Layer 7: Provenance). A `log.md` MAY exist at the bundle root and per entity directory. It is the named maintenance mechanism the Org-as-Code thesis requires against *ontology drift* — the failure mode where a knowledge/governance model silently decays until it becomes a hallucination source rather than a source of truth.

### 4.1 Format

OKF's `log.md` format, verbatim: a flat list of date-grouped entries, **newest first**, with ISO 8601 (`YYYY-MM-DD`) date headings.

```markdown
# Update Log

## 2026-06-17
* **Update**: dec-P001 review completed; JTBD retained for 2026-H2.
* **Creation**: Added knowledge concept jtbd-framework.

## 2026-03-05
* **Update**: dec-P002 enacted (one-sprint UX-debt pause).
```

### 4.2 Generation & Reconciliation

`log.md` is generated/reconciled from three sources, all of which already exist in OPI:

1. **Git history** of the OPI files (commit timestamps + messages).
2. **`decisions[]`** — each new, revised, or revoked decision produces an entry on its `date`.
3. **`status.drift[]`** — each severity/trend transition produces an entry.

It is therefore the chronological projection of the Decision Graph and Drift — no new authoring burden.

### 4.3 Freshness Rule

The `log.md` surface plus the existing `decisions[].review_date` (v0.5) yields the spec's first executable drift-detection rule (Rule 80): a decision whose `review_date` has passed **without** a later `log.md` entry referencing it is the detectable signature of an unmaintained model — surfaced as a WARNING. Active remediation (alerting, an auto-repair agent) stays in tooling and v0.7 (Design Decision D12).

---

## 5. Schema Reference: The Permissive Consumer Model

v0.6 adopts OKF's robustness stance ("consumers MUST NOT reject …") — carefully scoped so it does **not** weaken `orgspec lint`.

- **Producers and the validator (`orgspec lint`)** remain **strict**: all rules (1–86) apply; errors fail CI.
- **Consumers / readers** — agent runtimes, visualizers, the Context API endpoint (v0.5), OKF importers — MUST tolerate and degrade gracefully on:
  1. unknown top-level keys,
  2. unknown `x-*` extension fields,
  3. unknown enum values from a higher minor version (treat as opaque),
  4. broken bundle-relative links,
  5. missing optional sections or reserved files.

This is the central balancing decision of v0.6 (D11): OKF portability for *readers* without diluting the strictness that is OPI's whole point.

---

## 6. Validation Rules (v0.6)

Rules continue numbering from v0.5 (last rule: 71). Rules 72–75 cover Export; 76–78 cover the Knowledge Graph; 79–81 cover Provenance; 82–84 cover the Permissive Consumer Model; 85–86 cover Import.

### Rules 72–75: OKF Export

#### Rule 72: Every Exportable Entity Maps to a `type`

**Assertion:** On export, every exportable OPI entity (org, unit, role, gremium, decision, agent, drift, knowledge) MUST map to exactly one `type` in the OPI→OKF vocabulary (§1.1). An entity with no mapped type is an export error.

**Rationale:** Guarantees the export is lossless and that every produced `.md` carries a valid `type` (OKF's only required field).

**Level:** ERROR

**Example:**

```
✓ PASS: unit "product" → type "Org Unit"
✗ FAIL: a future entity "circle" with no vocabulary entry → cannot determine type
```

---

#### Rule 73: Export Bundle Must Be OKF-Conformant

**Assertion:** A generated OKF export MUST be a conformant OKF v0.1 bundle: every non-reserved `.md` file has a parseable YAML frontmatter block with a non-empty `type`, and the bundle-root `index.md` declares `okf_version: "0.1"`. This includes auxiliary files: the exporter MUST NOT place frontmatter-less `.md` files (e.g. a `README.md`) into the bundle — OKF reserves only `index.md` and `log.md`, so every other `.md` is a concept document.

**Rationale:** The whole point of the export is consumption by any OKF reader. A non-conformant bundle defeats the feature — and the easiest way to produce one accidentally is a harmless-looking documentation file without `type` frontmatter.

**Level:** ERROR

**Example:**

```markdown
<!-- /units/product.md -->
---
type: Org Unit        # ✓ PASS: non-empty type present
title: Product Organization
---

<!-- ✗ FAIL: a .md file with no frontmatter, or with empty `type:` -->
```

---

#### Rule 74: Reserved Files Must Follow OKF Structure

**Assertion:** Generated `index.md` and `log.md` files MUST follow OKF structure: `index.md` is a sectioned bullet list (`* [Title](url) - description`) with frontmatter only at the bundle root (`okf_version`); `log.md` uses ISO 8601 `## YYYY-MM-DD` headings, newest first.

**Rationale:** Reserved files are how humans and agents navigate the bundle. Malformed reserved files break navigation.

**Level:** WARNING

---

#### Rule 75: Export Links Resolve Within the Bundle

**Assertion:** On export, every OPI reference that resolves internally (e.g. `decisions[].gremium`, `agents[].owner`, `knowledge_refs[]` that point at local concepts) SHOULD emit a bundle-relative link that targets an existing concept file.

**Rationale:** Note the asymmetry with Rule 83: OKF *consumers* must tolerate broken links, but an OPI *producer* should emit none. External `resource` URIs are legitimately outside the bundle and are not checked.

**Level:** WARNING

**Example:**

```
✓ PASS: decisions[].gremium "product-board" → /gremien/product-board.md (exists)
✗ WARN: decisions[].gremium "ghost-board" → /gremien/ghost-board.md (no such file)
```

---

### Rules 76–78: Knowledge Graph

#### Rule 76: `knowledge[].id` Unique and Required Fields Present

**Assertion:** Each `knowledge[]` entry MUST have a non-empty `id`, `type`, `title`, and `description`. All `id` values MUST be unique across `knowledge[]`.

**Rationale:** Knowledge concepts are referenced by `id` from `knowledge_refs[]`. Missing or duplicate IDs break the graph.

**Level:** ERROR

**Example:**

```yaml
knowledge:
  - id: jtbd-framework        # ✓ PASS
    type: Playbook
    title: "Jobs-to-Be-Done Framework"
    description: "Discovery methodology …"

  - id: jtbd-framework        # ✗ FAIL: duplicate id
    type: Reference
    title: "JTBD reading list"
    description: "…"
```

---

#### Rule 77: `knowledge_refs[]` Local References Must Resolve

**Assertion:** Each `knowledge_refs[]` entry that is a local ID or a bundle-relative path MUST reference an existing `knowledge[].id` (or a concept file produced on export). External URIs are not checked.

**Rationale:** A dangling local knowledge reference attaches no context and silently fails at runtime.

**Level:** WARNING

**Example:**

```yaml
knowledge:
  - id: jtbd-framework
    type: Playbook
    title: "JTBD"
    description: "…"

decisions:
  - id: dec-P001
    knowledge_refs:
      - jtbd-framework          # ✓ PASS: resolves
      - ghost-concept           # ✗ WARN: no such knowledge[].id
      - https://wiki/x          # (not checked — external URI)
```

---

#### Rule 78: Bidirectional Link Consistency

**Assertion:** If a structural entity X declares `knowledge_refs` including concept K, and K declares a non-empty `relates_to`, then K SHOULD include X in `relates_to` (and vice versa). Asymmetric links generate a warning, not an error.

**Rationale:** The structure↔knowledge graph is most useful when traversable from both ends. Tooling MAY auto-reconcile; until then, warn.

**Level:** WARNING

---

### Rules 79–81: Provenance (`log.md`)

#### Rule 79: `log.md` Format

**Assertion:** If a `log.md` is present or generated, entries MUST use ISO 8601 `## YYYY-MM-DD` date headings, ordered newest first.

**Rationale:** Consistent, sortable provenance is the basis for freshness checks and audit.

**Level:** WARNING

**Example:**

```markdown
## 2026-06-17     # ✓ PASS
* **Update**: …

## June 2026      # ✗ WARN: not ISO 8601
```

---

#### Rule 80: Provenance Freshness vs. `review_date`

**Assertion:** If a `decisions[].review_date` has passed and there is no `log.md` entry dated on or after that `review_date` referencing the decision, emit a freshness warning.

**Rationale:** A passed review with no recorded activity is the detectable signature of ontology drift — the model may no longer reflect reality. This is the spec's first executable drift early-warning.

**Level:** WARNING

**Example:**

```
dec-P001 review_date 2026-07-01 has passed; last log entry referencing dec-P001: 2026-03-05
⚠  dec-P001 may be stale — review recorded no outcome
```

---

#### Rule 81: Decision↔Log Consistency

**Assertion:** Every `decisions[]` entry with `status: active | revoked | superseded` SHOULD have a corresponding `log.md` entry dated on or after its `date`.

**Rationale:** Surfaces silent decision changes — a decision that flipped status without leaving a provenance trace.

**Level:** WARNING

---

### Rules 82–84: Permissive Consumer Model (consumer-side)

> These rules constrain **consumers/readers**, not the strict producer validator. `orgspec lint` (producer mode) still flags genuinely malformed structure.

#### Rule 82: Consumers Tolerate Unknown Fields

**Assertion:** A conformant OPI *consumer* MUST NOT reject a document for unknown top-level keys, unknown `x-*` fields, or unknown optional sections. It degrades gracefully (ignores or passes through).

**Rationale:** Forward compatibility: a v0.6 consumer must keep working against a v0.7 document.

**Level:** WARNING (consumer-side)

---

#### Rule 83: Consumers Tolerate Broken Links

**Assertion:** A conformant OPI consumer reading an exported OKF bundle MUST tolerate broken bundle-relative links (per OKF). Pairs with Rule 75 (producers SHOULD emit none).

**Rationale:** OKF's permissive consumption mandate; a missing target must not crash a reader or agent.

**Level:** WARNING (consumer-side)

---

#### Rule 84: Consumers Tolerate Higher-Minor Enum Values

**Assertion:** A v0.6 consumer encountering an unknown enum value (e.g. a future agent `type`, decision `status`, or knowledge `type`) from a higher minor version MUST treat it as opaque rather than reject the document.

**Rationale:** New enum values are backward-compatible additions; rejecting them would break forward compatibility.

**Level:** WARNING (consumer-side)

---

### Rules 85–86: OKF Import

#### Rule 85: Import Must Report Down-Mapped Documents

**Assertion:** On import, every OKF document whose `type` is not in the OPI→OKF vocabulary (§1.1), and which is therefore imported as a generic `knowledge[]` concept, MUST be reported in the import summary.

**Rationale:** Best-effort import is lossy for third-party bundles. Silent down-mapping hides what structure was *not* reconstructed.

**Level:** WARNING

---

#### Rule 86: Import Source Must Be OKF-Conformant

**Assertion:** `orgspec import --okf` MUST refuse a source directory that is not a conformant OKF v0.1 bundle (a non-reserved `.md` lacking parseable frontmatter or a non-empty `type`).

**Rationale:** Importing from a malformed bundle produces unreliable OPI documents.

**Level:** ERROR

---

## 7. Backward Compatibility

All v0.6 features are additive. No changes to existing fields or validation rules 1–71.

| Document | v0.6 Behavior |
|----------|---------------|
| v0.5 document (no `knowledge[]`) | Valid. `knowledge[]` and `knowledge_refs[]` are optional. Rules 76–78 do not apply. |
| v0.5 document (no `log.md`) | Valid. Provenance rules 79–81 apply only when a `log.md` exists or is generated. |
| v0.4 / v0.3 document | Valid. All v0.4/v0.5/v0.6 features are optional. |
| v0.2 / v0.1 document | Valid. Only schema version may generate a deprecation notice from tooling. |

Upgrading is incremental:
1. **No action required.** Existing documents are valid as-is.
2. **Optional: Run the OKF export** (`orgspec export --target okf`) to produce a portable bundle.
3. **Optional: Add `knowledge[]`** concepts and link them with `knowledge_refs[]`.
4. **Optional: Adopt `log.md`** for provenance and the freshness check.

---

## 8. CLI Integration (`orgspec`)

### New Commands (v0.6)

| Command | Description |
|---------|-------------|
| `orgspec export --target okf [--out ./bundle]` | Render the OPI document set as a conformant OKF v0.1 bundle (generates concept docs, `index.md`, `log.md`). |
| `orgspec export --target okf --entity decisions` | Export a single entity class. |
| `orgspec import --okf <dir>` | Import a conformant OKF bundle into OPI; reports typed vs. down-mapped documents (Rules 85–86). |
| `orgspec provenance [--check]` | Render/validate `log.md`; `--check` runs the freshness rule (Rule 80). |
| `orgspec lint` | Runs all validation rules, including v0.6 rules 72–86. |

### Example Output: `orgspec export --target okf`

```
Exporting OPI → OKF bundle (./okf-export) …

okf-export/
├── index.md            (okf_version: "0.1")
├── log.md
├── units/      product.md
├── roles/      product-lead.md
├── gremien/    product-board.md
├── decisions/  dec-P001.md, dec-P002.md
├── agents/     product-context-agent.md
└── knowledge/  jtbd-framework.md

✓  9 concept documents written, all carry a non-empty `type`  (Rule 73)
✓  index.md / log.md conform to OKF structure                 (Rule 74)
⚠  1 bundle-relative link unresolved: dec-P002 → /knowledge/ux-audit.md  (Rule 75)
✓  Bundle is conformant OKF v0.1
```

### Example Output: `orgspec provenance --check`

```
Provenance freshness check (as of 2026-06-17):

⚠  dec-P001 review_date 2026-07-01 has passed; no log.md entry since 2026-03-05  (Rule 80)
✓  All active decisions have a log entry on/after their date                    (Rule 81)
```

---

## 9. JSON Schema Additions (v0.6)

JSON Schema fragments follow the style of `opi-v0.4.schema.json` and build on the v0.5 `$defs`. The **OKF Export Profile and Import are tooling-conformance behaviors, not document fields** — they are described normatively in §1 and §3 and validated by `orgspec`, not by the document schema (parallel to v0.5's D7).

### Fragment: `knowledge[]`

```json
{
  "$defs": {
    "KnowledgeConcept": {
      "type": "object",
      "required": ["id", "type", "title", "description"],
      "properties": {
        "id": {
          "type": "string",
          "pattern": "^[a-z0-9][a-z0-9\\-]*$",
          "description": "Unique knowledge concept identifier"
        },
        "type": {
          "type": "string",
          "minLength": 1,
          "description": "Concept kind (free string; becomes OKF type on export)"
        },
        "title": { "type": "string", "minLength": 1 },
        "description": { "type": "string", "minLength": 1 },
        "resource": { "type": "string" },
        "tags": { "type": "array", "items": { "type": "string" }, "default": [] },
        "body": { "type": "string" },
        "relates_to": { "type": "array", "items": { "type": "string" }, "default": [] },
        "citations": { "type": "array", "items": { "type": "string" }, "default": [] },
        "timestamp": { "type": "string", "format": "date-time" }
      },
      "additionalProperties": {
        "description": "x-* extension fields permitted"
      }
    },
    "KnowledgeRef": {
      "type": "string",
      "description": "A local knowledge[].id, a bundle-relative path (/knowledge/<id>.md), or an external URI"
    }
  },
  "properties": {
    "knowledge": {
      "type": "array",
      "items": { "$ref": "#/$defs/KnowledgeConcept" },
      "description": "Top-level knowledge graph"
    }
  }
}
```

### Fragment: `knowledge_refs[]` on entities

```json
{
  "$defs": {
    "WithKnowledgeRefs": {
      "properties": {
        "knowledge_refs": {
          "type": "array",
          "items": { "$ref": "#/$defs/KnowledgeRef" },
          "description": "Links from a structural entity to knowledge concepts"
        }
      }
    }
  }
}
```

The `WithKnowledgeRefs` fragment is mixed into the Unit, Role, Gremium, Decision, and AgentInstance definitions via the `allOf` extension idiom used for `AgentInstanceV5` in v0.5.

---

## 10. Design Decisions

### D9: Export Is a Generated Projection, Not a Second Authoring Format

**Decision:** OPI stays the strict YAML + JSON Schema source of truth. The OKF bundle is a *generated projection*, and import is *lossless out, best-effort in*.

**Rationale:**
- Avoids the "sync/staleness tax": a bundle is a second copy of the truth and is wrong the moment the source changes. Treating it as generated output (a CI step) keeps one source of truth.
- Preserves validation — the strict rules apply to the OPI source, not to the permissive bundle.

**Tradeoff:** The export must be re-run on change. Mirrors v0.5's D7 ("running process / committed snapshot").

---

### D10: OPI Defines Its Own OPI→OKF Type Vocabulary

**Decision:** OPI ships a controlled `type` vocabulary (Org Unit / Role / Committee / Decision / Agent / Drift / Organization) rather than letting each producer choose freely.

**Rationale:** OKF has no type registry *by design*. OPI's whole value is typing. So OPI provides the registry OKF omits — that is the typed layer riding on the untyped substrate.

**Tradeoff:** A new OPI entity needs a vocabulary addition (a minor-version concern).

---

### D11: Strict Producer, Permissive Consumer

**Decision:** Adopt OKF's robustness mandate for *readers* only. `orgspec lint` (producer/writer mode) stays strict.

**Rationale:** Gets OKF's portability and forward compatibility without diluting the strictness that is the point of OPI. "Die Strenge ist der Punkt."

**Tradeoff:** Two behavioral modes to document and test (producer vs. consumer). Worth it: it is the only way to be both strict and interoperable.

---

### D12: `log.md` Is the Provenance/Maintenance Surface; Remediation Stays in Tooling

**Decision:** The spec defines the provenance *structure* (`log.md`) and a freshness *warning* (Rule 80). The active maintenance protocol — alerting, auto-remediation, a drift-repair agent — lives in tooling and v0.7.

**Rationale:** Consistent with v0.4's D3 ("minimal spec, powerful tooling"). The spec names the surface against ontology drift; it does not mandate a runtime.

**Tradeoff:** The spec answers the drift limit with a warning, not a cure. The cure is deferred but now has a defined home.

---

### D13: The Knowledge Layer Is First-Class but Additive

**Decision:** `knowledge[]` is a first-class top-level entity, but every document without it remains valid.

**Rationale:** The knowledge graph is a major capability (Verhelst L4), worth first-class modeling — but forcing it on existing documents would break the additive promise held since v0.4.

**Tradeoff:** Two valid shapes (with/without knowledge). Handled by making all knowledge rules conditional on presence.

---

## 11. Relationship Between v0.6 Features and Prior Features

### OKF Export ↔ Decision Graph (v0.5)

Each `decisions[]` entry exports to `/decisions/<id>.md` (`type: Decision`); its `triggers`, `consequences`, and `revises` become bundle-relative links between Decision docs — the decision graph rendered as an OKF subgraph an external agent can traverse.

### Knowledge Graph ↔ Agent Context API (v0.5)

An agent's `context_endpoint` payload (v0.5) MAY include the knowledge concepts referenced by in-scope decisions/units via `knowledge_refs[]` — so an agent receives not just *what was decided* but *what is known* about it.

### `log.md` ↔ Drift Detection (v0.4) and `review_date` (v0.5)

`log.md` is the chronological projection of `decisions[]` and `status.drift[]`. The freshness rule (Rule 80) joins `log.md` to the v0.5 `review_date`, turning two existing fields into an executable drift early-warning.

### Permissive Consumer Model ↔ the whole spec

The consumer rules (82–84) generalize the `additionalProperties: true` / `^x-` posture already present in the JSON Schema into a stated forward-compatibility contract for readers.

---

## 12. Complete Example: OPI Source → OKF Bundle

A product unit combining v0.6 features with prior capabilities:

```yaml
opi: "0.6.0"

unit:
  id: product
  name: "Product Organization"
  purpose: "Define product strategy, roadmap, and user success metrics"
  type: stream-aligned
  knowledge_refs:
    - jtbd-framework

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
      Customer research in Q4 2025 revealed feature requests were driven by job stories rather
      than preference surveys. JTBD provides a more stable basis for roadmap decisions.
    scope: "Product Organization, Design, User Research"
    review_date: 2026-07-01
    knowledge_refs:
      - jtbd-framework

knowledge:
  - id: jtbd-framework
    type: Playbook
    title: "Jobs-to-Be-Done Framework"
    description: "Discovery methodology framing demand as the jobs customers hire a product to do."
    tags: [discovery, product, methodology]
    relates_to:
      - product
      - dec-P001
    body: |
      # Examples
      A job story: *When [situation], I want to [motivation], so I can [outcome].*
    timestamp: 2026-06-10T12:00:00Z
```

### Generated OKF bundle

```
okf-export/
├── index.md
├── log.md
├── units/product.md
├── gremien/product-board.md
├── decisions/dec-P001.md
└── knowledge/jtbd-framework.md
```

**`okf-export/index.md`:**

```markdown
---
okf_version: "0.1"
---

# Organization: Product Organization

## Units
* [Product Organization](/units/product.md) - Define product strategy, roadmap, and user success metrics

## Committees
* [Product Board](/gremien/product-board.md) - Quarterly product direction and prioritization

## Decisions
* [Adopt Jobs-to-Be-Done framework …](/decisions/dec-P001.md) - active, product-board

## Knowledge
* [Jobs-to-Be-Done Framework](/knowledge/jtbd-framework.md) - Discovery methodology framing demand as jobs.
```

**`okf-export/knowledge/jtbd-framework.md`:**

```markdown
---
type: Playbook
title: Jobs-to-Be-Done Framework
description: Discovery methodology framing demand as the jobs customers hire a product to do.
tags: [discovery, product, methodology]
timestamp: 2026-06-10T12:00:00Z
x-opi-id: jtbd-framework
---

# Jobs-to-Be-Done Framework

Related to [Product Organization](/units/product.md) and the decision
[Adopt JTBD framework](/decisions/dec-P001.md).

# Examples
A job story: *When [situation], I want to [motivation], so I can [outcome].*
```

**`okf-export/log.md`:**

```markdown
# Update Log

## 2026-06-17
* **Creation**: Exported OPI document set to OKF bundle.
* **Creation**: Added knowledge concept jtbd-framework.

## 2026-01-20
* **Update**: dec-P001 enacted (JTBD adopted as 2026 discovery methodology).
```

---

## 13. File Organization (v0.6 extension)

```
org-repo/
├── org.yaml
├── components/
│   ├── roles.yaml
│   └── agents.yaml
├── decisions/
│   └── …                              # decision graph (v0.5)
├── knowledge/
│   └── concepts.yaml                  # (NEW) knowledge[] concepts (or inline in unit opi.yaml)
├── units/
│   └── product/opi.yaml               # unit with knowledge_refs[], decisions[], agents[]
├── log.md                             # (NEW) bundle-level provenance
├── okf-export/                        # (NEW, generated) conformant OKF bundle — `orgspec export --target okf`
│   ├── index.md
│   ├── log.md
│   └── …
└── docs/
    ├── examples/
    └── migration-v05-to-v06.md
```

**Note:** `knowledge[]` may live inline in unit `opi.yaml` files or in a shared `knowledge/` directory. The `okf-export/` directory is generated output and SHOULD be reproducible from the OPI source (it MAY be git-committed as a snapshot, per D9).

---

## 14. Security Considerations (Export) — Non-Normative

An OKF export is **plaintext Markdown**. Everything in the OPI source — names, rationales, drift notes, knowledge bodies — travels in the bundle. Before any bundle leaves the organization (shared, sold, handed over to a client, or published), a **PII / secret scan and provenance/signing gate** ("Privacy Shield") is required. This gate is outside OPI's normative scope; OPI's responsibility ends at producing a conformant, accurate bundle. Treat `okf-export/` as a publishable artifact and run the gate as a pre-share CI step.

---

## 15. Migration Guide v0.5 → v0.6

**No breaking changes.** All v0.5 documents are valid v0.6 documents.

Optional adoption steps:
1. **Export:** run `orgspec export --target okf` to produce a portable bundle from your existing OPI source. Nothing in the source changes.
2. **Knowledge:** add `knowledge[]` concepts and attach them with `knowledge_refs[]` on the entities they inform. Add `relates_to` back-links for two-way traversal.
3. **Provenance:** start (or generate) a `log.md`; run `orgspec provenance --check` to surface stale decisions (Rule 80).
4. **Consumers:** if you build readers/agents against OPI, adopt the permissive consumer rules (82–84) so they survive future minor versions.

---

## 16. Changelog

**v0.6.0 (2026-06-17) — OKF Interoperability & Knowledge Graph**

- **Added:** OKF Export Profile — lossless OPI → OKF v0.1 bundle (`orgspec export --target okf`); OPI→OKF type vocabulary (§1.1).
- **Added:** `knowledge[]` first-class entity + `knowledge_refs[]` / `relates_to[]` — the bidirectional Knowledge Graph (§2).
- **Added:** OKF Import (`orgspec import --okf`) — round-trip, lossless-out/best-effort-in (§3).
- **Added:** Native `log.md` provenance convention + freshness rule (§4).
- **Added:** Permissive Consumer Model — strict producer / tolerant consumer (§5).
- **Added:** Validation Rules 72–86 (Export 72–75, Knowledge 76–78, Provenance 79–81, Consumer 82–84, Import 85–86).
- **Added:** Design Decisions D9–D13.
- **Deferred → v0.7:** ODRL/SHACL Policy Rules & Guardrails (Verhelst L6); automated drift-remediation agent; export signing.
- **Compatibility:** Fully additive. v0.5, v0.4, v0.3 documents valid without modification.
