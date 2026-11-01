# Portable Hermes installation candidate

The [Windows workspace package](../integrations/windows-workspace-mcp/README.md) contains the portable read/create-only server and its tests. Follow the main [installation draft](INSTALLATION.md) for the surrounding workstation components.

Use clean upstream Hermes source and explicit Windows workspace tools for the first reproducible agent profile. The existing reference machine's automatic Windows-path interceptor is excluded: it depends on an untracked helper and skips parts of Hermes' normal file checks. Upstream Hermes can discover and call MCP tools directly without that patch.

This is a qualification procedure for a separate clean environment. The pinned source, installer options, MCP configuration syntax, and Python acquisition record have been inspected. A clean installation and end-to-end agent run have not yet passed. The existing workstation should continue using its current runtime while this candidate is tested.

## Obtain a pinned upstream installation

Use a fresh WSL2 test distribution or dedicated Linux account with Git, curl, tar, and SHA-256 utilities. The installer manages that account's launcher and shell setup; do not run it over the working reference installation. A plain WSL source installation also does not inherit the reference NemoClaw/OpenShell sandbox boundary.

The inspected source is Hermes v0.22.4 at commit `4d04303818b61bf3aa09278af48356315515965b`. The following commands download the exact inspected installer, verify its hash, and select separate application and data directories. They have been source-reviewed, not executed as a clean-install test.

```bash
HERMES_SOURCE_COMMIT=4d04303818b61bf3aa09278af48356315515965b
HERMES_SOURCE_DIR="$HOME/local-ai-lab/hermes-source"
HERMES_DATA_DIR="$HOME/local-ai-lab/hermes-data"
HERMES_INSTALL_SCRIPT="$HOME/local-ai-lab/install-hermes-pinned.sh"
mkdir -p "$HOME/local-ai-lab"
curl --fail --location \
  "https://raw.githubusercontent.com/NousResearch/hermes-agent/$HERMES_SOURCE_COMMIT/scripts/install.sh" \
  --output "$HERMES_INSTALL_SCRIPT"
printf '%s  %s\n' \
  '20f44240ebada354a468104a6a6724d037afcb8883d4d09ddeb4815622c52d8b' \
  "$HERMES_INSTALL_SCRIPT" | sha256sum --check -
```

Stop if verification fails. After reviewing the installation plan and confirming that these destinations are unused in the test environment:

```bash
bash "$HERMES_INSTALL_SCRIPT" \
  --commit "$HERMES_SOURCE_COMMIT" \
  --dir "$HERMES_SOURCE_DIR" \
  --hermes-home "$HERMES_DATA_DIR" \
  --non-interactive \
  --skip-browser \
  --skip-computer-use
git -C "$HERMES_SOURCE_DIR" rev-parse HEAD
```

