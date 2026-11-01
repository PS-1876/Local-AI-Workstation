# Reference dependencies and reproduction gaps

Observed October 31, 2026, America/Los_Angeles. This read-only inventory records the existing full workstation: local inference, the user interface, Hermes and its tool environment, and ComfyUI for images and videos. No services were started or stopped, no inference or generation jobs were submitted, and no model residency was changed.

The [machine-readable baseline](../inventory/reference-2026-10-31.json) is an observed snapshot, not a dependency lock or installer manifest. It records concrete versions and unresolved items without claiming that this combination has been installed successfully on a clean machine.

## Core platform

| Component | Observed baseline | Reproduction status |
| --- | --- | --- |
| Windows | Windows 11 Education, build 26300 | Reference observation; supported editions/builds remain to qualify |
| CPU and RAM | Ryzen 9 9900X, 12 cores/24 logical processors, 61.07 GiB OS-visible RAM | Installed RAM module specifications not inventoried |
| GPU and driver | Two RTX 5080s, 16,303 MiB each; NVIDIA driver 617.42 | No fresh workload-fit or performance measurement |
| PowerShell and Git | PowerShell 7.6.5; Git 2.55.0.windows.5 | Tool versions, not minimum requirements |
| Ollama | Native Windows application; API reports 0.40.13 | Local inference and network topology still require explicit acceptance tests |
| Open WebUI | Application/package 0.11.4; Python 3.12.10 | Installed distribution inventory captured; local launcher not packaged |

The [Open WebUI package inventory](../inventory/open-webui-packages.json) contains 245 installed distribution names and versions. Presence does not mean every package is required for the selected local workflow or that cloud integrations are configured. It also does not identify original wheel sources, platform-specific downloads, or artifact hashes.

The installed Open WebUI distribution identifies its license as **Open WebUI License**, with accompanying license history and notices. Review that version's terms before packaging or changing branding; do not label the dependency as MIT or substitute this project's future license for it.

## Agent environment

| Component | Observed baseline | Reproduction status |
| --- | --- | --- |
| WSL | 3.0.3.0 | Existing distribution was already running before inspection |
| Linux distribution | Ubuntu 24.04.5 LTS | Distribution acquisition/export procedure not qualified |
| Active Linux kernel | 6.18.54.1-microsoft-standard-WSL2 | Recorded reference only |
| Podman | 6.1.3 | Running sandbox uses a separate existing API socket/storage context |
| OpenShell | 0.0.116 | Acquisition and binary-integrity record unresolved |
| NemoClaw checkout | Package 0.1.0; commit `6f3cced4230ae9660c049cc11804daf37797c595` | Tracked source clean; exact deployment relationship still to establish |
| Hermes health/source | 0.22.4; commit `4d04303818b61bf3aa09278af48356315515965b` | One tracked source modification plus local launch wrappers |
| Active Hermes Python | 3.14.7 | Separate from default container Python 3.13.5 and stale package metadata 0.21.3 |

The base sandbox image is `ghcr.io/nvidia/nemoclaw/hermes-sandbox@sha256:afe428ec04ff4cbc3c397756eb44224bd5212a4f7044928bed855a9f093761de`. The digest identifies the image, not the current modified container environment. The active source and launcher are not covered by a container mount, so their later changes must be captured separately.

