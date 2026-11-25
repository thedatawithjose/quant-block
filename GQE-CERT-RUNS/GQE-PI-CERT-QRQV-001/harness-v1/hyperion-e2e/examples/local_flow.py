"""Repeatable public-CLI demonstration; only a temporary repository is modified."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


CLI = Path(__file__).resolve().parents[1] / 'hyperion.py'
BUG = "def slugify(text):\n    return text.lower().replace(' ', '-')\n"
FIX = "def slugify(text):\n    return '-'.join(text.lower().split())\n"
ACCEPTANCE = """from pathlib import Path
import runpy
slugify = runpy.run_path(str(Path('src/notes/slug.py')))['slugify']
assert slugify('   ') == '', 'whitespace must be empty'
assert slugify('Hello World') == 'hello-world', 'Hello World regression'
print('both slug assertions passed')
"""


def main():
    with tempfile.TemporaryDirectory(prefix='hyperion-example-') as temp:
        root = Path(temp)
        repo = root / 'repo'
        repo.mkdir()
        task = root / 'task.json'
        acceptance = root / 'acceptance.py'
        acceptance.write_text(ACCEPTANCE)

        def command(argv):
            result = subprocess.run(list(map(str, argv)), capture_output=True,
                                    text=True, timeout=5,
                                    env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
            if result.returncode or result.stderr:
                raise RuntimeError(f'{argv}: {result.returncode}\n{result.stdout}\n{result.stderr}')
            return result.stdout.strip()

        def git(*args):
            return command(['git', '-C', repo, *args])

        def cli(*args):
            return json.loads(command([sys.executable, '-B', CLI, '--task-file', task, *args]))

        def commit(message):
            git('add', '-A')
            git('commit', '-qm', message)
            return git('rev-parse', 'HEAD')

        def deliver(candidate):
            return cli('deliver', '--commit', candidate, '--executor', 'local-worker')['delivery']

        def review(delivery, decision='approve'):
            return cli('review', '--delivery-id', delivery['delivery_id'],
                       '--reviewer', 'local-simulated-reviewer', '--decision', decision,
                       '--rationale', 'SIMULATION: automated gate test, not a real human review')

        def expect(label, expected, result):
            assert result['state'] == expected, (label, result)
            print(f'{label}: {result["state"]}')

        git('init', '-q')
        git('config', 'user.email', 'example@example.invalid')
        git('config', 'user.name', 'Temporary Example')
        slug = repo / 'src/notes/slug.py'
        slug.parent.mkdir(parents=True)
        slug.write_text(BUG)
        tests = repo / 'tests/test_slug.py'
        tests.parent.mkdir()
        tests.write_text("# Candidate tests are not the frozen acceptance oracle.\n")
        (repo / 'README.md').write_text('Temporary fixture\n')
        base = commit('base with whitespace bug')
        cli('freeze', '--repo', repo, '--base', base, '--task-id', 'slug-whitespace',
            '--task-version', '1', '--objective', 'Fix whitespace and preserve Hello World',
            '--allow', 'src/notes/slug.py', 'tests/test_slug.py',
            '--acceptance', acceptance, '--acceptance-id', 'slug-regression-v1')
        deliver(base)
        result = cli('validate', '--timeout', '2')
        assert result['acceptance']['exit_code'] != 0
        assert 'whitespace must be empty' in result['acceptance']['stderr']
        expect('Base fails expected whitespace assertion', 'NEEDS_CORRECTION', result)

        slug.write_text(FIX)
        fixed = commit('fix whitespace without Hello World regression')
        delivery = deliver(fixed)
        expect('Missing mandatory evidence', 'PENDING_VALIDATION', cli('status'))
        result = cli('validate', '--timeout', '2')
        assert result['acceptance']['exit_code'] == 0
        assert result['acceptance']['stdout'] == 'both slug assertions passed\n'
        print('Corrected acceptance (whitespace + unchanged Hello World): PASS')
        expect('Acceptance passes, review missing', 'PENDING_VALIDATION', result)
        expect('Review requests changes', 'NEEDS_CORRECTION', review(delivery, 'changes_requested'))
        expect('Exact current pass and distinct approval', 'DONE', review(delivery))

        newer = deliver(fixed)
        expect('New same-commit delivery needs fresh evidence', 'PENDING_VALIDATION', cli('status'))
        cli('validate', '--timeout', '2')
        expect('Stale old approval after new delivery', 'PENDING_VALIDATION', review(delivery))
        expect('New current approval', 'DONE', review(newer))

        (repo / 'README.md').write_text('Unauthorized change\n')
        out_of_scope = deliver(commit('fix plus unauthorized README change'))
        result = cli('validate', '--timeout', '2')
        assert result['acceptance']['exit_code'] == 0
        expect('Out-of-scope diff although acceptance passed', 'BLOCKED_SCOPE', review(out_of_scope))
        expect('Public status confirms scope-first verdict', 'BLOCKED_SCOPE', cli('status'))
        print('All demonstration state, acceptance files and repository are temporary.')


if __name__ == '__main__':
    main()
