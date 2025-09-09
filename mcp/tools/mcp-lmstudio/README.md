# MCP Server: LM Studio

Simple MCP server exposing LM Studio's local OpenAI-compatible API.

Tools
- `lm_list_models()` → list loaded model ids (GET /v1/models)
- `lm_chat(messages, model, ...)` → call /v1/chat/completions
- `lm_chat_structured(messages, model, schema, ...)` → chat with Structured Output (response_format)
- `lm_embeddings(text, model)` → embeddings via /v1/embeddings

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
# Replace MODEL_ID with one from lm_list_models
npx @modelcontextprotocol/inspector --cli --transport stdio \
  uv --directory mcp/tools/mcp-lmstudio run server.py \
  --method tools/call \
  --tool-name lm_chat \
  --tool-arg model=MODEL_ID \
  --tool-arg messages='[{"role":"user","content":"Hello from MCP"}]'
```

Example: call lm_chat_structured (tiny JSON schema)
```bash
# Replace MODEL_ID with one from lm_list_models
npx @modelcontextprotocol/inspector --cli --transport stdio \
  uv --directory mcp/tools/mcp-lmstudio run server.py \
  --method tools/call \
  --tool-name lm_chat_structured \
  --tool-arg model=MODEL_ID \
  --tool-arg messages='[{"role":"user","content":"Tell me a short joke."}]' \
  --tool-arg schema='{"name":"joke","schema":{"type":"object","properties":{"joke":{"type":"string"}},"required":["joke"]}}'
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
- Codex CLI can connect to MCP STDIO servers. Two easy options:
  - Use MCP Inspector (recommended for quick checks) as shown above.
  - Or have your Codex CLI invocation spawn the server via STDIO using the same command/args as in the Claude config (uv with `--directory` and `run server.py`).
- If your Codex CLI build supports a persistent MCP server config, mirror the Claude JSON format with `command`, `args`, and optional `env`.
