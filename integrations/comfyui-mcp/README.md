# ComfyUI stdio bridge

This small bridge exposes six ComfyUI API operations to an MCP client. It is the reviewed local reference source, without user configuration. It uses the Python MCP SDK and HTTPX; the two direct dependency pins are not a complete dependency lock.

Create a separate Python 3.12 environment in this folder, install the requirements, and launch the server through a client that supports local stdio MCP:

```powershell
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe -m pip check
```

Use the absolute `.venv/Scripts/python.exe` path as the client command and the absolute `server.py` path as its sole argument. Set `COMFYUI_URL=http://127.0.0.1:8188` in that child's environment. This address assumes the client process runs on the same Windows host as ComfyUI. A container needs a separately verified route. This is a client-neutral connection recipe; it does not establish availability in every chat application.

| Tool | Effect |
| --- | --- |
| `system_stats` | Reads runtime/device information |
| `queue_status` | Reads running and pending jobs |
| `node_info` | Reads one node schema |
| `list_node_classes` | Reads available class names |
| `submit_workflow` | Submits an API-format graph; can consume GPU resources and create files |
| `prompt_history` | Reads results for a prompt ID |

Check the queue before submitting work. Save the returned prompt ID immediately; inspect its history after a client timeout instead of blindly resubmitting. A UI workflow export is not an API-format graph. Tool authorization is enforced by the client and by the installed nodes; this bridge is not a sandbox for arbitrary workflows.

The test below launches the real stdio server against a temporary fake HTTP service. It checks MCP initialization, discovery, request routing, submission payloads, and error propagation. It does not run ComfyUI, use a GPU, or verify a render:

```powershell
& .\.venv\Scripts\python.exe test_bridge.py
```

See [local modifications](../../docs/LOCAL-MODIFICATIONS.md) for packaging decisions and remaining full-workstation qualification. Original project licensing is still pending as described in the root README; dependency licenses remain their own.
