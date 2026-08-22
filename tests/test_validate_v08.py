"""Fixture runner for v0.8 (spec/opi-v0.8.md §7 "Fixtures that must exist").

Every fixture asserts one of four outcomes — ERROR, WARNING-only, silent, or note —
because four of the expected outcomes are *silence*, which an exit code cannot see.

Run:  python3 -m unittest discover tests
"""

from __future__ import annotations

import datetime
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_spec = importlib.util.spec_from_file_location("validate", REPO / "tools" / "validate.py")
validate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate)

try:
    import jsonschema  # noqa: F401
    HAVE_JSONSCHEMA = True
except ImportError:  # pragma: no cover
    HAVE_JSONSCHEMA = False

AS_OF = datetime.date(2026, 8, 22)

BASE = {
    "opi": "0.8.0",
    "unit": {"id": "root", "name": "Root"},
    "components": {"roles": {
        "tech-lead": {"title": "Tech Lead", "purpose": "p", "accountabilities": ["a"]},
        "coo": {"title": "COO", "purpose": "p", "accountabilities": ["a"]},
        "ceo": {"title": "CEO", "purpose": "p", "accountabilities": ["a"]},
    }},
    "gremien": [{"id": "council", "name": "Council", "members": ["tech-lead", "coo"]}],
}


def decision(**over) -> dict:
    d = {"id": "dec-1", "date": "2026-05-04", "title": "A fixture decision", "status": "active",
         "gremium": "council", "driver": "tech-lead", "approver": "tech-lead",
         "rationale": "A fixture rationale long enough for the schema"}
    d.update(over)
    return d


def run(decisions: list[dict], opi: str = "0.8.0", extra: dict | None = None,
        as_of: datetime.date = AS_OF) -> validate.Report:
    doc = json.loads(json.dumps(BASE))
    doc["opi"] = opi
    doc["decisions"] = decisions
    if extra:
        doc.update(extra)
    report = validate.Report(Path("<fixture>"))
    validate.check_structure(report, doc, as_of=as_of)
    return report


class Outcome(unittest.TestCase):
    """Four outcomes, one assertion helper each."""

    def assertError(self, r: validate.Report, needle: str = ""):
        self.assertGreater(r.failed, 0, "\n".join(r.lines))
        if needle:
            self.assertTrue(any(needle in l for l in r.lines if l.startswith("  ✗")),
                            "\n".join(r.lines))

    def assertWarningOnly(self, r: validate.Report, needle: str = ""):
        self.assertEqual(r.failed, 0, "\n".join(r.lines))
        self.assertGreater(r.warned, 0, "\n".join(r.lines))
        if needle:
            self.assertTrue(any(needle in l for l in r.lines if l.startswith("  ⚠")),
                            "\n".join(r.lines))

    def assertSilent(self, r: validate.Report, rule: str):
        self.assertEqual(r.failed, 0, "\n".join(r.lines))
        self.assertEqual(r.warned, 0, "\n".join(r.lines))
        self.assertFalse(any(rule in l for l in r.lines if not l.startswith("  ·")),
                         "\n".join(r.lines))

    def assertNote(self, r: validate.Report, needle: str):
        self.assertTrue(any(needle in l for l in r.lines if l.startswith("  ·")),
                        "\n".join(r.lines))


