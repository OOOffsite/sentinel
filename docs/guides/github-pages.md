# GitHub Pages

The repository contains a static marketing site and a Markdown knowledge base. One build publishes guides, wiki, API documentation, specifications, and brand guidelines together.

Repository: [OOOffsite/sentinel](https://github.com/OOOffsite/sentinel). Published site: [oooffsite.github.io/sentinel](https://oooffsite.github.io/sentinel/). The initial [Pages deployment](https://github.com/OOOffsite/sentinel/actions/runs/45475301353) succeeded on 2026-11-24.

## Build locally

Use Python 3.11+ and an isolated environment with the optional pinned documentation requirements:

```bash
python -m pip install -r requirements-docs.txt
python tools/build_site.py --check
python -m http.server 8080 --bind 127.0.0.1 --directory _site
```

Open `http://127.0.0.1:8080/` and stop the server with Ctrl-C when finished. Check a nested page, narrow layout, keyboard navigation, and the illustrative evidence controls. The build uses a maintained CommonMark parser; browser JavaScript never fetches Markdown or connects to a fleet.

## Source map

| Source | Published result |
| --- | --- |
| `site/index.html` | Homepage |
| `site/assets/` | CSS, JavaScript, and original brand assets |
| `site/docs-template.html` + `docs/**/*.md` | Styled documentation pages |
| `contracts/` | Downloadable specifications in `references/contracts/` |
| Selected public files and examples | Downloadable reference material |

`_site/` is generated and ignored. The builder validates local links, anchors, and asset references. It only copies allowlisted public files; it does not copy runtime databases, checkpoints, global guidance, or the local dashboard. All navigation is relative and works under a repository subpath.

## Publish after review

1. Push the reviewed repository to the approved GitHub target.
2. In repository settings, select **Pages → Source → GitHub Actions**.
3. Review the `github-pages` environment and any protection rules.
4. Run the **Publish documentation** workflow manually on the approved branch.
5. Verify the workflow's returned URL, nested navigation, downloadable specs, and social preview before announcing it.

The Pages workflow is manual-only. CI builds and checks documentation without publishing. These workflows do not launch OpenRig, agents, or Sentinel's receiver.

## README badges

README badges link to the published PyPI package, GitHub alpha release, and actual CI workflow. Static badges describe Python support, contract, alpha status, runtime dependency count, and license. Keep workflow status dynamic and add new registry/deployment badges only after their targets exist.

## Wiki maintenance

Edit `docs/wiki/` in a normal pull request. This deliberately shares version control and navigation with the rest of the documentation; enabling a separate GitHub Wiki is unnecessary. If a separate Wiki is later required, define a single source and synchronization policy first.
