"""Run inside a fresh Python container; /input is a clean, read-only checkout."""
import functools
import http.server
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.request


def run(*args, cwd=None):
    result = subprocess.run(args, cwd=cwd, check=True, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout.strip(), flush=True)
    return result.stdout


root = Path('/tmp/skill-install-verification')
project = root / 'project'
skill = root / 'skills' / 'fluid-network'
work = root / 'work'
shutil.copytree('/input', project, ignore=shutil.ignore_patterns(
    '.git', '.venv', '__pycache__', '*.egg-info', '.pytest_cache', 'build', 'dist'))
shutil.copytree(project / 'skill', skill)
work.mkdir(parents=True)
assert not os.environ.get('PYTHONPATH'), 'Unexpected host PYTHONPATH'
run(sys.executable, '-m', 'pip', 'install', '--no-cache-dir', '-e', str(project))
os.chdir(work)

# Verify local references from the installed Skill package.
text = (skill / 'SKILL.md').read_text()
assert text.startswith('---\nname: fluid-network\ndescription:')
for target in re.findall(r'\]\(([^)]+)\)', text):
    if '://' not in target:
        assert (skill / target).is_file(), target
shutil.copy2(skill / 'assets/demo_network.toml', work / 'network.toml')
run('fluid-network', 'validate', 'network.toml')
run('fluid-network', 'solve', 'network.toml', '--scenario', 'normal', '--json', 'solution.json')
run('fluid-network', 'analyze', 'network.toml', '--scenario', 'normal', '--json', 'normal.json')
run('fluid-network', 'analyze', 'network.toml', '--scenario', 'cooling_off', '--json', 'closed.json')
run('fluid-network', 'export', 'network.toml', '--out', 'data')
normal = json.loads(Path('normal.json').read_text())
closed = json.loads(Path('closed.json').read_text())
assert normal['solution']['converged'] and normal['reliability'] == 1.0
assert closed['reliability'] == 0.5
cooling = next(f for f in closed['functions'] if f['node'] == 'cooling')
assert not cooling['reachable'] and cooling['flow_m3s'] == 0
baseline = json.loads((project / 'examples/expected_demo_result.json').read_text())
for sid, result in [('normal', normal), ('cooling_off', closed)]:
    for eid, flow in baseline['scenarios'][sid]['flows_m3s'].items():
        assert math.isclose(result['solution']['edges'][eid]['flow_m3s'], flow, rel_tol=1e-6, abs_tol=1e-10)
assert json.loads(Path('data/index.json').read_text())['scenarios'] == ['normal', 'cooling_off']

# Export through the project's documented static-view workflow.
run('fluid-network', 'export', str(work / 'network.toml'), '--out', 'web/data', cwd=project)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(project / 'web'))
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
url = f'http://127.0.0.1:{server.server_port}'
try:
    for path in ('/', '/app.js', '/styles.css', '/data/index.json', '/data/normal.json'):
        with urllib.request.urlopen(url + path) as response:
            assert response.status == 200
finally:
    server.shutdown()
    server.server_close()

api = subprocess.Popen([sys.executable, 'backend_server.py', '--port', '18080'], cwd=project)
try:
    for _ in range(40):
        try:
            with urllib.request.urlopen('http://127.0.0.1:18080/api/health', timeout=1) as response:
                assert json.load(response)['status'] == 'ok'
            break
        except OSError:
            if api.poll() is not None: raise RuntimeError('API exited unexpectedly')
            time.sleep(0.25)
    else:
        raise RuntimeError('API startup timeout')
    with urllib.request.urlopen('http://127.0.0.1:18080/api/scenarios/normal?cooling_valve=closed') as response:
        assert json.load(response)['reliability'] == 0.5
finally:
    api.terminate()
    api.wait(timeout=5)

print('PASS: isolated Skill references, editable install, CLI, independent analytic baseline, static HTTP, live API', flush=True)
