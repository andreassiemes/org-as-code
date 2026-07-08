# Pilot Starter Kit

**For leaders who want to run their first Org-as-Code pilot — no terminal required.**

Everything here works from the GitHub web interface (plus your AI assistant for drafting).
You will put ONE pilot area of your organization under version control, get every change
reviewed like code, and build a decision log as a by-product.

What's in this folder:

| File | What it is |
|------|------------|
| [`org.yaml`](org.yaml) | A complete, validated skeleton of a fictional product organization — copy and adapt |
| [`templates/`](templates/) | Copy-paste blocks for a new role, team, or decision |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | The 6-step change flow for non-technical contributors |
| [`invalid-example.yaml`](invalid-example.yaml) | A deliberately broken file — see what a red check looks like before your first real one |

## The 5-step path

### Step 0 — Repo foundation (30 minutes, once)

1. Create a **private** GitHub repository, e.g. `our-org`.
2. Upload `org.yaml` (adapted), `tools/validate.py`, and `.github/workflows/validate.yml`
   from this project (the workflow file explains its own adaptation in comments).
3. Add a `CODEOWNERS` file at the repo root — it decides who must approve changes:
   ```
   # Every change to the org model needs the org owner's approval
   org.yaml @your-github-handle
   ```
4. Protect the main branch: *Settings → Branches → Add branch ruleset* →
   require a pull request before merging, require the **Validate OPI documents**
   status check, require review from Code Owners.

Result: nobody — including you — can change the org model without a reviewed,
validated pull request. That is the whole trick.

### Step 1 — Structure as Code (your first afternoon)

Model **one pilot area only**. Not the whole company. One tribe, its teams, its roles.

- Open `org.yaml`, replace the fictional names (Checkout Tribe, Team Payments, …)
  with your pilot area. Every section has a comment saying what it is.
- Work **role-based, never person-based**: write `product-manager`, not a name.
  - **Compliance note:** person names in an org repo are personal data (GDPR).
    Keep the person→role mapping in your HR system, not in Git. This also keeps
    the model stable — people change, roles don't.
- Use `templates/role.template.yaml` and `templates/team.template.yaml` for new entries.

### Step 2 — Validation via Action

The GitHub Action runs automatically on every pull request. Green check = the model
is structurally sound (required fields, valid IDs, no dangling references). Red check =
the PR tells you exactly what and where — see [CONTRIBUTING.md](CONTRIBUTING.md)
for what to do then. Try it once on purpose: `invalid-example.yaml` shows the failure modes.

### Step 3 — Render & views

A YAML file convinces you; a picture convinces your leadership team. Ask your AI
assistant to generate views from `org.yaml` — an org chart (Mermaid or SVG), a role
catalog as a table, a decision-log page. Keep generated views in a `views/` folder
and regenerate them on change; the YAML stays the single source of truth.

### Step 4 — Decision Records

From now on, every decision your council makes becomes an entry in `decisions:` —
use `templates/decision.template.yaml`, one PR per decision. The log is append-only:
never rewrite a past decision; supersede it. After three months you have something
almost no organization has: a searchable, reasoned history of why things are the way they are.

### Step 5 — Drift & scaling

- **Drift:** once a quarter, compare the model against reality (staffing, cadences,
  mandates). Record deviations in the `status.drift` section instead of silently
  editing the target model — drift made visible is drift you can manage.
- **Scaling:** when the pilot holds, onboard the next area — new file, same role
  catalog, same workflow. Graduate teams that develop their own governance into
  their own files. The pilot's PR discipline scales; a big-bang rollout does not.

## Validate locally (optional, for the technically inclined)

```bash
pip install pyyaml jsonschema
python3 tools/validate.py examples/pilot-starter/org.yaml
```
