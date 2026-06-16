#!/usr/bin/env python3
"""Regression tests for audit_contract_sync.py.

Covers the C1 (R3) extension that audits dispatch_manager.py's operational tables
against the dispatch registry, and — importantly — proves the comparators actually
DETECT drift (so an `in_sync` result is meaningful, not trivially passing).

Run: python3 test_audit_contract_sync.py    (or via pytest from this dir)
"""
from __future__ import annotations

import importlib.util
import pathlib
import unittest

_HERE = pathlib.Path(__file__).resolve().parent          # .../_shared/scripts
_SKILLS_ROOT = _HERE.parent.parent                       # .../Skills-Create-Project
_DM = _SKILLS_ROOT / "codex-worktree-dispatch" / "scripts" / "dispatch_manager.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "audit_contract_sync", _HERE / "audit_contract_sync.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


aud = _load_module()


class ComparatorDriftTest(unittest.TestCase):
    """The comparators must flag real mismatches — proves in_sync is meaningful."""

    def test_compare_sets_flags_drift(self):
        self.assertEqual(aud._compare_sets("t", "o", {"a", "b"}, {"a"}).status, "drift")

    def test_compare_sets_in_sync_when_equal(self):
        self.assertEqual(aud._compare_sets("t", "o", {"a", "b"}, {"a", "b"}).status, "in_sync")

    def test_compare_sets_error_when_builder_none(self):
        self.assertEqual(aud._compare_sets("t", "o", {"a"}, None).status, "error")

    def test_compare_dicts_flags_value_drift(self):
        row = aud._compare_dicts("t", "o", {"queued": {"ready"}}, {"queued": {"blocked"}})
        self.assertEqual(row.status, "drift")

    def test_compare_dicts_flags_key_drift(self):
        row = aud._compare_dicts("t", "o", {"queued": {"ready"}, "x": {"y"}}, {"queued": {"ready"}})
        self.assertEqual(row.status, "drift")

    def test_compare_dicts_in_sync_when_equal(self):
        # registry values may be lists; builder values sets — both normalized to sets
        row = aud._compare_dicts("t", "o", {"queued": ["ready", "blocked"]}, {"queued": {"ready", "blocked"}})
        self.assertEqual(row.status, "in_sync")


class DispatchManagerExtractionTest(unittest.TestCase):
    """C1 extractors must pull real values from dispatch_manager.py (None => audit 'error')."""

    def setUp(self):
        self.src = _DM.read_text(encoding="utf-8")

    def test_extracts_valid_statuses(self):
        statuses = aud._extract_set_constant(self.src, "VALID_STATUSES")
        self.assertIsNotNone(statuses)
        self.assertEqual(len(statuses), 8)

    def test_extracts_valid_transitions(self):
        transitions = aud._extract_dict_constant(self.src, "VALID_TRANSITIONS")
        self.assertIsNotNone(transitions)
        self.assertEqual(len(transitions), 6)  # dm omits terminal (merged/abandoned) keys

    def test_extracts_forbidden_fields(self):
        self.assertIsNotNone(aud._extract_set_constant(self.src, "FORBIDDEN_FIELDS"))

    def test_extracts_required_fields(self):
        self.assertIsNotNone(aud._extract_set_constant(self.src, "REQUIRED_FIELDS"))


class TransitionNormalizationTest(unittest.TestCase):
    """C1 transition comparison uses terminal-empty normalization, NOT raw equality.

    dispatch_manager omits terminal statuses (no outgoing) from VALID_TRANSITIONS,
    whereas the registry lists them with empty arrays. Dropping empty-valued registry
    keys makes the representations compare equal — while still catching real diffs.
    """

    def test_terminal_empty_keys_normalize_to_in_sync(self):
        reg = {"queued": ["ready"], "merged": [], "abandoned": []}
        dm = {"queued": {"ready"}}
        reg_nonempty = {k: v for k, v in reg.items() if v}
        self.assertEqual(aud._compare_dicts("t", "o", reg_nonempty, dm).status, "in_sync")

    def test_real_transition_diff_still_caught_after_normalization(self):
        reg = {"queued": ["ready"], "merged": []}
        dm = {"queued": {"blocked"}}  # genuine difference
        reg_nonempty = {k: v for k, v in reg.items() if v}
        self.assertEqual(aud._compare_dicts("t", "o", reg_nonempty, dm).status, "drift")


class DispatchMgrAuditRowsTest(unittest.TestCase):
    """End-to-end: the C1 rows exist and are in_sync against the live registry today."""

    DISPATCH_MGR_FACTS = (
        "dispatch_mgr_status_enum",
        "dispatch_mgr_transitions",
        "dispatch_mgr_required_fields",
        "dispatch_mgr_forbidden_fields",
    )

    def setUp(self):
        self.rows = {r.fact_id: r for r in aud.run_audit(_SKILLS_ROOT)}

    def test_dispatch_mgr_rows_present(self):
        for fid in self.DISPATCH_MGR_FACTS:
            self.assertIn(fid, self.rows)

    def test_dispatch_mgr_rows_in_sync_today(self):
        for fid in self.DISPATCH_MGR_FACTS:
            self.assertEqual(self.rows[fid].status, "in_sync", f"{fid}: {self.rows[fid].detail}")


if __name__ == "__main__":
    unittest.main()
