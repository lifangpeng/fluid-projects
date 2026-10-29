import sys
sys.path.insert(0,"src")
from fluid_network.toml_loader import load_network
from fluid_network.solver import solve

def test_demo_converges():
 n=load_network("examples/demo_network.toml"); s=solve(n,n.resolve_scenario("normal"),"normal")
 assert s.converged
 assert s.edge_results["main"]["flow_m3s"]>0
