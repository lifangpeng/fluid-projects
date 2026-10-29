# TOML Schema Reference

Required top-level arrays are `nodes`, `edges`, `controls`, and `scenarios`.

- Node: `id`, optional `type`, `pressure_pa`, `min_flow_m3s`, `min_pressure_pa`, `function`.
- Edge: `id`, `from`, `to`, `resistance`, optional `model` (`linear`/`quadratic`), `diameter_m`, `enabled`.
- Control: `id`, `kind`, `target_ids`, `states`, `default`.
- Scenario: `id`, optional `description`, `extends`, and `set` mapping control IDs to legal states.

Only listed scenarios are evaluated; the solver does not enumerate the Cartesian product of controls.
