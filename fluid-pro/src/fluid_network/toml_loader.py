from __future__ import annotations
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 and earlier
    import tomli as tomllib
from pathlib import Path
import math
from .model import Network, Node, Edge, Control, Scenario

def _req(d, key, path):
    if key not in d: raise ValueError(f"missing {path}.{key}")
    return d[key]

def load_network(path: str | Path) -> Network:
    with open(path, "rb") as f: raw = tomllib.load(f)
    meta, fluid = raw.get("meta", {}), raw.get("fluid", {})
    nodes = tuple(Node(id=_req(x,"id",f"nodes[{i}]"), type=x.get("type","junction"),
        pressure_pa=x.get("pressure_pa"), min_flow_m3s=x.get("min_flow_m3s",0.0),
        min_pressure_pa=x.get("min_pressure_pa",0.0), function=x.get("function"))
        for i,x in enumerate(raw.get("nodes", [])))
    edges = tuple(Edge(id=_req(x,"id",f"edges[{i}]"), from_node=_req(x,"from",f"edges[{i}]"),
        to_node=_req(x,"to",f"edges[{i}]"), resistance=float(_req(x,"resistance",f"edges[{i}]")),
        model=x.get("model","quadratic"), diameter_m=x.get("diameter_m"), enabled=x.get("enabled",True))
        for i,x in enumerate(raw.get("edges", [])))
    controls = tuple(Control(id=_req(x,"id",f"controls[{i}]"), kind=x.get("kind","switch"),
        target_ids=tuple(x.get("target_ids", [])), states=tuple(x.get("states", [])), default=x.get("default"))
        for i,x in enumerate(raw.get("controls", [])))
    scenarios = tuple(Scenario(id=_req(x,"id",f"scenarios[{i}]"), description=x.get("description",""),
        set=dict(x.get("set", {})), extends=x.get("extends")) for i,x in enumerate(raw.get("scenarios", [])))
    network = Network(meta.get("name", "fluid-network"), float(fluid.get("density_kg_m3",1000.0)), nodes, edges, controls, scenarios)
    _validate(network)
    return network

def _validate(n: Network):
    def unique(items, label):
        ids=[x.id for x in items]
        if len(ids)!=len(set(ids)): raise ValueError(f"duplicate {label} id")
    unique(n.nodes,"node"); unique(n.edges,"edge"); unique(n.controls,"control"); unique(n.scenarios,"scenario")
    def finite(value, name, positive=False):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number")
        if positive and value <= 0: raise ValueError(f"{name} must be positive")
    if not n.nodes: raise ValueError("nodes must not be empty")
    for items in (n.nodes, n.edges, n.controls, n.scenarios):
        for item in items:
            if not isinstance(item.id, str) or not item.id.strip(): raise ValueError("id must be a nonempty string")
    finite(n.density_kg_m3, "density", True)
    for node in n.nodes:
        if node.type not in ("source", "pump", "junction", "load"): raise ValueError("invalid node type")
        if node.pressure_pa is not None: finite(node.pressure_pa, "pressure")
        if node.type in ("source", "pump") and node.pressure_pa is None: raise ValueError("source/pump requires pressure_pa")
        finite(node.min_flow_m3s, "flow threshold")
        finite(node.min_pressure_pa, "pressure threshold")
        if node.min_flow_m3s < 0: raise ValueError("flow threshold must be nonnegative")
    node_ids=set(n.node_map)
    for e in n.edges:
        finite(e.resistance, "resistance", True)
        if e.diameter_m is not None: finite(e.diameter_m, "diameter", True)
        if not isinstance(e.enabled, bool): raise ValueError("enabled must be boolean")
        if e.from_node == e.to_node: raise ValueError("self loops are unsupported")
        if e.from_node not in node_ids or e.to_node not in node_ids: raise ValueError(f"edge {e.id} references unknown node")
        if e.resistance <= 0: raise ValueError(f"edge {e.id} resistance must be positive")
        if e.model not in ("linear","quadratic"): raise ValueError(f"edge {e.id} has invalid model")
    for c in n.controls:
        if c.default not in c.states: raise ValueError(f"control {c.id} default not in states")
        if any(x not in n.edge_map for x in c.target_ids): raise ValueError(f"control {c.id} references unknown edge")
    for s in n.scenarios:
        for cid,state in s.set.items():
            if cid not in n.control_map: raise ValueError(f"scenario {s.id} references unknown control {cid}")
            if state not in n.control_map[cid].states: raise ValueError(f"invalid state {cid}={state}")

    for scenario in n.scenarios:
        if scenario.extends and scenario.extends not in n.scenario_map: raise ValueError("unknown parent scenario")
        n.resolve_scenario(scenario.id)
