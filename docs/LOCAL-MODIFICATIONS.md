# Local modifications: public packaging decisions

Reviewed October 31, 2026. Source and isolated checks resolve several previous inventory gaps. This review did not restart production services, install packages into them, load/unload models, or run a render.

| Component | Finding | Public installation decision |
| --- | --- | --- |
| Hermes file interceptor | Modified `tools/file_tools.py` routes Windows paths through an untracked helper; it forces replacement writes without passing the expected digest and skips native file checks | Exclude the interceptor. Use pinned upstream Hermes and the explicit [read/create-only workspace package](../integrations/windows-workspace-mcp/README.md); qualify their integration separately |
| Hermes Python | Upstream managed-tool lock and active package-manager facts agree on Python 3.14.7+20260901 and its archive digest | Use the upstream managed installation; do not copy private test-home directories |
| NemoClaw launcher/container | Installed wrapper differs materially from the checkout; base image digest does not capture later container changes | Exclude private wrappers. Publish the clean-source Hermes candidate with its different execution boundary stated explicitly |
| Rootless Podman | Socket/storage belong to the service-owning Linux account; another default account sees a different store | Document the account/context relationship; do not hard-code generated container IDs |
| Open WebUI launcher | Includes machine-specific origins, image workflow files, alternate endpoint routing, and disabled authentication | Use the minimal local, authenticated configuration in the guide; qualify additional integrations explicitly |
| ComfyUI-MultiGPU | Two compatibility changes with identifiable upstream bases | Publish [opt-in patches and regression checks](../patches/comfyui-multigpu/README.md); real CUDA qualification pending |
| ComfyUI-GGUF | All 16 non-cache source files match upstream Git blobs exactly | Pin commit `6ea2651e7df66d7585f6ffee804b20e92fb38b8a`; the moving `2.0.0` marker is insufficient |
| ComfyUI MCP bridge | Small portable stdio client of the ComfyUI API | Publish [source, direct pins, and a fake-service test](../integrations/comfyui-mcp/README.md) |
| Render-Coordinator | Hook adds resource coordination, not graph nodes; requires private launcher/token/configuration and unqualified network topology | Exclude from first portable candidate; qualify a manual sequential GPU transition before automating it |

The [GGUF verification record](../inventory/gguf-source-verification.json) identifies the public content, not the historical download method. Its pinned source carries Apache-2.0. MultiGPU's derived patches carry the upstream GPLv3 text and attribution. Original integrations remain subject to the root project's license decision. The [workspace tool report](../inventory/windows-workspace-bridge-checks.json) records 16 passing tests, one privilege-related symlink-fixture skip, and no failures; native stdio discovery and file calls passed. Three additional independent temporary-file edge checks also passed. This does not yet qualify the Hermes/WSL route.

## ComfyUI restart discrepancy

The inspected ComfyUI source requirements include these packages, but the on-disk virtual environment does not provide the expected complete installations:

| Requirement | Fresh interpreter observation |
| --- | --- |
| `comfyui-frontend-package==1.55.17` | Module not found |
| `comfyui-workflow-templates==0.11.82` | Module not found |
| `comfyui-embedded-docs==0.5.14` | Module not found |
| `comfy-kitchen==0.2.37` | Namespace directory and residual license metadata only |
| `comfy-aimdo==0.5.6` | Module not found; residual older license metadata |

The pinned source imports `comfy_aimdo.control` during startup. A fresh process using that source and the inspected environment would encounter that missing import. A current health response and passing `pip check` do not establish restart readiness: `pip check` checks installed distribution metadata, not whether every application requirement is present. A running process can retain already-imported code. The precise cause of the disk discrepancy and the live process's absolute source origin remain unresolved.

The public guide therefore builds a **new** environment from source requirements and checks imports before starting a test service. No repair was applied to the production environment while it was active. A controlled production repair/restart and real image/video verification are separate operational work. [Pinned requirements](https://github.com/Comfy-Org/ComfyUI/blob/3541246a9c997f4b8c32f9f88f3c985d02021c79/requirements.txt)

## What counts as resolved

- Exact Qwen Heretic model/projector acquisition sources are identified; rebuilding the weights from the original base is still not reproducible from available publisher details.
- All 21 media filenames have pinned upstream candidates. Seven have matching saved cache metadata; one has a matching download-script source; thirteen have filename/size evidence only. Large local file hashes and workflow qualification remain separate.
- MultiGPU patches reproduce the modified source bytes and pass isolated behavioral checks. That does not establish correct CUDA streams or render quality.
- The unsafe Hermes interceptor is replaced in the proposed design by explicit read/create tools. Complete Windows/WSL route and agent-task qualification remain required.
- Portable installation instructions now exist as a draft. A clean full installation, UI/agent/media integration, and acceptance report are still release requirements.

See [the guided draft](INSTALLATION.md), [Hermes candidate](HERMES-INSTALLATION-CANDIDATE.md), and [model sources](MODEL-SOURCES.md) for actionable next steps and their precise test limits.
