"""Ejecuta verificaciones existentes por modulo y conserva sus salidas completas."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parent
PREFIX = 'test_external_flow.ExternalCLI.'
MODULES = {
    'M01': ('Contrato', [
        'test_frozen_contract_is_canonical_and_cannot_be_replaced',
        'test_invalid_contract_inputs_no_reuse_or_writes',
        'test_state_and_acceptance_must_be_outside_canonical_repo',
        'test_exact_authorized_paths_only',
        'test_frozen_acceptance_bytes_checked_and_original_not_reused']),
    'M02': ('Repositorio y candidato', [
        'test_unknown_malformed_refs_and_blank_executor_rejected',
        'test_snapshot_not_dirty_worktree_or_moving_ref']),
    'M03': ('Alcance del diff', [
        'test_scope_precedes_passing_acceptance_and_approval',
        'test_deleted_and_renamed_old_and_new_paths_are_checked',
        'test_deleted_unauthorized_path_is_blocked']),
    'M04': ('Aceptacion', [
        'test_base_fails_expected_assertion_and_corrected_candidate_passes',
        'test_acceptance_timeout_is_bound_failure']),
    'M05': ('Revision', ['test_blank_and_self_review_and_unknown_delivery_rejected_without_writes']),
    'M06': ('Cierre e invalidacion', ['test_missing_evidence_review_changes_and_fresh_delivery_same_commit']),
    'M07': ('Compatibilidad legacy', ['test_legacy_init_can_still_replace_non_json_file']),
}

def integrity():
    manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
    failures = []
    for name, expected in manifest['sha256'].items():
        path = ROOT / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            failures.append(name)
    return {'passed': not failures, 'files': len(manifest['sha256']), 'mismatches': failures,
            'limit': 'Integridad accidental; el manifiesto no es una firma externa.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--modulo', choices=['todos', 'M00', *MODULES, 'M08'], default='todos')
    parser.add_argument('--salida', type=Path)
    args = parser.parse_args()
    selected = ['M00', *MODULES, 'M08'] if args.modulo == 'todos' else [args.modulo]
    out = (args.salida or ROOT / 'validaciones' /
           (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8])).resolve()
    out.mkdir(parents=True, exist_ok=False)
    report = {'schema_version': 1, 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
              'python': platform.python_version(), 'source_root': str(ROOT),
              'scope': 'E2E local de confianza; Pi, Quant y aislamiento NO certificados.',
              'modules': {}, 'automated_tests_run': 0}

    def run(name, argv, expected_code=0, expected_tests=None):
        command = list(map(str, argv))
        try:
            p = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                               timeout=120, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
            stdout, stderr, code = p.stdout, p.stderr, p.returncode
            count = re.search(r'Ran (\d+) tests?', stderr)
            count = int(count.group(1)) if count else 0
            passed = code == expected_code
            if expected_tests is not None:
                passed = passed and count == expected_tests and not re.search(r'OK \(skipped=', stderr)
            detail = {'argv': command, 'exit_code': code, 'passed': passed, 'tests': count}
        except subprocess.TimeoutExpired:
            stdout, stderr = '', 'Timeout del verificador: 120 segundos.'
            detail = {'argv': command, 'exit_code': None, 'passed': False, 'tests': 0}
        (out / (name + '.stdout.txt')).write_text(stdout)
        (out / (name + '.stderr.txt')).write_text(stderr)
        report['automated_tests_run'] += detail['tests']
        return detail

    for module in selected:
        if module == 'M00':
            result = integrity()
        elif module == 'M08':
            lab = out / 'laboratorio'
            checks = [run('M08-example', [sys.executable, '-B', ROOT / 'examples/local_flow.py']),
                      run('M08-steps', [sys.executable, '-B', ROOT / 'paso_a_paso.py',
                                       '--directorio', lab, '--todo'])]
            checks.append(run('M08-no-overwrite', [sys.executable, '-B', ROOT / 'paso_a_paso.py',
                               '--directorio', lab, '--paso', '1'], expected_code=1))
            checks.append(run('M08-order', [sys.executable, '-B', ROOT / 'paso_a_paso.py',
                               '--directorio', lab, '--paso', '10'], expected_code=1))
            result = {'passed': all(x['passed'] for x in checks), 'commands': checks,
                      'simulation': True, 'manual_review_performed': False}
        else:
            title, methods = MODULES[module]
            names = [PREFIX + method for method in methods]
            expected = len(names)
            if module == 'M07':
                names.append('test_hyperion')
                expected += 42
            result = run(module, [sys.executable, '-B', '-m', 'unittest', '-v', *names],
                         expected_tests=expected)
            result['title'] = title
        report['modules'][module] = result
        print(f"{'PASS' if result['passed'] else 'FAIL'} {module}", flush=True)
        if not result['passed']:
            break
    report['passed'] = (len(report['modules']) == len(selected) and
                        all(x['passed'] for x in report['modules'].values()))
    (out / 'resultado.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(f"Evidencia: {out / 'resultado.json'}")
    return 0 if report['passed'] else 1

if __name__ == '__main__':
    sys.exit(main())
