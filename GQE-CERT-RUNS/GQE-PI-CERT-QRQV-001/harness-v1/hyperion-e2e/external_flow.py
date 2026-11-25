"""Opt-in local Git delivery flow. Trusted local state, not a security sandbox."""
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import uuid


MODE = 'hyperion.external.v1'
COMMANDS = {'freeze', 'deliver', 'validate', 'review'}
BINDING = ('delivery_id', 'contract_hash', 'repository', 'base_commit', 'commit', 'tree')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def atomic_write(path, content):
    """Atomic replacement per file; no multi-file transaction or writer locking."""
    path = Path(path)
    temp = tempfile.NamedTemporaryFile(dir=path.parent, prefix='.' + path.name + '.',
                                       suffix='.tmp', delete=False)
    try:
        temp.write(content)
        temp.flush()
        os.fsync(temp.fileno())
        temp.close()
        os.replace(temp.name, path)
    except BaseException:
        temp.close()
        Path(temp.name).unlink(missing_ok=True)
        raise


def save_json(path, value):
    atomic_write(path, (json.dumps(value, indent=2, ensure_ascii=True) + '\n').encode())


def digest(content):
    return hashlib.sha256(content).hexdigest()


def contract_hash(contract):
    return digest(json.dumps(contract, sort_keys=True, separators=(',', ':'),
                             ensure_ascii=True).encode())


def nonblank(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + ' must not be blank')
    return value.strip()


def outside(path, repo):
    resolved = Path(path).resolve()
    if resolved.is_relative_to(repo):
        raise ValueError('state and acceptance must be outside target repository')
    return resolved


def exact_path(value):
    path = PurePosixPath(value)
    if (not value or not path.parts or path.is_absolute() or str(path) != value
            or any(p in ('.', '..', '.git') for p in path.parts)
            or any(c in value for c in '*?[]\\\x00')):
        raise ValueError('authorized paths must be exact repository-relative files')
    return value


def git(repo, *args):
    # No shell, no user-supplied options; replacement objects cannot alter identity.
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
               GIT_TERMINAL_PROMPT='0', GIT_NO_REPLACE_OBJECTS='1')
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True,
                            timeout=10, env=env)
    if result.returncode:
        raise ValueError('Git could not resolve or read requested repository object')
    return result.stdout


