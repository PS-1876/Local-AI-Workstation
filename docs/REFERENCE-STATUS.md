# Local AI Workstation reference status

This reference build was inspected on **October 31, 2026, America/Los_Angeles**. The inspection was read-only: it enumerated hardware and requested service health or version information. It did not start or stop services, load models, run inference, submit media workflows, or reproduce an installation.

The project is ready to document and develop in public. It is not yet a turnkey installation or a validated hardware compatibility matrix. A follow-up read-only [dependency inventory](DEPENDENCIES.md) now records source commits, runtime versions, local modifications, package inventories, and specific reproduction gaps. The [model guide](MODEL-GUIDE.md) separates candidate hardware tiers from tested profiles.

## Observed hardware and operating system

| Field | Observed value |
|---|---|
| Operating system | Microsoft Windows 11 Education |
| Windows version | `10.0.26300` |
| Windows build | `26300` |
| CPU | AMD Ryzen 9 9900X 12-Core Processor |
| Physical RAM reported by Windows | 61.07 GiB |
| GPUs | Two NVIDIA GeForce RTX 5080 devices |
| Memory reported by `nvidia-smi` | 16,303 MiB per GPU |

This is a reference configuration, not a minimum requirement or purchasing recommendation. The GPUs' memory figures do not establish a single shared memory pool. The RAM figure is the amount reported by the operating system; installed module specifications were not inventoried.

## Observed local service responses

Each request used a five-second timeout. All four requests returned HTTP 200.

| Service | Local endpoint inspected | Reported result |
|---|---|---|
| Ollama | `http://127.0.0.1:11434/api/version` | Version `0.40.13` |
| Open WebUI | `http://127.0.0.1:8080/health` | `status: true`; follow-up application/package inspection reports `0.11.4` |
| Hermes | `http://127.0.0.1:8642/health` | Version `0.22.4`; `status: ok` |
| ComfyUI | `http://127.0.0.1:8188/system_stats` | Version `0.40.0`; two CUDA devices reported |

ComfyUI also reported Python `3.13.12` and PyTorch `2.12.1+cu130`. Both enumerated CUDA devices were RTX 5080 GPUs.

These responses establish endpoint reachability and the values returned by those endpoints at inspection time. They do not establish successful model inference, agent completion, browser control, media quality, effective multi-GPU use, authentication coverage, offline operation, or ongoing availability.

## Historical local results

Earlier project notes describe a Hermes runtime in a Podman container under WSL, a local Ollama backend, and connections through Open WebUI and local tools. The notes also report independently checked small coding tasks, including a task that required host-path recovery and another that passed after a bounded repair.

These are historical local results. A public package containing the exact prompts, fixtures, component versions, model identifiers and digests, acquisition instructions, independent graders, and reproducible execution instructions has not yet been assembled. The results should therefore be treated as background evidence for choosing the next tests, not a public benchmark or a general reliability guarantee.

Earlier media and tool experiments likewise do not establish that a fresh agent can reproduce an entire workflow without assistance. Technical output checks and human approval of visual or audio quality are separate outcomes.

## Release evidence still required

- [x] Record the GPU driver, WSL distribution/kernel, Podman version, sandbox image digest, and selected active runtime details in the dependency baseline.
- [ ] Resolve the active gateway's separate Python runtime, local source changes, launch wrappers, and Podman socket/storage context into a reproducible recipe.
- [ ] Complete adapter versions, verified dependency locks, acquisition sources, and compatible version combinations; observed package inventories are now available.
- [ ] Identify the selected model artifact, digest, quantization, context configuration, download source, and applicable license.
- [ ] Document all host-to-container storage mappings and verify artifact creation at the intended host destination.
- [x] Publish a sanitized draft configuration example and structural schema.
- [ ] Convert the configuration draft into a tested installation guide; no complete guide or installer is included yet.
- [ ] Define supported hardware and operating-system profiles using measured tests; no minimum hardware specification is validated yet.
- [ ] Run a small, published end-to-end task suite with independent grading and bounded repair reporting.
- [ ] Test local inference with external network access disabled after installation and model acquisition.
- [ ] Test GPU workload transitions, memory pressure, interrupted jobs, and restart recovery.
- [ ] Test project-record retrieval in a fresh session and conflict handling during updates.
- [ ] Verify each intended MCP or tool client separately, including its permissions and failure behavior.
- [ ] Perform a clean installation or independent reproduction and retain a sanitized results report.
- [ ] Review all publication assets for secrets, personal information, and redistribution rights.

The [architecture](ARCHITECTURE.md) describes the intended component boundaries. Requirements and roadmap documents define the planned work; their presence does not imply those capabilities have passed acceptance testing.
