# Status and readiness

Last reviewed: **2026-11-24**. Package **0.4.0** is an alpha package. This page describes implementation readiness; GitHub release and PyPI records are the authority for publication status.

## Compatibility baseline

| Surface | Version / status |
| --- | --- |
| Python package | 0.4.0, Python 3.11+, zero third-party Python runtime dependencies |
| Observation contract | 1.1.0 |
| Preserved simulation | 1.0.0, unchanged |
| Project initialization | 1.0.0 |
| OpenRig documentation | Reviewed at 0.7.21; installed CLI must be verified |
| Exporter | Pin `1beecce96befec880a93f60b11d83b44d7347620` |
| Runtime requirements | OpenRig plus Node.js 22/24 and the exporter for real telemetry |

## Verified locally

- Six existing module fixture tests pass: schemas, HTTP receiver guards, ingestion, replay, freshness, namespace/instance/configuration behavior, and skill projection.
- Release preparation checks are described in the [release guide](guides/releasing.md).
- Documentation/site validation is recorded in [site verification](design/verification.md).

Fixture results establish local behavior, not real upstream integration, provider capacity, or production readiness.

## Release validation and production gates

Release preparation passed strict wheel/source metadata checks, archive validation, and clean isolated installation on Python 3.11, 3.12, 3.13, and 3.14. The six fixtures also passed against each installed wheel. See the [release guide](guides/releasing.md) for the exact scope and publishing procedure.

Before production use:

- Test the exact pinned exporter against the actual installed OpenRig version.
- Establish immutable seat bindings and approve a measured pilot before real fleet operations.
- Validate retention, backpressure, bounded journal growth, boot/staleness behavior, and sustained capacity before production claims.

Publication does not establish live exporter interoperability or production readiness. The 128-seat ceiling is an implementation limit, not a tested performance level. Future automated PyPI publication requires separately configured Trusted Publishing.

## License

The maintainer selected [Apache-2.0](../LICENSE). Sentinel and the upstream exporter are separate projects with separate provenance. Brand guidelines do not claim trademark registration.

## Harness readiness

Public documentation and package preparation do not establish Unified Live Harness adoption. No project adoption manifest or runtime acceptance evidence was established by this work. Global harness configuration and live sessions remain outside the release preparation scope; readiness remains unverified.

## Documentation change record

This release preparation adds the public README, consistent branding, marketing site, wiki, guides, reference catalog, static-site checks, and release packaging controls. It preserves package 0.4.0, observation contract 1.1.0, and simulation 1.0.0; no implicit schema migration is introduced.
