MCP Tools for mc-aixi

This folder contains a minimal Model Context Protocol (MCP) server that exposes repo-specific tools the assistant can call. It follows the reference PDF: mcp/reference/Understanding Model Context Protocol (MCP) and Building Custom MCP Tools.pdf

Active branch for this fork: `dev/mc-aixi-local`. Open PRs against that branch (not `main`) when working within this fork.

Tools
- list_envs(): List available conf files under conf/.
- build(target?): Run make at repo root; returns a concise log tail.
- run_agent(conf, log_path?): Run ./aixi with the given conf; auto-builds if missing.
- graph_log(log_file): Run python3 graph.py <log_file>; returns output dir.
- summarize_log(log_file): Quick metrics from a CSV-like agent .log.
- search_code(query, path?): Simple substring search across src/ (and a few text types).

Server
- Implementation: Python stdio MCP server at `mcp/tools/mcp-aixi-tools/server.py` using the Python MCP SDK (FastMCP).
- Transport: stdio (recommended for local hosts like Claude Desktop). No external processes are spawned except the requested tools.

Setup
1) Python deps (host machine):
   - pip install mcp  # Python MCP SDK

2) Claude Desktop (macOS) integration (example):
   - Create or edit: ~/Library/Application Support/Claude/claude_desktop_config.json
   - Add an MCP server entry:

     {
       "mcpServers": {
         "aixi-tools": {
           "command": "uv",
           "args": ["--directory", "/absolute/path/to/your/mc-aixi/mcp/tools/mcp-aixi-tools", "run", "server.py"]
         }
       }
     }

   - Restart Claude Desktop. In a new chat, the assistant will discover tools from "aixi-tools" and can call them as needed (it may ask for approval before running build/run commands).

3) OpenAI Agents/Responses (HTTP variant):
   - This server runs over stdio. If you prefer HTTP/SSE hosting, adapt the code to run with an HTTP transport and then reference it as an MCP tool from your agent (see the PDF for a server_url example). 

Operational Notes
- The server assumes it is launched with cwd as the repo root (cwd is set in the Claude config above). Paths are resolved relative to the repo.
- run_agent writes logs under log/ by default and will call make if ./aixi is missing.
- summarize_log expects CSV-style logs like the samples under log/.
- search_code is intentionally conservative; it indexes common text/code file types and limits results to 50 matches.

Troubleshooting
- If the host can’t discover tools, ensure the Python package mcp is installed and that Claude (or your client) is picking up the config. 
- If build fails, run make manually in the repo root to inspect errors, then rerun the tool.
- If graphing fails, confirm python3 and graph.py work locally: python3 graph.py log/tictactoe.log
