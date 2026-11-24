# Preparing a release

This guide covers releases from **OOOffsite/sentinel** to GitHub and the **sentinel-openrig** Python distribution on PyPI. A successful local build does not by itself publish an artifact or establish registry name ownership.

## 0.4.0 publication record

Published on **2026-11-24**, in order: GitHub tag/release, then PyPI. The annotated `v0.4.0` tag points to commit `9b9222c6b34b39aa1379697951979208e55b774a`.

- [GitHub alpha release and assets](https://github.com/OOOffsite/sentinel/releases/tag/v0.4.0)
- [PyPI 0.4.0](https://pypi.org/project/sentinel-openrig/0.4.0/)
- [Release-commit CI](https://github.com/OOOffsite/sentinel/actions/runs/45475204323): passed on Linux Python 3.11–3.14.
- [Initial Pages deployment](https://github.com/OOOffsite/sentinel/actions/runs/45475301353): succeeded.

Both registries report the same SHA-256 digests as the checked local artifacts:

| Artifact | SHA-256 |
| --- | --- |
| `sentinel_openrig-0.4.0-py3-none-any.whl` | `0c64acf14a3e8ed4b1e974bce5dfd80c519c3f0506da90029b3fcbc394fbb8c2` |
| `sentinel_openrig-0.4.0.tar.gz` | `1f9075a8228fb8d1b257cd47200f44c36f79d5cbadc9ef0012dc32f8f0a602fe` |

A fresh, disposable environment installed `sentinel-openrig==0.4.0` directly from PyPI with no dependencies. `pip check`, both installed CLI help commands, package version, and bundled dashboard resources passed. Local clean-wheel testing also passed the six fixtures on Python 3.11–3.14.

This first publication used a securely injected publishing token. No TestPyPI upload was performed and no PyPI Trusted Publisher configuration is claimed. The tagged artifacts remain immutable; subsequent documentation updates on `main` record publication without replacing those artifacts.

## Current release decisions

| Item | Decision |
| --- | --- |
| Package | `sentinel-openrig` |
| Import package | `atlas_sentinel` (preserved for compatibility) |
| Version | `0.4.0` |
| License | Apache-2.0, selected by the maintainer |
| GitHub repository | `https://github.com/OOOffsite/sentinel` |
| GitHub Pages | [Published site](https://oooffsite.github.io/sentinel/) |
| Observation contract | `1.1.0` |
| Preserved simulation contract | `1.0.0` |

The original wheel in `dist/` predates public release preparation. Build new artifacts from the final reviewed source; never upload the old wheel merely because its version matches.

## Build and inspect locally

Use an isolated development environment. The following commands install only explicitly selected development/build tools into that environment; the release checker itself never installs or publishes anything.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-release.txt -r requirements-dev.txt
python tests/test_module.py
python -m build --outdir release-dist
python -m twine check --strict release-dist/*
python tools/check_release.py release-dist --require-publishable
```

Use a new or empty `release-dist` directory for each version. The standard `build` frontend creates an sdist and then builds its wheel from that sdist. Review both artifacts and the checker's SHA-256 digests. The checker verifies version/metadata consistency, absolute PyPI description links, license contents, required runtime resources, archive paths, known local-state exclusions, and both packaged CLI help commands. It uses a disposable extraction directory and does not launch the receiver or an agent.

These are bounded checks, not a comprehensive credential audit, dependency audit, or proof of live interoperability. Inspect the full source distribution before publication. The PyPI description intentionally uses a separate `README.pypi.md` so GitHub-relative images and links do not break on the package index.

The initial release preflight passed clean wheel installation, both installed CLI entry points, `pip check`, and all six fixtures against the installed package on local Python **3.11.15**, **3.12.14**, **3.13.12**, and **3.14.6**. Twine's strict description/metadata check passed for the source archive and wheel. These checks were performed on macOS; they are not claims of Windows testing or live OpenRig compatibility. The workflow repeats installed-wheel fixtures on Python 3.11–3.14 using Linux runners before allowing publication.

## Configure publication

Before publication:

1. Create or verify the exact `OOOffsite/sentinel` repository and its ownership, then review the initial files before pushing. Do not include local configuration, runtime journals, checkpoints, caches, credentials, or workstation-specific instructions.
2. Confirm ownership or availability of `sentinel-openrig` separately on PyPI and TestPyPI. A missing public package page is not a reservation.
3. Choose the authorized publication path: GitHub Actions with Trusted Publishing, or a local upload using a securely injected token. OIDC configuration is required for the workflow path, not for a separately authorized local upload.
4. For the workflow path, create GitHub environments named `testpypi` and `pypi`; configure required reviewers and restrict deployment tags to reviewed release tags. Register a Trusted Publisher with owner `OOOffsite`, repository `sentinel`, workflow `release.yml`, and the matching environment. For a first release, use the index's pending publisher flow. Repository environment protection is external configuration; the YAML file cannot establish that it exists.
5. Enable two-factor authentication on maintainer accounts and review organization permissions. Never add an API token to the repository, command-line arguments, generated documentation, or release logs.

Follow the official [PyPA publishing guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/) and [PyPI Trusted Publisher setup](https://docs.pypi.org/trusted-publishers/adding-a-publisher/). First releases use [creating a project with a Trusted Publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/).

## Publish the same checked artifacts

Create the reviewed version tag and GitHub release first, attaching the checked wheel, source archive, and their SHA-256 checksum file. For this initial local prototype, identify the GitHub release as an alpha/prerelease; preserve the package's `0.4.0` version and development-status metadata.

Then upload those same two package files to PyPI. A local release runner may retrieve an authorized publishing token from a secret manager and pass it to Twine through the child process environment (`TWINE_USERNAME=__token__`, `TWINE_PASSWORD` supplied in memory). Do not print the token, place it in shell history, save it to `.pypirc`, or include it in public evidence. Run Twine noninteractively so failures cannot hang on credential prompts.

Upload only the `.whl` and `.tar.gz` files. Checksum files and verification reports belong in GitHub release assets or local evidence, not a PyPI upload glob. Verify the published version and file digests through PyPI metadata, then test a fresh installation from the index. A successful upload response alone is not the same evidence as a successful consumer installation.

## Review the manual workflow

The **Prepare or publish Python release** workflow runs only through `workflow_dispatch`. Its default target, **build-only**, runs fixtures, builds artifacts, checks metadata and packaged commands, uploads review artifacts to the workflow run, and tests the installed wheel across Python 3.11–3.14. It does not upload to an index.

Publication targets are **testpypi** and **pypi**. Both require the selected ref to be the exact version tag, such as `v0.4.0`, and the workflow to run in the approved repository. The build and installed-wheel test jobs have no index credentials. Only the separate publication job receives `id-token: write`, uses the selected environment, and downloads the artifacts checked by the build job after the full Python matrix passes.

Use TestPyPI for the first complete publication rehearsal. Verify installation from the uploaded artifact in a disposable environment, both commands, package resources, and README rendering. PyPI and TestPyPI have separate accounts, project ownership, and publisher configurations.

Production publication is a separate explicit selection after review. Tags and version numbers are not approval substitutes. Do not use a production release to test upload configuration; index filenames cannot simply be replaced after upload.

## Release evidence and remaining gates

Record the reviewed Git commit, matching version tag, artifact hashes, fixture results, TestPyPI installation result, and workflow run URL. Update [the changelog](../../CHANGELOG.md) and [status](../STATUS.md) with what actually happened. Add registry/build/deployment badges only when their targets exist and their meaning is accurate.

The current prototype must still pass interoperability tests against the installed OpenRig version and exporter commit `1beecce96befec880a93f60b11d83b44d7347620` before any production-readiness claim. Actual materialization, live model sessions, remote security, retention, and sustained capacity remain independent validation work. Publishing an alpha package does not complete those gates.

Use the [GitHub Pages guide](github-pages.md) for the static documentation site. Its deployment does not expose or start Sentinel's local receiver.
