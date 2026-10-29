---
name: fluid-network
description: Design TOML steady-state incompressible fluid networks, run the fluid-network Python solver, analyze explicit valve/fault scenarios, and export visualization data. Use for this project's fluid-network calculations and reports.
---

# Fluid network

Prerequisite: Python 3.11+ and the fluid-network project installed. This skill contains instructions and an example; it does not bundle the Python solver. Locate the user-provided project checkout and run `python3 -m pip install -e .` there. If no checkout is available, request its location or published repository URL; do not invent an installation URL.

Read [schema-reference.md](schema-reference.md) and [schema.json](schema.json) when designing TOML. Copy [assets/demo_network.toml](assets/demo_network.toml) as a starting example. Use SI units. Explicit pressure boundaries must include an outlet/backpressure to obtain nonzero flow. Source nodes must have type `source` or `pump`; a fixed-pressure load is not a supply source. Thresholds specify required performance, not imposed flow.

Resolve missing boundary conditions, resistance, pipe diameter and load thresholds with the user; label any requested assumptions. Only evaluate listed scenarios and explicit user overrides, never the Cartesian product of all controls.

From the project checkout:

```bash
fluid-network validate NETWORK.toml
fluid-network solve NETWORK.toml --scenario normal --json solution.json
fluid-network analyze NETWORK.toml --scenario normal --json report.json
fluid-network export NETWORK.toml --out web/data
```

Use the actual scenario ID from the file. Report convergence, mass residual, warnings, node pressures, signed flows and velocities. Never describe a nonconverged result as physically validated. `reliability` is the fraction of loads meeting requirements in this deterministic scenario, not a probability. `topology_path` is one undirected topological witness, not proof of positive directed flow or a full critical-path analysis.

For visualization, export data and run `python3 -m http.server 8080 --directory web` for static results. Run `python3 backend_server.py --port 8080` for live controls of the bundled demo network; a custom API network currently requires changing its NETWORK input. Docker usage is documented in the project's `docs/linux-deployment-demo.md`.

Example requests: “Create a two-branch network with a cooling valve”; “Compare normal and cooling_off”; “Export results and explain why cooling fails.” Do not publish the repository or Skill solely because it was used for a calculation.
