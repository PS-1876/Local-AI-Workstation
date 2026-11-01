# Guided installation draft

This is a **technical preview for a separate test machine**, assembled from reviewed upstream sources and the reference workstation. It is not a completed clean-install recipe. Core setup commands and media source pins are concrete; the Hermes host route, selected image/video graphs, integrated UI behavior, and clean-machine acceptance still need qualification. Stop at a failed check and record it rather than applying undocumented fixes.

The target remains the full workstation: local chat, an agent, and ComfyUI images and videos. The steps below build components in that order. Core alone is an intermediate profile.

## 1. Prepare a clean test workspace

Use Windows, a compatible NVIDIA driver, Git, PowerShell 7.4 or newer, Python 3.12 for Open WebUI/MCP, and Python 3.13 for the ComfyUI candidate. WSL2/Linux is needed for the Hermes candidate. Obtain operating-system features and drivers from their official sources; record any required elevation or reboot. See [prerequisites](PREREQUISITES.md) and [observed versions](DEPENDENCIES.md). The reference versions are not minimum hardware requirements.

Choose program, model, workspace, output, and state locations on existing volumes. Examples below use `C:\LocalAI` and `D:\LocalAI`; change them to your own locations. Do not point this draft at an existing working installation. Keep environments separate and state outside disposable virtual environments.

