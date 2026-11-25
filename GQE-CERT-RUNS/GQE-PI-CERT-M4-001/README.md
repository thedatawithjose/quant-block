# GQE-PI-CERT-M4-001 — disposable certification workspace

Own governance: `.governance/`
Authoritative inputs: `authoritative-inputs/`
Evidence and executable controls: `evidence/`
Human gate and disposition: `gates/`
Pi runtime capability manifest: `runtime/`
Acceptance report: `CERTIFICATION-REPORT.md`

This workspace is disposable and self-contained. It does not reuse governance or artifacts
from any other project. Canonical GQE sources are referenced read-only at revision
`ff16b6b1e21f34a6df9e72d6121bac93ee8fcd4b`.

Reproduce the enforcement evaluation:

```bash
python3 evidence/controls/evaluate_enforcement.py   # exit 1 while blocking controls are unsatisfied
```

Re-verify frozen authority:

```bash
sha256sum -c evidence/pre-qv-snapshot.sha256
```
