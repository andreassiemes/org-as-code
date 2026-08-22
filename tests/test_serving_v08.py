"""Serving-side tests for v0.8 (spec/opi-v0.8.md §3, Rule 103).

The first serving-side test in the project. Needs no HTTP harness: the catalog is
built in process and inspected like a `tools/list` call would see it.

Run:  python3 -m unittest discover tests
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import yaml  # noqa: F401
    HAVE_YAML = True
except ImportError:  # pragma: no cover
    HAVE_YAML = False

if HAVE_YAML:
    from orgspec.loader import load
    from orgspec.tools import Catalog

SERVE_DEMO = REPO / "examples" / "serve-demo"

MINIMAL = """
opi: "0.8.0"
unit: {id: root, name: Root}
gremien:
  - {id: council, name: Council}
decisions:
  - id: dec-1
    date: 2026-05-04
    title: "Decided and carried"
    status: active
    gremium: council
    driver: lead
    approver: lead
    rationale: r
    {SCOPE}
    enforcement: {status: in_effect, first_effect_at: 2026-05-20, ref: "pr:1"}
    approval:
      quorum: 1
      records: [{by: lead, at: 2026-05-04, ref: "minutes:1"}]
  - id: dec-2
    date: 2026-06-01
    title: "Decided, never carried"
    status: active
    gremium: council
    driver: lead
    approver: lead
    rationale: r
    enforcement: {status: pending, expected_by: 2026-07-01}
  - id: dec-3
    date: 2026-06-01
    title: "Decided, carried late but in time"
    status: active
    gremium: council
    driver: lead
    approver: lead
    rationale: r
    enforcement: {status: pending, expected_by: 2026-12-31}
  - id: dec-4
    date: 2026-06-01
    title: "Restricted and overdue"
    status: active
    visibility: restricted
    classification_reason: "personnel"
    gremium: council
    driver: lead
    approver: lead
    rationale: r
    enforcement: {status: pending, expected_by: 2026-07-01}
"""


def catalog(text: str, ceiling: str = "internal") -> "Catalog":
    tmp = Path(tempfile.mkdtemp())
    (tmp / "org.yaml").write_text(text, encoding="utf-8")
    return Catalog(load(tmp), ceiling=ceiling)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class Rule103(unittest.TestCase):
    def test_instance_bound_varied_field(self):
        # `scope` is whitelisted; it must produce a tool only when some record carries it
        with_scope = catalog(MINIMAL.replace("{SCOPE}", "scope: unit"))
        without = catalog(MINIMAL.replace("{SCOPE}", ""))
        self.assertIn("filter_decisions_by_scope", with_scope.tools)
        self.assertNotIn("filter_decisions_by_scope", without.tools)

    def test_nesting_bound_no_tools_from_v08_blocks(self):
        names = set(catalog(MINIMAL.replace("{SCOPE}", "")).tools)
        for forbidden in ("enforcement", "approval", "records", "first_effect_at",
                          "expected_by", "quorum"):
            self.assertFalse(any(forbidden in n for n in names), sorted(names))

    def test_v08_costs_exactly_one_catalog_entry_on_serve_demo(self):
        c = Catalog(load(SERVE_DEMO))
        self.assertIn("get_undelivered_decisions", c.tools)
        # 22 tools measured on the v0.7 document set (spec §3.1) plus the one composite
        self.assertEqual(len(c.tools), 23, sorted(c.tools))


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class UndeliveredDecisions(unittest.TestCase):
    def test_as_of_is_optional_in_input_schema(self):
        c = catalog(MINIMAL.replace("{SCOPE}", ""))
        schema = c.tools["get_undelivered_decisions"]["inputSchema"]
        self.assertEqual(schema["required"], [])
        self.assertIn("as_of", schema["properties"])

    def test_hits_and_coverage(self):
        c = catalog(MINIMAL.replace("{SCOPE}", ""))
        out = c.call("get_undelivered_decisions", {"as_of": "2026-08-22"})
        self.assertEqual([h["id"] for h in out["undelivered"]], ["dec-2"])
        self.assertEqual(out["undelivered"][0]["overdue_days"], 52)
        cov = out["coverage"]
        self.assertEqual((cov["active"], cov["with_enforcement"], cov["with_expected_by"]),
                         (3, 3, 2))  # dec-4 is restricted: invisible at ceiling internal
        self.assertIn("3 of 3 active decisions carry an enforcement block", cov["line"])

    def test_coverage_is_bounded_by_the_key(self):
        # a higher ceiling sees the restricted record in both the hits and the counts
        c = catalog(MINIMAL.replace("{SCOPE}", ""), ceiling="restricted")
        out = c.call("get_undelivered_decisions", {"as_of": "2026-08-22"})
        self.assertEqual([h["id"] for h in out["undelivered"]], ["dec-2", "dec-4"])
        self.assertEqual(out["coverage"]["active"], 4)

    def test_empty_answer_still_carries_coverage(self):
        c = catalog(MINIMAL.replace("{SCOPE}", ""))
        out = c.call("get_undelivered_decisions", {"as_of": "2026-06-15"})
        self.assertEqual(out["undelivered"], [])
        self.assertEqual(out["coverage"]["with_enforcement"], 3)

    def test_composites_redact_above_ceiling(self):
        # v0.7 §4.4 point 1 / Rule 95: every tool result is tier-enforced on the way
        # out. Before the fix, _slim() and the who_decides projection dropped
        # `visibility`, so a restricted decision reached by traversal or text match
        # was served in full under ceiling `internal`.
        text = MINIMAL.replace("{SCOPE}", "").replace(
            'title: "Decided and carried"', 'title: "Decided and carried"\n    supersedes: [dec-4]')
        c = catalog(text)
        chain = c.call("get_decision_chain", {"id": "dec-1"})
        node = next(n for n in chain["nodes"] if n["id"] == "dec-4")
        self.assertNotIn("title", node)          # redacted card: id, date, visibility
        self.assertEqual(node.get("visibility"), "restricted")
        who = c.call("who_decides", {"topic": "Restricted"})
        self.assertTrue(all("title" not in p for p in who["precedents"]), who)
        # a higher ceiling sees it in full
        full = catalog(text, ceiling="restricted").call("get_decision_chain", {"id": "dec-1"})
        self.assertIn("title", next(n for n in full["nodes"] if n["id"] == "dec-4"))

    def test_bad_as_of(self):
        c = catalog(MINIMAL.replace("{SCOPE}", ""))
        self.assertIn("error", c.call("get_undelivered_decisions", {"as_of": "next week"}))


if __name__ == "__main__":
    unittest.main()
