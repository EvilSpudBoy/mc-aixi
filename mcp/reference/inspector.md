# MCP Inspector

Purpose
- Interactive tool to test and debug MCP servers without a host app.

Install/Run (no install via npx)
- `npx @modelcontextprotocol/inspector <command>`
- Examples:
  - Inspect NPM server: `npx -y @modelcontextprotocol/inspector npx @modelcontextprotocol/server-filesystem /path`
  - Inspect local Node server: `npx @modelcontextprotocol/inspector node path/to/server/index.js`
  - Inspect local Python server: `npx @modelcontextprotocol/inspector python path/to/server.py`

Features
- Choose transport; customize command/env for local stdio servers.
- Browse resources (metadata, MIME types, content, subscriptions).
- Explore prompts (arguments, try runs, preview messages).
- List/call tools (validate inputs, view structured results).
- View notifications and server logs.

Workflow Tips
- Start Inspector with your server; verify initialize/capabilities.
- Iterate: edit server → rebuild/restart → reconnect → retest focused areas.
- Test edge cases: invalid inputs, missing args, concurrent ops; verify error handling.

