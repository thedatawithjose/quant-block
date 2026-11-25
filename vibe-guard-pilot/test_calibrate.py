#!/usr/bin/env python3
"""Offline tests for verifier/calibrate.py (unittest, mock reviewer only)."""

import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "verifier"))
import calibrate  # noqa: E402

FIXTURES = os.path.join(HERE, "verifier", "fixtures")


def fake_reviewer(failing):
    """Reviewer that FAILs exactly the fixtures whose dir name is in `failing`."""
    def run(path):
        v = "FAIL" if os.path.basename(path) in failing else "PASS"
        return [{"criterion": "C1", "verdict": v, "reason": "x", "proof": "x"}]
    return run


def fx(name, defect):
    return {"name": name, "path": "/x/" + name, "defect": defect, "defect_type": ""}


class RateMath(unittest.TestCase):
    def setUp(self):
        # 10 defect + 10 clean synthetic fixtures
        self.fixtures = [fx("d%d" % i, True) for i in range(10)] + \
                        [fx("c%d" % i, False) for i in range(10)]

    def test_perfect(self):
        r = calibrate.calibrate(self.fixtures, fake_reviewer({"d%d" % i for i in range(10)}))
        self.assertEqual(r["detection_rate"], 1.0)
        self.assertEqual(r["false_positive_rate"], 0.0)
        self.assertTrue(r["calibration_passed"])

    def test_rates_computed(self):
        failing = {"d%d" % i for i in range(9)} | {"c0"}   # 9/10 detected, 1/10 FP
        r = calibrate.calibrate(self.fixtures, fake_reviewer(failing))
        self.assertEqual(r["detection_rate"], 0.9)
        self.assertEqual(r["false_positive_rate"], 0.1)
        self.assertTrue(r["calibration_passed"])           # boundaries are inclusive

    def test_low_detection_fails(self):
        r = calibrate.calibrate(self.fixtures, fake_reviewer({"d0", "d1", "d2"}))
        self.assertEqual(r["detection_rate"], 0.3)
        self.assertFalse(r["calibration_passed"])

    def test_false_positives_fail(self):
        failing = {"d%d" % i for i in range(10)} | {"c0", "c1"}
        r = calibrate.calibrate(self.fixtures, fake_reviewer(failing))
        self.assertEqual(r["false_positive_rate"], 0.2)
        self.assertFalse(r["calibration_passed"])

    def test_rubber_stamp_reviewer_fails(self):
        r = calibrate.calibrate(self.fixtures, fake_reviewer(set()))
        self.assertEqual(r["detection_rate"], 0.0)
        self.assertFalse(r["calibration_passed"])

    def test_reviewer_error_fails_closed(self):
        def boom(path):
            raise calibrate.ReviewerError("boom")
        r = calibrate.calibrate(self.fixtures, boom)
        self.assertFalse(r["calibration_passed"])
        self.assertEqual(r["counts"]["reviewer_errors"], 20)

    def test_missing_class_fails_closed(self):
        r = calibrate.calibrate([fx("d0", True)], fake_reviewer({"d0"}))
        self.assertFalse(r["calibration_passed"])

    def test_thresholds_configurable(self):
        r = calibrate.calibrate(self.fixtures, fake_reviewer({"d0", "d1", "d2"}),
                                min_detection=0.3)
        self.assertTrue(r["calibration_passed"])


class MockOnRealFixtures(unittest.TestCase):
    def test_fixture_set_covers_required_cases(self):
        fixtures = calibrate.load_fixtures(FIXTURES)
        self.assertGreaterEqual(len(fixtures), 8)
        types = {f["defect_type"] for f in fixtures if f["defect"]}
        self.assertTrue({"claim_without_evidence", "test_asserts_nothing",
                         "criterion_unmet_marked_done", "inflated_metric",
                         "lookahead_bias", "evidence_file_missing"} <= types)
        self.assertGreaterEqual(sum(1 for f in fixtures if not f["defect"]), 2)

    def test_mock_passes_calibration(self):
        r = calibrate.calibrate(calibrate.load_fixtures(FIXTURES), calibrate.mock_reviewer)
        self.assertEqual(r["detection_rate"], 1.0)
        self.assertEqual(r["false_positive_rate"], 0.0)
        self.assertTrue(r["calibration_passed"], r["failure_reasons"])


class Cli(unittest.TestCase):
    def test_cli_exit_codes_and_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            rep = os.path.join(tmp, "r.json")
            self.assertEqual(calibrate.main(["--report", rep]), 0)
            with open(rep) as fh:
                self.assertTrue(json.load(fh)["calibration_passed"])
            # external rubber-stamp reviewer: always PASS -> must fail calibration
            cmd = "%s -c \"import json;print(json.dumps({'criterion':'C1','verdict':'PASS','reason':'','proof':''}))\"" % sys.executable
            self.assertEqual(calibrate.main(["--report", rep, "--reviewer-cmd", cmd]), 1)
            with open(rep) as fh:
                self.assertFalse(json.load(fh)["calibration_passed"])

    def test_malformed_external_output_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            rep = os.path.join(tmp, "r.json")
            cmd = "%s -c \"print('looks fine to me')\"" % sys.executable
            self.assertEqual(calibrate.main(["--report", rep, "--reviewer-cmd", cmd]), 1)


if __name__ == "__main__":
    unittest.main()
