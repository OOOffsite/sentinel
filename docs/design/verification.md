# Documentation and site verification

Date: 2026-11-24. Public documentation and marketing surface only. Package 0.4.0, observation 1.1.0, and simulation 1.0.0 remain unchanged.

## Automated checks

- All six existing module fixture tests passed using an existing development environment.
- Static build generated 21 documentation pages and validated all 24 HTML pages, including the marketing homepage and asset catalog.
- Local links, anchors, image/script references, duplicate IDs, CSS asset references, and repository-subpath paths passed.
- Site JavaScript passed Node syntax checking; original brand SVGs passed XML validation.
- Source distribution to extracted-source wheel round-trip, metadata, license, archive contents, package resources, RECORD hashes, and packaged CLI help passed. See [release preparation](../guides/releasing.md).

## Rendered browser inspection

The Codex in-app browser loaded the site under a `/sentinel/` prefix to represent GitHub project Pages. Requested desktop and mobile viewports were 1440 × 1000 and 390 × 844; the browser's current scaling produced measured CSS viewports of 1309px and 355px width. Those measured widths, not physical-device testing, are the basis of these observations.

- Homepage and getting-started guide rendered at both widths with no document horizontal overflow.
- The mobile contracts page also retained the viewport width; tables and code use local overflow containers.
- Homepage brand images loaded; the aperture mark identifies the brand, and the application preview now leads the product visual.
- Stale example selected by click produced “Current activity unknown.”
- Unmapped example activated with Enter produced “Seat identity unknown.”
- Getting-started navigation, mobile documentation disclosure, and contracts navigation reached the expected pages.
- Mobile Menu opened with Enter and closed with Escape, restoring focus to its summary control.
- The documentation sidebar marked the active page.
- No captured page warning/error logs were reported in the final check.

Desktop/mobile homepage screenshots were retained as local review artifacts outside the public source distribution. Source inspection confirmed reduced-motion rules; OS/browser motion emulation was not exercised. Code-copy controls were rendered but clipboard contents were not changed during review.

## Application preview follow-up

The homepage now reuses the original simulation canvas and observed SVG renderers. Integrated browser checks used requested and measured CSS viewports of 1440 × 1100 and 390 × 844.

- Simulation team filtering produced 32 visible seats; keyboard timeline selection reached 02:30.
- Agent selection updated the inspector to the selected accessibility seat.
- Observed mode rendered its SVG; switching to a 120-second-old fixture produced unknown activity and presence and no message links.
- A browser-specific SVG visibility bug was fixed by toggling the hidden attribute directly.
- A mobile decorative overflow was corrected; document and viewport widths both measured 390px.
- No captured page warning/error logs appeared. Desktop/mobile screenshots were retained outside the public source.
- Source hashes, extracted renderer equivalence, all three frozen moments, and generated preview consistency pass the build check.

## Limits

These are scoped layout and interaction checks, not a full screen-reader, browser-matrix, accessibility-conformance, or performance audit. GitHub/PyPI publication and Pages deployment are recorded separately in the [release guide](../guides/releasing.md#040-publication-record). No live OpenRig connection, exact exporter interoperability, sustained capacity, or Unified Live Harness adoption is established. No live agent or global harness configuration was changed.
