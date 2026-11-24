# Changelog

Release notes describe shipped behavior and its limits. See GitHub release assets and PyPI metadata for publication records.

## 0.4.0 — 2026-11-24

Initial public alpha release of the local observability companion.

### Public documentation and distribution

- Added a public README, marketing site, and shared documentation/wiki structure.
- Declared Apache-2.0 licensing and the designated `OOOffsite/sentinel` repository.
- Added PyPI-oriented package metadata and a README with absolute documentation links.
- Excluded local agent instructions and runtime state from new distribution builds.
- Added artifact checks and an explicitly dispatched build/TestPyPI/PyPI workflow using Trusted Publishing.

The release preserves observation contract **1.1.0** and simulation contract **1.0.0**. Release assets are rebuilt from reviewed source; the original development wheel is not a release asset.

### Observation and preparation

- Project-independent rosters, explicit identity bindings, and local observation views.
- OTLP HTTP JSON logs/metrics subset, allowlisted normalized records, and SQLite history.
- Read-only status, roster, snapshot, and history API.
- Declarative project validation and plan-first preparation of isolated resources.
- Optional read-only monitor skill projection for supported agent harnesses.

### Validation and limits

The receiver/module fixtures cover schema validation, ingestion/replay, freshness, instance/configuration boundaries, loopback HTTP behavior, and skill projection. Real upstream exporter interoperability, installed OpenRig materialization, live model sessions, remote security, and sustained capacity require separate evidence before production. This alpha release does not make a production-readiness claim.
