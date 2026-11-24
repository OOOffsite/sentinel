# Architecture

Sentinel follows an existing telemetry boundary. It does not read the OpenRig daemon database or implement a second source poller.

## Data flow

```text
OpenRig finite metadata API
        |
        v
smota/openrig-telemetry (pinned separately)
        |  OTLP HTTP JSON: logs + metrics, exporter scope v1
        v
Sentinel loopback receiver
        |  validate, normalize, allowlist, deduplicate
        v
SQLite metadata journal
        +--- status / roster / snapshot / history
        +--- observed dashboard

Legacy simulation 1.0.0 --- separate simulation view
```

Arrows describe component data flow, not messages between agents.

## Responsibilities

| Component | Owns |
| --- | --- |
| OpenRig | Agent lifecycle, queue authority, native metadata. |
| Exporter | Source cursor, coverage, retry, checkpoint, sampling. |
| Receiver | Supported-envelope validation, normalization, durable acknowledgement. |
| SQLite | Received metadata and replay cursors; no raw-payload archive. |
| Read API and UI | Evidence projections, unknown states, freshness, receipt history. |
| Preparation CLI | Validating declarations and preparing approved isolated resources. |

## Isolation and identity

Use one exporter per journal and namespace. Configuration and exporter instance are journal-bound. Bind immutable IDs using authoritative evidence, never roster order or display names.

Queue telemetry can remain daemon-wide even with exporter `--rig` seat filtering. Strict project isolation may require a dedicated daemon. This is an operator architecture decision.

## Publication surfaces

The Python package serves the local dashboard and API. GitHub Pages serves marketing, guides, wiki, and references. The Pages build excludes journals, checkpoints, private configuration, runtime dashboard pages, and agent sessions.

## Future work

See the [contracts](../reference/contracts.md) and [ADR-S01](../INTEGRATION.md). Native UI integration and directed-message metadata are proposals, not implemented capabilities.
