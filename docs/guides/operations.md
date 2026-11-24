# Operations

Keep one receiver and one exporter per isolated journal/namespace. Preserve configuration, journal, and checkpoint across normal restarts. Actual telemetry requires separately installed OpenRig and Node.js 22/24.

## Verify the integration

The reviewed exporter pin is `1beecce96befec880a93f60b11d83b44d7347620`. OpenRig documentation was reviewed at 0.7.21; inspect the installed CLI and test this exact pairing before production. Neither a listening port nor a recent receipt proves source health.

Identify the verified daemon HTTP URL and immutable materialized rig ID. Do not infer IDs from names or roster positions. Queue telemetry can remain daemon-wide with `--rig`; dedicated daemons may be necessary for strict project isolation.

## Run the receiver

Resolve these inputs in Bash. Use a new namespace/journal only when intentionally starting a new history; ordinary restarts reuse the existing values.

```bash
read -r -p 'Runtime directory: ' RUN_DIR
read -r -p 'Monitor port: ' PORT
read -r -p 'Exporter namespace: ' NAMESPACE
sentinel-openrig serve --config "$RUN_DIR/sentinel/config.json" \
  --db "$RUN_DIR/sentinel/observations.sqlite" --port "$PORT"
```

Use a dedicated managed foreground terminal. Never add a competing reader to an unmanaged terminal device. Use application logs, structured telemetry, process metadata, and file growth as separate signals.

## Attach the pinned exporter

Review upstream source and license before cloning. In a separate authorized Bash shell, resolve the same `RUN_DIR`, `PORT`, and `NAMESPACE`, then:

```bash
read -r -p 'Verified daemon HTTP source URL: ' SOURCE
read -r -p 'Immutable materialized rig ID: ' RIG_ID
git clone https://github.com/smota/openrig-telemetry.git "$RUN_DIR/sentinel/exporter"
git -C "$RUN_DIR/sentinel/exporter" checkout --detach 1beecce96befec880a93f60b11d83b44d7347620
node "$RUN_DIR/sentinel/exporter/telemetry-otlp.mjs" --help
node "$RUN_DIR/sentinel/exporter/telemetry-otlp.mjs" \
  --source "$SOURCE" --rig "$RIG_ID" \
  --endpoint "http://127.0.0.1:$PORT/v1/logs" \
  --namespace "$NAMESPACE" --checkpoint "$RUN_DIR/sentinel/checkpoint.json" \
  --signals logs,metrics --start latest --pseudonymize-seats \
  --poll-ms 2000 --seat-poll-ms 5000
```

Clone once; subsequent runs use the same pinned checkout. The illustrated flags are the original Atlas defaults. For a prepared project, use its generated `exporter-plan.json`. Preserve checkpoint-bound flags on restart. These commands are documented setup, not evidence that interoperability was executed in this release preparation.

## Establish identity

Confirm exported immutable node IDs from authoritative host evidence, including pseudonymized IDs when enabled. Leave nodes unmapped if correlation cannot be verified.

```bash
read -r -p 'Verified exported node ID: ' NODE
read -r -p 'Declared team.seat ID: ' SEAT
sentinel-openrig bind --config "$RUN_DIR/sentinel/config.json" \
  --node "$NODE" --seat "$SEAT"
```

Configure known bindings before creating the first journal. If a journal already exists, stop the receiver, preserve its old configuration/history, and plan a new journal or explicit migration before changing bindings. The receiver refuses changed journal configuration; `bind` does not migrate stored data.

## Inspect independent signals

Read `/api/v1/status`, `/api/v1/snapshot`, and exporter output. Compare source timestamps and journal advancement. Source silence may indicate idle data, stale coverage, or failure. Report what each signal proves, not inferred liveness.

| Symptom | Check |
| --- | --- |
| All seats unknown | Namespace, supported samples, immutable bindings, TTL, clock skew. |
| Unmapped observations | Authoritative identity evidence; never bind by order. |
| Instance/config mismatch | Existing journal's original configuration and exporter checkpoint. |
| No journal advancement | Exporter output, supported signals, source coverage, response errors. |
| Port already in use | Choose another free loopback port; do not stop an unrelated process. |
| Incomplete preparation | Inspect generated receipts, worktrees, branches before retry. |

## Backup and rollback

Use SQLite's online backup API or stop the receiver before copying a journal; account for WAL/SHM files. Never remove the exporter checkpoint while it runs or reset it to hide an error.

On incompatibility, stop only the companion/exporter you own, retain database/checkpoint, and investigate the pinned version. OpenRig and agent sessions need no restart. Restore generated skill resources from their backup only after review.

Retention, bounded journal size, sustained throughput, authenticated remote exposure, and exact upstream interoperability remain separate production gates. See [status](../STATUS.md).
