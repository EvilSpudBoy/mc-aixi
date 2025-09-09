# MCP Clients (Concepts)

Role
- The host app (e.g., Claude Desktop) manages one MCP client per connected server.
- Clients consume server primitives and also expose features servers can call.

Client Features
- Elicitation: request structured user input/approval during workflows.
- Roots: filesystem boundaries for server operations (`file://` URIs), with `roots/list_changed` notifications when updated.
- Sampling: request an LLM completion from the host on behalf of a server, with human‑in‑the‑loop checkpoints.

Elicitation
- Servers may pause execution to ask the client to gather specific user inputs, validated by a JSON Schema.
- Clients should present clear context, validation, and allow decline/cancel, preserving user autonomy.

Roots
- Communicate workspace boundaries to servers as `file://` URIs with display names.
- Updated dynamically as users change projects; clients keep final control over actual file access.

Sampling
- Lets servers stay model‑agnostic; the client performs model calls.
- Encourage approval gates and transparency (model, prompt, limits); redact sensitive data.

Best Practices
- Validate/limit server‑initiated requests; rate‑limit sampling.
- Provide clear UI for permissions and explain why info is requested.
- Keep robust error handling and graceful shutdown on disconnects.

