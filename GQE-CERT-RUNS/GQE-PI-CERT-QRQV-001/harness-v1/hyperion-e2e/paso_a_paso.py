"""Laboratorio persistente; todas las identidades y revisiones son simuladas."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'examples'))
from local_flow import BUG, FIX, ACCEPTANCE

TITLES = {
    1: 'Contrato congelado', 2: 'Base defectuosa rechazada',
    3: 'Correccion sin evidencia pendiente', 4: 'Aceptacion sin revision pendiente',
    5: 'Autorrevision rechazada sin escritura', 6: 'Revision pide cambios',
    7: 'Entrega aprobada con evidencia actual', 8: 'Nueva entrega invalida evidencia',
    9: 'Revision anterior no cierra entrega nueva', 10: 'Entrega nueva aprobada',
    11: 'Cambio fuera de alcance bloqueado', 12: 'Estado reconstruido al reabrir',
}

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def execute(root, number):
    manifest = root / 'laboratorio.json'
    if number == 1:
        require(not root.exists(), 'El directorio ya existe. Elige uno nuevo; no se sobrescribe.')
        root.mkdir(parents=True)
        state = {'format': 'hyperion-lab-demo-v1', 'completed': 0, 'simulation': True}
    else:
        state = json.loads(manifest.read_text(encoding='utf-8'))
        require(state.get('format') == 'hyperion-lab-demo-v1', 'No es un laboratorio de esta guia.')
    require(state['completed'] == number - 1, 'Ejecuta los pasos en orden, una sola vez.')
    require(not (root / f'paso-{number:02}-FALLO.json').exists(),
            'Hubo un fallo parcial en este paso. Conserva evidencia y empieza en otra carpeta.')
    repo, task = root / 'repo', root / 'task.json'
    transcript = []

    def command(argv, expected_code=0):
        result = subprocess.run(list(map(str, argv)), capture_output=True, text=True,
                                timeout=15, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        transcript.append({'argv': list(map(str, argv)), 'exit_code': result.returncode,
                           'stdout': result.stdout, 'stderr': result.stderr})
        require(result.returncode == expected_code,
                f'Codigo inesperado: {result.returncode}; {result.stderr}')
        return result

    def git(*args):
        return command(['git', '-C', repo, *args]).stdout.strip()

    def commit(message):
        git('add', '-A')
        git('commit', '-qm', message)
        return git('rev-parse', 'HEAD')

    def cli(*args, expected_code=0):
        result = command([sys.executable, '-B', ROOT / 'hyperion.py', '--task-file', task, *args],
                         expected_code)
        return json.loads(result.stdout) if expected_code == 0 else result

    def deliver(candidate):
        return cli('deliver', '--commit', candidate, '--executor', 'ejecutor-simulado')

    def review(delivery, decision='approve', reviewer='revisor-simulado', expected_code=0):
        return cli('review', '--delivery-id', delivery, '--reviewer', reviewer,
                   '--decision', decision, '--rationale',
                   'SIMULACION automatica: prueba del gate; no es revision humana real.',
                   expected_code=expected_code)

    def hashes():
        return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in [task, *sorted((root / 'task.json.d').glob('*'))] if p.is_file()}

    def expect(result, expected):
        require(result['state'] == expected, f"Esperado {expected}; recibido {result['state']}")

    try:
        if number == 1:
            repo.mkdir()
            git('init', '-q')
            git('config', 'user.name', 'Hyperion laboratorio')
            git('config', 'user.email', 'lab@example.invalid')
            slug = repo / 'src/notes/slug.py'
            slug.parent.mkdir(parents=True)
            slug.write_text(BUG)
            (repo / 'tests').mkdir()
            (repo / 'tests/test_slug.py').write_text('# Fixture; oraculo externo congelado.\n')
            (repo / 'README.md').write_text('Fixture de laboratorio\n')
            state['base'] = commit('base defectuosa')
            acceptance = root / 'acceptance.py'
            acceptance.write_text(ACCEPTANCE)
            result = cli('freeze', '--repo', repo, '--base', state['base'], '--task-id', 'lab-slug',
                         '--task-version', '1', '--objective', 'Corregir espacios y preservar Hello World',
                         '--allow', 'src/notes/slug.py', 'tests/test_slug.py',
                         '--acceptance', acceptance, '--acceptance-id', 'slug-v1')
            expect(result, 'PENDING_VALIDATION')
            require(result['delivery'] is None, 'No debe existir entrega inicial.')
        elif number == 2:
            deliver(state['base'])
            result = cli('validate', '--timeout', '2')
            expect(result, 'NEEDS_CORRECTION')
            require('whitespace must be empty' in result['acceptance']['stderr'], 'Fallo equivocado.')
        elif number == 3:
            (repo / 'src/notes/slug.py').write_text(FIX)
            state['fixed'] = commit('corregir espacios')
            result = deliver(state['fixed'])
            state['delivery_one'] = result['delivery']['delivery_id']
            expect(result, 'PENDING_VALIDATION')
        elif number == 4:
            result = cli('validate', '--timeout', '2')
            expect(result, 'PENDING_VALIDATION')
            require(result['acceptance']['exit_code'] == 0, 'Aceptacion no paso.')
            require(result['acceptance']['stdout'] == 'both slug assertions passed\n', 'Salida inesperada.')
            require(result['review'] is None, 'No debe existir revision actual.')
        elif number == 5:
            before = hashes()
            rejected = review(state['delivery_one'], reviewer='ejecutor-simulado', expected_code=1)
            require('reviewer must differ' in rejected.stderr, 'Rechazo equivocado.')
            require(before == hashes(), 'El rechazo modifico el estado.')
            result = cli('status')
            expect(result, 'PENDING_VALIDATION')
        elif number == 6:
            result = review(state['delivery_one'], 'changes_requested')
            expect(result, 'NEEDS_CORRECTION')
        elif number == 7:
            result = review(state['delivery_one'])
            expect(result, 'DONE')
        elif number == 8:
            result = deliver(state['fixed'])
            state['delivery_two'] = result['delivery']['delivery_id']
            require(state['delivery_two'] != state['delivery_one'], 'UUID reutilizado.')
            expect(result, 'PENDING_VALIDATION')
            require(result['acceptance'] is None and result['review'] is None, 'Evidencia reutilizada.')
        elif number == 9:
            cli('validate', '--timeout', '2')
            result = review(state['delivery_one'])
            expect(result, 'PENDING_VALIDATION')
            require(result['review'] is None, 'Revision antigua aplicada a entrega nueva.')
        elif number == 10:
            result = review(state['delivery_two'])
            expect(result, 'DONE')
        elif number == 11:
            (repo / 'README.md').write_text('Modificacion no autorizada\n')
            delivery = deliver(commit('cambio fuera de alcance'))['delivery']['delivery_id']
            result = cli('validate', '--timeout', '2')
            require(result['acceptance']['exit_code'] == 0, 'La aceptacion funcional debe pasar.')
            result = review(delivery)
            expect(result, 'BLOCKED_SCOPE')
            require(result['delivery']['unauthorized_paths'] == ['README.md'], 'Alcance incorrecto.')
        elif number == 12:
            result = cli('status')
            expect(result, 'BLOCKED_SCOPE')
            for record in ('acceptance', 'review'):
                for field in ('delivery_id', 'contract_hash', 'repository', 'base_commit', 'commit', 'tree'):
                    require(result[record][field] == result['delivery'][field], 'Binding incorrecto.')
        state['completed'] = number
        save(root / f'paso-{number:02}.json', {'step': number, 'title': TITLES[number],
             'passed': True, 'simulation': True, 'result': result, 'commands': transcript})
        save(manifest, state)
        print(f"PASS {number:02}: {TITLES[number]} -> {result['state']}")
    except Exception as exc:
        save(root / f'paso-{number:02}-FALLO.json', {'step': number, 'passed': False,
             'error': str(exc), 'commands': transcript})
        raise

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directorio', type=Path, required=True)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--paso', type=int, choices=range(1, 13))
    choice.add_argument('--todo', action='store_true')
    choice.add_argument('--estado', action='store_true')
    args = parser.parse_args()
    root = args.directorio.resolve()
    if args.estado:
        print((root / 'laboratorio.json').read_text())
        return
    for number in (range(1, 13) if args.todo else [args.paso]):
        execute(root, number)

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
