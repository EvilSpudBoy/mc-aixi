# AGENTS.md — MCP Tools (scope: mcp/)

This file applies to everything under `mcp/`.

Goals
- Keep MCP servers minimal, reliable, and easy to run locally.
- Avoid committing generated or user-specific artifacts.
- Maintain compatibility with the repo’s root guidelines.

Languages & Style
- Python 3.10+.
- Prefer small footprints and standard libs; avoid heavy deps.
- Use type hints and docstrings for public functions.
- STDIO servers must not write to stdout; use logging to stderr.
- Keep functions small, with clear input validation and timeouts on I/O.

Dependencies & Packaging
- Required deps: `mcp[cli] >= 1.2.0`, `httpx`.
- Prefer `uv` for local dev. Track `uv.lock` for reproducible installs.
- Do not commit virtualenvs, `__pycache__`, `*.egg-info`, or build outputs.

Local Development
- Using uv:
  - `uv venv`
  - `. .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
  - `uv pip install -e .`
- Using pip:
  - `python -m venv .venv`
  - `. .venv/bin/activate`
  - `pip install -e .`

Running & Testing
- STDIO server (example `mcp-hello`):
  - `python hello.py` or `uv run hello.py`
- MCP Inspector (CLI):
  - `npx @modelcontextprotocol/inspector --cli --transport stdio .venv/bin/python hello.py --method tools/list`
  - `npx @modelcontextprotocol/inspector --cli --transport stdio .venv/bin/python hello.py --method tools/call --tool-name hello --tool-arg name=World`
- Weather tools in `mcp-hello` query `api.weather.gov` and only support US locations.

Server Guidelines
- Never print to stdout; use `logging` to stderr for diagnostics.
- Validate tool inputs and return informative errors; avoid raising uncaught exceptions.
- Add conservative timeouts to network calls; avoid long blocking operations.
- Keep tool names stable and descriptive; prefer `snake_case` for Python functions.

Git Hygiene
- Already ignored by `.gitignore`: `__pycache__/`, `*.egg-info/`, `build/`, `dist/`, `.venv/`, etc.
- Do not commit generated files or local config. Commit `uv.lock` when updating deps.

Structure Notes
- Example servers live under `mcp/tools/*` (e.g., `mcp-hello`, `mcp-aixi-tools`).
- Keep each tool self-contained with a simple entrypoint (e.g., `hello.py`, `server.py`).

References (local)
- MCP Reference index: `mcp/reference/README.md`
- Overview: `mcp/reference/overview.md`
- Architecture: `mcp/reference/architecture.md`
- Servers: `mcp/reference/servers.md`
- Clients: `mcp/reference/clients.md`
- Connect (local): `mcp/reference/connect-local.md`
- Connect (remote): `mcp/reference/connect-remote.md`
- Build server (Python): `mcp/reference/build-server.md`
- Build client (Python): `mcp/reference/build-client.md`
- SDKs: `mcp/reference/sdks.md`
- Versioning: `mcp/reference/versioning.md`
- MCP Inspector: `mcp/reference/inspector.md`
