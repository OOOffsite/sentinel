# Product preview provenance

The public site preview reuses Sentinel's actual application renderers. It is a static demonstration, not a connection to an agent fleet. The source application files remain unchanged.

## Included simulation

Source: `web/simulation.html`, its embedded `atlas-data` JSON, and application JavaScript.

- Uses the first included scenario, `steady` / “Steady-state delivery”, seed 19, duration 240 seconds.
- Frozen moments are 45, 90, and 150 seconds. All 128 declared seats and four original teams are retained.
- Regeneration executes the original `blank`, `apply`, `advance`, and `at` reducer functions in Node with the included JSON as standard input. It does not execute the application startup code.
- An independent Python projection must agree with the original reducer for every exported agent state, last event, counter, mission, incident, recent event, and summary at each moment. Regeneration fails on disagreement.
- The generated adapter retains the original `posLayout`, `resize`, `col`, `draw`, and `desc` functions. Only textual canvas labels increase from 9–10 to 12 pixels; node glyph sizes remain the original sizes.
- Original supervisory topology, team colors, orbital arrangement, agent glyphs, sampled messages, and selected-agent rings come from the application implementation.
- Message highlights derive only from the included scenario's simulated `message.sent` events within the original 2.2-second display window. With motion disabled they remain frozen; they are never generated from unrelated UI interactions.
- Team strips, inspector fields, event feed, and timeline follow the application panel structure and reuse its visual palette. The compact public wrapper deliberately omits runtime, stream, export, launch, and agent-control actions.

## Observed mesh

Source: `web/live.html`, original SVG `draw(seats)` function. The original function is included unchanged in an isolated adapter, along with equivalent SVG creation/text helpers. Its HTTP polling and startup functions are excluded.

The two tiny datasets are explicitly synthetic rendering fixtures. Sixteen fictional fixture nodes map to the first four declared seats in each included team; all 128 planned seats are drawn. Fresh fixtures have sample ages of 5 seconds and supported working/idle activity. Stale fixtures have ages of 120 seconds against a 90-second TTL and unknown activity/presence. These objects contain renderer inputs, not a claim to be complete API responses or records from an actual deployment. The public preview does not assert real identity bindings.

Directed messages are unavailable in both observed fixtures. The observed renderer draws no message edges. The simulation-only agent phases and message counters are removed from the observed inspector.

## Generator and verification

```bash
python3 tools/build_product_preview.py          # Python + existing Node; regenerate
python3 tools/build_product_preview.py --check  # Python standard library only; verify
node --check site/assets/product-preview-data.js
node --check site/assets/product-preview.js
```

`--check` derives the expected output from current application source files and the independent deterministic Python projection, then compares the complete generated file byte-for-byte. It validates source hashes, renderer content, snapshot consistency, and synthetic fixture definitions without a Node dependency for routine documentation builds. Regeneration is the additional check that executes the original JavaScript reducer.

The generator and Python-only check both passed on 2026-11-24, as did JavaScript syntax checks for the generated adapter and controller. A Node canvas/SVG stub smoke check rendered all 15 combinations of the three simulation moments and all/team filters with finite coordinates. Both observed fixtures produced 128 planned SVG nodes, 16 selectable synthetic nodes, and no path/line message edges. Fragment IDs were checked for uniqueness and the `product-` prefix, all controller ID references resolved, and no network, polling, or animation-loop calls were found in the controller. These are source and renderer execution checks, separate from actual browser QA.

SHA-256 hashes of both source HTML files, the extracted reducer, the original simulation draw function, and original observed draw function are stored in `SentinelProductPreviewData.provenance` at the start of the generated `site/assets/product-preview-data.js` file. No timestamp or local host path enters the generated asset, so unchanged inputs reproduce identical output.

## Integration

`site/assets/product-preview.html` is a fragment with one root section. Embed it in the page and include these assets, in order:

1. `assets/product-preview.css`
2. `assets/product-preview-data.js` (deferred script)
3. `assets/product-preview.js` (deferred script)

All element IDs start with `product-`. Scripts use the DOM and bundled data only: no fetch, WebSocket, storage, interval, animation loop, daemon access, or original application startup. A `ResizeObserver` redraws the static selected state when layout changes. Native team/agent selectors and the labeled range input provide keyboard alternatives to the canvas. Provenance labels are visible in both modes. Mobile layout puts the mesh before the inspector and team strips.

## Limits

The preview is not a screenshot of a verified live runtime, an exporter interoperability check, a workload benchmark, or evidence that a 128-seat deployment has been validated. The original simulation is fictional, and the observed fixtures are authored examples. Browser verification must exercise the integrated static page; source parsing and hashes do not establish visual usability or accessibility conformance.
