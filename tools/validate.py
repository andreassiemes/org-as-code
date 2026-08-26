#!/usr/bin/env python3
"""Validate OPI YAML documents (structural core checks + optional JSON Schema).

Two validation layers, degrading gracefully with what is installed:

* **PyYAML** (required) parses the document. There is deliberately no
  fallback parser here — a validator that guesses at YAML would defeat
  its purpose. If PyYAML is missing you get a clear install hint instead.
* **jsonschema** (optional) runs the full JSON Schema validation against
  the matching spec/opi-v<major.minor>.schema.json. Without it, the
  built-in structural core checks still run: required fields, ID
  patterns, referential integrity units <-> roles <-> gremien, and the
  decisions[] contract.

The report is human-readable (one ✓/✗ line per check, with line hints
where the source line can be located) and the exit code is CI-friendly:
0 = all checks passed, 1 = at least one check failed, 2 = usage error.

Usage:
    tools/validate.py <org.yaml> [more.yaml ...] [--schema spec/opi-v0.6.schema.json]
    tools/validate.py org.yaml --schema auto     # default: pick schema by opi version
    tools/validate.py org.yaml --schema none     # structural checks only
    tools/validate.py org.yaml --as-of 2026-06-30 # clock for Rule 101 (default: today)

Severities (v0.8 §7): ✗ = ERROR (counts as failed, fails CI), ⚠ = WARNING (counted,
never fails CI), · = note. The summary line is `N passed, M failed, K warnings`;
the exit code depends on failures only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

try:
    import jsonschema  # type: ignore
except ImportError:
    jsonschema = None

REPO_ROOT = Path(__file__).resolve().parent.parent

ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VERSION_PATTERN = re.compile(r"^\d+\.\d+(\.\d+)?$")

DECISION_REQUIRED = ["id", "date", "gremium", "title", "driver", "approver", "status", "rationale"]
DECISION_STATUS_ENUM = {"active", "planned", "revoked", "superseded"}
# v0.7 additions (spec/opi-v0.7.md)
DECISION_STATUS_ENUM_V07 = DECISION_STATUS_ENUM | {"hypothesis"}
DECISION_TYPE_ENUM = {"two-way", "one-way", "big-bet", "delegated"}
VISIBILITY_ENUM = {"public", "internal", "restricted", "confidential"}
REOPEN_ENTRY = re.compile(r"^\d{4}-\d{2}-\d{2}\s*[—-]\s*\S.*")
ROLE_REQUIRED = ["title", "purpose", "accountabilities"]
# v0.8 additions (spec/opi-v0.8.md)
ENFORCEMENT_STATUS_ENUM = {"pending", "in_effect", "lapsed"}

MAX_SCHEMA_ERRORS = 10  # keep the report readable on badly broken files


# --------------------------------------------------------------------------- report

class Report:
    """Collects ✓/✗/note lines for one file and prints them at the end."""

    def __init__(self, path: Path):
        self.path = path
        self.lines: list[str] = []
        self.failed = 0
        self.passed = 0
        self.warned = 0
        try:
            self.source = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            self.source = []

    def ok(self, msg: str) -> None:
        self.passed += 1
        self.lines.append(f"  ✓ {msg}")

    def fail(self, msg: str, needle: str | None = None) -> None:
        self.failed += 1
        hint = self.line_hint(needle) if needle else ""
        self.lines.append(f"  ✗ {msg}{hint}")

    def warn(self, msg: str, needle: str | None = None) -> None:
        """WARNING: counted and printed, never fails the run (v0.8 §5, §7)."""
        self.warned += 1
        hint = self.line_hint(needle) if needle else ""
        self.lines.append(f"  ⚠ {msg}{hint}")

    def note(self, msg: str) -> None:
        self.lines.append(f"  · {msg}")

    def line_hint(self, needle: str) -> str:
        """Best-effort line number for a value or key in the raw source."""
        for i, line in enumerate(self.source, start=1):
            if needle in line:
                return f" (line {i})"
        return ""

    def emit(self) -> None:
        print(f"\n{self.path}")
        for line in self.lines:
            print(line)
        verdict = "PASS" if self.failed == 0 else "FAIL"
        print(f"  {verdict}: {self.passed} passed, {self.failed} failed, {self.warned} warnings")


# --------------------------------------------------------------------------- helpers

def as_list(value) -> list:
    return value if isinstance(value, list) else []


def as_dict(value) -> dict:
    return value if isinstance(value, dict) else {}


def check_id(report: Report, context: str, value) -> None:
    if value is None:
        return  # optional ids are checked as required fields by their owners
    if not isinstance(value, str) or not ID_PATTERN.match(value):
        report.fail(f"{context}: id '{value}' does not match ^[a-z0-9][a-z0-9-]*$",
                    needle=str(value))


def collect_units(doc: dict) -> list[dict]:
    """The root unit plus any inline child units (pilot convenience: a
    document set may keep small child units in a top-level units[] list)."""
    units = []
    if isinstance(doc.get("unit"), dict):
        units.append(doc["unit"])
    units.extend(u for u in as_list(doc.get("units")) if isinstance(u, dict))
    return units


def is_iso_date(value) -> bool:
    import datetime
    if isinstance(value, datetime.date):
        return True
    if not isinstance(value, str) or not DATE_PATTERN.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def to_date(value):
    """PyYAML parses unquoted dates to datetime.date and quoted ones stay str;
    compare through this, never as raw values of mixed type (v0.8 §7)."""
    import datetime
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def is_local_ref(ref) -> bool:
    """knowledge_refs may be local ids, bundle paths, or external URIs.
    Only bare slugs are resolvable inside this document."""
    return isinstance(ref, str) and "/" not in ref and ":" not in ref


# --------------------------------------------------------------------------- checks

def check_visibility(report: Report, label: str, entity: dict, v07: bool) -> bool:
    """Rules 87-88 for any entity carrying a tier.

    The spec has permitted `visibility` on every entity since v0.7 §1.1; until
    v0.7.1 only decisions[] were checked. Returns False on a finding.
    """
    if not v07:
        return True
    vis = as_dict(entity).get("visibility")
    ok = True
    if vis is not None and vis not in VISIBILITY_ENUM:  # Rule 87
        report.fail(f"{label}: visibility '{vis}' not in {sorted(VISIBILITY_ENUM)} (Rule 87)",
                    needle=str(vis))
        ok = False
    if vis in ("restricted", "confidential") and not entity.get("classification_reason"):  # Rule 88
        report.fail(f"{label}: visibility '{vis}' requires classification_reason (Rule 88)",
                    needle=str(vis))
        ok = False
    return ok


def version_at_least(version, floor: tuple[int, int]) -> bool:
    """True when the declared opi version is >= (major, minor).

    A prefix test ("0.7") answers the wrong question: a document declaring 0.8
    would fall out of every 0.7 gate and be judged against pre-0.7 rules.
    """
    if not isinstance(version, str):
        return False
    parts = version.split(".")
    try:
        return (int(parts[0]), int(parts[1])) >= floor
    except (IndexError, ValueError):
        return False


def check_enforcement(report: Report, label: str, d: dict, as_of, dfail) -> None:
    """Rule 101: effect is recorded, never assumed (spec/opi-v0.8.md §1, §5)."""
    enf = d.get("enforcement")
    if not isinstance(enf, dict) or not enf.get("status"):
        dfail(f"{label}: enforcement present without status — an empty block asserts "
              f"nothing and still counts as coverage (Rule 101)",
              needle="enforcement")
        return
    st = enf["status"]
    if st not in ENFORCEMENT_STATUS_ENUM:
        dfail(f"{label}: enforcement.status '{st}' not in {sorted(ENFORCEMENT_STATUS_ENUM)} "
              f"(Rule 101)", needle=str(st))
        return
    dates = {}
    for key in ("first_effect_at", "lapsed_at", "expected_by"):
        if key in enf:
            if not is_iso_date(enf[key]):
                dfail(f"{label}: enforcement.{key} '{enf[key]}' is not a valid ISO 8601 date "
                      f"(Rule 101)", needle=str(enf[key]))
            else:
                dates[key] = to_date(enf[key])
    # presence contract per status value: each value states exactly one dated fact
    if st == "pending":
        for key in ("first_effect_at", "lapsed_at"):
            if key in enf:
                dfail(f"{label}: enforcement pending must not carry {key} (Rule 101)",
                      needle=key)
    else:  # in_effect / lapsed assert that an effect occurred
        if "first_effect_at" not in enf:
            dfail(f"{label}: enforcement {st} requires first_effect_at (Rule 101)",
                  needle=str(st))
        if st == "in_effect" and "lapsed_at" in enf:
            dfail(f"{label}: enforcement in_effect must not carry lapsed_at (Rule 101)",
                  needle="lapsed_at")
        if st == "lapsed" and "lapsed_at" not in enf:
            dfail(f"{label}: enforcement lapsed requires lapsed_at (Rule 101)",
                  needle=str(st))
        if not enf.get("ref"):
            report.warn(f"{label}: enforcement {st} without ref — an effect date without an "
                        f"external anchor is self-report (Rule 101, DD-9)", needle=str(st))
    # order of facts: an effect cannot precede its cause, a lapse cannot precede its effect
    decided = to_date(d.get("date"))
    fea, lap = dates.get("first_effect_at"), dates.get("lapsed_at")
    if fea and decided and fea < decided:
        dfail(f"{label}: enforcement.first_effect_at {fea} precedes the decision date "
              f"{decided} (Rule 101)", needle=str(enf.get("first_effect_at")))
    if fea and lap and lap < fea:
        dfail(f"{label}: enforcement.lapsed_at {lap} precedes first_effect_at {fea} "
              f"(Rule 101)", needle=str(enf.get("lapsed_at")))
    # overdue: only active + pending, only on expected_by, judged by the clock outside
    exp = dates.get("expected_by")
    if st == "pending" and d.get("status") == "active" and exp and exp < as_of:
        report.warn(f"{label}: decided {decided}, effect expected by {exp}, none recorded "
                    f"as of {as_of} (Rule 101)", needle=str(enf.get("expected_by")))


def check_approval(report: Report, label: str, d: dict, roles: dict, gremien: list,
                   dfail) -> None:
    """Rule 102: a recorded quorum must be met (spec/opi-v0.8.md §2, §5)."""
    ap = d.get("approval")
    if not isinstance(ap, dict):
        dfail(f"{label}: approval must be a mapping (Rule 102)", needle="approval")
        return
    quorum = ap.get("quorum")
    if not isinstance(quorum, int) or isinstance(quorum, bool) or quorum < 1:
        dfail(f"{label}: approval.quorum must be an integer >= 1 (got {quorum!r}) (Rule 102)",
              needle="quorum")
        return
    if "records" not in ap:
        report.warn(f"{label}: quorum {quorum} declared, no consents recorded (Rule 102)",
                    needle="quorum")
        return
    records = as_list(ap.get("records"))
    structure_ok = True
    for j, r in enumerate(records):
        r = as_dict(r)
        if not r.get("by") or not isinstance(r.get("by"), str):
            structure_ok = False
            dfail(f"{label}: approval.records[{j}] without by (Rule 102)", needle="records")
        if not is_iso_date(r.get("at")):
            structure_ok = False
            dfail(f"{label}: approval.records[{j}].at '{r.get('at')}' is not a valid "
                  f"ISO 8601 date (Rule 102)", needle=str(r.get("at") or "records"))
    if not structure_ok:
        return
    status = d.get("status")
    distinct = {as_dict(r)["by"] for r in records}
    if len(distinct) < quorum:
        msg = (f"{label}: quorum {quorum} declared, {len(distinct)} distinct consent(s) "
               f"recorded (Rule 102)")
        if status == "active":
            dfail(msg + " — a decision in force without the legitimacy it claims",
                  needle="quorum")
        elif status in ("planned", "hypothesis"):
            report.warn(msg, needle="quorum")
        # revoked / superseded / unknown status: no finding (honest history)
    # entitlement: only where both sides resolve to declared roles
    gremium = next((as_dict(g) for g in gremien if as_dict(g).get("id") == d.get("gremium")),
                   None)
    members = as_list(gremium.get("members")) if gremium else []
    role_members = {m for m in members if isinstance(m, str) and m in roles}
    if role_members:
        for by in sorted(distinct):
            if by in roles and by not in role_members:
                report.warn(f"{label}: consent by '{by}' is outside the declared membership "
                            f"of gremium '{d.get('gremium')}' (Rule 102)", needle=str(by))
    if status == "active":
        for j, r in enumerate(records):
            if not as_dict(r).get("ref"):
                report.warn(f"{label}: approval.records[{j}] ('{as_dict(r).get('by')}') "
                            f"without ref — a consent date without an anchor is self-report "
                            f"(Rule 102, DD-9)", needle=str(as_dict(r).get("by")))


def report_coverage(report: Report, decisions: list) -> None:
    """Coverage lines (v0.8 §1.1, §7): notes, never findings — the only
    counter-pressure against leaving the optional blocks out."""
    active = [as_dict(d) for d in decisions if as_dict(d).get("status") == "active"]
    if not active:
        return
    with_block = [d for d in active if isinstance(d.get("enforcement"), dict)]
    with_expect = [d for d in with_block if d["enforcement"].get("expected_by")]
    report.note(f"enforcement: {len(with_block)}/{len(active)} active decisions carry a block, "
                f"{len(with_expect)}/{len(with_block)} of those state an expectation")
    with_approval = [d for d in active if isinstance(d.get("approval"), dict)]
    report.note(f"approval: {len(with_approval)}/{len(active)} active decisions carry a quorum")


def check_structure(report: Report, doc: dict, as_of=None) -> None:
    import datetime
    as_of = as_of or datetime.date.today()
    # -- opi version
    version = doc.get("opi")
    if isinstance(version, str) and VERSION_PATTERN.match(version):
        report.ok(f"opi version declared ({version})")
    else:
        report.fail(f"opi: missing or not a semver string (got {version!r})", needle="opi")
    v07 = version_at_least(version, (0, 7))
    v08 = version_at_least(version, (0, 8))

    # -- unit identity
    unit = as_dict(doc.get("unit"))
    if unit.get("name"):
        report.ok(f"unit.name present ('{unit['name']}')")
    else:
        report.fail("unit.name missing — every OPI document needs a named root unit",
                    needle="unit")
    check_id(report, "unit", unit.get("id"))

    units = collect_units(doc)
    unit_ids = {u.get("id") for u in units if u.get("id")}
    for u in as_list(doc.get("units")):
        u = as_dict(u)
        check_id(report, f"units[] '{u.get('name', '?')}'", u.get("id"))

    # -- parent references (info only: parents may live in other documents of the set)
    for u in units:
        parent = u.get("parent")
        if parent and parent not in unit_ids:
            report.note(f"unit '{u.get('id', u.get('name'))}': parent '{parent}' "
                        f"not in this document (ok if defined elsewhere in the document set)")

    # -- roles catalog
    roles = as_dict(as_dict(doc.get("components")).get("roles"))
    role_errors = 0
    for key, role in roles.items():
        check_id(report, "components.roles", key)
        missing = [f for f in ROLE_REQUIRED if not as_dict(role).get(f)]
        if missing:
            role_errors += 1
            report.fail(f"components.roles.{key}: missing required field(s) {', '.join(missing)}",
                        needle=f"{key}:")
    if roles and role_errors == 0:
        report.ok(f"components.roles: {len(roles)} role(s), all with title/purpose/accountabilities")

    # -- members -> roles referential integrity
    member_lists = [("members", as_list(doc.get("members")))]
    member_lists += [(f"unit '{u.get('id', u.get('name', '?'))}' members",
                      as_list(u.get("members"))) for u in units]
    ref_errors = 0
    ref_total = 0
    for where, members in member_lists:
        for m in members:
            m = as_dict(m)
            if "role_ref" in m:
                ref_total += 1
                if m["role_ref"] not in roles:
                    ref_errors += 1
                    report.fail(f"{where}: role_ref '{m['role_ref']}' not defined "
                                f"in components.roles", needle=str(m["role_ref"]))
    if ref_total and ref_errors == 0:
        report.ok(f"members: all {ref_total} role_ref(s) resolve to components.roles")

    # -- gremien
    gremien = as_list(doc.get("gremien"))
    gremium_ids = set()
    gremien_ok = True
    for g in gremien:
        g = as_dict(g)
        check_id(report, "gremien[]", g.get("id"))
        if not g.get("id") or not g.get("name"):
            gremien_ok = False
            report.fail(f"gremien[] entry '{g.get('id') or g.get('name') or '?'}': "
                        f"id and name are required", needle=str(g.get("id") or g.get("name") or ""))
        if g.get("id") in gremium_ids:
            gremien_ok = False
            report.fail(f"gremien[]: duplicate id '{g['id']}'", needle=str(g["id"]))
        gremium_ids.add(g.get("id"))
        # gremium members may be role keys OR plain names from other documents -> note only
        for member in as_list(g.get("members")):
            if roles and isinstance(member, str) and ID_PATTERN.match(member) and member not in roles:
                report.note(f"gremium '{g.get('id')}': member '{member}' is not a "
                            f"components.roles key (ok if it is a person/external role)")
    if gremien and gremien_ok:
        report.ok(f"gremien: {len(gremien)} gremium/gremien with id + name")

    # -- decisions[] contract
    decisions = as_list(doc.get("decisions"))
    decision_ids = set()
    decisions_ok = True

    def dfail(msg: str, needle: str | None = None) -> None:
        nonlocal decisions_ok
        decisions_ok = False
        report.fail(msg, needle=needle)

    for i, d in enumerate(decisions):
        d = as_dict(d)
        label = f"decisions[{i}] '{d.get('id', '?')}'"
        missing = [f for f in DECISION_REQUIRED if not d.get(f)]
        if missing:
            dfail(f"{label}: missing required field(s) {', '.join(missing)}",
                  needle=str(d.get("id") or d.get("title") or ""))
        check_id(report, label, d.get("id"))
        if d.get("id") in decision_ids:
            dfail(f"{label}: duplicate decision id", needle=str(d["id"]))
        decision_ids.add(d.get("id"))
        date = d.get("date")
        if date is not None and not is_iso_date(date):
            dfail(f"{label}: date '{date}' is not a valid ISO 8601 date (YYYY-MM-DD)",
                  needle=str(date))
        status = d.get("status")
        allowed = DECISION_STATUS_ENUM_V07 if v07 else DECISION_STATUS_ENUM
        if status is not None and status not in allowed:
            hint = " ('hypothesis' requires opi >= 0.7)" if status == "hypothesis" and not v07 else ""
            dfail(f"{label}: status '{status}' not in {sorted(allowed)}{hint}",
                  needle=str(status))
        # -- v0.7 lifecycle checks. Version-gated: `decision_type` carried no controlled
        # vocabulary before v0.7, and under the permissive consumer model (v0.6, rules
        # 82-84) a pre-0.7 document may use the key freely.
        if v07 and d.get("decision_type") and d["decision_type"] not in DECISION_TYPE_ENUM:  # Rule 90
            dfail(f"{label}: decision_type '{d['decision_type']}' not in {sorted(DECISION_TYPE_ENUM)}",
                  needle=str(d["decision_type"]))
        if v07 and d.get("decision_type") in ("one-way", "big-bet") and not d.get("rationale"):  # Rule 90 WARN
            report.warn(f"{label}: {d['decision_type']} decision without rationale (Rule 90)")
        if status == "hypothesis" and (not d.get("validate") or not d.get("validate_by")):  # Rule 91
            dfail(f"{label}: hypothesis without validate + validate_by (Rule 91)",
                  needle=str(d.get("id") or ""))
        for entry in as_list(d.get("reopen_log")):  # Rule 92 (format)
            if not REOPEN_ENTRY.match(str(entry)):
                dfail(f"{label}: reopen_log entry not 'YYYY-MM-DD — reason' (Rule 92): {entry!r}",
                      needle=str(entry)[:30])
        vis = d.get("visibility")
        if vis is not None and vis not in VISIBILITY_ENUM:  # Rule 87
            dfail(f"{label}: visibility '{vis}' not in {sorted(VISIBILITY_ENUM)}", needle=str(vis))
        if vis in ("restricted", "confidential") and not d.get("classification_reason"):  # Rule 88
            dfail(f"{label}: visibility '{vis}' requires classification_reason (Rule 88)",
                  needle=str(d.get("id") or ""))
        if d.get("gremium") and gremien and d["gremium"] not in gremium_ids:
            dfail(f"{label}: gremium '{d['gremium']}' not found in gremien[]",
                  needle=str(d["gremium"]))
        # -- v0.8 Decision Effect and Legitimacy (Rules 101-102). Presence-gated; in a
        # document declaring < 0.8 the block is noted, never judged (v0.8 §5, §6).
        if "enforcement" in d or "approval" in d:
            if not v08:
                report.note(f"{label}: carries v0.8 key(s) "
                            f"{[k for k in ('enforcement', 'approval') if k in d]} "
                            f"under opi {version} — not checked (Rules 101-102 need opi >= 0.8)")
            else:
                if "enforcement" in d:
                    check_enforcement(report, label, d, as_of, dfail)
                if "approval" in d:
                    check_approval(report, label, d, roles, gremien, dfail)
        for xk, k in (("x-enforcement", "enforcement"), ("x-approval", "approval")):
            if xk in d and k in d:
                report.note(f"{label}: both '{xk}' and '{k}' present — the adopted key is "
                            f"authoritative, the x- field is now double maintenance")
    # decision graph edges must stay inside the document (spec v0.5 rules 63-65)
    for i, d in enumerate(decisions):
        d = as_dict(d)
        label = f"decisions[{i}] '{d.get('id', '?')}'"
        for field in ("triggers", "consequences", "conflicts_with", "supersedes", "superseded_by"):
            for ref in as_list(d.get(field)):
                if ref not in decision_ids:
                    dfail(f"{label}: {field} references unknown decision '{ref}'",
                          needle=str(ref))
        if d.get("revises") and d["revises"] not in decision_ids:
            dfail(f"{label}: revises unknown decision '{d['revises']}'",
                  needle=str(d["revises"]))
    if decisions and decisions_ok:
        report.ok(f"decisions: {len(decisions)} decision(s) with required fields, "
                  f"valid status, resolvable gremium and graph edges")
    if v08 and decisions:
        report_coverage(report, decisions)

    # -- agents[] -> components.agents / gremien
    agent_types = as_dict(as_dict(doc.get("components")).get("agents"))
    agents_ok = True
    agents = as_list(doc.get("agents"))
    for i, a in enumerate(agents):
        a = as_dict(a)
        label = f"agents[{i}]"
        if a.get("ref") and agent_types and a["ref"] not in agent_types:
            agents_ok = False
            report.fail(f"{label}: ref '{a['ref']}' not defined in components.agents",
                        needle=str(a["ref"]))
        scope = as_dict(a.get("scope"))
        if not as_list(scope.get("units")) or not as_list(scope.get("data")):
            agents_ok = False
            report.fail(f"{label}: scope.units and scope.data are required", needle="scope")
        for gid in as_list(scope.get("gremien")):
            if gremien and gid not in gremium_ids:
                agents_ok = False
                report.fail(f"{label}: scope.gremien '{gid}' not found in gremien[]",
                            needle=str(gid))
        # -- v0.7 agent mandate provenance (rules 99-100); fires only when declared
        src = a.get("mandate_source")
        if src:
            role_keys = set(as_dict(as_dict(doc.get("components")).get("roles")))
            is_role, is_gremium = src in role_keys, src in gremium_ids
            if not is_role and not is_gremium:  # Rule 100
                agents_ok = False
                report.fail(f"{label}: mandate_source '{src}' resolves to neither "
                            f"components.roles nor gremien[] (Rule 100)", needle=str(src))
            else:  # Rule 99 — only the dimensions this document can answer
                if is_role:
                    owned = {u.get("id") for u in units if u.get("owner") == src}
                    allowed_gremien = {g.get("id") for g in gremien
                                       if src in as_list(as_dict(g).get("members"))}
                else:
                    owned = None  # a gremium owns no units — not resolvable
                    allowed_gremien = {src}
                if owned is not None:
                    for uid in as_list(scope.get("units")):
                        if uid in unit_ids and uid not in owned:
                            agents_ok = False
                            report.fail(f"{label}: scope.units '{uid}' exceeds the authority "
                                        f"of mandate_source '{src}' (Rule 99)", needle=str(uid))
                for gid in as_list(scope.get("gremien")):
                    if gid in gremium_ids and gid not in allowed_gremien:
                        agents_ok = False
                        report.fail(f"{label}: scope.gremien '{gid}' exceeds the authority "
                                    f"of mandate_source '{src}' (Rule 99)", needle=str(gid))
    if agents and agents_ok:
        report.ok(f"agents: {len(agents)} instance(s) with resolvable ref + valid scope")

    # -- tier classification across every entity type (v0.7 §1.1, rules 87-88).
    # decisions[] are checked inline above; this sweep covers the rest.
    tiers_ok = True
    tiered: list[tuple[str, dict]] = []
    for u in units:
        tiered.append((f"unit '{as_dict(u).get('id', as_dict(u).get('name', '?'))}'", as_dict(u)))
        for m in as_list(as_dict(u).get("members")):
            if isinstance(m, dict):
                tiered.append((f"member '{m.get('id', m.get('name', '?'))}'", m))
    for g in gremien:
        tiered.append((f"gremien[] '{as_dict(g).get('id', '?')}'", as_dict(g)))
    for i, a in enumerate(agents):
        tiered.append((f"agents[{i}] '{as_dict(a).get('ref', '?')}'", as_dict(a)))
    for k in as_list(doc.get("knowledge")):
        tiered.append((f"knowledge[] '{as_dict(k).get('id', '?')}'", as_dict(k)))
    for label, entity in tiered:
        if not check_visibility(report, label, entity, v07):
            tiers_ok = False
    classified = [1 for _, e in tiered if e.get("visibility")]
    if v07 and tiers_ok and classified:
        report.ok(f"visibility: {len(classified)} classified entity/entities, tiers valid")

    # -- knowledge graph
    knowledge_ids = set()
    for k in as_list(doc.get("knowledge")):
        k = as_dict(k)
        check_id(report, "knowledge[]", k.get("id"))
        missing = [f for f in ("id", "type", "title", "description") if not k.get(f)]
        if missing:
            report.fail(f"knowledge[] '{k.get('id', '?')}': missing {', '.join(missing)}",
                        needle=str(k.get("id") or ""))
        knowledge_ids.add(k.get("id"))
    kref_errors = 0
    kref_total = 0

    def check_krefs(owner: str, entity: dict) -> None:
        nonlocal kref_errors, kref_total
        for ref in as_list(as_dict(entity).get("knowledge_refs")):
            if is_local_ref(ref):
                kref_total += 1
                if ref not in knowledge_ids:
                    kref_errors += 1
                    report.fail(f"{owner}: knowledge_ref '{ref}' not found in knowledge[]",
                                needle=str(ref))

    for u in units:
        check_krefs(f"unit '{u.get('id', u.get('name', '?'))}'", u)
    for g in gremien:
        check_krefs(f"gremium '{as_dict(g).get('id', '?')}'", g)
    for d in decisions:
        check_krefs(f"decision '{as_dict(d).get('id', '?')}'", d)
    if kref_total and kref_errors == 0:
        report.ok(f"knowledge_refs: all {kref_total} local ref(s) resolve to knowledge[]")


# --------------------------------------------------------------------------- schema

def resolve_schema(doc: dict, schema_arg: str, report: Report) -> Path | None:
    if schema_arg == "none":
        return None
    if schema_arg != "auto":
        path = Path(schema_arg)
        if not path.is_file():
            report.fail(f"--schema {path}: file not found")
            return None
        return path
    # auto: pick spec/opi-v<major.minor>.schema.json for the document's version
    version = str(doc.get("opi") or "")
    m = re.match(r"^(\d+\.\d+)", version)
    if not m:
        return None  # structural check already flagged the version
    candidate = REPO_ROOT / "spec" / f"opi-v{m.group(1)}.schema.json"
    if not candidate.is_file():
        report.note(f"no schema for OPI {m.group(1)} at {candidate} — structural checks only")
        return None
    return candidate


def jsonify(value):
    """YAML 1.1 parses unquoted dates into date objects; JSON Schema expects
    ISO strings ('format: date'). Normalize before schema validation."""
    import datetime
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: jsonify(v) for k, v in value.items()}
    if isinstance(value, list):
        return [jsonify(v) for v in value]
    return value


def check_schema(report: Report, doc: dict, schema_path: Path) -> None:
    if jsonschema is None:
        report.note("jsonschema not installed — skipped full schema validation "
                    "(pip install jsonschema); structural core checks ran instead")
        return
    import json
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = sorted(validator.iter_errors(jsonify(doc)), key=lambda e: list(e.absolute_path))
    if not errors:
        report.ok(f"JSON Schema: valid against {schema_path.name}")
        return
    for error in errors[:MAX_SCHEMA_ERRORS]:
        where = "/".join(str(p) for p in error.absolute_path) or "<root>"
        report.fail(f"schema: {where}: {error.message}")
    if len(errors) > MAX_SCHEMA_ERRORS:
        report.note(f"schema: {len(errors) - MAX_SCHEMA_ERRORS} further error(s) suppressed")


# --------------------------------------------------------------------------- main

def validate_file(path: Path, schema_arg: str, as_of=None) -> bool:
    report = Report(path)
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        report.fail(f"cannot read file: {exc}")
        report.emit()
        return False
    except (yaml.YAMLError, ValueError) as exc:
        # ValueError: PyYAML raises it for impossible timestamps (e.g. month 13)
        mark = getattr(exc, "problem_mark", None)
        where = f" (line {mark.line + 1})" if mark else ""
        report.fail(f"YAML parse error{where}: {exc}")
        report.emit()
        return False

    if not isinstance(doc, dict):
        report.fail("document root must be a YAML mapping")
        report.emit()
        return False
    report.ok("parses as a YAML mapping")

    check_structure(report, doc, as_of=as_of)
    schema_path = resolve_schema(doc, schema_arg, report)
    if schema_path:
        check_schema(report, doc, schema_path)

    report.emit()
    return report.failed == 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="+", type=Path, help="OPI YAML document(s) to validate")
    ap.add_argument("--schema", default="auto",
                    help="JSON Schema path, 'auto' (default: match spec/opi-v<version>."
                         "schema.json to the document's opi version), or 'none'")
    ap.add_argument("--as-of", default=None, metavar="YYYY-MM-DD",
                    help="clock for time-bound findings (Rule 101 overdue); default: today. "
                         "Fix it in fixtures so a report is reproducible")
    args = ap.parse_args()

    import datetime
    if args.as_of:
        try:
            as_of = datetime.date.fromisoformat(args.as_of)
        except ValueError:
            print(f"error: --as-of {args.as_of!r} is not a YYYY-MM-DD date", file=sys.stderr)
            return 2
    else:
        as_of = datetime.date.today()

    if yaml is None:
        print("error: PyYAML is required to validate OPI documents.\n"
              "       Install it with:  pip install pyyaml\n"
              "       (This validator deliberately has no fallback parser — "
              "a guessing validator is worse than none.)", file=sys.stderr)
        return 2

    print(f"validate.py — as-of {as_of.isoformat()} (Rule 101 clock)")
    failed = 0
    for path in args.files:
        if not path.is_file():
            print(f"error: {path}: no such file", file=sys.stderr)
            return 2
        if not validate_file(path, args.schema, as_of=as_of):
            failed += 1

    total = len(args.files)
    print(f"\n{'=' * 40}\n{total - failed}/{total} file(s) valid")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
