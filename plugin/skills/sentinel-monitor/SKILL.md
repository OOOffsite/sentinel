---
name: sentinel-monitor
description: Inspect Sentinel's local OpenRig observation status and explain coverage gaps without changing agents or queues. Use for fleet monitoring, blocked input investigation, and read-only telemetry inspection.
---
# Sentinel monitor
Use the already-running shared module. Never launch an exporter per seat, install hooks, alter OpenRig state, send messages or modify the journal. Read-only local requests, with operator-approved port if not default:

```sh
curl --fail --silent --show-error --max-time 3 http://127.0.0.1:8766/api/v1/status
curl --fail --silent --show-error --max-time 3 http://127.0.0.1:8766/api/v1/snapshot
curl --fail --silent --show-error --max-time 3 'http://127.0.0.1:8766/api/v1/history?after=0&limit=100'
```

The status `cursor` is a journal position, not a source sequence. History cursors are monotonic, not necessarily dense. Page with `next_cursor` until `has_more` is false. Do not interpret stale, unavailable or unknown data as idle or healthy. Presence/activity are sampled daemon projections, not proof of coding or testing; queue transitions do not prove task execution or message delivery. Do not infer sender/recipient links or identify unknown node IDs by current seat names. Never request transcripts, prompts, credentials or tool contents. If the endpoint is unavailable, report it; ask the operator to start the shared companion. To view visually, use http://127.0.0.1:8766/ . Its simulation is separate and clearly labeled.
