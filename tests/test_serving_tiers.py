"""Rule 95 / v0.7 §4.4 point 1: every tool result is tier-enforced on the way out.

Regression for v0.7.2: composite projections dropped `visibility` before
enforce_tier ran, so a restricted decision reached by traversal or text match
was served in full under ceiling `internal`.

Run:  python3 -m unittest discover tests
"""
import sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from orgspec.loader import load
from orgspec.tools import Catalog

DOC = """
opi: "0.7.0"
unit: {id: root, name: Root}
gremien:
  - {id: council, name: Council, purpose: "Restricted topics and more"}
decisions:
  - id: dec-1
    date: 2026-05-04
    title: "Visible decision"
    status: active
    gremium: council
    driver: lead
    approver: lead
    rationale: "reason"
    supersedes: [dec-4]
  - id: dec-4
    date: 2026-06-01
    title: "Restricted merger decision"
    status: active
    visibility: restricted
    classification_reason: "personnel"
    gremium: council
    driver: lead
    approver: lead
    rationale: "reason"
"""


def catalog(ceiling):
    tmp = Path(tempfile.mkdtemp())
    (tmp / "org.yaml").write_text(DOC, encoding="utf-8")
    return Catalog(load(tmp), ceiling=ceiling)


class CompositesRedactAboveCeiling(unittest.TestCase):
    def test_chain_serves_card_for_restricted_node(self):
        chain = catalog("internal").call("get_decision_chain", {"id": "dec-1"})
        node = next(n for n in chain["nodes"] if n["id"] == "dec-4")
        self.assertNotIn("title", node)
        self.assertEqual(node.get("visibility"), "restricted")

    def test_who_decides_precedent_is_redacted(self):
        who = catalog("internal").call("who_decides", {"topic": "Restricted"})
        self.assertTrue(all("title" not in p for p in who["precedents"]), who)

    def test_higher_ceiling_sees_content(self):
        chain = catalog("restricted").call("get_decision_chain", {"id": "dec-1"})
        self.assertIn("title", next(n for n in chain["nodes"] if n["id"] == "dec-4"))

    def test_by_id_unchanged(self):
        card = catalog("internal").call("get_decision_by_id", {"id": "dec-4"})
        self.assertEqual(set(card), {"id", "date", "visibility"})


if __name__ == "__main__":
    unittest.main()
