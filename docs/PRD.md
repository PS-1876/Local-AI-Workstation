# Local AI Workstation product requirements

Version: 0.1 draft  
Date: October 31, 2026  
Stage: reference workstation to reproducible setup  
Status: requirements describe intended behavior unless explicitly identified as an observation.

## 1. Product purpose

Local AI Workstation helps individuals build and operate their own local AI environment. It brings local language models, an agent runtime, tool access, project continuity, and optional creative workflows into a documented system with verifiable results.

The central product outcome is replication: a person who did not build the original workstation can determine what they need, follow the published process, and verify that their own setup works. The eventual setup script should ask for only the choices that depend on the user's machine or preferences.

The existing workstation is the reference implementation. It demonstrates useful ingredients and prior local workflows. A working personal setup does not yet establish an installable product for other people.

## 2. Problem and intended users

Local AI applications can each work while the combined workstation remains difficult to reproduce. Dependencies, model choices, storage locations, Windows-to-Linux paths, startup behavior, GPU usage, and private configuration can be spread across several services. A successful agent response can also conceal a missing file or an unverified result.

The initial audience is technically comfortable Windows users, independent researchers, developers, and creators who want to own their AI environment. Later releases should reduce the technical knowledge needed through guided installation, useful diagnostics, and clear recovery steps.

### Primary user stories

- As a builder, I can assess my hardware and required storage before downloading large models or changing my machine.
- As a new user, I can choose capabilities and storage locations, complete guided setup, and run a small demonstration that proves the installation works.
- As an operator, I can tell which service has failed and recover it without reinstalling everything.
- As an agent user, I receive real files in the selected workspace, with independent checks and honest failure reporting.
- As a creator, I can switch between language-model work and media work without losing task state or unexpectedly exhausting GPU memory.
- As a contributor, I can reproduce a reported result using published versions, fixtures, commands, and checks.

## 3. Goals and release boundaries

| Goal | Observable outcome |
| --- | --- |
| Reproducibility | A separate clean installation completes the published acceptance suite without undocumented maintainer fixes. |
| Local core operation | Representative core tasks succeed with external network access unavailable after dependencies and models are installed. |
| Simple configuration | The standard installer flow asks for capability profile, file locations, a tested model profile, and required account or permission choices. |
| Verifiable work | Completion reports reference host-visible artifacts and independent results, including repairs and failures. |
| Recoverability | Interrupted setup resumes, rerunning setup preserves existing data, and diagnostics identify incomplete components. |
| Honest hardware support | Each supported profile has a dated, measured workload result and explicit limitations. |

### Delivery stages

**Documentation baseline:** publish the PRD, architecture, reference status, prerequisite checklist, and roadmap. This release makes the project understandable and reviewable.

**Guided reference build:** publish exact dependencies, sanitized configuration, a written setup procedure, and small acceptance workflows. Prove the procedure in a separate clean environment before calling it reproducible.

**Installer release:** automate the proven procedure with preflight checks, resumable steps, diagnostics, and safe handling of existing installations. Expand supported hardware only after testing it.

### Initial exclusions

The first reproducible release does not promise universal hardware support, unrestricted desktop autonomy, simultaneous heavy language and media workloads, model training, automatic cloud fallback, remote multi-user hosting, or automatic publishing to external accounts. Media production and browser automation are modules with separate acceptance criteria.

## 4. Product profiles

**Core:** local inference, a local chat interface, configurable storage, service diagnostics, and one offline document task. The reference direction is Ollama with Open WebUI.

**Agent:** the core profile plus Hermes, its required Linux/container environment, selected local tools, an explicit writable workspace, and independent artifact verification. The current Windows/WSL/Podman and NemoClaw-related arrangement must be inventoried before it becomes a supported installation recipe.

**Media:** selected ComfyUI workflows and dedicated speech, transcription, OCR, or other utility components as needed. Install only the components chosen for a supported sample workflow. Media jobs share finite hardware resources with general model work.

Profiles are product packaging proposals. The current repository contains documentation for them, not functioning profile installers.

## 5. Setup experience

The intended flow is:

1. Detect Windows version, CPU, RAM, GPU/VRAM, driver, virtualization support, disk capacity, existing software, and service-port conflicts.
2. Explain which tested profiles fit the machine. If none fit, stop with actionable guidance rather than silently selecting an untested setup.
3. Ask the user to select capabilities, program and data locations, and a tested model profile. Offer advanced settings separately.
4. Show the planned changes, download size estimate, required space, network use, and any elevation, reboot, license, or account steps.
5. Install or reuse compatible dependencies, write local configuration, and run each component's readiness checks.
6. Run the profile's sample tasks and independent checks. Open the local interface only after distinguishing service health from task readiness.
7. Save a local report with versions, completed steps, failures, artifact locations, and recovery instructions.

