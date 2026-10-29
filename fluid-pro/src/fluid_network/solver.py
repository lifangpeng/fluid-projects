from __future__ import annotations
import math
from .model import Network, Solution

def _gauss(a, b):
    n=len(b)
    for i in range(n):
        p=max(range(i,n), key=lambda r: abs(a[r][i]))
        if a[p][i] == 0.0: raise ValueError("singular pressure system; missing boundary or disconnected node")
        a[i],a[p]=a[p],a[i]; b[i],b[p]=b[p],b[i]
        q=a[i][i]; a[i]=[x/q for x in a[i]]; b[i]/=q
        for r in range(n):
            if r==i: continue
            q=a[r][i]
            if q:
                a[r]=[x-q*y for x,y in zip(a[r],a[i])]; b[r]-=q*b[i]
    return b

def solve(network: Network, state: dict[str,str], scenario_id: str = "", *, max_iterations: int = 100) -> Solution:
    if max_iterations < 1: raise ValueError("max_iterations must be positive")
    nodes=network.node_map
    fixed={n.id:float(n.pressure_pa) for n in network.nodes if n.pressure_pa is not None}
    unknown=[n.id for n in network.nodes if n.id not in fixed]
    if not fixed: raise ValueError("at least one node pressure boundary is required")
    active=[]
    warnings=[]
    for e in network.edges:
        enabled=e.enabled
        for c in network.controls:
            if e.id in c.target_ids and state.get(c.id,c.default) in ("closed","off","failed","blocked"):
                enabled=False
        if enabled: active.append(e)
    p={n: fixed.get(n, sum(fixed.values())/len(fixed)) for n in nodes}
    # A nonzero seed is important for quadratic resistance: q=0 would create
    # an artificially enormous conductance and make the first iterate look
    # converged while carrying almost no flow.
    prev_q={e.id:(1e-3 if e.model=="quadratic" else 0.0) for e in active}; converged=False; residual=float("inf")
    for iteration in range(1,max_iterations+1):
        idx={nid:i for i,nid in enumerate(unknown)}; a=[[0.0]*len(unknown) for _ in unknown]; b=[0.0]*len(unknown)
        conductance={}
        for e in active:
            if e.model=="linear": g=1.0/e.resistance
            else: g=1.0/(e.resistance*max(abs(prev_q[e.id]),1e-7))
            conductance[e.id]=g; u,v=e.from_node,e.to_node
            if u in idx: a[idx[u]][idx[u]]+=g; b[idx[u]]+=g*fixed.get(v,0.0)
            if v in idx: a[idx[v]][idx[v]]+=g; b[idx[v]]+=g*fixed.get(u,0.0)
            if u in idx and v in idx: a[idx[u]][idx[v]]-=g; a[idx[v]][idx[u]]-=g
        try: sol=_gauss(a,b) if unknown else []
        except ValueError as ex: return Solution(scenario_id,False,iteration,float("inf"),p,{},[str(ex)])
        for nid,i in idx.items(): p[nid]=sol[i]
        qnow={}; maxchange=0.0
        for e in active:
            dp=p[e.from_node]-p[e.to_node]
            q=dp/e.resistance if e.model=="linear" else math.copysign(math.sqrt(abs(dp)/e.resistance),dp) if abs(dp)>0 else 0.0
            qnow[e.id]=q; maxchange=max(maxchange,abs(q-prev_q[e.id]))
        prev_q=qnow
        balance = {nid: 0.0 for nid in unknown}
        for e in active:
            if e.from_node in balance: balance[e.from_node] -= qnow[e.id]
            if e.to_node in balance: balance[e.to_node] += qnow[e.id]
        residual=max((abs(v) for v in balance.values()), default=0.0)
        if maxchange < 1e-9 and residual < 1e-9: converged=True; break
    if not converged: warnings.append(f"nonlinear iteration did not converge within {max_iterations} iterations")
    edge_results={}
    for e in network.edges:
        enabled=e in active
        q=prev_q.get(e.id,0.0) if enabled else 0.0
        dp=p[e.from_node]-p[e.to_node] if e.from_node in p and e.to_node in p else 0.0
        velocity=None
        if e.diameter_m:
            velocity=q/(math.pi*e.diameter_m**2/4)
        elif enabled: warnings.append(f"edge {e.id} has no diameter; velocity omitted")
        edge_results[e.id]={"from":e.from_node,"to":e.to_node,"enabled":enabled,"flow_m3s":q,"pressure_drop_pa":dp,"velocity_mps":velocity}
    return Solution(scenario_id,converged,iteration,residual,p,edge_results,warnings)
