# Build an MCP Client (Python summary)

System Requirements
- Python, `uv`, Anthropic SDK (or other LLM), `mcp` Python SDK.

Outline
1) Create project and install: `uv init mcp-client && uv venv && uv add mcp anthropic python-dotenv`.
2) Read `ANTHROPIC_API_KEY` from `.env` (never commit it).
3) Use `mcp.client.stdio.stdio_client` to launch/connect to a server script.
4) Initialize a `ClientSession`, call `list_tools()`, and relay tool calls from the model.

Sketch
```py
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

async def connect(server_path: str) -> ClientSession:
    params = StdioServerParameters(command="python", args=[server_path], env=None)
    read, write = await stdio_client(params)
    session = ClientSession(read, write)
    await session.initialize()
    return session
```

Loop
- Prompt the user → send to model with `tools` from `list_tools()`.
- For each `tool_use` in the model response: `session.call_tool(name, args)` and feed `tool_result` back.
- Render final text from the model.

Tips
- Use `AsyncExitStack` to manage transports; handle timeouts and retries.
- Validate server responses; print concise errors; keep UX responsive.

