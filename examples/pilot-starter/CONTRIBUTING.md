# Changing the org model — the 6-step flow

You don't need Git knowledge or a terminal. Everything below happens in the
GitHub web interface. A change takes 5–10 minutes; the review protects you.

## The 6 steps

1. **Open the file.** In GitHub, navigate to `org.yaml` (or the file you want
   to change) and click the **pencil icon** (top right of the file view).

2. **Make your edit.** Add a team, change a mandate, append a decision. Use the
   blocks in [`templates/`](templates/) — copy, paste, replace the `<placeholders>`.
   Tip: draft the block with your AI assistant, paste the result here.

3. **Describe the change.** Click **Commit changes…** and write one honest
   sentence: *"Add Team Onboarding to Checkout Tribe (council decision of 2026-07-01)"*.
   Choose **Create a new branch and start a pull request** — never commit
   directly to main (branch protection will refuse anyway).

4. **Open the pull request.** In the PR description, add the *why*: what problem
   does this change solve, who was involved in deciding it.

5. **Wait for the check.** Within a minute, **Validate OPI documents** turns
   green ✓ or red ✗ at the bottom of the PR. Green: continue. Red: see below.

6. **Review by the owner.** The code owner (see `CODEOWNERS`) gets a review
   request automatically. Once they approve, click **Merge**. The change is now
   the official org model — versioned, reviewed, and traceable.

## What if the check is red?

Red is not broken — red is the system doing its job before a broken model reaches main.

1. On the PR page, click **Details** next to the failed check.
2. Find the lines starting with **✗** — each one names the problem and usually
   the line number, e.g.:
   ```
   ✗ decisions[0] 'dec-003': gremium 'portfolio-board' not found in gremien[] (line 33)
   ```
3. Fix it in the same PR: go to the **Files changed** tab → pencil icon → edit →
   commit to the **same branch**. The check re-runs automatically.
4. Stuck? Paste the ✗ lines to your AI assistant together with your edit and ask
   what to fix — or comment on the PR and tag the code owner.

The most common failures, in order:

| ✗ message says… | You probably… |
|---|---|
| `does not match ^[a-z0-9][a-z0-9-]*$` | used uppercase, spaces, or `_` in an `id` — use lowercase and hyphens |
| `role_ref '…' not defined in components.roles` | referenced a role before adding it to the role catalog |
| `gremium '…' not found in gremien[]` | typo'd the committee id in a decision |
| `missing required field(s) …` | deleted or forgot a mandatory line — compare with the template |

Want to see a red check safely? [`invalid-example.yaml`](invalid-example.yaml)
contains nine deliberate bugs with the matching ✗ output explained in comments.
