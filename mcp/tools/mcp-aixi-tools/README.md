# mcp-aixi-tools

MCP stdio server exposing mc-aixi repo tools using FastMCP.

Tools:
- `list_envs()` – list `conf/*.conf`
- `build(target?: str)` – run `make` (optionally `clean`, `test-agent`, etc.)
- `run_agent(conf: str, log_path?: str)` – run `./aixi <conf> <log>` (auto-builds if missing)
- `graph_log(log_file: str)` – run `python3 graph.py <log>` and report output dir
- `summarize_log(log_file: str)` – quick CSV-like log summary
- `search_code(query: str, path: str = "src")` – simple substring search

## Requirements
- Python 3.10+
- `mcp` SDK (CLI extras) 1.2.0+

## Setup
Using uv (recommended):

```bash
cd mcp/tools/mcp-aixi-tools
uv venv
. .venv/bin/activate  # Windows: .venv\\Scripts\\activate
uv pip install -e .
```

Using pip:

```bash
cd mcp/tools/mcp-aixi-tools
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e .
```

## Run the server (STDIO)

```bash
python server.py
# or
uv run server.py
```

## Try with MCP Inspector (UI)

```bash
npx @modelcontextprotocol/inspector python server.py
```

- Choose STDIO transport. You should see the tools listed.
- Node.js >= 22.7.5 is required for Inspector (upgrade via nvm if needed).

## CLI examples (Inspector)

From the project folder with venv active:

```bash
cd mcp/tools/mcp-aixi-tools
. .venv/bin/activate

# List tools
npx @modelcontextprotocol/inspector --cli --transport stdio .venv/bin/python server.py --method tools/list

# Call list_envs
npx @modelcontextprotocol/inspector --cli --transport stdio .venv/bin/python server.py \
  --method tools/call --tool-name list_envs

# Call search_code
npx @modelcontextprotocol/inspector --cli --transport stdio .venv/bin/python server.py \
  --method tools/call --tool-name search_code --tool-arg query=Agent --tool-arg path=src
```

## Claude Desktop
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aixi-tools": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/mc-aixi/mcp/tools/mcp-aixi-tools",
        "run",
        "server.py"
      ]
    }
  }
}
```

Notes:
- STDIO servers must not write to stdout; use logging to stderr only if needed.
- `run_agent` writes logs under `log/` and may take time depending on the environment.

## Configure Codex CLI (MCP)
Add an entry to `~/.codex/config.toml` under `mcp_servers` (TOML format):

```toml
# IMPORTANT: top-level key is `mcp_servers` (TOML), not `mcpServers`.
[mcp_servers.aixi-tools]
command = "uv"
args = [
  "--directory",
  "/ABSOLUTE/PATH/TO/mc-aixi/mcp/tools/mcp-aixi-tools",
  "run",
  "server.py"
]
# Optional: set env vars for the server process
# env = { SOME_FLAG = "1" }
```

- Use absolute paths. You may need the full path to `uv` (e.g., `which uv`).
- Codex currently supports stdio MCP servers; SSE servers require an adapter.
