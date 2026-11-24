# Security

Sentinel is a local prototype under a trusted OS account. It is not a multi-user security boundary or authenticated remote service.

## Operating boundary

- The receiver binds to loopback. Host, Origin, and Fetch Metadata checks reduce common browser-origin risks; they are not authentication.
- Ingestion accepts a specific exporter JSON subset. No secrets, prompts, transcripts, or message bodies belong in that telemetry.
- Keep journals, checkpoints, configuration, and identity bindings local. Back up deliberately.
- Static GitHub Pages output contains documentation only. Never publish a runtime directory or expose a receiver through Pages, a proxy, or an iframe.
- Pin and inspect the separate upstream exporter. Exact-version interoperability remains a production gate.

Remote exposure would require a separately reviewed read-only broker, scoped authentication, TLS, and additional isolation. It is outside this implementation.

## Reporting a vulnerability

Do not put sensitive payloads, identities, journals, or credentials in a public issue. Use GitHub private vulnerability reporting if it is enabled on [OOOffsite/sentinel](https://github.com/OOOffsite/sentinel/security). Its availability and a dedicated security contact have not yet been verified. If no private channel is available, request one in an issue without disclosing exploit or private details.

No response-time commitment or supported-version security policy is claimed for this prototype. The maintainer should configure private reporting before public release.
