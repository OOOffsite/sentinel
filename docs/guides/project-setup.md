# Project preparation

`sentinel-project` validates a project definition and prepares isolated resources. It never launches agents. This standalone repository includes schemas, not the full Atlas parent project kit.

## Declare the inputs

Follow the [project initialization schema](../../contracts/project-init.schema.json), [fleet registry schema](../../contracts/fleet-registry.schema.json), and [mission registry schema](../../contracts/mission-registry.schema.json).

A project manifest references its roster, ordered missions, mission briefs, guidance, and context directories. Paths are relative to the manifest directory. Validation checks unique seats, lead membership, capacity, owner/reviewer separation, and dependency order. Each mission needs a matching brief.

```bash
sentinel-project validate /absolute/path/to/project.json
```

The original `projects/atlas` and `projects/example-docs` paths belong to a separate parent kit and are not supplied here. Do not treat the minimal receiver roster as a complete project manifest.

## Review a preparation plan

In Bash, supply a complete manifest, a clean Git checkout with a commit, a new runtime directory outside that checkout, a unique namespace, and a free loopback port:

```bash
read -r -p 'Project manifest: ' PROJECT
read -r -p 'Approved integration checkout: ' REPO
read -r -p 'New runtime directory: ' RUN_DIR
read -r -p 'Unique namespace: ' NAMESPACE
read -r -p 'Free local monitor port: ' PORT
sentinel-project prepare "$PROJECT" --repo "$REPO" --output "$RUN_DIR" \
  --namespace "$NAMESPACE" --port "$PORT"
```

The default is plan-only and selects the pilot fleet. Review the base SHA, branches, roles, paths, budget, and ready candidates. Only after approval repeat with `--apply`. `--fleet full` prepares logical seats, not a launch instruction. The 128-seat/16-team ceiling is an implementation bound, not verified provider capacity.

## Generated resources

Explicit apply creates isolated Git worktrees, `rig.yaml`, AgentSpecs with projected skills, mission registry, read-only context, Sentinel configuration/roster/exporter plan, and preparation receipts. The full logical roster remains unknown until verified telemetry is bound.

Do not overwrite an existing runtime or retry incomplete preparation blindly. Inspect partial worktrees, branches, and the incomplete receipt first. Preparation requires a clean source checkout; this protects reproducible base identity.

## Materialize deliberately

Check installed `rig --version`, `rig preflight`, and help for `rig spec preflight`, `rig import`, and `rig launch`. The following documented syntax must be confirmed on the installed version:

```bash
cd "$RUN_DIR"
rig spec preflight rig.yaml
rig up rig.yaml --plan
rig import rig.yaml --materialize-only
```

Confirm the returned immutable rig ID and stop on mismatch. Plain `rig up` may launch seats. Do not launch until the monitor/exporter are verified and approval is recorded. Launch only approved pilot seats individually; queue operations remain native OpenRig operations. Scale only with measured resource and budget approval.

Continue with [operations](operations.md) and [ADR-S01](../INTEGRATION.md).
