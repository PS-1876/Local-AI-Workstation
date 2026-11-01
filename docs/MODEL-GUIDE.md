# Model selection and GPU fit

Reviewed: October 31, 2026. The full workstation covers language models, agents, local image generation, and local video generation. Model selection must account for those workloads sharing the same hardware.

## One workstation with standard and Heretic profiles

Keep standard and Heretic model options in this repository. They share the same service setup, storage configuration, tool interfaces, and verification requirements. Each model entry should identify its variant explicitly; a separate workstation repository would duplicate most of the installation work.

Create a separate repository only if an independently maintained model-conversion or research tool emerges with its own code, dependencies, releases, and tests. If the project later distributes original model weights, use a dedicated model-hosting repository with a model card and lineage. Keep acquisition references and integration profiles here.

[Heretic](https://github.com/p-e-w/heretic) is a model-modification tool using directional ablation and parameter optimization. A model bearing the Heretic name is a derivative artifact, not a universally interchangeable model release. The exact publisher, base model, revision, transformation, quantization, and runtime matter. Heretic's own documentation also distinguishes automated metrics from human evaluation; its refusal metrics do not establish workstation task quality.

Record the licenses for the tool, base model, derivative, and quantized distribution separately. A tool license must not be copied into a model's license field by assumption. Using a Heretic model does not require installing or running the Heretic conversion tool on every workstation.

## Initial language-model candidates by GPU memory

The following are **first candidates to qualify**, selected from published package sizes with room for runtime overhead. The tier assignments are this project's estimates, not measured compatibility results or minimum requirements. The project has not benchmarked these standard models on every tier.

| GPU capacity class | First candidate to test | Published llama.cpp/GGUF package size | Initial qualification target |
| --- | --- | --- | --- |
| One 8 GiB GPU | [Qwen3.5 4B Q4_K_M](https://ollama.com/library/qwen3.5:4b) | About 3.3 GB | Basic text task at 4,096 tokens; measure vision separately |
| One 12 GiB GPU | [Qwen3.5 9B Q4_K_M](https://ollama.com/library/qwen3.5:9b) | About 6.6 GB | Text and bounded tools at 4,096 tokens, then increase context if measured headroom permits |
| One 16 GiB GPU | [Qwen3.5 9B Q4_K_M](https://ollama.com/library/qwen3.5:9b) | About 6.6 GB | More context or vision testing after the initial text check |
| One 24 GiB GPU | [Qwen3.6 27B Q4_K_M](https://ollama.com/library/qwen3.6:27b) | About 18 GB | Start at 4,096 tokens; measure peak allocation before longer agent tasks |
| One 32 GiB GPU | [Qwen3.6 35B Q4_K_M](https://ollama.com/library/qwen3.6:35b) | About 23 GB | Start at 4,096 tokens, then qualify the intended agent context |
| Two 16 GiB GPUs | Reference custom 35B Q4_K_M, described below | 22.14 GB API-reported package size | Reproduce the reference runtime's device split and context; do not assume equivalence to one 32 GiB GPU |

The source pages contain multiple backend variants. The sizes above refer to their llama.cpp/GGUF entries, not MLX variants. Package sizes are decimal GB; GPU capacities are shown in GiB classes. These are acquisition-size observations, not measured VRAM consumption. Mutable tags must be replaced by recorded revisions/digests when a profile is qualified.

The 4,096-token setting is a proposed first fit test, not the final target for full agent work. Longer prompts, concurrent requests, KV cache, image inputs, runtime buffers, and display use can change memory needs. Ollama documents that increasing context increases required memory and provides `ollama ps` to inspect offloading and allocated context. Measure the intended workload before calling a profile supported. [Ollama context guidance](https://docs.ollama.com/context-length)

A practical operating target is one general model at a time. Prefer a smaller model that completes the required task with useful headroom over a larger model that fits only with unacceptable latency or CPU offloading. The choice must follow measured accuracy and performance, not parameter count alone.

## Current custom Heretic reference

The reference endpoint reports the local tag `qwen3.6-35b-heretic:latest`, GGUF format, `Q4_K_M`, approximately 34.7B parameters, a package size of 22,136,431,022 bytes, and a configured context of 65,536. Its metadata context limit is 262,144; that is not a validated operating target.

The current API-reported model digest is `16a40cd6f9365c840caea50337d80cd741e26180d50a01f496bb9d3a559a413f`. Its exact public download source, base revision, transformation recipe, and applicable artifact license remain unresolved. The tag must therefore be documented as a local reference, not published as a working download command. A similarly named online model is not proof of identical weights.

The model was not loaded during the inventory; no fresh inference or memory-fit benchmark was performed. Earlier reference-machine tests remain historical observations. Standard-versus-Heretic task performance has not been compared in a controlled test.

## Qualifying a model entry

Every installable model profile must include:

- Base model, publisher, source URL, revision, and variant: standard or Heretic.
- Exact quantized artifact and digest, including a projector where needed.
- Applicable model/distribution terms and any gated acquisition steps.
- Runtime and version, GPU topology, quantization, context, cache settings, and concurrency.
- Peak GPU/RAM usage, load time, warm throughput, and any CPU offloading.
- Results for the same local document, coding, tool-call, and vision tasks where applicable.
- Evidence level: source-listed, installed metadata, historical local result, or fresh independently checked test.

Compare standard and Heretic variants at equivalent quantization, context, runtime, and task settings. Evaluate task correctness, tool-call validity, instruction following, latency, and resource use. Fewer refusals alone are not a quality result.

## Image and video models need their own profiles

ComfyUI is a first-class part of the full workstation. Its image and video profiles need their own model sources, node versions, quantization, encoder/VAE requirements, resolution, frame count, duration, steps, peak VRAM, and output checks.

A GPU that runs a language model is not automatically qualified for a particular video workflow. Measure one image workflow and one short video workflow, then test the transition from agent work to media generation and back. Heavy media work should follow an explicit save, resource-release, generation, verification, and resume sequence.

Do not infer a video recommendation from an LLM fit table or download every installed reference model. The next manifest work selects the smallest set of components needed to reproduce the accepted image and video examples.
