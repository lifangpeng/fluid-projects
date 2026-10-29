from __future__ import annotations
import argparse, json
from pathlib import Path
from .toml_loader import load_network
from .solver import solve
from .analyzer import analyze

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True)
    for cmd in ("validate","solve","analyze","export"):
        x=sub.add_parser(cmd); x.add_argument("file")
        if cmd!="validate": x.add_argument("--scenario",default=None)
        if cmd in ("solve","analyze"): x.add_argument("--json",default=None)
        if cmd=="export": x.add_argument("--out",default="web/data")
    a=p.parse_args(); n=load_network(a.file)
    if a.cmd=="validate": print(f"valid: {n.name} ({len(n.nodes)} nodes, {len(n.edges)} edges)"); return
    scenarios=[a.scenario] if getattr(a,"scenario",None) else [s.id for s in n.scenarios]
    if not scenarios: scenarios=["default"]
    out={}
    for sid in scenarios:
        state=n.resolve_scenario(sid) if sid!="default" else {c.id:c.default for c in n.controls}
        sol=solve(n,state,sid); report=analyze(n,state,sol); out[sid]=report
        if a.cmd in ("solve","analyze"): print(json.dumps(report if a.cmd=="analyze" else sol.to_dict(),indent=2))
    if getattr(a, "json", None):
        results = [r if a.cmd == "analyze" else r["solution"] for r in out.values()]
        Path(a.json).write_text(json.dumps(results[0] if len(results) == 1 else results, indent=2), encoding="utf-8")
    if a.cmd=="export":
        Path(a.out).mkdir(parents=True,exist_ok=True)
        for sid,data in out.items(): Path(a.out,f"{sid}.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
        Path(a.out,"index.json").write_text(json.dumps({"scenarios":list(out)},indent=2),encoding="utf-8")
        print(f"exported {len(out)} scenario(s) to {a.out}")
if __name__=="__main__": main()
