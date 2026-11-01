"""Local ComfyUI API bridge. The MCP client launches this using stdio."""
import os
from typing import Any
from uuid import uuid4

import httpx
from mcp.server.fastmcp import FastMCP

BASE_URL = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
mcp = FastMCP("comfyui")


async def request(method: str, path: str, **kwargs: Any) -> Any:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60, trust_env=False) as client:
        response = await client.request(method, path, **kwargs)
        if response.is_error:
            raise ValueError(f"ComfyUI HTTP {response.status_code}: {response.text[:4000]}")
        return response.json()


@mcp.tool()
async def system_stats() -> dict:
    """Check the ComfyUI connection and read Python, GPU and memory information."""
    return await request("GET", "/system_stats")


@mcp.tool()
async def queue_status() -> dict:
    """Read running and pending ComfyUI jobs without changing them."""
    return await request("GET", "/queue")


@mcp.tool()
async def node_info(node_class: str) -> dict:
    """Read input/output schemas for a node class, such as EmptyLatentImage."""
    from urllib.parse import quote
    return await request("GET", "/object_info/" + quote(node_class, safe=""))


@mcp.tool()
async def list_node_classes() -> list[str]:
    """List available node class names without returning all their schemas."""
    return sorted((await request("GET", "/object_info")).keys())


@mcp.tool()
async def submit_workflow(workflow: dict[str, Any]) -> dict:
    """Queue an API-format workflow for execution. May use GPU and create outputs.

    workflow maps node IDs to class_type and inputs; UI-format workflows are
    not supported. Existing workflow files are never edited by this tool.
    """
    return await request("POST", "/prompt", json={"prompt": workflow, "client_id": str(uuid4())})


@mcp.tool()
async def prompt_history(prompt_id: str) -> dict:
    """Read completion status and output metadata for a submitted prompt ID."""
    from urllib.parse import quote
    return await request("GET", "/history/" + quote(prompt_id, safe=""))


if __name__ == "__main__":
    mcp.run(transport="stdio")
