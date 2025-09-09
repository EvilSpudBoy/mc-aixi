# MCP Versioning

Scheme
- Protocol versions are date strings: `YYYY-MM-DD`.
- The version only increments when backwards‑incompatible changes occur.
- Backwards‑compatible changes do not change the version.

Negotiation
- Happens during initialization (`initialize`).
- Clients and servers may support multiple versions but must agree on one per session.
- On failure to negotiate, terminate the connection gracefully with an error.

Current Version (as of docs)
- 2025-06-18

