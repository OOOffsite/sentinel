# Sentinel wiki

The wiki lives alongside the code and is published with the site. Documentation changes can be reviewed with implementation changes; there is no separate Wiki repository to synchronize.

## Learn the model

- [Architecture](architecture.md): component responsibilities and data flow.
- [Observation model](observation-model.md): identity, freshness, replay, and uncertainty.
- [Integration decision](../INTEGRATION.md): ADR-S01 and proposed enhancements.

## Frequently asked questions

### Does Sentinel run agents?

No. OpenRig controls agents and queues. The separate preparation CLI can explicitly create isolated worktrees and generated resources after plan review, but does not launch agents.

### Why are seats unknown?

A planned seat may have no binding, no supported sample, a stale sample, a future timestamp, or insufficient presence evidence. See the [observation model](observation-model.md).

### Can I watch messages between agents?

Current exported metadata does not establish authoritative sender/receiver pairs. Sentinel reports `communication_available: false`; it does not invent directed messages or substitute simulation.

### Does working mean coding?

No. It means sampled working activity. Coding, testing, and review phases need additional authoritative evidence and verified semantic mapping.

### Is Sentinel an OpenRig plugin?

It is an independent companion. Optional manifests provide a read-only monitor skill for unmanaged sessions. Managed agents should use native OpenRig resource projection. No daemon UI plugin registration is claimed.

### Can the monitor run on the internet?

The receiver is loopback-only and trusts the local OS account. It has no remote authentication boundary. The public site contains only documentation. See [security](../SECURITY.md).

### Where do I begin?

Read [getting started](../guides/getting-started.md), then [operations](../guides/operations.md). The [contract catalog](../reference/contracts.md) is for consumer implementers.
