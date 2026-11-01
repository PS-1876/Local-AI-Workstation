import asyncio
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = Path(__file__).resolve().parents[1] / "server.py"


def payload(result):
    if result.structuredContent is not None:
        return result.structuredContent
    return json.loads(next(block.text for block in result.content if block.type == "text"))


@unittest.skipUnless(os.name == "nt", "Native Windows stdio tests")
class StdioTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_stdio_discovery_and_synthetic_file_operations(self):
        temporary = tempfile.TemporaryDirectory(prefix="local-ai-workspace-mcp-stdio-")
        root = Path(temporary.name).resolve(strict=True)
        try:
            parameters = StdioServerParameters(
                command=sys.executable,
                args=[str(SERVER)],
                env={"WORKSTATION_WORKSPACE_ROOT": str(root)},
            )
            with open(os.devnull, "w") as errors:
                async with stdio_client(parameters, errlog=errors) as (reader, writer):
                    async with ClientSession(reader, writer) as session:
                        await session.initialize()
                        listed = await session.list_tools()
                        tools = {tool.name: tool for tool in listed.tools}
                        self.assertEqual(set(tools), {"read_windows_text", "create_windows_text"})
                        self.assertTrue(tools["read_windows_text"].annotations.readOnlyHint)
                        self.assertFalse(tools["create_windows_text"].annotations.readOnlyHint)
                        text = "Synthetic MCP test \u2713\n"
                        created = payload(await session.call_tool("create_windows_text", {"path": "stdio.txt", "text": text}))
                        self.assertTrue(created["ok"] and created["created"] and created["verified"])
                        self.assertEqual(created["sha256"], hashlib.sha256(text.encode()).hexdigest())
                        self.assertEqual((root / "stdio.txt").read_bytes(), text.encode())
                        read = payload(await session.call_tool("read_windows_text", {"path": "stdio.txt"}))
                        self.assertEqual(read["text"], text)
                        duplicate = payload(await session.call_tool("create_windows_text", {"path": "stdio.txt", "text": "must not replace"}))
                        self.assertEqual(duplicate["error"]["code"], "already_exists")
                        outside = payload(await session.call_tool("read_windows_text", {"path": "../outside.txt"}))
                        self.assertEqual(outside["error"]["code"], "invalid_path")
                        self.assertEqual((root / "stdio.txt").read_bytes(), text.encode())
        finally:
            self.assertEqual(root.resolve(strict=True), root)
            self.assertEqual(root.parent, Path(tempfile.gettempdir()).resolve(strict=True))
            self.assertTrue(root.name.startswith("local-ai-workspace-mcp-stdio-"))
            temporary.cleanup()

    async def test_startup_without_root_fails_before_protocol_output(self):
        environment = dict(os.environ)
        environment.pop("WORKSTATION_WORKSPACE_ROOT", None)
        result = await asyncio.to_thread(
            subprocess.run, [sys.executable, str(SERVER)], env=environment, capture_output=True, timeout=10,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"WORKSTATION_WORKSPACE_ROOT", result.stderr)


if __name__ == "__main__":
    unittest.main()
