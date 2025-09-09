# MCP Servers (Concepts)

Core Features
- Tools: functions with JSON Schema inputs, executed via `tools/call`; discover via `tools/list`.
- Resources: read‑only data by direct URI or template URIs; list via `resources/list` and `resources/templates/list`; read via `resources/read`; subscribe via `resources/subscribe`.
- Prompts: reusable templates; discover via `prompts/list`; retrieve via `prompts/get`.

Tools
- Schema‑defined inputs/outputs; one operation per tool.
- Recommended fields in definitions: `name`, `title`, `description`, `inputSchema`.
- Protocol operations:
  - `tools/list` → array of tool definitions
  - `tools/call` → tool execution result (array of content parts)

Resources
- Two discovery patterns:
  - Direct resources: fixed URI (e.g., `file:///...`), advertised with MIME type.
  - Resource templates: `uriTemplate` with params and metadata (title, description, mimeType); may support parameter completion.
- Protocol operations:
  - `resources/list` → array of resource descriptors
  - `resources/templates/list` → array of templates
  - `resources/read` → resource content + metadata
  - `resources/subscribe` → change notifications subscription

Prompts
- User‑invoked templates with typed arguments; may support parameter completion.
- Protocol operations:
  - `prompts/list` → descriptors
  - `prompts/get` → full definition

User Interaction and Safety
- Tools are model‑initiated but must respect user approvals and permissions.
- Applications should provide tool visibility, approvals, and activity logs.
- Treat external calls (APIs/DBs) with timeouts, retries, and clear errors.

Design Guidance
- Prefer stable, descriptive tool names (e.g., `weather_current` vs `weather`).
- Keep JSON Schemas precise: required vs optional, value enums, formats.
- Document MIME types for resources; keep URIs stable and self‑describing.
- Emit notifications when dynamic registries change (e.g., tool list).

