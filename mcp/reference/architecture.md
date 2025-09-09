# MCP Architecture

Participants
- MCP host: the AI application (e.g., Claude Desktop, IDE) that manages sessions.
- MCP client: per‑server connector managed by the host; maintains one connection per server.
- MCP server: program exposing capabilities (tools/resources/prompts).

Layers
- Data layer (JSON‑RPC 2.0):
  - Lifecycle: initialization, capability negotiation, termination.
  - Server primitives: tools, resources, prompts.
  - Client primitives: sampling, elicitation, logging.
  - Notifications: server‑to‑client updates (e.g., `notifications/tools/list_changed`).
- Transport layer:
  - stdio: local process communication; no network; fastest path.
  - streamable HTTP: HTTP POST + optional Server‑Sent Events; supports standard auth (bearer/API keys/custom headers); OAuth recommended.

Lifecycle (Initialization)
- Client sends `initialize` with `protocolVersion`, `capabilities`, and `clientInfo`.
- Server replies with its `capabilities` and `serverInfo`.
- Client emits `notifications/initialized` when ready.
- Version is negotiated here. If incompatible, terminate gracefully.

Server Primitives
- Tools
  - Discover: `tools/list` → array of tool definitions: `name`, `title`, `description`, `inputSchema`.
  - Execute: `tools/call` with `name` and `arguments` validated against `inputSchema`.
  - Responses: array of content objects (e.g., `{type: "text", text: "..."}`), enabling rich, multi‑part outputs.
- Resources
  - Direct resources: fixed URIs with MIME types.
  - Resource templates: parameterized URI templates with metadata (title/description/mimeType) and optional parameter completion.
  - Operations: `resources/list`, `resources/templates/list`, `resources/read`, `resources/subscribe`.
- Prompts
  - Discover `prompts/list`; fetch details via `prompts/get` (name, description, arguments with types, defaults, and `required`).

Client Primitives
- Sampling: server requests model completion via client (`sampling/*` methods), enabling model‑independent servers.
- Elicitation: server requests structured user input/confirmation (schema‑driven UI).
- Logging: server emits diagnostic messages to the client.

Notifications
- Sent as JSON‑RPC notifications (no id, no response).
- Example: `notifications/tools/list_changed` → client typically follows up with `tools/list`.
- Capability‑gated: only sent if server advertised support (e.g., `tools.listChanged: true`).

Typical Flow
1) Initialize and negotiate capabilities/version.
2) Discover tools/resources/prompts.
3) Execute tool calls; handle content arrays in responses.
4) React to notifications to refresh dynamic registries.

Practical Notes
- Keep tool names stable and descriptive (namespace‑like); define precise JSON Schemas.
- Use MIME types for resource payloads; prefer URIs and templates for discovery.
- Add timeouts and input validation; propagate structured errors.

