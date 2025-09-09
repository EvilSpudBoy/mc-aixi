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

Notes
- Keep LM Studio running as a local server (Developer tab or `lms server start`).
- For chat structured output, the tool parses JSON content when possible and returns it under `parsed`.

