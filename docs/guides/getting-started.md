# Getting started

Initialize an intentionally empty observation journal. Real observations require a separately verified OpenRig/exporter setup.

## Requirements

Python 3.11 or newer; Git for project preparation. Actual telemetry additionally requires separately installed OpenRig and Node.js 22/24. Sentinel has no third-party Python runtime dependencies. It is a Python package, not npm.

## Install from this checkout

From the repository root:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
sentinel-openrig --help
sentinel-project --help
```

Source-build isolation may fetch setuptools. An offline install can use `python -m pip install --no-deps --no-index /path/to/sentinel_openrig-0.4.0-py3-none-any.whl` after obtaining reviewed release artifacts. The old local `dist/` wheel predates release preparation and is excluded from public source control; see the [release guide](releasing.md).

## Declare a small roster

The [minimal roster](../../examples/minimal-roster.json) contains an illustrative logical seat. Its ID is a declaration, not evidence that a real agent exists.

```bash
sentinel-openrig init --config runtime/sentinel/config.json \
  --namespace docs-lab --project-id docs-lab --title 'Docs Lab' \
  --roster examples/minimal-roster.json
```

Initialization creates a new configuration with empty bindings and a 90-second freshness TTL. It refuses to overwrite existing configuration. Choose a unique namespace for each isolated journal/exporter setup; `docs-lab` is for a fresh local trial.

## Open the local dashboard

Choose a free loopback port and run the foreground monitor in a dedicated terminal. Use tmux if you need parseable interactive-terminal monitoring.

```bash
sentinel-openrig serve --config runtime/sentinel/config.json \
  --db runtime/sentinel/observations.sqlite --port 8766
```

Open `http://127.0.0.1:8766/`. The roster remains unknown until verified bindings and fresh telemetry exist. An empty view is a valid initial state. The separate `/simulation.html` is the legacy simulated Atlas scene, not observed evidence.

The GitHub Pages site contains static documentation only. It does not host the receiver or query visitors' local daemons.

## Connect observations

Follow [operations](operations.md) to verify the exporter pin, immutable rig ID, source URL, checkpoint, and seat identity. Validate exact-version interoperability before production.

For project manifests, AgentSpecs, and isolated worktrees, use [project preparation](project-setup.md). This standalone checkout does not include the original parent kit's `projects/atlas` or `projects/example-docs` directories.

## Stop the trial

Use Ctrl-C in the terminal you started. Preserve configuration, journal, and exporter checkpoint when continuing the same history. Stopping Sentinel does not require stopping OpenRig or agent sessions.
