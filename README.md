# Local AI Workstation

Build a personal AI workstation that runs core inference locally, connects useful tools, and produces work that can be checked independently.

This project turns an existing Windows workstation into a documented, reproducible setup that other people can build. The intended experience is a hardware and software checklist followed by a guided setup script with a small number of choices.

**Current stage: source resolution and guided setup draft.** The repository includes pinned model sources, reviewed compatibility patches, portable tool bridges, integrity checks, and a step-by-step installation candidate. It does not yet contain a turnkey installer or a qualified clean-machine recipe. The remaining agent integration and full image/video tests are explicit in the guide.

## Start here

- [Product requirements](docs/PRD.md): scope, user experience, requirements, and acceptance criteria.
- [Guided installation draft](docs/INSTALLATION.md): concrete setup steps, checks, and remaining qualification work.
- [Local modifications](docs/LOCAL-MODIFICATIONS.md): what is packaged, replaced, or excluded from the portable candidate.
- [Pinned model sources](docs/MODEL-SOURCES.md): exact language/media artifact references and integrity evidence.
- [Dependency baseline](docs/DEPENDENCIES.md): component versions, local modifications, and specific reproduction gaps.
- [Model and GPU guide](docs/MODEL-GUIDE.md): standard and Heretic options, source references, and candidate hardware tiers.
- [Portable configuration](docs/CONFIGURATION.md): the proposed installer inputs and full-workstation profile.
- [Architecture](docs/ARCHITECTURE.md): component relationships and operating boundaries.
- [Reference status](docs/REFERENCE-STATUS.md): dated hardware and service observations, with their limits.
- [Build prerequisites](docs/PREREQUISITES.md): what a builder will need and which specifications still need qualification.
- [Roadmap](docs/ROADMAP.md): the work between the reference workstation and a dependable installer.

## Intended capabilities

| Profile | Intended purpose | Delivery status |
| --- | --- | --- |
| Core | Local chat and document work through Ollama and Open WebUI | Guided chat setup candidate; clean reproduction and document/offline qualification pending |
| Agent | Local planning, coding, and bounded tool use through Hermes and local integrations | Clean-source candidate and portable workspace tools; full integration pending |
| Media | Local image and video creation through ComfyUI, plus required media utilities | Pinned artifact candidates, loader, patches and MCP bridge; complete sample graphs and GPU tests pending |

**Full workstation is the main product target: Core + Agent + Media.** ComfyUI is a first-class component. Smaller profiles support constrained hardware or staged setup; they do not replace the goal of reproducing the integrated workstation. Standard and Heretic model options stay in this repository and share the same setup infrastructure.

Core inference should not require a cloud AI subscription. Internet access may be needed to obtain dependencies or perform explicitly selected online tasks. Offline operation after installation is a requirement to test, not a completed certification.

The current reference machine has an AMD Ryzen 9 9900X, 61.07 GiB of OS-visible physical RAM, and two NVIDIA RTX 5080 GPUs. That is an observed reference configuration, not a minimum requirement or purchasing recommendation. Smaller hardware profiles need separate model and workload testing.

## What this repository contains

The repository contains documentation, sanitized dependency snapshots, source catalogs, a draft configuration example/schema, two opt-in MultiGPU patches, portable MCP source, and a read-only media integrity checker. The package snapshots are observations, not installable lockfiles. Models under `models/` are metadata and an import example only; no weights are included. Verified environment locks, small accepted image/video workflows, and a full installer remain planned.

Personal project records, credentials, browser sessions, model weights, private service configuration, and production media are excluded. Models and upstream applications will be obtained from their approved sources with their own applicable terms.

## Current priorities

1. Qualify the published clean-source agent candidate, portable host route, and separate application environments.
2. Prove the guided Core/Agent setup, then complete the full image/video examples, UI/tool integration, and GPU transitions.
3. Turn the tested full procedure into a resumable installer.
4. Qualify standard and Heretic model profiles on additional hardware and publish the results.

## Licensing

A license for original project documentation and future code has not been selected. This is a public development project; an open-source license decision is an outstanding release task. Third-party software, models, and assets retain their own licenses. See [GitHub's licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).