class Rule101(Outcome):
    def test_bogus_status(self):
        self.assertError(run([decision(enforcement={"status": "bogus"})]), "Rule 101")

    def test_empty_block(self):
        self.assertError(run([decision(enforcement={})]), "without status")

    def test_in_effect_without_first_effect_at(self):
        self.assertError(run([decision(enforcement={"status": "in_effect", "ref": "pr:1"})]),
                         "requires first_effect_at")

    def test_lapsed_without_first_effect_at(self):
        self.assertError(run([decision(enforcement={"status": "lapsed", "lapsed_at": "2026-06-01",
                                                    "ref": "pr:1"})]), "requires first_effect_at")

    def test_lapsed_without_lapsed_at(self):
        self.assertError(run([decision(enforcement={"status": "lapsed",
                                                    "first_effect_at": "2026-06-01",
                                                    "ref": "pr:1"})]), "requires lapsed_at")

    def test_in_effect_with_lapsed_at(self):
        self.assertError(run([decision(enforcement={"status": "in_effect",
                                                    "first_effect_at": "2026-06-01",
                                                    "lapsed_at": "2026-07-01",
                                                    "ref": "pr:1"})]), "must not carry lapsed_at")

    def test_lapsed_at_before_first_effect_at(self):
        self.assertError(run([decision(enforcement={"status": "lapsed",
                                                    "first_effect_at": "2026-06-01",
                                                    "lapsed_at": "2026-05-01",
                                                    "ref": "pr:1"})]), "precedes first_effect_at")

    def test_first_effect_at_before_decision_date(self):
        self.assertError(run([decision(enforcement={"status": "in_effect",
                                                    "first_effect_at": "2026-05-01",
                                                    "ref": "pr:1"})]), "precedes the decision date")

    def test_pending_with_first_effect_at(self):
        self.assertError(run([decision(enforcement={"status": "pending",
                                                    "first_effect_at": "2026-06-01"})]),
                         "pending must not carry")

    def test_in_effect_without_ref_is_warning_only(self):
        self.assertWarningOnly(run([decision(enforcement={"status": "in_effect",
                                                          "first_effect_at": "2026-06-01"})]),
                               "without ref")

    def test_overdue_pending_on_active(self):
        self.assertWarningOnly(run([decision(enforcement={"status": "pending",
                                                          "expected_by": "2026-06-30"})]),
                               "expected by 2026-06-30")

    def test_expected_by_on_the_as_of_day_is_silent(self):
        # the overdue boundary is strict: expected_by == as-of raises nothing
        self.assertSilent(run([decision(enforcement={"status": "pending",
                                                     "expected_by": AS_OF.isoformat()})]), "Rule 101")

    def test_future_expected_by_is_silent(self):
        self.assertSilent(run([decision(enforcement={"status": "pending",
                                                     "expected_by": "2027-01-01"})]), "Rule 101")

    def test_no_expected_by_and_stale_review_date_is_silent(self):
        # guards the removed review_date fallback
        self.assertSilent(run([decision(review_date="2026-01-01",
                                        enforcement={"status": "pending"})]), "Rule 101")

    def test_hypothesis_overdue_is_silent(self):
        self.assertSilent(run([decision(status="hypothesis", validate="v", validate_by="2026-12-31",
                                        enforcement={"status": "pending",
                                                     "expected_by": "2026-06-30"})]), "Rule 101")

    def test_superseded_in_effect_is_silent(self):
        self.assertSilent(run([decision(status="superseded",
                                        enforcement={"status": "in_effect",
                                                     "first_effect_at": "2026-06-01",
                                                     "ref": "pr:1"})]), "Rule 101")

    def test_absent_block_is_never_flagged(self):
        self.assertSilent(run([decision()]), "Rule 101")

    def test_dates_may_arrive_as_date_objects(self):
        # PyYAML parses unquoted dates to datetime.date — mixed types must compare
        r = run([decision(date=datetime.date(2026, 5, 4),
                          enforcement={"status": "lapsed",
                                       "first_effect_at": "2026-06-01",
                                       "lapsed_at": datetime.date(2026, 7, 1),
                                       "ref": "pr:1"})])
        self.assertEqual(r.failed, 0, "\n".join(r.lines))


class Rule102(Outcome):
    def records(self, *by, ref="minutes:1"):
        return [{"by": b, "at": "2026-05-04", "ref": ref} for b in by]

    def test_quorum_without_records_is_warning(self):
        self.assertWarningOnly(run([decision(approval={"quorum": 3})]), "no consents recorded")

    def test_quorum_invalid(self):
        self.assertError(run([decision(approval={"quorum": 0})]), "integer >= 1")
        self.assertError(run([decision(approval={"records": []})]), "integer >= 1")

    def test_shortfall_on_active_is_error(self):
        self.assertError(run([decision(approval={"quorum": 3,
                                                 "records": self.records("tech-lead", "coo")})]),
                         "quorum 3 declared, 2 distinct")

    def test_shortfall_on_planned_is_warning(self):
        self.assertWarningOnly(run([decision(status="planned",
                                             approval={"quorum": 3,
                                                       "records": self.records("tech-lead", "coo")})]),
                               "quorum 3 declared, 2 distinct")

    def test_shortfall_on_revoked_is_silent(self):
        self.assertSilent(run([decision(status="revoked",
                                        approval={"quorum": 3,
                                                  "records": self.records("tech-lead")})]),
                          "Rule 102")

    def test_distinct_counting(self):
        self.assertError(run([decision(approval={"quorum": 2,
                                                 "records": self.records("tech-lead", "tech-lead")})]),
                         "1 distinct")

    def test_consent_outside_declared_membership(self):
        self.assertWarningOnly(run([decision(approval={"quorum": 1,
                                                       "records": self.records("ceo")})]),
                               "outside the declared membership")

    def test_no_members_declared_is_silent(self):
        extra = {"gremien": [{"id": "council", "name": "Council"}]}
        self.assertSilent(run([decision(approval={"quorum": 1,
                                                  "records": self.records("ceo")})], extra=extra),
                          "Rule 102")

    def test_person_names_in_members_is_silent(self):
        # form mismatch: members[] holds unresolvable person names -> no comparison
        extra = {"gremien": [{"id": "council", "name": "Council",
                              "members": ["Alice Example", "Bob Example"]}]}
        self.assertSilent(run([decision(approval={"quorum": 1,
                                                  "records": self.records("ceo")})], extra=extra),
                          "Rule 102")

    def test_record_without_ref_on_active_is_warning(self):
        self.assertWarningOnly(run([decision(approval={"quorum": 1,
                                                       "records": [{"by": "tech-lead",
                                                                    "at": "2026-05-04"}]})]),
                               "without ref")

    def test_record_without_by_or_at_is_error(self):
        self.assertError(run([decision(approval={"quorum": 1, "records": [{"at": "2026-05-04"}]})]),
                         "without by")
        self.assertError(run([decision(approval={"quorum": 1, "records": [{"by": "tech-lead"}]})]),
                         "not a valid ISO 8601 date")

    def test_met_quorum_is_clean(self):
        r = run([decision(approval={"quorum": 2, "records": self.records("tech-lead", "coo")})])
        self.assertEqual((r.failed, r.warned), (0, 0), "\n".join(r.lines))