Clone this repository into a new directory. In PowerShell 7.4 or newer, select the repository and roots. This version floor makes the native-command error preference below a [stable feature](https://devblogs.microsoft.com/powershell/powershell-7-4-general-availability/), so failed Git/pip commands stop the sequence.

```powershell
if ($PSVersionTable.PSVersion -lt [version]'7.4') { throw 'Use PowerShell 7.4 or newer' }
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
$repoRoot = (Get-Location).Path
$programRoot = 'C:\LocalAI'
$dataRoot = 'D:\LocalAI'
```

Inspect versions with `git --version`, `py -3.12 --version`, `py -3.13 --version`, `nvidia-smi`, and, for Agent, `wsl --version`. Confirm space for selected downloads, temporary files, imported copies, environments, and outputs. Confirm ports 11434, 8080, and 8188 are unused before creating services. If occupied, identify the owner and use separate test ports consistently; do not terminate someone else's service.

The JSON [configuration example](../config/workstation.example.json) is a planning worksheet. No installer consumes it yet.

## 2. Install Ollama and qualify one model

Follow the official [Windows installation instructions](https://docs.ollama.com/windows). For the exact Heretic import candidate, use the recorded 0.40.13 release. Choose `OLLAMA_MODELS` before acquiring models. Apply environment changes to the process running Ollama; changing an unrelated terminal does not reconfigure an already-running tray application.

For this same-host Core test, bind Ollama to `127.0.0.1:11434`. Verify the actual listener as well as `http://127.0.0.1:11434/api/version`; reaching a local URL alone does not prove it is inaccessible over the network. Do not enable broad network binding just to make a container connection succeed.

Choose a standard candidate from the [GPU guide](MODEL-GUIDE.md), or follow the two-file [Heretic import procedure](HERETIC-IMPORT.md). Standard library tags can change: record the resolved digest, runtime version, quantization, and context at acquisition. Do not use the private reference alias as an `ollama pull` instruction.

For an idle test machine with enough measured memory headroom, run a small text check at an explicit initial context. Replace the tag first:

```powershell
$modelTag = '<YOUR_ACQUIRED_TEST_TAG>'
$body = @{
    model = $modelTag
    prompt = 'Return the sum of 19 and 23 as a single number.'
    stream = $false
    keep_alive = 0
    options = @{ num_ctx = 4096; temperature = 0 }
} | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:11434/api/generate' -ContentType 'application/json' -Body $body
```

Independently check the answer is 42. This verifies one request, not coding, tools, vision, long context, or overall reliability. Record offloading and memory while a representative task is running. Increase context only after measuring it.

## 3. Install Open WebUI in its own environment

The reference uses Open WebUI 0.11.4. [PyPI metadata](https://pypi.org/pypi/open-webui/0.11.4/json) confirms Python `>=3.11,<3.13.0a1`; this candidate uses 3.12. Review the version's Open WebUI license and preserve its required notices/branding.

```powershell
$webuiRoot = Join-Path $programRoot 'OpenWebUI'
if (Test-Path -LiteralPath $webuiRoot) { throw 'Use a new Open WebUI test directory' }
py -3.12 -m venv (Join-Path $webuiRoot '.venv')
$webuiPython = Join-Path $webuiRoot '.venv\Scripts\python.exe'
& $webuiPython -m pip install 'open-webui==0.11.4'
& $webuiPython -m pip check
```

This pins the application, not every transitive wheel. Preserve the resolved package inventory and download report during the clean test; the reference's 245-package inventory is not an installation lock.

Start the UI in the same terminal where the step 1 variables and `$webuiRoot` above are defined, with local data and account authentication. This foreground process keeps that terminal occupied; leave it open while using the UI.

```powershell
$env:DATA_DIR = Join-Path $dataRoot 'State\OpenWebUI'
$env:OLLAMA_BASE_URL = 'http://127.0.0.1:11434'
$env:ENABLE_OLLAMA_API = 'True'
$env:ENABLE_OPENAI_API = 'False'
$env:WEBUI_AUTH = 'True'
$env:ANONYMIZED_TELEMETRY = 'False'
$env:DO_NOT_TRACK = 'True'
New-Item -ItemType Directory -Path $env:DATA_DIR -Force | Out-Null
Set-Location -LiteralPath $env:DATA_DIR
& (Join-Path $webuiRoot '.venv\Scripts\open-webui.exe') serve --host 127.0.0.1 --port 8080
```

Keep the working directory and state location stable across starts; preserve the generated local secret and database in backups. Do not publish them. Open the local UI, create your own initial account, verify only the intended local provider is configured, select the test model, and check a response against a known answer. Confirm `/health` separately. The reference launcher's disabled-auth setting, personal network origins, image-workflow files, and alternate service ports are deliberately replaced by this minimal configuration.

Document extraction, embeddings, speech, and offline first-start behavior need separate model/cache acquisition and tests. Do not advertise those as working merely because chat succeeds. After selected assets are cached, test the intended offline workload. [Upstream Python setup](https://docs.openwebui.com/getting-started/quick-start/)

## 4. Qualify the agent candidate

Follow [the pinned Hermes candidate](HERMES-INSTALLATION-CANDIDATE.md) in a separate WSL2 test distribution or dedicated Linux account. It uses clean upstream source and explicit workspace tools instead of copying the private interceptor or container wrappers.

The candidate is **not yet a drop-in recreation of NemoClaw/OpenShell or its Open WebUI adapter**. A plain WSL process has a different execution boundary. Verify the local inference route from inside that exact environment, tool discovery, a host-visible artifact, and project continuity before marking Core-Agent complete. The guide identifies the remaining integration checks rather than inventing a universal container address.

## 5. Prepare a separate ComfyUI environment

The selected reference source is [ComfyUI commit 3541246](https://github.com/Comfy-Org/ComfyUI/tree/3541246a9c997f4b8c32f9f88f3c985d02021c79). Use a new source checkout; do not copy the reference virtual environment. Its on-disk missing-package discrepancy is documented in [local modifications](LOCAL-MODIFICATIONS.md).

Open a second terminal, select this repository's root, and repeat the variable definitions in step 1 before continuing:

```powershell
$comfyRoot = Join-Path $programRoot 'ComfyUI'
if (Test-Path -LiteralPath $comfyRoot) { throw 'Use a new ComfyUI test directory' }
git clone https://github.com/Comfy-Org/ComfyUI.git $comfyRoot
git -C $comfyRoot checkout --detach 3541246a9c997f4b8c32f9f88f3c985d02021c79
git -C $comfyRoot rev-parse HEAD
py -3.13 -m venv (Join-Path $comfyRoot '.venv')
$comfyPython = Join-Path $comfyRoot '.venv\Scripts\python.exe'
$gpuPins = Join-Path $repoRoot 'requirements\comfyui-gpu-windows-py313.txt'
& $comfyPython -m pip install -r $gpuPins --index-url https://download.pytorch.org/whl/cu130
& $comfyPython -m pip install -r (Join-Path $comfyRoot 'requirements.txt') -c $gpuPins
& $comfyPython -m pip check
& $comfyPython -c "from importlib.metadata import version; packages = ('comfyui-frontend-package', 'comfyui-workflow-templates', 'comfyui-embedded-docs', 'comfy-kitchen', 'comfy-aimdo'); print({name: version(name) for name in packages})"
& $comfyPython -c "import comfyui_frontend_package, comfyui_workflow_templates, comfyui_embedded_docs, comfy_kitchen, comfy_aimdo; print('Required modules import')"
& $comfyPython -c "import torch, torchvision, torchaudio; print(torch.__version__, torchvision.__version__, torchaudio.__version__); print(torch.cuda.is_available(), torch.cuda.device_count())"
```

The five package versions must match the pinned source requirements: frontend 1.55.17, templates 0.11.82, embedded docs 0.5.14, kitchen 0.2.37, and aimdo 0.5.6. Checking distribution metadata as well as imports catches incomplete namespace-package remnants. The CUDA probe must report `True` and at least one device; stop qualification otherwise.

The three exact Windows x64 CPython 3.13 CUDA wheels are present in the official index, and their metadata/declaration compatibility was reviewed. The [wheel source record](../inventory/pytorch-wheel-sources.json) records URLs, hashes, and limits. This does not establish a complete environment lock or clean GPU execution. Do not ignore resolver/import errors or replace a dependency silently. A GPU count is device discovery, not a successful render or proof of multi-GPU placement. [ComfyUI manual installation](https://docs.comfy.org/installation/manual_install)

For the Wan GGUF candidate, clone and pin the loader under the new checkout:

```powershell
$ggufRoot = Join-Path $comfyRoot 'custom_nodes\ComfyUI-GGUF'
git clone https://github.com/city96/ComfyUI-GGUF.git $ggufRoot
git -C $ggufRoot checkout --detach 6ea2651e7df66d7585f6ffee804b20e92fb38b8a
& $comfyPython -m pip install -r (Join-Path $ggufRoot 'requirements.txt') -c $gpuPins
& $comfyPython -m pip check
```

MultiGPU is a separate optional qualification step. The [reviewed reference patches](../patches/comfyui-multigpu/README.md) are not applied automatically or claimed necessary for every workflow. Establish a single-device task first where the selected model fits; otherwise qualify the intended device split explicitly.

Use ComfyUI's `extra_model_paths.yaml` mechanism to point to your chosen external model root. Start from the example at the pinned source; map `diffusion_models`, `unet`, `text_encoders`, `vae`, and any other categories actually used by your selected graph. Do not overwrite another installation's path configuration. Acquire only the chosen [model bundle](MODEL-SOURCES.md), and verify its file hashes.

From the new checkout, start in the foreground:

```powershell
Set-Location -LiteralPath $comfyRoot
& $comfyPython main.py --listen 127.0.0.1 --port 8188
```

Check startup errors, `/system_stats`, node schemas, and the queue. Then use a synthetic/licensed image fixture and a short video graph whose complete model/node dependencies have been recorded. **Those release fixtures and their measured settings are still being qualified.** Preserve prompt IDs and inspect existing job history before retrying a timed-out request. Full decode and visual review are separate checks.

## 6. Connect tools and manage GPU transitions

The [ComfyUI MCP bridge](../integrations/comfyui-mcp/README.md) includes portable source and a fake-service protocol test. Install it in its own environment and configure a compatible stdio client. Confirm its read-only tools against the new ComfyUI instance before submitting a graph. A bridge test is not proof that every chat application can use it.

For the first full-workstation trial, use a manual sequence: save agent work; confirm no active requests; unload only the selected test LLM with `ollama stop <test-tag>`; inspect `ollama ps` and actual GPU use; run one media job; verify its saved output; use ComfyUI's supported model-release behavior or stop your foreground test process when idle; then resume the agent and check its saved state. Other GPU processes may retain memory. Avoid automated process termination.

The reference Render-Coordinator is excluded from this candidate because it depends on private launcher/control plumbing and needs a portable network/lifecycle design. Its omission is explicit; automatic resource coordination is not yet a shipped capability.

## 7. Record qualification before wider use

Save a sanitized report with component versions and download hashes, selected model digests, resolved package lists, manual interventions, task inputs/results, GPU topology, peak RAM/VRAM, and timings. Run the PRD's [acceptance checks](PRD.md#8-acceptance-workflows) appropriate to the selected profile. Keep credentials, personal paths, and private prompts out of shared reports.

The full profile still requires clean Core-Agent reproduction, approved image/video fixtures, UI/tool integration, resource transitions, offline behavior, and recovery checks. The installer will automate the procedure after those checks pass. This draft and the reusable source pieces are available now for review and controlled testing.
