# Roadmap to a reproducible workstation

The project has a functioning reference environment and is making it reproducible. The full target includes local inference, agents, and ComfyUI image/video creation. Milestones are evidence-based; dates should be set after unresolved dependency details and the clean-install test environment are known.

## Milestone 0: Public documentation baseline

Deliver the project README, PRD, architecture, dated reference status, prerequisite checklist, and this roadmap. Identify the difference between observed components and proposed product behavior.

Status: completed initial publication. The README, PRD, architecture, reference status, prerequisites, and roadmap are public.

Exit condition: the documents are available in the repository, their internal links work, and they make no turnkey-installation claim.

## Milestone 1: Exact reference manifest

Status: in progress. A [sanitized baseline](DEPENDENCIES.md), package inventories, source fingerprints, [model guide](MODEL-GUIDE.md), and [draft configuration contract](CONFIGURATION.md) are published. The baseline is an observation, not a verified installation lock.

- Resolve the dependencies used by Core, Agent, and the selected image and video examples.
- Record versions, image/model digests, custom-node commits, installation sources, licenses, and compatibility constraints.
- Extract configuration into sanitized templates with configurable paths and ports.
- Document Windows-to-container file mapping, local inference routing, service startup, and GPU ownership.
- Measure download size, installed size, peak disk use, RAM/VRAM use, and baseline task timings.
- Select an original-material license and review redistributable fixtures.

Exit condition: another contributor can identify every required component and every user-specific input without access to private machine configuration.

## Milestone 2: Guided installation and independent checks

- Write a step-by-step Core and Agent installation procedure.
- Provide sample tasks and external checkers for local document work, a host-visible coding artifact, and fresh-session project continuity.
- Add component readiness checks and common-failure diagnostics.
- Prepare a clean test environment or recruit a separate tester with a matching profile.
- Reproduce the installation and record all deviations from the written guide.
- Fix the guide/configuration and repeat the affected checks.

Exit condition: a clean installation separate from the original configured environment passes the required profile tests without undocumented fixes. This establishes the tested profile only.

## Milestone 3: Full image/video integration

- Package one small redistributable image workflow and one video workflow with their complete dependency sets.
- Verify both outputs independently and record human quality review separately.
- Demonstrate saving general-model work, releasing required GPU resources, completing the media jobs, and resuming general work.
- Document interruption, out-of-memory handling, and recovery.
- Extend the guided procedure to the full profile and reproduce it in a separate clean environment.

Exit condition: the full profile passes its image, video, agent, continuity, and resource-transition checks without undocumented fixes. The clean Core/Agent subset alone is not this milestone.

## Milestone 4: Installer prototype and release

- Build read-only preflight and an installation plan first.
- Ask for capability profile, locations, a tested model profile, and necessary onboarding choices.
- Automate the proven full guide with explicit per-step state and bounded retries; offer smaller subsets for constrained hardware.
- Detect compatible existing installations and preserve user data.
- Support interrupted downloads, resumed configuration, reruns, and clear failure reports.
- Expose status and bounded repair operations.
- Before the installer release, test upgrades, managed-configuration rollback, and uninstall that preserves models and user data.

Exit condition: the installer passes all P1 criteria in the PRD on the qualified reference profile, including recovery, reruns, upgrade/rollback, and data-preserving uninstall. A written fallback guide remains available.

## Milestone 5: Wider hardware and operator support

- Qualify a smaller model/hardware profile using the same task suite.
- Compare standard and Heretic variants at equivalent quantization, context, and task settings; keep both profiles in this repository.
- Publish measured tradeoffs instead of assuming equivalent capability.
- Extend installer lifecycle checks to each newly supported hardware profile.
- Add browser or desktop workflows only with bounded permissions and concrete end-to-end tests.

Exit condition: each advertised hardware profile or integration has its own published evidence and support limits.

## Initial work backlog

| ID | Work item | Depends on | Completion evidence |
| --- | --- | --- | --- |
| LAIW-001 | Complete the reference dependency manifest (partial snapshot published) | Documentation baseline | Every sample dependency has a source, version/digest, and license status |
| LAIW-002 | Qualify portable configuration and data locations (draft published) | LAIW-001 | Tested templates contain no personal paths or secrets |
| LAIW-003 | Write service lifecycle and diagnostic guide | LAIW-001 | Independently checked health and recovery behavior |
| LAIW-004 | Package synthetic acceptance fixtures/checkers | PRD | Deterministic checks with explicit pass/fail output |
| LAIW-005 | Prove guided Core/Agent reproduction | LAIW-002, 003, 004 | Dated clean-install report and complete result set |
| LAIW-006 | Implement installer preflight and plan | LAIW-005, 008 | No-change checks for missing prerequisites and conflicts |
| LAIW-007 | Implement resumable installation | LAIW-006 | Successful install, interruption recovery, and unchanged-data rerun |
| LAIW-008 | Qualify full image/video integration and resource transitions | LAIW-001, 004, 005 | Clean full-profile reproduction with both media outputs and transition report |
| LAIW-009 | Choose licensing and contribution policy | Maintainer decision | Applicable license and clear contribution terms |
| LAIW-010 | Qualify additional hardware | LAIW-005, 007 | Profile-specific measurements and acceptance results |

These identifiers are planning labels, not GitHub issue numbers. The starter publication does not create an installer or mark these work items complete.
