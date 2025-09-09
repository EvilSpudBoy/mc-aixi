# Build an MCP Server (Python summary)

System Requirements
- Python 3.10+; `mcp[cli] >= 1.2.0`; `httpx`; optional `uv` for workflow.

Key Practices
- STDIO servers must not write to stdout; use `logging` to stderr.
- Validate inputs with type hints/JSON Schema; add timeouts for I/O.
- Advertise capabilities precisely; send notifications for dynamic changes.

Quickstart (outline)
- Create env and install deps (with uv):

```bash
uv init weather && cd weather
uv venv && . .venv/bin/activate
uv add "mcp[cli]" httpx
```

- Minimal server structure (FastMCP):

```py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Return concise weather alerts for a US state (e.g., CA)."""
    # fetch + format alerts (network call with timeout)
    return "No active alerts"

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Return a short forecast for a lat/lon pair."""
    return "Sunny, light winds"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Testing with Claude Desktop
- Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": ["--directory", "/ABS/PATH/weather", "run", "weather.py"]
    }
  }
}
```

Then restart the app and verify tool discovery and calls.

Troubleshooting
- If tools aren’t listed, ensure the server runs and stdout isn’t polluted.
- Prefer absolute paths; on Windows, escape backslashes or use forward slashes.

