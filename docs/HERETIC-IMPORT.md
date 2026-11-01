# Qwen Heretic import candidate

Status: source-reviewed procedure; **clean import and inference have not been executed for this recipe**. Use a separate test installation. The purpose is to import the identified public weights with a portable stock chat renderer, then measure the result before adopting it.

The [provenance record](../models/general-heretic.json) identifies the exact GGUF and BF16 vision projector, their immutable download URLs and hashes, the publisher's transformation description, and the applicable license references. It distinguishes publisher declarations from independently verified facts. Heretic conversion software is not required to import published weights.

1. Install the official [Ollama 0.40.13 release](https://github.com/ollama/ollama/releases/tag/v0.40.13) for the first matching-version test. Record the installer checksum and architecture. This project's binary acquisition/clean-install check remains pending. Current documentation may target a newer runtime; do not silently substitute it when reporting reproduction.
2. Choose a new empty staging directory on a volume with room for both downloads and Ollama's imported storage. Download only the two artifacts listed in `artifact_source.artifacts` at the pinned revision. Do not rename a similarly named quantization or substitute a stock projector.
3. From the repository root, check the completed files against the catalog. Change only the staging path below:

```powershell
$ErrorActionPreference = 'Stop'
$stagingRoot = 'D:\AI\Staging\qwen36-heretic'
$source = Get-Content -Raw -LiteralPath '.\models\general-heretic.json' | ConvertFrom-Json
foreach ($artifact in $source.artifact_source.artifacts) {
    $artifactPath = Join-Path $stagingRoot $artifact.filename
    if ((Get-Item -LiteralPath $artifactPath -ErrorAction Stop).Length -ne $artifact.size_bytes) {
        throw "Size mismatch: $($artifact.filename)"
    }
    if ((Get-FileHash -LiteralPath $artifactPath -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant() -ne $artifact.sha256) {
        throw "SHA-256 mismatch: $($artifact.filename)"
    }
}
```

4. Copy [the example Modelfile](../models/qwen36-heretic.Modelfile.example) into that new staging directory as `Modelfile`. It contains two `FROM` entries: model and projector. The `RENDERER`/`PARSER qwen3.5` and multiple-file import are supported by the [reviewed runtime source](https://github.com/ollama/ollama/tree/04088e7c9d41cba5d33bafbf788d87a465c79d5b). No private system prompt is carried over. `REQUIRES` expresses a minimum runtime; verify the exact version separately for the first test.
5. The example preserves the reference setting `num_ctx 65536`. For an initial fit check, change it to `4096` and record that deviation. The [GPU table](MODEL-GUIDE.md) is a list of candidates to measure. Neither the weight size nor the context declaration guarantees a fit.
6. Confirm the `ollama` client selected by your terminal is version 0.40.13 with `ollama --version`. Select the local test endpoint, verify its server version, and ensure the new tag is unused. From the staging directory:

```powershell
$ErrorActionPreference = 'Stop'
$env:OLLAMA_HOST = '127.0.0.1:11434'
$apiRoot = 'http://127.0.0.1:11434'
if ((Invoke-RestMethod -Uri "$apiRoot/api/version" -TimeoutSec 30).version -ne '0.40.13') {
    throw 'Matching-version test requires Ollama 0.40.13'
}
$testTag = 'laiw-qwen36-heretic:import-test'
if (@((Invoke-RestMethod -Uri "$apiRoot/api/tags" -TimeoutSec 30).models.name) -contains $testTag) {
    throw 'Test tag already exists; choose a different unused test tag'
}
ollama create $testTag -f .\Modelfile
if ($LASTEXITCODE -ne 0) { throw 'Import failed' }
```

7. Inspect the new model with `/api/show`. Check its architecture, parameters, renderer/parser, and reported capabilities. Inspect its manifest to confirm the **model and projector** digest/size pairs match the provenance record. Do not expect its overall manifest digest to match if parameters, license fields, or runtime metadata differ.
8. During an idle GPU window, test a short chat, a deterministic coding task checked by a separate program, a bounded tool call, and an image with known contents. Verify thinking parsing and the Open WebUI connection. Measure peak RAM/VRAM and CPU offload at 4,096 tokens before increasing context. Record errors and timings, not just whether a model appeared in a dropdown.

Keep the existing reference alias intact until the new profile passes. The current provenance record establishes matching artifact acquisition; it does **not** establish bit-for-bit regeneration from the base model. The publisher's exact quantizer revision, conversion procedure, and original input revisions remain incomplete.
