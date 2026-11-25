#!/usr/bin/env python3
"""Seeded fail-closed tests for gate.py / report.py (unittest only)."""

import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gate  # noqa: E402
import report  # noqa: E402


def inv_yaml(id_, vtype, command, severity="CRITICAL", extra=""):
    cmd = "null" if command is None else '"%s"' % command
    return f"""
  - id: "{id_}"
    title: "Check {id_}"
    severity: "{severity}"
    source: "USER_DECLARED"
    enforcement_status: "ENFORCED"
    owner: "qa"
    verification:
      type: "{vtype}"
      command: {cmd}
      working_directory: "."
      timeout_seconds: 5
      expected_exit_code: 0
{extra}    evidence:
      required: true
      type: null
      path: null
    traceability:
      contract_section: "§1"
      tests: []
"""


def config(*invariants, policy_extra=""):
    return f"""schema_version: "1.0"
project:
  name: "seed"
  governance_status: "DRAFT"
  human_approved: false
policy:
  fail_closed: true
  agent_claims_are_evidence: false
  unknown_control_state: "BLOCK"
{policy_extra}  evidence:
    directory: ".governance/evidence"
    preserve_failed_checks: true
defaults:
  working_directory: "."
  timeout_seconds: 300
  expected_exit_code: 0
invariants:
""" + "".join(invariants)


class GateCase(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="vibeguard-")
        self.addCleanup(shutil.rmtree, self.root, True)

    def run_cfg(self, text, via_cli=False):
        os.makedirs(os.path.join(self.root, ".governance"))
        with open(os.path.join(self.root, ".governance", "enforcement.yaml"), "w") as fh:
            fh.write(text)
        if via_cli:
            p = subprocess.run([sys.executable, os.path.join(HERE, "gate.py"), "--project", self.root],
                               capture_output=True, text=True)
            return p.returncode
        verdict, code = gate.run_gate(self.root)
        self.verdict = verdict
        return code

    def status(self, id_):
        return next(i for i in self.verdict["invariants"] if i["id"] == id_)


class SeededFailClosed(GateCase):
    def test_a_passing_invariant_is_pass(self):
        code = self.run_cfg(config(inv_yaml("T-001", "command", "exit 0")))
        self.assertEqual(code, 0)
        r = self.status("T-001")
        self.assertEqual((r["status"], r["exit_code"]), ("PASS", 0))
        self.assertTrue(os.path.isfile(os.path.join(self.root, r["evidence_path"])))

    def test_b_failing_invariant_is_fail_and_blocks(self):
        code = self.run_cfg(config(inv_yaml("T-002", "test", "echo boom >&2; exit 3")))
        self.assertNotEqual(code, 0)
        r = self.status("T-002")
        self.assertEqual((r["status"], r["exit_code"]), ("FAIL", 3))
        self.assertEqual(self.verdict["overall"], "BLOCK")
        # failed check evidence is preserved, including stderr
        with open(os.path.join(self.root, r["evidence_path"])) as fh:
            self.assertIn("boom", json.load(fh)["stderr"])

    def test_c_type_none_blocks(self):
        code = self.run_cfg(config(inv_yaml("T-003", "none", None)))
        self.assertNotEqual(code, 0)
        self.assertEqual(self.status("T-003")["status"], "BLOCKED")

    def test_c_unknown_type_blocks(self):
        code = self.run_cfg(config(inv_yaml("T-004", "vibes", "exit 0")))
        self.assertNotEqual(code, 0)
        self.assertEqual(self.status("T-004")["status"], "BLOCKED")

    def test_unknown_when_command_missing(self):
        code = self.run_cfg(config(inv_yaml("T-005", "command", None)))
        self.assertNotEqual(code, 0)
        self.assertEqual(self.status("T-005")["status"], "UNKNOWN")

    def test_claim_without_evidence_never_counts(self):
        # enforcement_status ENFORCED is only a claim; type none stays blocked.
        self.run_cfg(config(inv_yaml("T-006", "none", None)))
        r = self.status("T-006")
        self.assertNotEqual(r["status"], "PASS")
        self.assertIn("not evidence", r["reason"])

    def test_timeout_is_fail(self):
        text = config(inv_yaml("T-007", "command", "sleep 30").replace("timeout_seconds: 5", "timeout_seconds: 1"))
        code = self.run_cfg(text)
        self.assertNotEqual(code, 0)
        self.assertEqual(self.status("T-007")["status"], "FAIL")

    def test_noncritical_failure_does_not_block_but_is_recorded(self):
        code = self.run_cfg(config(inv_yaml("T-008", "command", "exit 0"),
                                   inv_yaml("T-009", "command", "exit 1", severity="LOW")))
        self.assertEqual(code, 0)
        self.assertEqual(self.status("T-009")["status"], "FAIL")

    def test_expected_exit_code_honoured(self):
        text = config(inv_yaml("T-010", "command", "exit 7").replace("expected_exit_code: 0", "expected_exit_code: 7"))
        self.assertEqual(self.run_cfg(text), 0)

    def test_failed_evidence_not_overwritten_between_runs(self):
        self.run_cfg(config(inv_yaml("T-011", "command", "exit 1")))
        gate.run_gate(self.root)
        files = glob.glob(os.path.join(self.root, ".governance", "evidence", "T-011-*.json"))
        self.assertEqual(len(files), 2)

    def test_cli_exit_codes(self):
        self.assertEqual(self.run_cfg(config(inv_yaml("T-012", "command", "exit 1")), via_cli=True), 1)

    def test_weakened_policy_is_rejected(self):
        os.makedirs(os.path.join(self.root, ".governance"))
        bad = config(inv_yaml("T-013", "command", "exit 0")).replace(
            "agent_claims_are_evidence: false", "agent_claims_are_evidence: true")
        with open(os.path.join(self.root, ".governance", "enforcement.yaml"), "w") as fh:
            fh.write(bad)
        with self.assertRaises(gate.GateError):
            gate.run_gate(self.root)

    def test_missing_config_is_error(self):
        with self.assertRaises(gate.GateError):
            gate.run_gate(self.root)


class ParserAndReport(unittest.TestCase):
    def test_template_parses(self):
        tpl = "/home/datawithjose/Documents/GENTLE-QUANT-ECOSYSTEM/templates/project-governance/enforcement.template.yaml"
        if not os.path.exists(tpl):
            self.skipTest("template not present")
        with open(tpl) as fh:
            cfg = gate.load_yaml(fh.read())
        self.assertEqual(cfg["schema_version"], "1.0")
        inv = cfg["invariants"][0]
        self.assertEqual(inv["verification"]["type"], "none")
        self.assertIsNone(inv["verification"]["command"])
        self.assertEqual(inv["traceability"]["tests"], [])
        gate.validate_config(cfg)

    def test_report_statuses_come_from_table(self):
        v = {"project": "p", "overall": "BLOCK", "blocking_invariants": ["B"], "invariants": [
            {"id": "A", "status": "PASS", "severity": "CRITICAL", "command": "true", "exit_code": 0},
            {"id": "B", "status": "FAIL", "severity": "CRITICAL", "command": "false", "exit_code": 1},
            {"id": "C", "status": "UNKNOWN", "severity": "LOW", "command": None, "exit_code": None},
            {"id": "D", "status": "BLOCKED", "severity": "LOW", "command": None, "exit_code": None}]}
        text = report.render(v)
        for expected in ("Status: verified", "Status: incomplete", "NOT ACCEPTED"):
            self.assertIn(expected, text)
        self.assertEqual(text.count("Status: blocked"), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