### Inputs and automatic choices

| Item | Intended handling |
| --- | --- |
| Hardware and current dependencies | Detect automatically; show the findings. |
| Capability profile | User chooses Core, Agent, and optional Media. |
| Program, model, workspace, and output locations | Propose valid locations; let the user change them. Never assume a particular drive letter or username. |
| Model and context | Offer only profiles with measured fit; default to the qualified general model for that hardware. |
| Ports | Propose available local ports and persist the selected values. |
| Local account setup | Use the component's supported onboarding; do not place passwords in repository configuration. |
| Online integrations | Optional and separate; the core must not require cloud AI credentials. |
| Startup behavior | Let the user choose manual startup or a documented startup option. |

Some steps may require user participation, including firmware settings, account sign-in, license acceptance, and reboot. The installer must surface these explicitly and resume afterward. It must not promise to bypass them.

## 6. Functional requirements

Priority P0 is required for the first guided reproducible build; P1 is required for the installer release; P2 is later expansion.

| ID | Priority | Requirement | Acceptance evidence |
| --- | --- | --- | --- |
| FR-01 | P0 | Maintain a versioned bill of materials: applications, runtime versions, container images/digests, model identifiers/digests, quantization, context, custom nodes, source URLs, licenses, and required storage. | Every dependency used by the accepted sample tasks has a recorded source and version; unresolved entries block a reproducibility claim. |
| FR-02 | P0 | Define one qualified reference hardware/software profile and configurable host/container paths. | The guide lists prerequisites and path mappings; an artifact produced inside the agent environment is found at the expected Windows path. |
| FR-03 | P0 | Run the core model locally with no silent cloud fallback. | An offline sample task completes; provider configuration and a bounded network observation support the local-processing claim. |
| FR-04 | P0 | Document start, stop, restart, readiness, and recovery for each required service. | Each service can be diagnosed independently; a failed component is reported as failed or unavailable rather than as a successful setup. |
| FR-05 | P0 | Support bounded agent work with independent validation. | A published file-producing coding task passes an external checker; attempts, failures, and repairs are recorded. |
| FR-06 | P0 | Define permitted tool operations, accessible folders, and authorization boundaries. | A permitted workspace operation succeeds; a test operation outside the configured scope is blocked or requires explicit approval. External text cannot expand permissions. |
| FR-07 | P0 | Separate public project specification from private runtime state and project memory. | A fresh session retrieves a seeded project fact with provenance; conflicting updates are detected without silent overwrite. The repository contains no private runtime memory. |
| FR-08 | P0 | Keep general inference Qwen-first on the reference build; add specialist routing only after measured benefit. | A selected model/context is recorded, and any new general-model route includes an accuracy, latency, and resource comparison. No specialist switching is required merely because a model is installed. |
| FR-09 | P0 for Media | Provide an explicit transition between general inference and heavy media work. | Save state, release the required resources, complete a selected media job, and resume general work. Record resource use and any interrupted jobs. |
| FR-10 | P0 for Media | Package one small redistributable sample workflow with all dependencies and independent output checks. | The output exists, decodes, and meets specified technical properties. Human review is separately recorded where quality or synchronization matters. |
| FR-11 | P1 | Perform a read-only installation preflight and generate an installation plan before mutations. | Unsupported hardware, missing virtualization, insufficient disk capacity, invalid paths, and occupied ports produce actionable results with no partial installation. |
| FR-12 | P1 | Implement resumable, repeatable installation using explicit completed-step state. | A second run makes no unintended changes; recovery from an interrupted download and an interrupted configuration step completes without duplicate services or lost user data. |
| FR-13 | P1 | Detect and preserve existing installations and user assets. | An existing model/workflow fixture remains unchanged. Incompatible dependencies trigger a clear choice or stop; no silent overwrite, uninstall, disk initialization, or drive migration occurs. |
| FR-14 | P1 | Fetch dependencies from recorded sources and verify integrity where available. | A deliberately corrupted download is rejected. Required terms and user actions are presented at the appropriate step. |
| FR-15 | P1 | Provide status, repair, upgrade, and uninstall behavior with documented limits. | Status identifies a failed component; a bounded repair works; upgrade rollback is tested for managed configuration; uninstall preserves user models/data by default. |
| FR-16 | P1 | Produce a local diagnostic report suitable for deliberate sanitization and sharing. | It includes component versions and error categories without tokens, passwords, prompts, personal paths, or raw project content by default. No automatic telemetry upload occurs. |
| FR-17 | P2 | Qualify smaller hardware profiles and optional browser/desktop integrations. | Each new profile or integration passes its own published end-to-end task and failure/recovery checks. Configuration alone is insufficient. |

