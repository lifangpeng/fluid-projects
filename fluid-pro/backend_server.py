"""Same-origin static UI and read-only scenario calculation API."""
import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs, unquote
from fluid_network import load_network, solve, analyze

ROOT = Path(__file__).resolve().parent
NETWORK = load_network(ROOT / 'examples/demo_network.toml')


class Handler(SimpleHTTPRequestHandler):
    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == '/api/health':
            self.send_json({'status': 'ok', 'service': 'fluid-network'})
        elif url.path == '/api/network':
            self.send_json({'scenarios': [s.id for s in NETWORK.scenarios],
                            'controls': [{'id': c.id, 'states': c.states, 'default': c.default}
                                         for c in NETWORK.controls]})
        elif url.path.startswith('/api/scenarios/'):
            try:
                sid = unquote(url.path.rsplit('/', 1)[-1])
                state = NETWORK.resolve_scenario(sid)
                for key, values in parse_qs(url.query).items():
                    if key not in NETWORK.control_map or len(values) != 1 or values[0] not in NETWORK.control_map[key].states:
                        raise ValueError('unknown control or invalid state: ' + key)
                    state[key] = values[0]
                result = analyze(NETWORK, state, solve(NETWORK, state, sid))
                result['state'] = state
                self.send_json(result)
            except (ValueError, KeyError) as ex:
                self.send_json({'error': str(ex)}, 400)
        elif url.path.startswith('/api/'):
            self.send_json({'error': 'not found'}, 404)
        else:
            super().do_GET()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    ThreadingHTTPServer(('0.0.0.0', args.port), partial(Handler, directory=str(ROOT / 'web'))).serve_forever()
