"""Protocol/HTTP contract check using a temporary local fake ComfyUI server."""
import asyncio
import json
import os
from pathlib import Path
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

requests = []


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_GET(self):
        requests.append(("GET", self.path, None))
        responses = {
            "/system_stats": {"system": {"comfyui_version": "fixture"}},
            "/queue": {"queue_running": [], "queue_pending": []},
            "/object_info": {"TestNode": {}, "OtherNode": {}},
            "/object_info/TestNode": {"TestNode": {"input": {"required": {}}}},
            "/history/fixture-id": {"fixture-id": {"status": {"completed": True}}},
        }
        self.reply(200, responses[self.path]) if self.path in responses else self.reply(404, {"error": "fixture missing"})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        requests.append(("POST", self.path, body))
        if self.path == "/prompt":
            self.reply(200, {"prompt_id": "fixture-id", "number": 0, "node_errors": {}})
        else:
            self.reply(404, {"error": "fixture missing"})


async def check(port):
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).with_name("server.py"))],
        env={**os.environ, "COMFYUI_URL": f"http://127.0.0.1:{port}"},
    )
    graph = {"1": {"class_type": "TestNode", "inputs": {}}}
    cases = [
        ("system_stats", {}, "fixture"),
        ("queue_status", {}, "queue_running"),
        ("list_node_classes", {}, "TestNode"),
        ("node_info", {"node_class": "TestNode"}, "required"),
        ("submit_workflow", {"workflow": graph}, "fixture-id"),
        ("prompt_history", {"prompt_id": "fixture-id"}, "completed"),
    ]
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listed = await session.list_tools()
            assert {t.name for t in listed.tools} == {c[0] for c in cases}
            for name, args, expected in cases:
                result = await session.call_tool(name, args)
                assert not result.isError, (name, result)
                assert expected in result.model_dump_json(), (name, result)
            result = await session.call_tool("node_info", {"node_class": "Missing"})
            assert result.isError and "404" in result.model_dump_json()
    submitted = [r for r in requests if r[0] == "POST"]
    assert len(submitted) == 1 and submitted[0][1] == "/prompt"
    assert submitted[0][2]["prompt"] == graph
    assert isinstance(submitted[0][2]["client_id"], str) and submitted[0][2]["client_id"]
    assert len(requests) == 7
    print("PASS: MCP initialization, six tools, HTTP payloads, and HTTP error propagation; fake service only")


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        asyncio.run(check(server.server_port))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
