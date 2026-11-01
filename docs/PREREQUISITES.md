# Build prerequisites

This checklist defines the information needed before a reproducible installation can be offered. The [guided draft](INSTALLATION.md) now supplies concrete setup candidates and checks; it is not yet a qualified clean-machine recipe or a hardware shopping list. The [dependency inventory](DEPENDENCIES.md) and [local modifications](LOCAL-MODIFICATIONS.md) distinguish observed versions from reviewed packaging decisions; the [model guide](MODEL-GUIDE.md) provides initial GPU-tier candidates to qualify.

## Reference hardware

The October 31, 2026 reference observation reports Windows 11 Education, an AMD Ryzen 9 9900X, 61.07 GiB of OS-visible physical RAM, and two NVIDIA RTX 5080 GPUs with 16,303 MiB each. See [reference status](REFERENCE-STATUS.md) for software observations and limitations.

The existing machine reports 61.07 GiB of physical RAM and two GPUs with 16,303 MiB each. Installed RAM module specifications were not inventoried. A supported minimum has not been established. Different models, quantization, context lengths, and media workflows require different resources. Two GPUs must not be assumed to behave like one GPU with all of their memory available to every application.

## What a builder will need

| Area | Required information or capability | Qualification still needed |
| --- | --- | --- |
| Operating system | A tested Windows version and an account able to complete required setup steps | Supported Windows editions/builds |
| Graphics | A supported GPU/driver combination for the chosen workload | Minimum and recommended VRAM, supported single-GPU profiles |
| Memory | Enough RAM for the chosen model, services, and workload | Measured minimum and headroom |
| Storage | Space for programs, runtime environments, downloads, model files, cache, workspace, and outputs | Download size and peak installation space per profile |
| Linux environment | WSL and container prerequisites for the selected Agent profile | Exact distribution, container image/digest, network and mount recipe |
| Model runtime | A qualified Ollama release and selected model | Exact digest, quantization, context and source terms |
| User interface | A qualified Open WebUI release and its runtime | Version, dependency lock, local onboarding, backup procedure |
| Agent | Hermes and the selected local tool/inference integration | Complete launch, dependency, permission and path configuration |
| Full-workstation media | ComfyUI plus the custom nodes and models used by selected image and video samples | Pinned versions, model terms, sample fixtures and output checks |
| Connectivity | Initial access to approved download sources; optional later online tasks | Offline operation test after dependencies are present |
| Credentials | User-created local credentials where required; optional third-party credentials only for selected integrations | Supported secure local storage and onboarding behavior |

## Decisions the future setup flow should collect

1. Full workstation (Core + Agent + ComfyUI images/videos) or a smaller Core/Core-Agent subset.
2. Where to put programs, models, workspace data, and output files.
3. Which tested model profile to use for the detected hardware.
4. Whether services should start manually or at sign-in.
5. Any required local account setup and optional integration choices.

The standard local profile should not ask for cloud AI API keys. Advanced network access should be configured separately from the local setup.

## Before an installation guide can be called complete

- [ ] Publish exact source locations, dependency versions, and model identifiers/digests.
- [ ] Measure disk, RAM, VRAM, and installation time for the reference profile.
- [ ] Resolve Windows/container path mappings and network dependencies.
- [ ] Document required elevation, reboot, license, and sign-in steps.
- [ ] Document startup, failure recovery, upgrades, and data preservation.
- [ ] Provide synthetic or licensed sample data and independent checks.
- [ ] Complete a separate clean installation using the guide alone.

Until those checks are complete, use the guided draft for controlled technical review and separate test installations. There is no supported one-command installation yet.
