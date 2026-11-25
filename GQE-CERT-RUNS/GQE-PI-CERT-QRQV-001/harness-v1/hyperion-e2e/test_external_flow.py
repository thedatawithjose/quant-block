"""Public-CLI acceptance and rejection checks; no fabricated passing evidence."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).resolve().with_name("hyperion.py")
BUG = "def slugify(text):\n    return text.lower().replace(' ', '-')\n"
FIX = "def slugify(text):\n    return '-'.join(text.lower().split())\n"
ACCEPTANCE = """from pathlib import Path
import runpy
slugify = runpy.run_path(str(Path('src/notes/slug.py')))['slugify']
assert slugify('   ') == '', 'whitespace must be empty'
assert slugify('Hello World') == 'hello-world', 'Hello World regression'
print('both slug assertions passed')
"""


class ExternalCLI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.task = self.root / 'task.json'
        self.acceptance = self.root / 'accept.py'
        self.acceptance.write_text(ACCEPTANCE)
        self.git('init', '-q')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'user.name', 'Fixture')
        self.put('src/notes/slug.py', BUG)
        self.put('tests/test_slug.py', '# executor tests are not acceptance\n')
        self.put('README.md', 'unchanged\n')
        self.base = self.commit('base')

    def git(self, *args):
        result = subprocess.run(['git', '-C', str(self.repo), *args],
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def put(self, name, text):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def commit(self, message):
        self.git('add', '-A')
        self.git('commit', '-qm', message)
        return self.git('rev-parse', 'HEAD')

    def raw(self, *args, task=None):
        return subprocess.run([sys.executable, '-B', str(CLI), '--task-file',
                               str(task or self.task), *map(str, args)],
                              capture_output=True, text=True, timeout=5)

    def cli(self, *args, task=None):
        result = self.raw(*args, task=task)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        return json.loads(result.stdout)

    def freeze_args(self):
        return ['freeze', '--repo', self.repo, '--base', self.base,
                '--task-id', 'slug', '--task-version', '1', '--objective',
                'Fix whitespace without changing Hello World', '--allow',
                'src/notes/slug.py', 'tests/test_slug.py', '--acceptance',
                self.acceptance, '--acceptance-id', 'slug-acceptance']

    def freeze(self):
        return self.cli(*self.freeze_args())

    def deliver(self, commit=None):
        return self.cli('deliver', '--commit', commit or self.base,
                        '--executor', 'worker')['delivery']

    def validate(self):
        return self.cli('validate', '--timeout', '2')

    def review(self, delivery, decision='approve', reviewer='human'):
        return self.cli('review', '--delivery-id', delivery['delivery_id'],
                        '--reviewer', reviewer, '--decision', decision,
                        '--rationale', 'Inspected exact candidate and acceptance')

    def corrected(self):
        self.put('src/notes/slug.py', FIX)
        return self.commit('fix')

    def persisted(self):
        paths = [self.task]
        directory = Path(str(self.task) + '.d')
        if directory.exists():
            paths += sorted(directory.rglob('*'))
        return {str(p): p.read_bytes() for p in paths if p.is_file()}

    def reject(self, *args, task=None):
        before = self.persisted()
        result = self.raw(*args, task=task)
        self.assertEqual(result.returncode, 1, (result.stdout, result.stderr))
        self.assertEqual(result.stdout, '')
        self.assertTrue(result.stderr.startswith('Error: '), result.stderr)
        self.assertEqual(self.persisted(), before)
        return result.stderr

    def test_frozen_contract_is_canonical_and_cannot_be_replaced(self):
        frozen = self.freeze()
        contract = frozen['contract']
        encoded = json.dumps(contract, sort_keys=True, separators=(',', ':'),
                             ensure_ascii=True).encode()
        self.assertEqual(frozen['contract_hash'], hashlib.sha256(encoded).hexdigest())
        self.assertEqual(contract['base_commit'], self.base)
        self.assertEqual(contract['schema_version'], 1)
        self.assertEqual(contract['task_id'], 'slug')
        self.assertEqual(contract['task_version'], '1')
        self.assertEqual(contract['repository']['root'], str(self.repo.resolve()))
        self.assertTrue(contract['review_required'])
        self.assertEqual(contract['acceptance']['sha256'],
                         hashlib.sha256(ACCEPTANCE.encode()).hexdigest())
        self.reject(*self.freeze_args())
        for args in [('init', '--title', 'bypass', '--objective', 'x', '--done', 'x'),
                     ('propose', '--description', 'bypass', '--problem', 'x'),
                     ('submit', self.root / 'forged.json')]:
            self.reject(*args)

    def test_base_fails_expected_assertion_and_corrected_candidate_passes(self):
        self.freeze()
        self.deliver()
        failed = self.validate()
        self.assertEqual(failed['state'], 'NEEDS_CORRECTION')
        self.assertNotEqual(failed['acceptance']['exit_code'], 0)
        self.assertIn('whitespace must be empty', failed['acceptance']['stderr'])
        current = self.deliver(self.corrected())
        passed = self.validate()
        self.assertEqual(passed['state'], 'PENDING_VALIDATION')
        self.assertEqual(passed['acceptance']['stdout'], 'both slug assertions passed\n')
        self.assertEqual(passed['acceptance']['exit_code'], 0)
        self.assertEqual(self.review(current)['state'], 'DONE')
        self.assertEqual(self.cli('status')['state'], 'DONE')

    def test_missing_evidence_review_changes_and_fresh_delivery_same_commit(self):
        self.freeze()
        delivery = self.deliver(self.corrected())
        self.assertEqual(self.cli('status')['state'], 'PENDING_VALIDATION')
        self.assertEqual(self.review(delivery, 'changes_requested')['state'], 'NEEDS_CORRECTION')
        self.validate()
        self.assertEqual(self.review(delivery)['state'], 'DONE')
        newer = self.deliver(delivery['commit'])
        self.assertNotEqual(newer['delivery_id'], delivery['delivery_id'])
        self.assertEqual(self.cli('status')['state'], 'PENDING_VALIDATION')
        self.assertEqual(self.validate()['state'], 'PENDING_VALIDATION')
        self.assertEqual(self.review(delivery)['state'], 'PENDING_VALIDATION')
        self.assertEqual(self.review(newer)['state'], 'DONE')
        marker = json.loads(self.task.read_text())
        history = json.loads((Path(marker['state_dir']) / 'deliveries.json').read_text())
        evidence = json.loads((Path(marker['state_dir']) / 'evidence.json').read_text())
        self.assertEqual(len(history), 2)
        self.assertEqual(len([e for e in evidence if e['kind'] == 'acceptance']), 2)

    def test_scope_precedes_passing_acceptance_and_approval(self):
        self.freeze()
        self.corrected()
        self.put('README.md', 'unauthorized\n')
        delivery = self.deliver(self.commit('out of scope'))
        result = self.validate()
        self.assertEqual(result['acceptance']['exit_code'], 0)
        self.assertEqual(self.review(delivery)['state'], 'BLOCKED_SCOPE')
        self.assertIn('README.md', result['delivery']['unauthorized_paths'])

    def test_deleted_and_renamed_old_and_new_paths_are_checked(self):
        self.freeze()
        self.corrected()
        self.git('mv', 'README.md', 'tests/renamed.md')
        delivery = self.deliver(self.commit('rename'))
        self.assertEqual(delivery['unauthorized_paths'], ['README.md', 'tests/renamed.md'])
        self.assertEqual(self.validate()['state'], 'BLOCKED_SCOPE')

    def test_deleted_unauthorized_path_is_blocked(self):
        self.freeze()
        (self.repo / 'README.md').unlink()
        self.deliver(self.commit('delete'))
        self.assertEqual(self.validate()['state'], 'BLOCKED_SCOPE')

    def test_snapshot_not_dirty_worktree_or_moving_ref(self):
        self.freeze()
        self.deliver('HEAD')
        self.corrected()
        self.assertEqual(self.validate()['state'], 'NEEDS_CORRECTION')
        delivery = self.deliver('HEAD')
        self.put('src/notes/slug.py', 'raise RuntimeError("dirty worktree")\n')
        self.assertEqual(self.validate()['acceptance']['exit_code'], 0)
        result = self.review(delivery)
        self.assertEqual(result['state'], 'DONE')
        for key in ('delivery_id', 'contract_hash', 'repository', 'base_commit', 'commit', 'tree'):
            self.assertEqual(result['acceptance'][key], result['delivery'][key])

    def test_blank_and_self_review_and_unknown_delivery_rejected_without_writes(self):
        self.freeze()
        delivery = self.deliver()
        for reviewer in ('', '  ', 'worker', ' worker '):
            self.reject('review', '--delivery-id', delivery['delivery_id'],
                        '--reviewer', reviewer, '--decision', 'approve', '--rationale', 'ok')
        self.reject('review', '--delivery-id', 'missing', '--reviewer', 'human',
                    '--decision', 'approve', '--rationale', 'ok')
        self.reject('review', '--delivery-id', delivery['delivery_id'], '--reviewer', 'human',
                    '--decision', 'approve', '--rationale', ' ')

    def test_unknown_malformed_refs_and_blank_executor_rejected(self):
        self.freeze()
        for ref in ('unknown-ref', '--help', 'HEAD^{tree}', 'HEAD:src', ' '):
            self.reject('deliver', '--commit=' + ref, '--executor', 'worker')
        self.reject('deliver', '--commit', self.base, '--executor', ' ')
        self.reject('validate', '--timeout', '2')

    def test_state_and_acceptance_must_be_outside_canonical_repo(self):
        self.reject(*self.freeze_args(), task=self.repo / 'task.json')
        alias = self.root / 'repo-alias'
        alias.symlink_to(self.repo, target_is_directory=True)
        self.reject(*self.freeze_args(), task=alias / 'task.json')
        inside = self.repo / 'accept.py'
        inside.write_text(ACCEPTANCE)
        self.acceptance.unlink()
        self.acceptance.symlink_to(inside)
        self.reject(*self.freeze_args())

    def test_exact_authorized_paths_only(self):
        args = self.freeze_args()
        index = args.index('src/notes/slug.py')
        for path in ('../escape', '/absolute', 'src/../README.md', 'src/**', 'src/', '.'):
            changed = list(args)
            changed[index] = path
            self.reject(*changed)

    def test_frozen_acceptance_bytes_checked_and_original_not_reused(self):
        result = self.freeze()
        self.acceptance.write_text('raise RuntimeError("changed original")\n')
        self.deliver(self.corrected())
        self.assertEqual(self.validate()['acceptance']['exit_code'], 0)
        frozen = Path(result['contract']['acceptance']['path'])
        frozen.write_text('print("forged")\n')
        self.reject('validate', '--timeout', '2')
        self.reject('status')

    def test_acceptance_timeout_is_bound_failure(self):
        self.acceptance.write_text('import time\nprint("started", flush=True)\ntime.sleep(2)\n')
        self.freeze()
        self.deliver()
        result = self.cli('validate', '--timeout', '0.05')
        self.assertEqual(result['state'], 'NEEDS_CORRECTION')
        self.assertTrue(result['acceptance']['timed_out'])
        self.assertIsNone(result['acceptance']['exit_code'])
        self.assertIn('started', result['acceptance']['stdout'])

    def test_legacy_init_can_still_replace_non_json_file(self):
        self.task.write_text('legacy init historically overwrites this')
        result = self.raw('init', '--title', 'Legacy', '--objective', 'Keep behavior',
                          '--done', 'C1')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        self.assertIn('Task initialized: Legacy', result.stdout)
        self.assertEqual(json.loads(self.task.read_text())['state'], 'DEFINED')

    def test_invalid_contract_inputs_no_reuse_or_writes(self):
        args = self.freeze_args()
        for flag, value in (('--base', 'not-a-ref'), ('--task-id', ' '),
                            ('--objective', ' '), ('--acceptance-id', ' ')):
            changed = list(args)
            changed[changed.index(flag) + 1] = value
            self.reject(*changed)
        self.freeze()
        self.reject('validate', '--timeout', '0')


if __name__ == '__main__':
    unittest.main()
