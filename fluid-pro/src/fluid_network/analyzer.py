from collections import deque


def analyze(network, state, solution):
    """Reachability is from explicit sources; load flow means incoming flow."""
    sources = [n.id for n in network.nodes if n.type in ('source', 'pump')]
    adj = {n.id: [] for n in network.nodes}
    for eid, edge in solution.edge_results.items():
        if edge['enabled']:
            adj[edge['from']].append((edge['to'], eid))
            adj[edge['to']].append((edge['from'], eid))
    paths = {s: [] for s in sources}
    queue = deque(sources)
    while queue:
        u = queue.popleft()
        for v, eid in adj[u]:
            if v not in paths:
                paths[v] = paths[u] + [eid]
                queue.append(v)
    functions = []
    for node in network.nodes:
        if node.type != 'load':
            continue
        flow = sum(max(0.0, r['flow_m3s'] if r['to'] == node.id else -r['flow_m3s'])
                   for r in solution.edge_results.values()
                   if r['enabled'] and node.id in (r['from'], r['to']))
        pressure = solution.node_pressures_pa.get(node.id, 0.0)
        reason = ('solver_not_converged' if not solution.converged else
                  'unreachable' if node.id not in paths else
                  'below_flow_threshold' if flow < node.min_flow_m3s else
                  'below_pressure_threshold' if pressure < node.min_pressure_pa else None)
        functions.append(dict(node=node.id, function=node.function or node.id,
                              reachable=node.id in paths, flow_m3s=flow, pressure_pa=pressure,
                              min_flow_m3s=node.min_flow_m3s, min_pressure_pa=node.min_pressure_pa,
                              functional=reason is None, reason=reason,
                              topology_path=paths.get(node.id, [])))
    return dict(scenario=solution.scenario, functions=functions,
                reliability=sum(f['functional'] for f in functions)/len(functions) if functions else 1.0,
                reachable_nodes=sorted(paths), solution=solution.to_dict())
