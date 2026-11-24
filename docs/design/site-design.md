# Sentinel public site design

Date: 2026-11-24. Scope: static marketing site and shared documentation presentation. Package 0.4.0; observation contract 1.1.0 and simulation contract 1.0.0 unchanged.

## Brief

Introduce Sentinel to developers operating OpenRig-managed Codex and Claude Code fleets. Help visitors understand the local observation boundary and reach a practical guide, conceptual wiki, or precise reference. The marketing site is static documentation; it never connects to the local receiver or a fleet.

## Direction: the application is the visual

The homepage introduces the product with compact editorial typography, then gives the full-width centerpiece to Sentinel’s own interface. The team constellation, activity glyphs, team strips, agent inspector, metadata panel, and replay controls come from the app’s existing visual language.

The fleet simulation uses the original canvas renderer and three frozen moments projected from the included recording. A second mode uses the original observed SVG renderer with explicit synthetic fixtures. Persistent labels distinguish the two views; simulated phases and message signals are never described as observed telemetry capabilities. Visitors can select a team or seat and scrub between samples without a daemon connection.

The source runtime pages are unchanged. The public preview excludes their startup, polling, mock socket, and background animation paths. Rendering is driven by user input and resize. [Product preview provenance](product-preview.md) records extraction and verification details.

The existing aperture logo remains the shared brand identity. The application now carries the product story; an abstract brand graphic is no longer the hero. Guides, wiki, reference navigation, and the original system-font palette remain shared with the rest of the site.

## Reference ledger

Sources were fetched as text on 2026-11-24. These observations are about information architecture and semantics, not a visual screenshot inspection or an asset license grant.

| Primary source | Useful pattern | Application |
| --- | --- | --- |
| [Grafana](https://grafana.com/) | Product value appears before deeper technical and documentation pathways. | Lead with a concrete visibility promise, then provide technical detail and a knowledge hub. No copy or assets reused. |
| [Diátaxis](https://diataxis.fr/) | Learning, practical tasks, explanation, and reference serve different reader needs. | Distinct guides, wiki, and reference entry points with persistent docs navigation. |
| [GitHub Pages documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages) | Static HTML/CSS/JS hosting and repository subpaths. | Relative links and assets; no server, authentication, or live collector embedded in the public site. |
| [MDN reduced motion](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion) | User motion preference can remove unnecessary motion. | Disable smooth scrolling and hover transforms under reduced motion. No perpetual decorative animation. |

## Shared build contract

- `site/index.html` is the homepage template. The builder inserts the product preview HTML fragment at its single marked slot.
- `tools/build_product_preview.py --check` verifies the committed fixture/renderer asset against the source app without Node or network access. Regeneration additionally checks the original reducer with Node.
- `site/docs-template.html` accepts `{{TITLE}}`, `{{CONTENT}}`, `{{TOC}}`, and `{{ROOT}}`; the root prefix ends in `/`.
- The template expects rendered Markdown content to supply the document's `h1`.
- The parent builder owns Markdown rendering, title escaping, local link rewriting, generated HTML, and copying source contracts and license.
- Documentation lives at `docs/.../*.html` with the same stem as its Markdown sources.
- Styles and JavaScript are shared by marketing and documentation pages.
- The dedicated brand worker supplies the self-contained README banner SVG under `site/assets/brand/`.
- The homepage evidence explorer uses fixed illustrative prose. It performs no fetches, storage, or background polling.
- Clipboard enhancement appears only when the browser has a secure clipboard API; the code remains selectable when it is absent.

## Verification and limitations

Source-level checks passed: HTML parsing with no duplicate IDs in both source pages, SVG XML parsing of the provisional favicon, and `node --check site/assets/site.js`. Calculated contrast ratios for main text pairs range from 5.82:1 to 14.09:1; the tested pairs include muted and dim text, cyan links, and dark text on lime. Keyboard focus, semantic buttons, descriptive link text, explicit illustration labels, a skip link, mobile navigation disclosure, and reduced-motion styling are implemented. Responsive breakpoints are provided for narrow, medium, and wide screens. The parent agent owns actual rendered browser verification and the integrated documentation/link build check.

The attempted system-Python run of `tests/test_module.py` failed before running tests because `jsonschema` was not installed in that interpreter. No dependency installation, fleet launch, telemetry test, or deployment was performed by the site worker. Static-site preparation does not establish runtime adoption, upstream compatibility, sustained capacity, or accessibility conformance.
