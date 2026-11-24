# SENTINEL

*monitor the situation*

**Local, evidence-driven observability for OpenRig-managed agent fleets.**

Sentinel receives a defined OTLP HTTP JSON subset from the existing upstream exporter, retains allowlisted metadata in SQLite, and serves a loopback dashboard and read API. It distinguishes observed activity, declared topology, and simulation. Missing or stale evidence remains unknown.

This is a **Python package** for Python 3.11 or newer, with no third-party Python runtime dependencies. Its commands are `sentinel-openrig` and `sentinel-project`.

**Actual fleet telemetry requires a separately installed OpenRig system and the pinned upstream exporter running on Node.js 22/24.** These integration prerequisites are not installed by pip. Sentinel can initialize configuration and show an empty monitor without them.

## Capabilities

- Inspect sampled presence and activity with explicit freshness rules.
- Associate immutable exported node IDs with operator-verified logical seats.
- Read local status, roster, snapshots, and cursor-based history.
- Retain metadata without prompts, transcripts, or message bodies.
- Validate project declarations and review plans for isolated worktrees and AgentSpecs.

OpenRig remains the agent and queue authority. Sentinel does not launch agents or enqueue work. The separate legacy Atlas simulation never substitutes for real observations, and the current observation API does not establish directed messages between agents.

## Installation

Use a project-local environment for the release:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install sentinel-openrig==0.4.0
sentinel-openrig --help
sentinel-project --help
```

For a source checkout, use `python -m pip install .` from the repository root instead. To use a downloaded release wheel without resolving dependencies, run `python -m pip install --no-deps --no-index /path/to/sentinel_openrig-0.4.0-py3-none-any.whl`.

Git is needed for project preparation. No upstream binary or exporter is vendored.

## Documentation

Source, issues, release assets, and documentation are maintained in [OOOffsite/sentinel](https://github.com/OOOffsite/sentinel).

- [Getting started](https://github.com/OOOffsite/sentinel/blob/main/docs/guides/getting-started.md)
- [Operations](https://github.com/OOOffsite/sentinel/blob/main/docs/guides/operations.md)
- [Wiki](https://github.com/OOOffsite/sentinel/tree/main/docs/wiki)
- [API and contracts](https://github.com/OOOffsite/sentinel/tree/main/docs/reference)
- [Status and verification limits](https://github.com/OOOffsite/sentinel/blob/main/docs/STATUS.md)
- [Release notes](https://github.com/OOOffsite/sentinel/blob/main/CHANGELOG.md)

## Compatibility and boundaries

Package **0.4.0** is an **alpha release of a local prototype**. Observation contract **1.1.0** and simulation contract **1.0.0** remain separate. OpenRig documentation was reviewed at **0.7.21**; verify the actual installed CLI and exact exporter commit `1beecce96befec880a93f60b11d83b44d7347620` before production use.

The receiver binds to loopback and trusts the local OS account. It is not an authenticated remote gateway. A received observation is not proof of source reachability or complete history. The 128-seat implementation ceiling is not a validated capacity claim. Retention, remote security, and sustained throughput remain future work.

## License

Sentinel is licensed under **Apache-2.0**. The separately obtained upstream exporter has its own license and is not included in this distribution.
