# CLI reference

The installed package exposes two commands. The source equivalents are `python tools/sentinel.py` and `python tools/bootstrap.py`.

## sentinel-openrig

| Command | Required arguments | Optional arguments | Effects |
| --- | --- | --- | --- |
| `init` | `--config`, `--namespace`, `--project-id`, `--title`, `--roster` | `--ttl` (90 seconds) | Creates a new config; no overwrite. |
| `bind` | `--config`, `--node`, `--seat` | None | Adds a unique verified identity binding. |
| `serve` | `--config`, `--db` | `--port` (8766) | Starts the foreground loopback receiver and read UI. |

TTL must be 10–600 seconds. Bindings are immutable per journal configuration; stop the receiver and plan configuration/journal migration before changing identity. `bind` refuses reused nodes or seats.

## sentinel-project

| Command | Arguments | Effects |
| --- | --- | --- |
| `validate` | Project manifest path | Validates declarations and references. |
| `prepare` | Manifest, `--repo`, `--output`, `--namespace` | Prints a plan. |
| `prepare --apply` | Same required arguments | Creates isolated resources after approval. |

Preparation options: `--fleet pilot` (default) or `full`; `--port` overrides the manifest. Output must be new and separate from a clean Git checkout. Preparation never launches agents.

## Skill projection

`python tools/project_skill.py --rig-dir PATH` plans resource projection. `--apply` copies the shared read-only monitor skill into generated agent resources. Do not run projection during live launches; preserve generated resources before changes.

Use `--help` on the installed version for exact syntax. See [getting started](../guides/getting-started.md), [project setup](../guides/project-setup.md), and [operations](../guides/operations.md).
