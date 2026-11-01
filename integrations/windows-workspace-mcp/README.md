# Windows workspace MCP bridge

A small native Windows stdio server for reading existing text and creating new text files in one explicitly selected workspace. It gives Hermes a direct host-artifact interface without modifying Hermes' built-in file tools.

The server exposes exactly two tools:

| Tool | Inputs | Result |
|---|---|---|
| `read_windows_text` | Workspace-relative `path` | Exact UTF-8 text, byte count, and SHA-256 |
| `create_windows_text` | Workspace-relative `path`, `text` | A new file and verified byte count/SHA-256; an existing destination is never replaced |

There are no overwrite, patch, delete, directory-creation, shell, or HTTP operations. The server listens only on stdin/stdout. It has no model dependency and does not load a model.

## Requirements and installation

Use native **Windows Python 3.12** and **`mcp==1.30.0`**. The requirements file pins the direct SDK dependency; it is not a complete transitive dependency lock.

From this folder in PowerShell:

```powershell
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Choose an existing, dedicated local workspace folder. Parent directories for new files must already exist. The server never creates the workspace or chooses one implicitly.

```powershell
$env:WORKSTATION_WORKSPACE_ROOT = 'D:\LocalAI\Workspace'
& .\.venv\Scripts\python.exe .\server.py
```

The drive and folder are examples. A stdio client normally launches the server; starting it in a terminal leaves it waiting for MCP input. Do not paste ordinary chat into its stdin.

## Native Windows client configuration

Replace both example paths with the absolute paths selected during installation:

```json
{
  "mcpServers": {
    "local-workspace": {
      "command": "C:\\LocalAI\\windows-workspace-mcp\\.venv\\Scripts\\python.exe",
      "args": ["C:\\LocalAI\\windows-workspace-mcp\\server.py"],
      "env": {
        "WORKSTATION_WORKSPACE_ROOT": "D:\\LocalAI\\Workspace"
      }
    }
  }
}
```

This is a common MCP client shape; a specific client's configuration syntax still applies. Hermes uses `mcp_servers` in its YAML configuration, rather than this JSON root name. Running the Windows executable from a WSL Hermes process requires a separately qualified Windows-interop path and argument mapping. A Podman container does not automatically inherit WSL executable interop. This package does not claim those integrations have passed.

## File contract

- Paths are relative to the configured root; either slash separator is accepted. Absolute paths, drive-relative paths, UNC/device paths, parent traversal, alternate data streams, reserved Windows names, and ambiguous trailing dots/spaces are rejected.
- The root and every existing ancestor are checked for reparse points. File symlinks, directory junctions, other reparse points, and files with multiple hard links are rejected.
- Files must be UTF-8 text without NUL characters, at most **204,800 bytes**. Limits apply to encoded bytes, not character count.
- Creation stages complete bytes in an exclusively created temporary file in the destination directory, flushes it, then uses Windows' non-replacing rename. Read-back verification must succeed before `created: true` and `verified: true` are returned.
- Internal cleanup removes only the current operation's unpublished temporary file after identity checks. There is no tool for deleting user files. A crash may leave a `.workspace-create-*.tmp` file for operator inspection.
- Results contain relative paths. Errors use `ok: false` and a stable error code, without returning the host's absolute paths. After a verification error, inspect the destination before retrying; a new file may already exist.

This helper is **not an OS sandbox** and does not defend against a malicious process running as the same Windows user that races filesystem checks. Normalization and reparse checks are path-based checks, not a proof of hostile-filesystem containment. Keep the selected workspace under the operator's control and configure other agent tools independently; a restricted file tool does not restrict terminal or desktop access.

## Verification

Run from this folder:

```powershell
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests use disposable temporary directories. They cover exact bytes/hashes, limits, duplicate and concurrent create attempts, invalid/outside paths, hard links, junctions, and real MCP stdio discovery/calls. The file-symlink case explicitly skips if Windows does not grant permission to create a test symlink. No existing workstation outputs or live Hermes services are used.

The implementation and tests establish this bridge's bounded behavior on the tested Windows environment. Clean-machine installation, WSL/container integration, agent reliability, and full-workstation reproduction remain separate checks.

## Licensing

The original-material license for this project remains pending. No upstream license is assigned to this new bridge by assumption. The MCP SDK and Python retain their respective upstream terms.
