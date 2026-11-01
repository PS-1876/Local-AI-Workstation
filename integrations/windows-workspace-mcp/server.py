"""Two-tool Windows workspace MCP server. Stdio only; no network listener."""

import importlib.metadata
import sys

from workspace import Workspace, WorkspaceError, result_for


def build_server(workspace: Workspace):
    from mcp.server.fastmcp import FastMCP
    from mcp.types import ToolAnnotations

    server = FastMCP("local-workspace")

    @server.tool(annotations=ToolAnnotations(
        readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False,
    ))
    def read_windows_text(path: str) -> dict:
        """Read an existing UTF-8 file under the configured workspace using a relative path.

        Maximum size is 204800 bytes. Returns text, byte count, and SHA-256.
        Absolute paths, traversal, streams, links, and reparse points are rejected.
        """
        return result_for(workspace.read, path)

    @server.tool(annotations=ToolAnnotations(
        readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False,
    ))
    def create_windows_text(path: str, text: str) -> dict:
        """Create a NEW UTF-8 file under the workspace; never overwrite an existing file.

        Use a relative path in an existing directory. Maximum size is 204800 bytes.
        Success requires created=true and verified=true. An error after publication
        may leave the new file present; inspect it before any retry. There is no
        replace, patch, delete, command-execution, or directory-creation operation.
        """
        return result_for(workspace.create, path, text)

    return server


def main() -> int:
    try:
        if sys.version_info[:2] != (3, 12):
            raise WorkspaceError("unsupported_python", "This package requires Python 3.12.")
        if importlib.metadata.version("mcp") != "1.30.0":
            raise WorkspaceError("unsupported_sdk", "Install the pinned mcp==1.30.0 dependency.")
        if len(sys.argv) != 1:
            raise WorkspaceError("unexpected_arguments", "Configure the root through WORKSTATION_WORKSPACE_ROOT; no command-line options are supported.")
        workspace = Workspace.from_environment()
    except (WorkspaceError, importlib.metadata.PackageNotFoundError) as exc:
        print(f"Windows workspace MCP could not start: {exc}", file=sys.stderr)
        return 2
    build_server(workspace).run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
