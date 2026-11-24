# Contracts and specifications

The package version, observation contract, initialization contract, and preserved simulation format are separate versioned surfaces. Documentation changes do not migrate runtime journals.

## Module and observation contract 1.1.0

| File | Purpose |
| --- | --- |
| [Module manifest](../../module.json) | Sentinel-owned capability metadata. |
| [Manifest schema](../../contracts/module-manifest.schema.json) | Manifest validation. |
| [Configuration](../../contracts/module-config.schema.json) | Namespace, roster, bindings, TTL. |
| [Observation](../../contracts/observation.schema.json) | Normalized retained metadata. |
| [Seat observation](../../contracts/seat-observation.schema.json) | Attributed sampled evidence. |
| [Status](../../contracts/status.schema.json) | Journal status. |
| [Roster](../../contracts/roster.schema.json) | Planned membership. |
| [Snapshot](../../contracts/snapshot.schema.json) | Current/replayed projections. |
| [History](../../contracts/history.schema.json) | Paginated retained observations. |
| [TypeScript types](../../contracts/types.d.ts) | Consumer declarations. |
| [OpenAPI](../../contracts/openapi.json) | HTTP routes and envelopes. |

## Project initialization 1.0.0

- [Project manifest](../../contracts/project-init.schema.json)
- [Fleet registry](../../contracts/fleet-registry.schema.json)
- [Mission registry](../../contracts/mission-registry.schema.json)
- [Project TypeScript declarations](../../contracts/project-init.d.ts)

The receiver roster and preparation fleet registry have different shapes; use the appropriate contract.

## Preserved simulation 1.0.0

- [Simulation event](../../contracts/simulation-event.schema.json)
- [Telemetry event](../../contracts/telemetry-event.schema.json)
- [Recording](../../contracts/recording.schema.json)

These are preserved legacy simulation specifications. The recording retains its original telemetry-event filename reference. They are not observation schemas and must not be silently reinterpreted as live evidence.

## Compatibility

Configuration 1.1.0 differs from the old Atlas 1.0 configuration. Preserve old journals and explicitly create or migrate configuration/history. The exporter pin and interoperability gates are in [ADR-S01](../INTEGRATION.md). Unsupported evidence stays unknown.
