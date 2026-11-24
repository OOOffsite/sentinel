# DRTW: public documentation and GitHub Pages

**Date:** 2026-11-24. **Consumer:** UI Studio / Sentinel documentation. **Question:** Which existing tools and conventions make a distinctive public README and a maintainable static knowledge site without another runtime stack?

## Discovery

L1: The repository is Python 3.11+ with no runtime dependencies, HTML dashboards, JSON Schema, OpenAPI, and unittest/jsonschema fixtures. An existing local development environment supplies markdown-it-py 4.2.0 and mdurl 0.1.2. No installation was needed for this work.

L2: Python pathlib/shutil/html.parser provide static assembly and local-link validation; browsers supply responsive CSS, native disclosure controls, buttons, and reduced-motion preferences. Python does not supply a Markdown parser.

L3: Installed DRTW, UI Studio, and Sites guidance favor reusable primitives, static output, original identity, and rendered verification. No existing project design system or docs generator was present.

L4: Primary docs and registries were fetched for markdown-it-py, Python-Markdown, MkDocs, Sphinx, and VitePress. These sources were text-inspected for architecture, compatibility, and licensing, not installed to manufacture comparison results.

L5: Adopt GitHub's README, relative-link, wiki, Pages Actions, and Shields static-badge conventions. Separate overview, task guides, explanation/wiki, and exact reference. Keep Markdown as the single knowledge source.

L6: Only a small assembly/link-rewrite adapter and original visual presentation are project-specific. Markdown parsing is reused, not recreated.

## Candidate assessment

Scores are 0–5: 1 poor fit, 3 workable with tradeoffs, 5 strong fit. Weights: security .30, adoption .25, compatibility .25, maintenance .15, bundle .05. Unknown dimensions are **null**, not assumed safe. Security advisory audits and comparable current adoption measurements were not performed, so rankings below are provisional fit rankings; weighted ranges overlap. Bundle scores describe architectural browser cost, not a benchmark.

| Candidate | Layer | Adoption | Security | Compatibility | Maintenance | Bundle | Known contribution / possible total |
| --- | --- | --- | --- | --- | --- | --- | --- |
| markdown-it-py + static template | L1/L4 | null | null | 5 | 4 | 5 | 2.10 / 2.10–4.85 |
| MkDocs | L4 | null | null | 4 | 4 | 5 | 1.85 / 1.85–4.60 |
| Python-Markdown + template | L4 | null | null | 4 | 4 | 5 | 1.85 / 1.85–4.60 |
| Sphinx | L4 | null | null | 3 | 4 | 5 | 1.60 / 1.60–4.35 |
| VitePress | L4 | null | null | 2 | 4 | 3 | 1.25 / 1.25–4.00 |
| Handwritten Markdown parser | L6 | 0 | null | 2 | 1 | 5 | 0.90 / 0.90–2.40 |

## Top three and decision

| Rank | Candidate | Pros | Cons |
| --- | --- | --- | --- |
| 1 | markdown-it-py | Already available; CommonMark; MIT; Python; server-rendered static HTML. | Needs thin template/link adapter. |
| 2 | MkDocs | Complete docs system and static deployment conventions. | New generator/theme integration for a small bespoke marketing surface. |
| 3 | Python-Markdown | Established Python parser with table/TOC extensions; BSD-3-Clause. | Not already installed here; not CommonMark. |

**Adopted:** adapt markdown-it-py 4.2.0 with pinned mdurl 0.1.2 for build time only. Also adopt GitHub Pages Actions, static metadata badges, and the repository-owned wiki pattern. Choice is based on existing availability and scope fit, not a claim of audited superiority.

**Deferred:** MkDocs when search, localization, or documentation scale warrants a full generator; Sphinx if autodoc/cross-reference needs grow; VitePress if a Vue-based product ecosystem emerges.

**Rejected:** handwritten parsing, browser-time Markdown/CDN loaders, copied marketing templates, invented passing CI or registry badges. Established tools already cover the needed behavior.

## Integration notes

- Build with `python tools/build_site.py --check` into ignored `_site/`.
- `docs/**/*.md` renders through one HTML template; relative Markdown links become HTML links.
- Downloadable schemas stay together so JSON Schema references resolve.
- Only explicit public inputs enter the site; no whole-repository copy.
- No runtime npm dependency, external font, analytics, or live telemetry connection.
- Native controls and responsive CSS carry the interactions; reduced motion is honored.
- Preview under both root and a repository subpath before release.
- Pages publication is a manual workflow; CI builds without deploying.
- Removing the site build has no effect on the Python receiver or its contracts.
- Reuse documentation under the package's Apache-2.0 terms; dependency licenses remain distinct.

## Sources

- [GitHub README conventions](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [GitHub wiki model](https://docs.github.com/en/communities/documenting-your-project-with-wikis/about-wikis)
- [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Shields static badges](https://shields.io/badges/static-badge)
- [markdown-it-py documentation](https://markdown-it-py.readthedocs.io/en/latest/) and [package metadata](https://pypi.org/project/markdown-it-py/)
- [MkDocs](https://www.mkdocs.org/), [Python-Markdown](https://python-markdown.github.io/), [Sphinx](https://www.sphinx-doc.org/en/master/), [VitePress](https://vitepress.dev/)

## Follow-ups

- Reassess dependency advisories and pinned actions before a release.
- Replace provisional publication status with verified receipts after the actual GitHub/Pages/PyPI runs.
- Revisit a full documentation generator if scale justifies it.
