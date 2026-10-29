import json
import math
import subprocess
import sys
from dataclasses import replace

import pytest
from fluid_network.model import Network, Node, Edge
from fluid_network.solver import solve
from fluid_network.analyzer import analyze
from fluid_network.toml_loader import load_network


@pytest.mark.parametrize('model,resistance,expected', [
    ('linear', 1e12, 4e-7), ('quadratic', 1e11, 0.002)])
def test_analytic_series(model, resistance, expected):
    n = Network('series',1000,(Node('s','source',800000), Node('j'),
                Node('l','load',0)),
                (Edge('a','s','j',resistance,model), Edge('b','j','l',resistance,model)),(),())
    s = solve(n,{})
    assert s.converged
    assert s.node_pressures_pa['j'] == pytest.approx(400000)
    assert s.edge_results['a']['flow_m3s'] == pytest.approx(expected)
    assert s.edge_results['b']['flow_m3s'] == pytest.approx(expected)
    assert s.residual < 1e-9


def test_fixed_pressure_load_is_not_source():
    n=load_network('examples/demo_network.toml')
    state=n.resolve_scenario('cooling_off')
    r=analyze(n,state,solve(n,state))
    f=next(f for f in r['functions'] if f['node']=='cooling')
    assert not f['reachable']
    assert f['reason']=='unreachable'


def test_nonconvergence_invalidates_functions():
    n=load_network('examples/demo_network.toml'); state=n.resolve_scenario('normal')
    s=replace(solve(n,state),converged=False)
    assert all(not f['functional'] for f in analyze(n,state,s)['functions'])


def test_flow_not_double_counted():
    n=Network('through',1000,(Node('s','source',200),Node('l','load'),Node('t','junction',0)),
              (Edge('a','s','l',100,'linear'),Edge('b','l','t',100,'linear')),(),())
    r=analyze(n,{},solve(n,{}))
    assert r['functions'][0]['flow_m3s']==pytest.approx(1)


def test_cli_json_file(tmp_path):
    dest=tmp_path/'result.json'
    subprocess.run([sys.executable,'-m','fluid_network.cli','solve','examples/demo_network.toml',
                    '--scenario','normal','--json',str(dest)],check=True,capture_output=True)
    assert json.loads(dest.read_text())['converged']


def test_unreferenced_component_fails_with_valid_json():
    n=Network('floating',1000,(Node('s','source',200),Node('a'),Node('b')),
              (Edge('x','a','b',100,'linear'),),(),())
    s=solve(n,{})
    assert not s.converged
    json.dumps(s.to_dict(),allow_nan=False)


def test_iteration_limit():
    n=load_network('examples/demo_network.toml')
    s=solve(n,n.resolve_scenario('normal'),max_iterations=1)
    assert not s.converged
    assert s.warnings


def test_loop_with_reverse_flow():
    n=Network('loop',1000,(Node('s','source',800000),Node('a'),Node('b'),Node('t','load',0)),
       (Edge('sa','s','a',1e11),Edge('at','a','t',1e11),
        Edge('bs','b','s',1e11),Edge('tb','t','b',1e11),Edge('ab','a','b',1e11)),(),())
    s=solve(n,{})
    assert s.converged
    assert s.node_pressures_pa['a']==pytest.approx(400000)
    assert s.edge_results['bs']['flow_m3s']==pytest.approx(-0.002)
    assert s.edge_results['ab']['flow_m3s']==pytest.approx(0,abs=1e-8)


@pytest.mark.parametrize('fragment', ['resistance=nan','resistance=-1','resistance=1\ndiameter_m=0'])
def test_invalid_numeric_input(tmp_path,fragment):
    f=tmp_path/'invalid.toml'
    f.write_text('[[nodes]]\nid="a"\n[[nodes]]\nid="b"\n[[edges]]\nid="e"\nfrom="a"\nto="b"\n'+fragment)
    with pytest.raises(ValueError): load_network(f)


def test_inheritance_cycle(tmp_path):
    f=tmp_path/'cycle.toml'
    f.write_text('[[nodes]]\nid="a"\n[[scenarios]]\nid="a"\nextends="b"\n[[scenarios]]\nid="b"\nextends="a"')
    with pytest.raises(ValueError,match='cycle'): load_network(f)


def test_analytic_demo_baseline():
    baseline=json.loads(open('examples/expected_demo_result.json').read())
    n=load_network('examples/demo_network.toml')
    for sid, expected in baseline['scenarios'].items():
        s=solve(n,n.resolve_scenario(sid),sid)
        assert s.converged
        assert s.node_pressures_pa['junction']==pytest.approx(expected['junction_pressure_pa'],rel=1e-6)
        for eid,q in expected['flows_m3s'].items():
            assert s.edge_results[eid]['flow_m3s']==pytest.approx(q,rel=1e-6,abs=1e-10)
