# Local AI Workstation

Build a personal AI workstation that runs core inference locally, connects useful tools, and produces work that can be checked independently.

This project turns an existing Windows workstation into a documented, reproducible setup that other people can build. The intended experience is a hardware and software checklist followed by a guided setup script with a small number of choices.

**Current stage: documentation and product requirements.** The reference workstation has running components, but this repository does not yet contain an installer or a complete installation guide. Reproduction on a clean machine remains a release milestone.

## Start here

- [Product requirements](docs/PRD.md): scope, user experience, requirements, and acceptance criteria.
- [Architecture](docs/ARCHITECTURE.md): component relationships and operating boundaries.
- [Reference status](docs/REFERENCE-STATUS.md): dated hardware and service observations, with their limits.
- [Build prerequisites](docs/PREREQUISITES.md): what a builder will need and which specifications still need qualification.
- [Roadmap](docs/ROADMAP.md): the work between the reference workstation and a dependable installer.

## Intended capabilities

| Profile | Intended purpose | Delivery status |
| --- | --- | --- |
| Core | Local chat and document work through Ollama and Open WebUI | Existing reference components; reproducible setup pending |
| Agent | Local planning, coding, and bounded tool use through Hermes and local integrations | Prior local experiments; packaged acceptance suite pending |
| Media | Local image, video, and audio workflows, including ComfyUI | Reference tools exist; redistributable examples and setup pending |

Core inference should not require a cloud AI subscription. Internet access may be needed to obtain dependencies or perform explicitly selected online tasks. Offline operation after installation is a requirement to test, not a completed certification.

The current reference machine has an AMD Ryzen 9 9900X, 61.07 GiB of OS-visible physical RAM, and two NVIDIA RTX 5080 GPUs. That is an observed reference configuration, not a minimum requirement or purchasing recommendation. Smaller hardware profiles need separate model and workload testing.

## What this repository contains

The initial publication contains documentation and Git exclusion rules. Planned additions include sanitized configuration templates, dependency manifests, setup and diagnostic scripts, small sample workflows, and independent verification tools.

Personal project records, credentials, browser sessions, model weights, private service configuration, and production media are excluded. Models and upstream applications will be obtained from their approved sources with their own applicable terms.

## Current priorities

1. Record the exact dependencies and settings that make the reference build work.
2. Reproduce the core and agent profiles from a written procedure in a separate clean environment.
3. Turn that tested procedure into a resumable installer and add optional media support.
4. Qualify additional hardware profiles and publish the results.

## Licensing

A license for original project documentation and future code has not been selected. This is a public development project; an open-source license decision is an outstanding release task. Third-party software, models, and assets retain their own licenses. See [GitHub's licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).
