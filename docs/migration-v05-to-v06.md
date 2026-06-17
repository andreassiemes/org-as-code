# Migration Guide: OPI v0.5 → v0.6

> OKF Interoperability & the Knowledge Graph
> See also: [OPI Spec v0.6](../spec/opi-v0.6.md)

**No breaking changes — all v0.5 documents are valid v0.6 documents.**

No existing field, enum, or validation rule (1–71) changed. `knowledge[]`, `knowledge_refs[]`, `log.md`, and the OKF export/import are all additive and optional. Bump `opi:` to `"0.6.0"` when you start using a v0.6 feature; otherwise nothing is required.

The four adoption steps below are independent — adopt any subset, in any order.

---

## 1. Export — produce a portable OKF bundle

Render your existing OPI document set as a conformant [OKF v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog) bundle. Nothing in the source changes; the bundle is a generated projection (Design Decision D9), so re-run it on change (ideally as a CI step).

```bash
orgspec export --target okf --out ./okf-export
```

The result is consumable by any OKF reader — no OPI tooling required. Treat `okf-export/` as generated output; commit it as a snapshot only if you want a frozen artifact.

> **Before sharing a bundle externally:** an export is plaintext Markdown carrying everything in the source (names, rationales, drift notes). Run a PII/secret scan ("Privacy Shield") as a pre-share gate — see spec §14.

---

## 2. Knowledge — add the Knowledge Graph

Add `knowledge[]` concepts and link them to the structure they inform via `knowledge_refs[]`. Add `relates_to` back-links for two-way traversal (Rule 78).

```yaml
opi: "0.6.0"

knowledge:
  - id: jtbd-framework
    type: Playbook
    title: "Jobs-to-Be-Done Framework"
    description: "Discovery methodology framing demand as the jobs customers hire a product to do."
    relates_to: [product, dec-P001]   # knowledge → structure

decisions:
  - id: dec-P001
    # … existing v0.5 fields …
    knowledge_refs: [jtbd-framework]   # structure → knowledge
```

`knowledge[]` may live inline in a unit's `opi.yaml` or in a shared `knowledge/` directory.

---

## 3. Provenance — adopt `log.md` and the freshness check

Start (or generate) a `log.md` — OKF's chronological provenance surface, newest first, with ISO 8601 date headings. It is the projection of your `decisions[]` and `status.drift[]`, so there is no new authoring burden.

```markdown
# Update Log

## 2026-06-17
* **Update**: dec-P001 review completed; JTBD retained for 2026-H2.
```

Then surface stale decisions — a passed `review_date` with no later log entry referencing it (Rule 80):

```bash
orgspec provenance --check
# ⚠  dec-P001 review_date 2026-07-01 has passed; no log.md entry since 2026-03-05  (Rule 80)
```

---

## 4. Consumers — adopt the permissive consumer model

If you build readers or agents against OPI, make them tolerant so they survive future minor versions (Rules 82–84). Your producer/validator stays strict — `orgspec lint` still fails CI on genuinely malformed structure.

Consumers MUST NOT reject a document for:

- unknown top-level keys or `x-*` extension fields,
- unknown enum values from a higher minor version (treat as opaque),
- broken bundle-relative links,
- missing optional sections or reserved files.

```bash
orgspec lint   # producer mode: strict, all rules 1–86 apply
```

---

## Round-trip (optional)

To ingest an existing OKF bundle back into OPI:

```bash
orgspec import --okf ./some-okf-bundle
```

Import is **lossless out, best-effort in**: bundles produced by OPI export (carrying `x-opi-*` frontmatter) round-trip exactly; third-party bundles map recognized types to typed entities and down-map the rest to `knowledge[]` concepts — every down-mapped document is reported (Rule 85). A non-conformant source is refused (Rule 86).
