# Pinned model sources

Reviewed October 31, 2026. This catalog separates a reproducible upstream download from proof that an existing local file is identical. No model weights are stored in this repository.

## Language model

The custom Qwen3.6 35B Heretic model and its vision projector are traced to the same pinned [llmfan46 distribution](https://huggingface.co/llmfan46/Qwen3.6-35B-A3B-uncensored-heretic-GGUF/tree/f70be2db155a4192a59c559ece01572f3cd508ab). The local Ollama manifest's two artifact hashes and sizes match the publisher's LFS metadata. The small manifest itself was freshly hashed and matches Ollama's API digest. The large weight files have not been freshly hashed in this review.

See [language-model provenance](../models/general-heretic.json) and the [import candidate](HERETIC-IMPORT.md) for the exact files, checksums, transformation references, and remaining runtime tests. A local Ollama tag is not an upstream registry download name. Fresh imports use a separate name and must pass chat, tools, and vision checks before replacing a working profile.

## Image and video files

The [media catalog](../models/media-sources.json) contains **21 pinned file references**, with repository paths, immutable revisions, byte sizes, publisher SHA-256 values, and model-card/license links. Seven entries match saved local download-cache revisions, ETags, and byte sizes. One additional encoder has a local download script identifying its repository; the other thirteen have matching upstream filenames and byte sizes only. None of these 21 large local files was freshly hashed during this review. Do not mistake a filename/size match for confirmed file identity.

These are acquisition candidates for files observed on the reference machine. They are not a bulk shopping list, a complete workflow lock, a license clearance, or a GPU-fit claim. Select a complete workflow before downloading its components.

| Candidate bundle | Components in the catalog | Source and terms |
| --- | --- | --- |
| Qwen Image 2.1 standard image candidate | INT8 convrot diffusion model, matching Qwen3-VL encoder, Qwen Image 2.1 VAE | [Comfy-Org](https://huggingface.co/Comfy-Org/Qwen-Image-2.1/tree/aacf31a6d48e707f352ecba714cee0680da3479b); declares Qwen Research terms |
| Qwen Image 2.1 alternative encoder | `qwen3vl_8b_fp8_heretic.safetensors` | [pottokao](https://huggingface.co/pottokao/Qwen-Image-2.1-Text-Encoder-Heretic-GGUF/tree/23813717f7f9282b372c23c7207468a7a168fa68); publisher declares Apache-2.0; review complete lineage separately |
| Wan 2.2 I2V candidate | HighNoise + LowNoise Q4_K_M, UMT5 encoder, Wan 2.1 VAE | [QuantStack I2V](https://huggingface.co/QuantStack/Wan2.2-I2V-A14B-GGUF/tree/6c6717459277b9cd1f72579d78a0fd62a79e57dc) and [Comfy-Org companions](https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/tree/123acf1cc74bccbb9bfff8ac1ee72edc08c2341d); declare Apache-2.0 |
| Wan 2.2 T2V candidate | Its own HighNoise + LowNoise Q4_K_M pair, UMT5, Wan 2.1 VAE | [QuantStack T2V](https://huggingface.co/QuantStack/Wan2.2-T2V-A14B-GGUF/tree/73eafba53a1a8f29254e4c77f92e74ea27d7cd6f); declares Apache-2.0 |
| LTX 2.5 expansion | Distilled NVFP4 transformer, audio/video VAEs, alternative Gemma Heretic encoder | [Lightricks](https://huggingface.co/Lightricks/LTX-2.5/tree/49b093a39c19169a8a81721dcc541e07e945232f) has gated access and LTX community terms; [encoder publisher](https://huggingface.co/r3lax/gemma4-12b-heretic-ltx-2.5-comfy-nvfp4/tree/6c6b69e0e7b1b01b8f6804c2cc8c9f36d3351dc5) declares Apache-2.0 |
| MiniMax H3 expansion | Ref2VA W6A8 transformer, audio/video VAEs, alternative Qwen Heretic encoder | [Comfy-Org](https://huggingface.co/Comfy-Org/MiniMax-H3/tree/e5eb578a89295337b8ff433a035929ce0279e0b6) and [dotexec encoder](https://huggingface.co/dotexec/MiniMax-H3-T2V-NVFP4/tree/4898bd4f7e65504435749cec13ed4f0ca23a7720); declare MiniMax H3 community terms |
| Other observed components | LTX 2.3 FP8 checkpoint, older Qwen 2.5-VL encoder, Qwen3 4B mixed-FP8 encoder | Exact source/revision and terms recorded per entry; they are not substitutes for the bundles above |

The Qwen Image 2.1 standard three-file bundle is 17,283,091,112 bytes. The Wan I2V four-file candidate is 26,293,180,007 bytes. These are download payload sizes, not VRAM requirements or peak installation space. Companion requirements still depend on the selected workflow; optional LoRAs, prompt enhancers, upscalers, and other models are not implicitly included.

A Heretic encoder does not change the terms of the diffusion model, VAE, or any other component. Publisher license badges are recorded as declarations, not a substitute for reviewing the complete base/derivative chain. Gated access must be completed by each builder using their own account. The catalog supplies no shared credentials or bypass.

## Acquire and verify one selected bundle

1. Open each entry's pinned model card and license reference. Select the exact `repository_path` at `revision`; avoid a mutable `main` download when reproducing the recorded source.
2. Download through Hugging Face using the pinned file URL or its official client. Keep incomplete downloads outside the live model directories. For gated files, complete the publisher's access process first.
3. Place completed files under your chosen model root using `comfyui_model_subdir` and `filename` from the catalog. Preserve existing files; a different checksum calls for investigation or a separate filename/profile.
4. Run full-byte verification for the selected files. For example, from the repository root:

```powershell
python scripts/verify-media.py --root 'D:\AI\Models\ComfyUI' --file 'wan_2.1_vae.safetensors'
```

Repeat `--file` to check more files. The script reads the whole selected file, compares size and SHA-256, writes no files, performs no downloads, and does not load a model. Exit 0 means all selected files match the catalog; 1 means missing/mismatched content; 2 means an invalid request or read error. Schedule large checks while disk-intensive production is idle. A successful checksum establishes artifact identity, not generation quality.

The next qualification target is one image graph and one short Wan video graph, followed by the general-model/media transition. LTX and H3 remain expansion candidates until their complete graphs and resource requirements have been checked.
