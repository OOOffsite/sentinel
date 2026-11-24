# Contributing

Help improve accurate observation, documentation, and reproducible local behavior. Target repository: [OOOffsite/sentinel](https://github.com/OOOffsite/sentinel).

## Before a change

Read [ADR-S01](INTEGRATION.md) and [observation semantics](wiki/observation-model.md). Preserve local-only collection, OpenRig's authority, explicit identity, and simulation separation. Do not modify upstream OpenRig, global harness settings, credentials, or live sessions as part of a contribution.

## Local checks

Use Python 3.11+ in an isolated development environment. Optional dependencies can be installed by the contributor:

```bash
python -m pip install -r requirements-dev.txt -r requirements-docs.txt
python tests/test_module.py
python tools/build_site.py --check
```

The six module tests use temporary fixtures, including a local test server. Passing fixtures does not establish real exporter interoperability. Run the exact pinned exporter against the intended installed OpenRig version before production claims.

## Documentation and brand

Edit Markdown in `docs/`; the build publishes it into the same navigation as the marketing site. The wiki is repository-owned. Keep links relative, label sample data, and use the [brand guide](brand/style-guide.md). Do not commit generated `_site/` output or runtime data.

## Pull requests and reports

Describe the concrete behavior change, the evidence used, checks performed, and remaining limits. Include synthetic repro fixtures, versions, and expected/actual results. Exclude secrets, raw prompts, transcripts, private paths, databases, and checkpoints from public reports.

Changes to contracts require an explicit compatibility decision. Preserve the simulation 1.0.0 baseline. See [release preparation](guides/releasing.md) for distribution checks and approval gates.

## License

Contributions are intended for distribution under the project's [Apache-2.0 license](../LICENSE). Third-party assets need their own compatible provenance; do not infer rights from a screenshot or public repository.