## 7. Nonfunctional requirements

**Resource use:** treat each GPU and its available memory explicitly. Do not assume all workloads pool GPU memory. Record model context, quantization, residency, peak memory, cold start, warm response time, and media duration when qualifying a profile. Performance targets should follow measurements; this draft sets no unmeasured speed claim.

**Privacy and access:** default services to local access appropriate to the documented Windows/container topology. Any required bridge must be documented and constrained. LAN access, public tunnels, cloud inference, remote accounts, and external publishing require separate configuration. Verify actual bindings and traffic before claiming isolation.

**Reliability:** fail visibly, retain useful local error information, bound retries, and preserve work before unloading a model or restarting a service. A successful health response and a successful user task are distinct states.

**Portability:** avoid embedded usernames, drive letters, secrets, and production asset paths. Runtime state belongs in user-selected locations outside the repository. The existing reference machine's storage layout is an example only.

**Maintainability:** pin tested versions, identify dependency ownership, record compatibility changes, and keep automated checks small enough for contributors to run. Hardware-dependent acceptance results must state the hardware and date.

## 8. Acceptance workflows

| Test | Proposed procedure | Pass condition |
| --- | --- | --- |
| AT-01 Core offline task | With dependencies installed and external network unavailable, submit a small synthetic local document with predetermined facts and questions. | Local inference completes and answers match the fixture's independently defined checks. |
| AT-02 Agent artifact | Ask the agent to implement a bounded file-processing function from a published specification in its allowed workspace. | The host file exists, external targeted and randomized checks pass, and attempts/repairs are recorded. |
| AT-03 Project continuity | Seed a synthetic project decision, end the session, and retrieve it from a new session; simulate a conflicting revision. | Correct retrieval with provenance and visible conflict handling; no silent lost update. |
| AT-04 Media module | Run a small licensed sample, checking dependencies and outputs; transition from general inference and back. | Technical output checks pass, task state survives, and any human quality review remains explicit. |
| AT-05 Installer recovery | Run preflight; install; interrupt a download/configuration step; resume; rerun; test an existing-data fixture. | Every required step finishes or clearly reports its blocker, and existing data remains unchanged. |
| AT-06 Independent reproduction | A second person or a separate clean environment follows only the published guide/configuration for the selected profile. | All required tests for that profile pass without undocumented intervention; any intervention becomes a documented defect and retest. |

These are proposed acceptance tests. The current repository does not include their implementations or claim that they have passed.

## 9. Release metrics

For each candidate release, publish the number of installation attempts, completed installations, failure causes, manual interventions, and successful reruns. Report setup time with download time separated, downloaded bytes, peak disk/RAM/VRAM use, and task completion results.

The first reproducible release requires at least one documented clean installation separate from the original configured environment. That result establishes only the tested profile; broader reliability needs additional installations. Any unresolved P0 failure blocks the corresponding profile's release claim.

## 10. Distribution and ownership

GitHub holds the public specification, original integration code when ready, sanitized templates, small licensed fixtures, and shareable test reports. It does not hold model weights, credentials, conversation databases, private memories, personal documents, production media, or a copy of the original machine's configuration.

Download instructions must identify upstream software and model terms. The license for original project material remains a maintainer decision. Selecting a project license does not change upstream licenses.

The repository is the proposed source of truth for public product requirements. Private operational notes and user content remain in their own stores. A workflow for promoting sanitized findings into the public project must preserve that boundary.

## 11. Risks and open decisions

| Risk or decision | Next action |
| --- | --- |
| Hidden dependencies and undocumented manual fixes | Inventory the actual reference components and trace each accepted sample task. |
| Windows, WSL, container, and GPU compatibility | Record exact versions and test the combination in a separate environment. |
| Model fit changes with context and concurrent work | Qualify profiles using measured memory and workload behavior. |
| Public code/configuration may include private material | Use explicit file selection and inspect candidate commits before publication. |
| Clean-machine validation requires suitable hardware | Arrange a separate installation or external tester without dismantling the working reference machine. |
| Scope expands before the core is reproducible | Release Core and Agent first; qualify Media and desktop automation separately. |
| Original-material license not chosen | Select and add a license before describing the project as open source. |
| Minimum supported hardware and disk space are unknown | Publish measured requirements after the dependency manifest and profile tests exist. |
| Installer packaging and support policy are undecided | Start from a proven PowerShell-oriented guided procedure; choose final packaging after reproduction. |

## 12. Immediate next milestone

Complete a sanitized dependency manifest and a guided Core-plus-Agent installation procedure, then prove it outside the existing configured workstation. Automate that proven procedure next. See the [roadmap](ROADMAP.md) for the work items and exit conditions.
