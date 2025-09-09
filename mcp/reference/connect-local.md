# Connect to Local MCP Servers

Overview
- Local servers run as child processes over stdio and are started by the client/host.
- Example host: Claude Desktop; configuration file defines server commands and args.

Claude Desktop Config
- Path (macOS): `~/Library/Application Support/Claude/claude_desktop_config.json`
- Path (Windows): `%APPDATA%\Claude\claude_desktop_config.json`
- Example (filesystem server via npx):

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/username/Desktop", "/Users/username/Downloads"]
    }
  }
}
```

Notes
- Replace `username` and directories to control allowed access roots.
- Restart the app after editing the config to spawn servers.
- Look for the server indicator in the UI and verify tools are listed.

Security
- Servers run with your user permissions. Only grant access to intended directories.
- Review and approve each tool call.

Troubleshooting
- If the server icon doesn’t appear: validate JSON, restart, check logs.
- Collect host logs from its support docs; verify Node or runtime availability when using npx/node.

