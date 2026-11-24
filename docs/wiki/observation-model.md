# Observation model

Observed metadata, declared topology, and simulation are separate categories.

## Interpret evidence

| Signal | Establishes | Does not establish |
| --- | --- | --- |
| Roster seat | Intended logical membership | Running agent or exported identity |
| Verified binding | Operator-confirmed node-to-seat association | Current activity |
| Fresh supported sample | Sampled activity under freshness rules | Exact task phase or continuous work |
| Last receipt | Receiver accepted an observation | Source reachability or complete coverage |
| Queue transition | Exported queue metadata | Message sender/recipient or comprehension |
| Journal cursor | Local receipt order | Source causality or full history |
| Simulation | Illustrative behavior | Actual telemetry |

## Unknown is a result

Missing or unsupported fields remain unknown. Old or future timestamps, stale flags, and insufficient presence evidence can prevent an activity claim. Unmapped nodes are listed neutrally; planned seats remain dim until verified attribution.

The API returns `communication_available: false`. Directed-message particles and coding/testing/review claims require stronger evidence.

## Journal semantics

Only allowlisted normalized observations are stored. Prompts, transcripts, message bodies, raw actors, and incidental paths are excluded. Identical normalized observations are deduplicated; distinct source records can collapse, so journal counts are not source event counts.

Metric values, counts, and nanosecond timestamps use decimal strings where specified. Do not coerce large identifiers into JavaScript numbers. Cumulative counters are retained, not summed into inferred performance metrics.

## Replay and continuity

`snapshot?at=N` reconstructs receipt history. A cursor inside a batch can expose incomplete one-hot observations; use end-of-batch cursors for operational comparisons. Cursors are monotonic but may contain holes.

Historical completeness remains unknown across daemon restarts. Keep checkpoint-bound flags stable. Changed configuration or exporter instance is refused by an existing journal. Preserve old data before deliberate migration.

Report process existence, terminal progress, and structured telemetry advancement separately. None establishes the others.
