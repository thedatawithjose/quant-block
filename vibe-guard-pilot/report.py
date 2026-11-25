#!/usr/bin/env python3
"""vibe-guard report: turn verdict.json into a plain-language Markdown acceptance report.

Statuses are mapped from the gate's verdict by a fixed table below. No LLM,
no free-text judgement: the wording around a status never changes it.

Usage: python3 report.py VERDICT_JSON [-o REPORT_MD]
"""

import argparse
import json
import sys

# Fixed, script-owned mapping. Anything unrecognised is treated as blocked.
LABELS = {
    "PASS": ("verified", "The check was run by the gate and gave the expected result."),
    "FAIL": ("blocked", "The check was run and did NOT give the expected result."),
    "UNKNOWN": ("incomplete", "The check could not be run properly, so nothing is proven."),
    "BLOCKED": ("blocked", "No automatic check exists for this rule, so it cannot be accepted."),
}


def label_for(status):
    return LABELS.get(status, ("blocked", "Unrecognised status; treated as not accepted."))


def render(verdict):
    invs = verdict.get("invariants", [])
    counts = {"verified": 0, "incomplete": 0, "blocked": 0}
    for inv in invs:
        counts[label_for(inv.get("status"))[0]] += 1
    accepted = verdict.get("overall") == "PASS"
    lines = [
        "# Acceptance report: %s" % (verdict.get("project") or "(unnamed project)"),
        "",
        "Generated from the gate's verdict at %s." % verdict.get("generated_at", "unknown time"),
        "",
        "**Overall result: %s**" % ("ACCEPTED - every critical rule is verified."
                                    if accepted else "NOT ACCEPTED - at least one critical rule is not verified."),
        "",
        "- Verified: %d" % counts["verified"],
        "- Incomplete: %d" % counts["incomplete"],
        "- Blocked: %d" % counts["blocked"],
        "",
    ]
    if verdict.get("blocking_invariants"):
        lines += ["Critical rules holding this back: %s." % ", ".join(verdict["blocking_invariants"]), ""]
    for inv in invs:
        word, meaning = label_for(inv.get("status"))
        title = inv.get("title") or inv.get("id")
        lines += ["## %s - %s" % (inv.get("id"), title), "",
                  "- **Status: %s** (%s)" % (word, meaning),
                  "- Severity: %s" % inv.get("severity")]
        if inv.get("contract_section"):
            lines.append("- Requirement reference: %s" % inv["contract_section"])
        cmd = inv.get("command")
        if cmd:
            lines.append("- What was tested: running `%s` in `%s`; it should exit with code %s."
                         % (cmd, inv.get("working_directory") or ".", inv.get("expected_exit_code")))
            lines.append("- How to repeat it: from the project root, `cd %s && %s`"
                         % (inv.get("working_directory") or ".", cmd))
        else:
            lines.append("- What was tested: nothing. No command is defined for this rule.")
            lines.append("- How to repeat it: define `verification.type` and `verification.command` "
                         "in `.governance/enforcement.yaml`, then re-run the gate.")
        code = inv.get("exit_code")
        lines.append("- Result: %s (exit code: %s)" % (inv.get("reason") or "n/a",
                                                         "none" if code is None else code))
        lines.append("- Evidence file: `%s` (sha256 %s)" % (inv.get("evidence_path"),
                                                             (inv.get("evidence_sha256") or "n/a")[:16]))
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render verdict.json as a Markdown acceptance report")
    ap.add_argument("verdict", help="path to verdict.json")
    ap.add_argument("-o", "--output", help="write report here instead of stdout")
    args = ap.parse_args(argv)
    try:
        with open(args.verdict, encoding="utf-8") as fh:
            verdict = json.load(fh)
        text = render(verdict)
    except (OSError, ValueError, AttributeError, TypeError) as exc:
        print("report: cannot render %s: %s" % (args.verdict, exc), file=sys.stderr)
        return 2
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
