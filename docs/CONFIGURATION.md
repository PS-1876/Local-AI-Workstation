# Portable workstation configuration

The [example configuration](../config/workstation.example.json) and [JSON schema](../schemas/workstation.schema.json) define a proposed input contract for a future installer. They do not change a machine or configure any service. Schema validation checks document shape, not installation readiness, filesystem access, GPU fit, service bindings, or end-to-end operation.

## Full workstation is the main target

The `full` profile includes local inference, Open WebUI, Hermes with its tool environment, and ComfyUI for images and videos. `core` and `core-agent` are smaller subsets for constrained hardware or incremental setup. Completing a subset does not satisfy the full-workstation release.

## Choices a user should make

| Choice | Proposed field | Behavior |
| --- | --- | --- |
| Full or smaller installation | `installationProfile` | Full is the intended main experience. |
| Program and data locations | `paths` | The sample C: and D: locations are examples. The installer must detect real volumes and allow different locations. |
| Standard or Heretic general model | `generalModel.variant` | Both use the same setup infrastructure; select an exact qualified artifact. |
| Model and usable context | `generalModel.tag`, `digest`, `contextTokens` | Unset until a hardware profile and exact source have been qualified. |
| Image/video workflows | `media` | Unset until redistributable workflows, dependencies, and output checks exist. |
| Startup behavior | `operation.startAtSignIn` | Manual startup is the example; automatic startup is a deliberate choice. |

Passwords, tokens, personal prompts, browser sessions, and project content do not belong in this configuration. Future secret references need a separate supported storage design.

## Host URLs and container routing

`hostServiceUrls` describes addresses a Windows-side client would use. These are not a promise that each service binds only to loopback. A container's `127.0.0.1` addresses that container, not the Windows host; container-to-host routes must be defined separately once the deployment recipe is qualified.

The draft permits local HTTP addresses only. Its URL pattern is a structural restriction, not a complete port or reachability check. A future preflight must validate ports, path overlap, free space, Windows permissions, container mounts, version compatibility, and actual network bindings before any installation.

## Unresolved values are intentional

Null model and workflow selections prevent an illustrative profile from masquerading as a working install recipe. Before downloads or mutations, an installer must reject unresolved selections required by the selected profile. Image and video workflow selections are required for `full`; smaller subsets may leave them null. The local custom Heretic model is not the default downloadable artifact because its public provenance remains unresolved.

The `local-only`, `sequential`, and `manual` policy values express requirements. No enforcement mechanism is implemented by these JSON files. The GPU transition must still be proved by saving work, releasing resources, generating and verifying media, and resuming the agent.

## Configuration lifecycle

Keep the example in Git. Copy user selections to an ignored local configuration file, validate them, and review the proposed changes before running a future installer. Separate runtime state from configuration, preserve existing files, record applied steps, and retain recoverable configuration backups.