The returned source commit must match the selected commit. These options select the upstream source installer and omit its optional browser and computer-use tool installations. The source installer still selects the upstream `all` Python extra and managed tools; this is not a minimal-dependency packaging claim. Review and measure its actual downloads and native-library requirements during qualification. [Pinned installer](https://github.com/NousResearch/hermes-agent/blob/4d04303818b61bf3aa09278af48356315515965b/scripts/install.sh), [installation documentation](https://github.com/NousResearch/hermes-agent/blob/4d04303818b61bf3aa09278af48356315515965b/website/docs/getting-started/installation.md).

The upstream package manager pins Python `3.14.7+20260901` for Linux x64. Its archive is `cpython-3.14.7+20260901-x86_64-unknown-linux-gnu-install_only.tar.gz` from Astral's python-build-standalone release `20260901`, with SHA-256 `0ab3305457051cd3e7c031857e005f1bda17c218a1990567dacaaac6dd1d14f0`. The reference runtime's package-manager facts record that same artifact identity. This resolves the acquisition record; it does not independently attest every installed runtime file. Use the managed upstream installation instead of copying the reference machine's `test-home` directories or custom launcher. [Pinned tool lock](https://github.com/NousResearch/hermes-agent/blob/4d04303818b61bf3aa09278af48356315515965b/pm/lock.json).

## Select local inference explicitly

Configure a qualified Ollama model through `hermes model` or the following upstream config shape. Replace every placeholder before use:

```yaml
model:
  provider: custom
  default: "<QUALIFIED_OLLAMA_TAG>"
  base_url: "<OLLAMA_V1_URL_REACHABLE_FROM_THIS_ENVIRONMENT>"
fallback_providers: []
```

An Ollama URL ends in `/v1`. Windows loopback, WSL loopback, and container loopback are different deployment contexts; test the chosen route from the environment running Hermes. Do not copy the reference machine's network addresses. Set and measure the intended context in the selected model runtime; the maximum in model metadata is not a validated operating setting. Keep cloud fallback and cloud credentials out of this local profile. [Pinned local-model configuration](https://github.com/NousResearch/hermes-agent/blob/4d04303818b61bf3aa09278af48356315515965b/website/docs/guides/local-ollama-setup.md).

## Connect a bounded Windows workspace server

The repository now contains a separate create-only stdio bridge at `integrations/windows-workspace-mcp`. Use native Windows Python 3.12 and its pinned `mcp==1.30.0` dependency. It exposes exactly these tools:

| Tool | Interface | Behavior |
|---|---|---|
| `read_windows_text` | Workspace-relative `path` | Read UTF-8 text and return exact bytes/SHA-256 metadata. |
| `create_windows_text` | Workspace-relative `path`, `text` | Exclusively create a new file in an existing parent directory and verify its bytes. Existing destinations are never replaced. |

Set `WORKSTATION_WORKSPACE_ROOT` to an existing, dedicated Windows workspace folder. The bridge rejects absolute paths, traversal, alternate streams, reparse points, junctions, symlinks, and files with multiple hard links. Text is limited to 204,800 UTF-8 bytes. It has no overwrite, patch, delete, directory-creation, command-execution, or HTTP operation. Creating a new version under a new name preserves the existing file.

Install its requirements in a dedicated Windows virtual environment and run its synthetic tests as described in the package README. The following upstream Hermes YAML shape is for a **native Windows client**; replace the example paths. It does not edit Hermes' built-in file tools:

```yaml
mcp_servers:
  local-workspace:
    command: 'C:\LocalAI\windows-workspace-mcp\.venv\Scripts\python.exe'
    args:
      - 'C:\LocalAI\windows-workspace-mcp\server.py'
    env:
      WORKSTATION_WORKSPACE_ROOT: 'D:\LocalAI\Workspace'
    enabled: true
    connect_timeout: 15
    timeout: 60
    supports_parallel_tool_calls: false
    trust: untrusted
    tools:
      include:
        - read_windows_text
        - create_windows_text
      resources: false
      prompts: false
```

The bridge launches as a stdio child and does not open a network listener. `trust: untrusted` retains upstream creation approval during initial qualification. A WSL-hosted Hermes needs a separately qualified recipe for launching the Windows executable, passing Windows arguments, and propagating the root environment variable. A Podman container does not automatically inherit WSL Windows-executable interop. The native Windows MCP test is not evidence that either cross-environment route works. [Pinned MCP configuration reference](https://github.com/NousResearch/hermes-agent/blob/4d04303818b61bf3aa09278af48356315515965b/website/docs/reference/mcp-config-reference.md).

After the launch mapping for the selected client environment is qualified, run `hermes mcp test local-workspace` and confirm that only the selected tools are exposed. Ask the agent to call those discovered tools explicitly with workspace-relative paths. A successful connection test proves discovery, not file-writing success. Use `hermes tools` to select the intended tool surface. This helper is not an OS sandbox or a defense against malicious same-user filesystem races. Terminal, browser, and desktop access need separate restrictions; limiting this MCP server does not contain the whole agent.

## Qualify the host artifact contract

Use a disposable workspace and synthetic text for these checks:

1. Create a new text file, read it through the MCP tool, and independently check its Windows path, bytes, and SHA-256.
2. Try to create the same file again without replacement authorization; it must leave the existing file unchanged.
3. Create a revised artifact under a new filename; independently confirm that the original remains unchanged.
4. Submit concurrent creates to one unused name; exactly one may succeed, with complete verified content and no overwritten destination.
5. Reject parent traversal, another drive, an absolute outside-workspace path, alternate data streams, and junction/link paths.
6. Repeat a bounded agent task without the interceptor and verify the host artifact independently. Record repairs and failures.

The new package includes synthetic filesystem tests and real SDK stdio tests. They operate only in disposable temporary directories and do not touch the reference host-tool service or its outputs. Test reports must identify skips, including Windows environments without permission to create a symlink fixture. A malicious filesystem race is explicitly outside this helper's containment claim. Direct Hermes use and clean-machine installation remain qualification work.

## Existing Podman reference context

The current sandbox uses rootless Podman. Its API socket follows `$XDG_RUNTIME_DIR/podman/podman.sock`; storage follows the service account's `$HOME/.local/share/containers/storage`, with run state under `$XDG_RUNTIME_DIR/containers`. These variables must refer to the account owning the rootless service. A different WSL default account or rootful Podman sees a different container store.

For a deployment retaining the managed sandbox, document the service-owning account and user-service lifecycle, and discover the current container by its sandbox identity instead of pinning a generated container ID. Keep the Podman control socket separate from agent tools. Do not transplant the running reference container or its modified wrappers into a clean release. [Podman API and rootless socket documentation](https://docs.podman.io/en/latest/markdown/podman-system-service.1.html).

The clean source candidate is not yet a drop-in replacement for the NemoClaw/OpenShell deployment, its Open WebUI adapter, or its startup services. Those integration and isolation contracts require separate acceptance results before a full-workstation installation can be described as reproducible.
