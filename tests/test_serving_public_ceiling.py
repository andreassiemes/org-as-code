"""Composite tools under ceiling `public` — the case no test covered.

Rule 95 / v0.7 §4.4 point 1 sends every tool result through `enforce_tier` on
the way out. `enforce_tier` classified *every* mapping it met, and §1.2's
default reads an absent `visibility` as `internal`. A composite's result
wrapper carries no `visibility`, because it is not an entity — so under a
`public` ceiling the wrapper itself was read as internal, redacted to the
fields of REDACTED_KEEP, and returned as `{}`.

Two further cases are the same defect one level down and one level up:

  * A sub-object of an answer (`scope`) is no more an entity than the wrapper
    around it, and was stripped out of a record the caller may read in full.
  * `get_agent_mandate` built its answer from an agent's fields without ever
    checking that agent's own tier — so a `restricted` agent's mandate,
    including its `scope`, was served to any ceiling. This is the serious one:
    it is a disclosure, not an empty answer.

The suites next to this one exercise the default ceiling (`internal`), where
none of it shows: an unmarked wrapper is exactly at the ceiling and passes.

Run:  python3 -m unittest discover tests
"""
import sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from orgspec.loader import load          # noqa: E402
from orgspec.tools import Catalog        # noqa: E402

DOC = """
opi: "0.7.0"
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
            ("get_agent_mandate", {"ref": "public-agent"}),
        ):
            with self.subTest(tool=name):
                self.assertNotEqual(
                    self.pub.call(name, args), {},
                    f"{name} returned an empty wrapper at ceiling public")

    def test_chain_keeps_its_required_keys(self):
        got = self.pub.call("get_decision_chain", {"id": "dec-1"})
        for key in ("root", "nodes", "edges"):
            self.assertIn(key, got)

    # --- a sub-object travels with its record ----------------------------
    def test_agent_scope_sub_object_survives(self):
        got = self.pub.call("get_agent_mandate", {"ref": "public-agent"})
        self.assertEqual(got.get("scope", {}).get("data"), ["tickets"])

    # --- what is above the ceiling stays above it ------------------------
    def test_restricted_decision_stays_a_card_inside_a_wrapper(self):
        got = self.pub.call("who_decides", {"topic": "pricing"})
        for p in got.get("precedents", []):
            if p.get("id") == "dec-2":
                self.assertNotIn("title", p)
                self.assertIn("id", p)

    def test_who_decides_does_not_name_a_restricted_precedent(self):
        got = self.pub.call("who_decides", {"topic": "pricing"})
        self.assertNotIn("Restricted pricing decision", str(got))

    # --- the disclosure: an agent mandate ignored its own tier -----------
    def test_restricted_agent_mandate_is_a_card_not_a_mandate(self):
        got = self.pub.call("get_agent_mandate", {"ref": "secret-agent"})
        self.assertNotIn("scope", got,
                         "restricted agent's scope served to a public caller")
        self.assertNotIn("payroll", str(got))
        self.assertIn("ref", got, "existence should stay visible as a card")

    def test_restricted_agent_mandate_is_served_at_its_own_ceiling(self):
        got = _catalog(Path(self._dir.name), "restricted").call(
            "get_agent_mandate", {"ref": "secret-agent"})
        self.assertEqual(got.get("scope", {}).get("data"), ["payroll"])

    def test_internal_ceiling_still_withholds_the_restricted_mandate(self):
        got = self.int.call("get_agent_mandate", {"ref": "secret-agent"})
        self.assertNotIn("payroll", str(got))


if __name__ == "__main__":
    unittest.main()
