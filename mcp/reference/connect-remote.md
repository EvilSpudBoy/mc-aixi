# Connect to Remote MCP Servers

Concepts
- Remote servers are internet‑hosted and communicate over the streamable HTTP transport.
- In Claude (web), you add them via Custom Connectors; other clients offer similar flows.

Typical Steps (Claude)
1) Open Settings → Connectors → Add custom connector.
2) Enter the remote MCP server URL (https://...).
3) Complete server auth (OAuth/API key/etc.).
4) Use the attachment/tools UI to browse resources and prompts.
5) Configure tool permissions per connector.

Best Practices
- Verify server authenticity and review requested permissions.
- Organize multiple connectors by project; remove unused ones.
- Prefer OAuth; use bearer/API keys over plain credentials.

Notes
- Remote servers expose the same primitives as local ones (tools, resources, prompts).
- Transport details (framing, SSE streaming) differ, but JSON‑RPC messages are the same.