The source tree for [Hermes](https://github.com/NousResearch/hermes-agent) has a modified `tools/file_tools.py`. The observed [NemoClaw](https://github.com/NVIDIA/NemoClaw) checkout requires Node at least 22.19.0, but no native Node executable was found on the default Linux path. An `npm` version response alone did not resolve Windows-versus-Linux runtime provenance.

Hermes has a `uv.lock` with 328 package records; NemoClaw has a version-3 package lock with 613 entries. Their hashes are recorded in the baseline. Neither lock has been shown to recreate the active interpreter, local wrappers, or current tool environment. The deployment guide must reconcile those layers before automating them.

## General model

The selected local reference is `qwen3.6-35b-heretic:latest`, a Q4_K_M GGUF with approximately 34.7B parameters and a reported 22.14 GB package size. Configuration specifies 65,536 context tokens. The metadata maximum of 262,144 is not a validated target.

The API reported no resident models during this inventory. The custom model's API digest and local blob metadata are recorded, but a public acquisition source, exact base revision, transformation recipe, and applicable artifact license have not been established. Do not convert the local tag into a public download instruction. See the [model guide](MODEL-GUIDE.md) for standard-model candidates and the Heretic profile policy.

## ComfyUI and media

ComfyUI is a required part of the **full** workstation. Smaller installation profiles may omit media, but they are subsets of the product.

| Component | Observed baseline | Reproduction status |
| --- | --- | --- |
| ComfyUI | 0.40.0; commit `3541246a9c997f4b8c32f9f88f3c985d02021c79` | Tracked source clean; active virtual environment identified |
| Python and PyTorch | Python 3.13.12; PyTorch 2.12.1+cu130 | Separate environment from Open WebUI |
| ComfyUI-MultiGPU | 2.6.4; commit `37a73feda5804045e4f39d8c640905d62a2169d1` | Two tracked source files modified |
| ComfyUI-GGUF | Source version 2.0.0 | No Git checkout; exact archive/revision provenance unresolved |
| Render-Coordinator | Local source without Git metadata | Source packaging, provenance, and licensing unresolved |
| ComfyUI MCP bridge | Python 3.12.10; `mcp==1.30.0`; `httpx==0.28.1` | Local code and stored dependency pins; no clean-install or live handshake test in this inventory |

Sources recorded in local metadata include [ComfyUI](https://github.com/Comfy-Org/ComfyUI), [MultiGPU](https://github.com/pollockjj/ComfyUI-MultiGPU), and [GGUF](https://github.com/city96/ComfyUI-GGUF). A Git origin or a version string does not prove that local modified files equal an upstream release.

MultiGPU's modified files are `__init__.py` and `p2p_registry.py`. Their source fingerprints are recorded without copying the code. Current ComfyUI launch arguments do not include the historically used `--cuda-device all`; two devices were nevertheless enumerated by the endpoint. Actual workload placement needs a new task-level check.

The ComfyUI and bridge environments pass `pip check`. However, five declarations in ComfyUI's source requirements have no matching installed distribution metadata: frontend package, workflow templates, embedded docs, comfy-kitchen, and comfy-aimdo. This discrepancy must be explained before deriving an installation lock. It is not evidence by itself that the running application is broken.

The [media file inventory](../inventory/media-model-files.json) lists 21 targeted model files with byte sizes, including Qwen Image, Wan, LTX, encoders, and VAEs. Presence and filenames do not prove source, integrity, licensing, or workflow compatibility. The full release must select and qualify one redistributable image workflow and one video workflow with the complete dependency set for each.

## Keep environments separate

This reference uses different Python and library versions for different workloads. For example, Open WebUI's speech-related environment pins PyAV 16.1.0, while ComfyUI has PyAV 18.1.0. The local speech constraint's rationale has not been functionally retested.

A future installer should create component-specific environments rather than combine every package into one Python environment. [ComfyUI package observations](../inventory/comfyui-packages.json) and [bridge package observations](../inventory/comfyui-mcp-packages.json) are evidence to reconcile, not commands to install blindly.

## Remaining work before a reproducible recipe

1. Review and package the local Hermes, MultiGPU, launcher, coordinator, and bridge changes with appropriate source attribution.
2. Resolve the active container connection, storage, Python, Node, mount, and inference-routing recipe.
3. Trace exact model downloads, digests, projectors, licenses, and transformation provenance.
4. Explain source-versus-installed dependency differences and create verified, platform-specific locks.
5. Define host/container configuration and actual local network boundaries; local URL checks do not prove isolation.
6. Choose synthetic or licensed image/video fixtures and independent output checks.
7. Reproduce the guided full setup separately, including model/media resource transitions.

The original working environment remains intact. This inventory advances the dependency milestone and identifies why copying version numbers alone would not yet reproduce the whole workstation.
