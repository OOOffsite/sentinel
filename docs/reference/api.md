# HTTP API

The local receiver defaults to `http://127.0.0.1:8766`. It trusts the local OS account. Browser guards are not authentication; do not expose it remotely.

Download the [OpenAPI 3.1 specification](../../contracts/openapi.json). Schema references are served beside it; the [contract catalog](contracts.md) explains compatibility.

## Read routes

| Method | Route | Meaning |
| --- | --- | --- |
| GET | `/api/v1/status` | Journal state, last receipt, unknown historical completeness. |
| GET | `/api/v1/roster` | Configured planned seats, teams, runtimes. |
| GET | `/api/v1/snapshot` | Latest observed projections, freshness, recent records. |
| GET | `/api/v1/snapshot?at=N` | Replay at receipt cursor N. |
| GET | `/api/v1/history?after=0&limit=100` | Bounded ordered observations and continuation. |

History limits are 1–500. Cursors are nonnegative integers and can have holes. A status response does not prove the source is reachable. Snapshot communication is explicitly unavailable.

## Ingestion routes

`POST /v1/logs` and `POST /v1/metrics` accept only the allowlisted exporter scope-v1 OTLP HTTP JSON subset from the configured namespace and bound exporter instance. Maximum body: 2 MiB. No protobuf, compression, or traces. This is not a general OTLP collector.

| Status | Meaning |
| --- | --- |
| 200 | Accepted; transaction committed before acknowledgement. |
| 400 | Unsupported/malformed telemetry or invalid read query. |
| 403 | Local request guard rejected the request. |
| 413 | Invalid or excessive body length. |
| 415 | Unsupported media type or encoding. |
| 503 | Journal unavailable. |

No route launches agents or writes OpenRig queues. Public documentation contains no interactive console connected to the local receiver.

## Consumer rules

Preserve string IDs and decimal timestamp/count strings. Follow continuation fields rather than assuming dense cursors. Do not derive source event totals from normalized journal counts. See [observation semantics](../wiki/observation-model.md) for replay caveats and unknown values.
