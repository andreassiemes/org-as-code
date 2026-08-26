"""Composite tools under ceiling `public` — the case no test covered.

Rule 95 / v0.7 §4.4 point 1 sends every tool result through `enforce_tier` on
the way out. `enforce_tier` classified *every* mapping it met, and §1.2's
default reads an absent `visibility` as `internal`. A composite's result
wrapper carries no `visibility`, because it is not an entity — so under a
`public` ceiling the wrapper itself was read as internal, redacted to the
fields of REDACTED_KEEP, and returned as `{}`.

That made every composite answer empty for a public caller, including
`get_undelivered_decisions`, whose own description in v0.8 §3.2 requires that
an empty answer never be readable as "nothing open". The two follow-on cases
are the same defect one level down: a sub-object of an answer (`coverage`,
`scope`) is no more an entity than the wrapper, and a projection that drops the
tier before the gate gets re-read as internal and stripped to a bare id.

The suites next to this one exercise the default ceiling (`internal`), where
none of it shows: an unmarked wrapper is exactly at the ceiling and passes.

Run:  python3 -m unittest discover tests
"""
import sys, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from orgspec.loader import load          # noqa: E402
from orgspec.tools import Catalog        # noqa: E402

DOC = """
opi: "0.8.0"
unit: {id: root, name: Root, visibility: public}
gremien:
  - {id: council, name: Council, purpose: "Pricing and access", visibility: public}
decisions:
  - id: dec-1
    visibility: public
    date: 2026-05-04
    title: "Pricing is usage-based"
    status: active
    gremium: council
    driver: lead
    approver: lead
    rationale: "pricing reason"
    enforcement: {status: pending, expected_by: 2026-06-01}
  - id: dec-2
    visibility: restricted
    classification_reason: "personnel"
    date: 2026-05-05
    title: "Restricted pricing decision"
    status: active
    gremium: council
    driver: lead
    approver: lead
    rationale: "pricing reason, restricted"
    enforcement: {status: pending, expected_by: 2026-06-01}
agents:
  - ref: public-agent
    visibility: public
    mandate_source: council
    scope: {units: [root], data: [tickets], note: "reads only"}
    escalation_path: [council]
  - ref: secret-agent
    visibility: restricted
    mandate_source: council
    scope: {units: [root], data: [payroll], note: "must not leak"}
    escalation_path: [council]
"""


def _catalog(tmp_path, ceiling):
    (tmp_path / "org.yaml").write_text(DOC, encoding="utf-8")
    return Catalog(load(tmp_path), ceiling=ceiling)


class PublicCeilingComposites(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._dir = tempfile.TemporaryDirectory()
        self.pub = _catalog(Path(self._dir.name), "public")
        self.int = _catalog(Path(self._dir.name), "internal")

    def tearDown(self):
        self._dir.cleanup()

    # --- the wrapper is not an entity ------------------------------------
    def test_composites_are_not_empty_at_public_ceiling(self):
        for name, args in (
            ("who_decides", {"topic": "pricing"}),
            ("get_decision_chain", {"id": "dec-1"}),
            ("get_undelivered_decisions", {"as_of": "2026-07-01"}),
            ("get_agent_mandate", {"ref": "public-agent"}),
        ):
            with self.subTest(tool=name):
                self.assertNotEqual(self.pub.call(name, args), {},
                                    f"{name} redacted its own result wrapper")

    def test_undelivered_keeps_its_required_keys(self):
        # v0.8 §3.2: the result MUST carry as_of, undelivered[] and coverage.
        got = self.pub.call("get_undelivered_decisions", {"as_of": "2026-07-01"})
        self.assertEqual({"as_of", "undelivered", "coverage"}, set(got) & {
            "as_of", "undelivered", "coverage"})
        self.assertEqual(got["as_of"], "2026-07-01")

    def test_coverage_sub_object_survives(self):
        # `coverage` is part of the answer, not an entity: it has no tier to fail.
        cov = self.pub.call("get_undelivered_decisions", {"as_of": "2026-07-01"})["coverage"]
        for key in ("active", "with_enforcement", "with_expected_by", "line"):
            self.assertIn(key, cov)

    def test_agent_scope_sub_object_survives(self):
        scope = self.pub.call("get_agent_mandate", {"ref": "public-agent"})["scope"]
        self.assertEqual(scope.get("data"), ["tickets"])

    def test_public_decision_keeps_its_enforcement_block(self):
        # Rule 103: nested objects travel with their record. A decision the
        # caller may read in full must not lose `enforcement` on the way out.
        got = self.pub.call("get_decision_by_id", {"id": "dec-1"})
        self.assertEqual(got["enforcement"]["status"], "pending")

    # --- and redaction still happens where it must -----------------------
    def test_restricted_decision_stays_a_card_inside_a_wrapper(self):
        nodes = self.pub.call("get_decision_chain", {"id": "dec-1"})["nodes"]
        by_id = {n.get("id"): n for n in nodes}
        if "dec-2" in by_id:
            self.assertNotIn("title", by_id["dec-2"])

    def test_restricted_decision_is_not_named_in_undelivered(self):
        hits = self.pub.call("get_undelivered_decisions", {"as_of": "2026-07-01"})["undelivered"]
        self.assertNotIn("dec-2", [h.get("id") for h in hits if h.get("title")])

    def test_public_overdue_decision_is_named_not_anonymised(self):
        # The projection carries its tier, so the gate re-reads it as public.
        hits = {h.get("id"): h for h in
                self.pub.call("get_undelivered_decisions", {"as_of": "2026-07-01"})["undelivered"]}
        self.assertIn("dec-1", hits)
        self.assertEqual(hits["dec-1"]["title"], "Pricing is usage-based")
        self.assertEqual(hits["dec-1"]["overdue_days"], 30)

    def test_restricted_agent_mandate_is_a_card_not_a_mandate(self):
        got = self.pub.call("get_agent_mandate", {"ref": "secret-agent"})
        self.assertNotIn("scope", got)
        self.assertEqual(got.get("ref"), "secret-agent")

    def test_restricted_agent_mandate_is_served_at_its_own_ceiling(self):
        got = self.int.call("get_agent_mandate", {"ref": "secret-agent"})
        self.assertNotIn("scope", got, "restricted must not open at internal")
        got_r = _catalog(Path(self._dir.name), "restricted").call(
            "get_agent_mandate", {"ref": "secret-agent"})
        self.assertEqual(got_r["scope"]["data"], ["payroll"])

    def test_who_decides_does_not_name_a_restricted_precedent(self):
        got = self.pub.call("who_decides", {"topic": "pricing"})
        named = [p.get("title") for p in got["precedents"] if p.get("title")]
        self.assertIn("Pricing is usage-based", named)
        self.assertNotIn("Restricted pricing decision", named)


if __name__ == "__main__":
    unittest.main()
