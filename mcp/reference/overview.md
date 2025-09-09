# MCP Overview

Purpose
- Model Context Protocol (MCP) standardizes how AI apps connect to external tools, data, and workflows.
- Think “USB‑C for AI”: one interface to plug in many capabilities.

What MCP Enables
- Access calendars, docs, databases, and other systems from an AI.
- Invoke tools and multi‑step workflows (e.g., code tools, search, file ops).
- Mix local capabilities (filesystem) with remote/cloud ones (SaaS APIs).

Key Ideas
- Client–server model: a host app (e.g., Claude Desktop) runs one MCP client per MCP server.
- Two layers:
  - Data layer: JSON‑RPC 2.0 messages; lifecycle; primitives (tools, resources, prompts); notifications.
  - Transport layer: how bytes flow (stdio for local; streamable HTTP for remote).
- Primitives exposed by servers:
  - Tools: executable functions with JSON Schema inputs (discover via `tools/list`, invoke via `tools/call`).
  - Resources: read‑only data by URI or templates (list via `resources/list` and `resources/templates/list`, read via `resources/read`).
  - Prompts: reusable templates and arguments (discover via `prompts/list`, get via `prompts/get`).
- Client features servers can use:
  - Sampling: ask the client to obtain an LLM completion.
  - Elicitation: ask the user for input/approval with a schema.
  - Logging: send log messages to the client.

Why It Matters
- Developers: consistent model, less integration time and bespoke glue.
- AI apps: unified registry of tools/resources; dynamic discovery and updates.
- Users: better control and visibility; approvals and clear provenance.

See also
- Architecture: ./architecture.md
- Servers: ./servers.md • Clients: ./clients.md
- Local/Remote connection guides: ./connect-local.md • ./connect-remote.md
- SDKs: ./sdks.md • Versioning: ./versioning.md • Inspector: ./inspector.md

