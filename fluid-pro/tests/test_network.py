import sys
sys.path.insert(0, "src")
from fluid_network.toml_loader import load_network
from fluid_network.solver import solve
from fluid_network.analyzer import analyze

def network(): return load_network("examples/demo_network.toml")
def test_closed_valve_zero_flow_and_unreachable():
 n=network(); s=solve(n,n.resolve_scenario("cooling_off"),"cooling_off"); r=analyze(n,n.resolve_scenario("cooling_off"),s)
 assert s.edge_results["cooling_branch"]["enabled"] is False
 assert s.edge_results["cooling_branch"]["flow_m3s"] == 0
 assert r["functions"][0]["functional"] is False

def test_mass_balance():
 n=network(); s=solve(n,n.resolve_scenario("normal"),"normal")
 incoming=s.edge_results["main"]["flow_m3s"]
 outgoing=s.edge_results["cooling_branch"]["flow_m3s"]+s.edge_results["process_branch"]["flow_m3s"]
 assert abs(incoming-outgoing) < 1e-8

def test_export_shape():
 n=network(); s=solve(n,n.resolve_scenario("normal"),"normal"); report=analyze(n,n.resolve_scenario("normal"),s)
 assert report["reliability"] == 1.0
 assert set(s.edge_results) == {"main","cooling_branch","process_branch"}