class CoverageAndVersion(Outcome):
    def test_no_enforcement_anywhere(self):
        self.assertNote(run([decision(), decision(id="dec-2")]),
                        "enforcement: 0/2 active decisions carry a block")

    def test_blocks_without_expectation(self):
        r = run([decision(enforcement={"status": "pending"}),
                 decision(id="dec-2", enforcement={"status": "pending"})])
        self.assertNote(r, "enforcement: 2/2 active decisions carry a block, 0/2 of those")
        self.assertEqual((r.failed, r.warned), (0, 0))

    def test_x_enforcement_co_presence(self):
        self.assertNote(run([decision(enforcement={"status": "pending"},
                                      **{"x-enforcement": {"state": "open"}})]),
                        "double maintenance")

    def test_v07_document_with_enforcement_is_noted_not_judged(self):
        r = run([decision(enforcement={"status": "bogus"})], opi="0.7.0")
        self.assertEqual(r.failed, 0, "\n".join(r.lines))
        self.assertNote(r, "not checked")

    def test_v08_hypothesis_passes(self):
        # guards the forward break fixed in c33280f
        r = run([decision(status="hypothesis", validate="v", validate_by="2026-12-31")])
        self.assertEqual(r.failed, 0, "\n".join(r.lines))

    def test_summary_line_has_three_counts(self):
        import contextlib
        import io
        r = run([decision(approval={"quorum": 3})])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            r.emit()
        self.assertIn("passed, 0 failed, 1 warnings", out.getvalue())


@unittest.skipUnless(HAVE_JSONSCHEMA, "jsonschema not installed")
class Schema(Outcome):
    SCHEMA = REPO / "spec" / "opi-v0.8.schema.json"

    def schema_errors(self, decisions, opi="0.8.0"):
        doc = json.loads(json.dumps(BASE))
        doc["opi"], doc["decisions"] = opi, decisions
        report = validate.Report(Path("<fixture>"))
        validate.check_schema(report, doc, self.SCHEMA)
        return report

    def test_valid_blocks(self):
        r = self.schema_errors([decision(enforcement={"status": "in_effect",
                                                      "first_effect_at": "2026-06-01",
                                                      "ref": "pr:1"},
                                         approval={"quorum": 1,
                                                   "records": [{"by": "tech-lead",
                                                                "at": "2026-05-04"}]})])
        self.assertEqual(r.failed, 0, "\n".join(r.lines))

    def test_if_then_dependencies(self):
        self.assertError(self.schema_errors([decision(enforcement={"status": "in_effect"})]))
        self.assertError(self.schema_errors([decision(enforcement={"status": "pending",
                                                                   "first_effect_at": "2026-06-01"})]))
        self.assertError(self.schema_errors([decision(enforcement={"status": "lapsed",
                                                                   "first_effect_at": "2026-06-01"})]))

    def test_strict_date_format(self):
        self.assertError(self.schema_errors([decision(enforcement={"status": "pending",
                                                                   "expected_by": "Q3 2026"})]))

    def test_version_pattern_is_narrow(self):
        self.assertEqual(self.schema_errors([decision()], opi="0.6.0").failed, 0)
        self.assertError(self.schema_errors([decision()], opi="0.5.0"))


if __name__ == "__main__":
    unittest.main()