def repository(path):
    root = Path(git(path, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
    common = Path(git(root, 'rev-parse', '--path-format=absolute',
                      '--git-common-dir').decode().strip()).resolve()
    return {'root': str(root), 'git_common_dir': str(common)}


def resolve(repo, ref):
    ref = nonblank(ref, 'commit')
    if ref.startswith('-'):
        raise ValueError('invalid commit reference')
    commit = git(repo, 'rev-parse', '--verify', '--end-of-options', ref + '^{commit}').decode().strip()
    tree = git(repo, 'rev-parse', '--verify', '--end-of-options', commit + '^{tree}').decode().strip()
    return commit, tree


def is_external(task_file):
    path = Path(task_file)
    if Path(str(path) + '.d').exists():
        return True
    if path.exists():
        try:
            data = read_json(path)
        except (OSError, ValueError):
            # Legacy init intentionally permits replacement of non-JSON files.
            # A reserved external state directory above still blocks replacement.
            return False
        return isinstance(data, dict) and data.get('mode') == MODE
    return False


def reject_legacy(task_file):
    if is_external(task_file):
        print('Error: external tasks require deliver/validate/review; contract is frozen',
              file=sys.stderr)
        return True
    return False


def add_parsers(subparsers):
    freeze = subparsers.add_parser('freeze', help='Freeze an external Git task contract')
    for name in ('repo', 'base', 'task-id', 'task-version', 'objective',
                 'acceptance', 'acceptance-id'):
        freeze.add_argument('--' + name, required=True)
    freeze.add_argument('--allow', nargs='+', required=True)
    deliver = subparsers.add_parser('deliver', help='Record a resolved candidate commit')
    deliver.add_argument('--commit', required=True)
    deliver.add_argument('--executor', required=True)
    validate = subparsers.add_parser('validate', help='Run frozen acceptance on current delivery')
    validate.add_argument('--timeout', type=float, default=10,
                          help='Acceptance timeout in seconds, >0 and <=30 (default 10)')
    review = subparsers.add_parser('review', help='Record separate manual review')
    review.add_argument('--delivery-id', required=True)
    review.add_argument('--reviewer', required=True)
    review.add_argument('--decision', choices=['approve', 'changes_requested'], required=True)
    review.add_argument('--rationale', required=True)


def freeze(args):
    identity = repository(args.repo)
    repo = Path(identity['root'])
    marker = outside(args.task_file, repo)
    directory = outside(str(marker) + '.d', repo)
    source = outside(args.acceptance, repo)
    if marker.exists() or directory.exists():
        raise ValueError('task already exists; frozen tasks cannot be overwritten or reused')
    acceptance_bytes = source.read_bytes()
    base, _ = resolve(repo, args.base)
    contract = {
        'schema_version': 1,
        'task_id': nonblank(args.task_id, 'task ID'),
        'task_version': nonblank(args.task_version, 'task version'),
        'repository': identity,
        'base_commit': base,
        'objective': nonblank(args.objective, 'objective'),
        'authorized_paths': sorted(set(exact_path(p) for p in args.allow)),
        'acceptance': {'id': nonblank(args.acceptance_id, 'acceptance ID'),
                       'sha256': digest(acceptance_bytes),
                       'path': str(directory / 'acceptance.py')},
        'review_required': True,
    }
    # All ordinary input validation precedes persistence. Partial I/O failures leave
    # a reserved directory, deliberately not eligible for silent reuse.
    directory.mkdir()
    atomic_write(directory / 'acceptance.py', acceptance_bytes)
    save_json(directory / 'contract.json', {'contract': contract,
                                          'contract_hash': contract_hash(contract)})
    save_json(directory / 'deliveries.json', [])
    save_json(directory / 'evidence.json', [])
    save_json(marker, {'mode': MODE, 'state_dir': str(directory)})


def load(task_file):
    marker = Path(task_file).resolve()
    data = read_json(marker)
    if data.get('mode') != MODE:
        raise ValueError('not an external task')
    directory = Path(data['state_dir']).resolve()
    frozen = read_json(directory / 'contract.json')
    contract = frozen['contract']
    if frozen['contract_hash'] != contract_hash(contract):
        raise ValueError('frozen contract hash mismatch')
    identity = repository(contract['repository']['root'])
    if identity != contract['repository']:
        raise ValueError('repository identity changed')
    repo = Path(identity['root'])
    outside(marker, repo)
    outside(directory, repo)
    for name in ('contract.json', 'deliveries.json', 'evidence.json'):
        outside(directory / name, repo)
    acceptance = outside(contract['acceptance']['path'], repo)
    if digest(acceptance.read_bytes()) != contract['acceptance']['sha256']:
        raise ValueError('frozen acceptance hash mismatch')
    return directory, frozen, read_json(directory / 'deliveries.json'), read_json(directory / 'evidence.json')


def binding(delivery):
    return {key: delivery[key] for key in BINDING}


def scope(contract, commit):
    changed = git(contract['repository']['root'], 'diff', '--no-ext-diff',
                  '--no-textconv', '--no-renames', '--name-only', '-z',
                  contract['base_commit'], commit, '--').split(b'\0')
    paths = sorted(os.fsdecode(p) for p in changed if p)
    return paths, sorted(set(paths) - set(contract['authorized_paths']))


def deliver(args, directory, frozen, deliveries):
    contract = frozen['contract']
    executor = nonblank(args.executor, 'executor')
    commit, tree = resolve(contract['repository']['root'], args.commit)
    paths, unauthorized = scope(contract, commit)
    delivery = {'delivery_id': uuid.uuid4().hex, 'contract_hash': frozen['contract_hash'],
                'repository': contract['repository'], 'base_commit': contract['base_commit'],
                'commit': commit, 'tree': tree, 'executor': executor,
                'changed_paths': paths, 'unauthorized_paths': unauthorized}
    save_json(directory / 'deliveries.json', deliveries + [delivery])


def snapshot(repo, commit, destination):
    # Copy every blob from the resolved tree, including export-ignored files.
    # Do not follow symlinks or initialize submodules from an untrusted commit.
    entries = git(repo, 'ls-tree', '-rz', '--full-tree', commit).split(b'\0')
    for entry in entries:
        if not entry:
            continue
        metadata, name = entry.split(b'\t', 1)
        mode, kind, oid = metadata.split()
        relative = os.fsdecode(name)
        exact_path(relative)
        if kind != b'blob' or mode not in (b'100644', b'100755'):
            raise ValueError('snapshot supports regular files only (no symlinks/submodules)')
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(git(repo, 'cat-file', 'blob', oid.decode()))
        target.chmod(0o755 if mode == b'100755' else 0o644)


def validate(args, directory, frozen, deliveries, evidence):
    if not math.isfinite(args.timeout) or not 0 < args.timeout <= 30:
        raise ValueError('timeout must be greater than zero and at most 30 seconds')
    if not deliveries:
        raise ValueError('no current delivery')
    delivery = deliveries[-1]
    repo = delivery['repository']['root']
    commit, tree = resolve(repo, delivery['commit'])
    if (commit, tree) != (delivery['commit'], delivery['tree']):
        raise ValueError('delivery object identity mismatch')
    contract = frozen['contract']
    record = dict(binding(delivery), kind='acceptance', evidence_id=uuid.uuid4().hex,
                  acceptance_id=contract['acceptance']['id'],
                  acceptance_sha256=contract['acceptance']['sha256'], timeout=args.timeout)
    with tempfile.TemporaryDirectory(prefix='hyperion-snapshot-') as temp:
        destination = outside(temp, Path(repo))
        snapshot(repo, commit, destination)
        try:
            result = subprocess.run([sys.executable, '-I', '-B', contract['acceptance']['path']],
                                    cwd=destination, capture_output=True, timeout=args.timeout)
            record.update(exit_code=result.returncode, stdout=result.stdout.decode('utf-8', 'replace'),
                          stderr=result.stderr.decode('utf-8', 'replace'), timed_out=False)
        except subprocess.TimeoutExpired as exc:
            record.update(exit_code=None, stdout=(exc.stdout or b'').decode('utf-8', 'replace'),
                          stderr=(exc.stderr or b'').decode('utf-8', 'replace'), timed_out=True)
    # Recheck bytes after execution too; this is detection, not same-user protection.
    if digest(Path(contract['acceptance']['path']).read_bytes()) != contract['acceptance']['sha256']:
        raise ValueError('frozen acceptance hash mismatch after execution')
    save_json(directory / 'evidence.json', evidence + [record])


def review(args, directory, deliveries, evidence):
    reviewer = nonblank(args.reviewer, 'reviewer')
    rationale = nonblank(args.rationale, 'rationale')
    delivery = next((d for d in deliveries if d['delivery_id'] == args.delivery_id), None)
    if delivery is None:
        raise ValueError('unknown delivery ID')
    if reviewer == delivery['executor']:
        raise ValueError('reviewer must differ from executor')
    record = dict(binding(delivery), kind='review', evidence_id=uuid.uuid4().hex,
                  reviewer=reviewer, decision=args.decision, rationale=rationale)
    save_json(directory / 'evidence.json', evidence + [record])


def status(frozen, deliveries, evidence):
    delivery = deliveries[-1] if deliveries else None
    acceptance = review_record = None
    if delivery:
        matching = [e for e in evidence if all(e.get(k) == delivery[k] for k in BINDING)]
        acceptance = next((e for e in reversed(matching) if e['kind'] == 'acceptance'), None)
        review_record = next((e for e in reversed(matching) if e['kind'] == 'review'), None)
    state = 'PENDING_VALIDATION'
    if delivery and delivery['unauthorized_paths']:
        state = 'BLOCKED_SCOPE'
    elif ((acceptance and (acceptance['timed_out'] or acceptance['exit_code'] != 0))
          or (review_record and review_record['decision'] == 'changes_requested')):
        state = 'NEEDS_CORRECTION'
    elif (acceptance and review_record and review_record['decision'] == 'approve'
          and review_record['reviewer'].strip()
          and review_record['reviewer'] != delivery['executor']):
        state = 'DONE'
    return dict(frozen, state=state, delivery=delivery, acceptance=acceptance, review=review_record)


def run(args):
    try:
        if args.command == 'freeze':
            freeze(args)
        else:
            directory, frozen, deliveries, evidence = load(args.task_file)
            if args.command == 'deliver':
                deliver(args, directory, frozen, deliveries)
            elif args.command == 'validate':
                validate(args, directory, frozen, deliveries, evidence)
            elif args.command == 'review':
                review(args, directory, deliveries, evidence)
        _, frozen, deliveries, evidence = load(args.task_file)
        print(json.dumps(status(frozen, deliveries, evidence), ensure_ascii=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print('Error: ' + str(exc), file=sys.stderr)
        return 1
