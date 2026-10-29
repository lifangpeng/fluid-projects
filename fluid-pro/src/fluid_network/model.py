from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import math

@dataclass(frozen=True)
class Node:
    id: str
    type: str = "junction"
    pressure_pa: float | None = None
    min_flow_m3s: float = 0.0
    min_pressure_pa: float = 0.0
    function: str | None = None

@dataclass(frozen=True)
class Edge:
    id: str
    from_node: str
    to_node: str
    resistance: float
    model: str = "quadratic"
    diameter_m: float | None = None
    enabled: bool = True

@dataclass(frozen=True)
class Control:
    id: str
    kind: str
    target_ids: tuple[str, ...]
    states: tuple[str, ...]
    default: str

@dataclass(frozen=True)
class Scenario:
    id: str
    description: str = ""
    set: dict[str, str] = field(default_factory=dict)
    extends: str | None = None

@dataclass(frozen=True)
class Network:
    name: str
    density_kg_m3: float
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]
    controls: tuple[Control, ...]
    scenarios: tuple[Scenario, ...]

    @property
    def node_map(self): return {x.id: x for x in self.nodes}
    @property
    def edge_map(self): return {x.id: x for x in self.edges}
    @property
    def control_map(self): return {x.id: x for x in self.controls}
    @property
    def scenario_map(self): return {x.id: x for x in self.scenarios}

    def resolve_scenario(self, scenario_id: str) -> dict[str, str]:
        if scenario_id not in self.scenario_map:
            raise ValueError(f"unknown scenario: {scenario_id}")
        def merge(sid, seen):
            if sid in seen: raise ValueError("scenario inheritance cycle")
            s = self.scenario_map[sid]
            result = merge(s.extends, seen | {sid}) if s.extends else {}
            result.update(s.set)
            return result
        result = {c.id: c.default for c in self.controls}
        result.update(merge(scenario_id, set()))
        return result

@dataclass
class Solution:
    scenario: str
    converged: bool
    iterations: int
    residual: float
    node_pressures_pa: dict[str, float]
    edge_results: dict[str, dict[str, Any]]
    warnings: list[str] = field(default_factory=list)

    def to_dict(self):
        return {"scenario": self.scenario, "converged": self.converged,
                "iterations": self.iterations, "residual": self.residual if math.isfinite(self.residual) else None,
                "nodes": self.node_pressures_pa, "edges": self.edge_results,
                "warnings": self.warnings}
