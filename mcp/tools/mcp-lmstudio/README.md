# MCP Server: LM Studio

Simple MCP server exposing LM Studio's local OpenAI-compatible API.

Tools
- `lm_list_models()` → list loaded model ids (GET /v1/models)
- `lm_chat(messages, model, ...)` → call /v1/chat/completions
- `lm_chat_structured(messages, model, schema, ...)` → chat with Structured Output (response_format)
- `lm_embeddings(text, model)` → embeddings via /v1/embeddings
- `lm_demo_tool_use(model, user_message, tools?)` → end‑to‑end tool‑use demo with safe built‑ins (say_hello, get_current_time)

Recommended model for tool use
- Prefer `openai/gpt-oss-20b` if loaded — it’s trained for tool use and tends to emit proper `tool_calls`.

Config
- `LMSTUDIO_BASE_URL` (default `http://localhost:1234/v1`)
- `LMSTUDIO_API_KEY` (default `lm-studio`)

Run
```bash
cd mcp/tools/mcp-lmstudio
uv venv && . .venv/bin/activate
uv pip install -e .  # not required to run, but recommended
uv run server.py
```

Inspect (MCP Inspector CLI)
```bash
npx @modelcontextprotocol/inspector --cli --transport stdio \
  uv --directory mcp/tools/mcp-lmstudio run server.py --method tools/list
```

Example: call lm_chat (minimal payload)
```bash
# Prefer openai/gpt-oss-20b if loaded; otherwise use a model from lm_list_models
npx @modelcontextprotocol/inspector --cli --transport stdio \
  uv --directory mcp/tools/mcp-lmstudio run server.py \
  --method tools/call \
  --tool-name lm_chat \
  --tool-arg model=openai/gpt-oss-20b \
  --tool-arg messages='[{"role":"user","content":"Hello from MCP"}]'
```

Example: call lm_chat_structured (tiny JSON schema)
```bash
# Prefer openai/gpt-oss-20b if loaded; otherwise use a model from lm_list_models
npx @modelcontextprotocol/inspector --cli --transport stdio \
  uv --directory mcp/tools/mcp-lmstudio run server.py \
  --method tools/call \
  --tool-name lm_chat_structured \
  --tool-arg model=openai/gpt-oss-20b \
  --tool-arg messages='[{"role":"user","content":"Tell me a short joke."}]' \
  --tool-arg schema='{"name":"joke","schema":{"type":"object","properties":{"joke":{"type":"string"}},"required":["joke"]}}'
```

Example: tool use demo (model calls built‑in tools)
```bash
# Prefer openai/gpt-oss-20b if loaded; otherwise use a model from lm_list_models
npx @modelcontextprotocol/inspector --cli --transport stdio \
  uv --directory mcp/tools/mcp-lmstudio run server.py \
  --method tools/call \
  --tool-name lm_demo_tool_use \
  --tool-arg model=openai/gpt-oss-20b \
  --tool-arg user_message='Say hello to Alice, then tell me the current time.'
```

Notes
- Keep LM Studio running as a local server (Developer tab or `lms server start`).
- For chat structured output, the tool parses JSON content when possible and returns it under `parsed`.

Configure Claude Desktop
```json
{
  "mcpServers": {
    "lmstudio": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/mcp/tools/mcp-lmstudio",
        "run",
        "server.py"
      ],
      "env": {
        "LMSTUDIO_BASE_URL": "http://localhost:1234/v1",
        "LMSTUDIO_API_KEY": "lm-studio"
      }
    }
  }
}
```

Configure Codex CLI
- Codex uses `~/.codex/config.toml` (TOML). To enable this MCP server:

```toml
# IMPORTANT: top-level key is `mcp_servers` (not `mcpServers`).
[mcp_servers.lmstudio]
command = "uv"
args = [
  "--directory",
  "/ABSOLUTE/PATH/TO/mcp/tools/mcp-lmstudio",
  "run",
  "server.py",
]
# Optional environment for the server process
env = { LMSTUDIO_BASE_URL = "http://localhost:1234/v1", LMSTUDIO_API_KEY = "lm-studio" }
# Optional: increase startup timeout for tools/list on slower machines
startup_timeout_ms = 20000
```

- Notes from Codex docs:
  - Only STDIO MCP servers are supported directly (this server uses STDIO).
  - Codex may cache tools/resources; it starts servers lazily when needed.
  - See `docs/config.md#mcp_servers` in codex repo for full reference.

Optional: point Codex model provider to LM Studio (OpenAI-compatible)
- If you want Codex’s main model calls to go through LM Studio too, define a provider:

```toml
# Example provider for OpenAI-compatible chat completions via LM Studio
[model_providers.lmstudio]
name = "LM Studio"
base_url = "http://localhost:1234/v1"
# If you use an API key, set env var LMSTUDIO_API_KEY and reference it here
env_key = "LMSTUDIO_API_KEY"
wire_api = "chat"

# Then select it
model_provider = "lmstudio"
model = "phi-3.1-mini-4k-instruct" # or one from lm_list_models
```
