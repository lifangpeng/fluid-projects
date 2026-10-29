# Architecture

The project has four layers: TOML input and validation, immutable Python domain models, a deterministic solver/analyzer pipeline, and JSON consumers (CLI, API, and SVG web UI). Scenario state is resolved before graph construction so each run is isolated. The static UI reads exported JSON; `backend_server.py` exposes the same analyzer output for API use.
