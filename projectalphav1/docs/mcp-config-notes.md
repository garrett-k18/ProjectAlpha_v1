# MCP Configuration Notes

## Neon MCP

- **File:** `C:\Users\garre\.cursor\mcp.json`
- **Reason for custom command:** Windows sometimes resolves `npx` incorrectly (or not at all) when the command is just `"npx ..."`. Pointing directly to `A:\Program Files\node_js\npx.cmd` guarantees Cursor launches the right Node.js runtime.
- **PATH requirement:** `mcp-remote` spawns `node`/`npm`. Adding `A:\Program Files\node_js;C:\Users\garre\AppData\Roaming\npm` to the `PATH` env ensures those binaries are discovered.
- **Working configuration:**
  ```json
  "Neon": {
    "command": "A:\\\\Program Files\\\\node_js\\\\npx.cmd",
    "args": [
      "-y",
      "mcp-remote",
      "https://mcp.neon.tech/sse"
    ],
    "env": {
      "PATH": "A:\\\\Program Files\\\\node_js;C:\\\\Users\\\\garre\\\\AppData\\\\Roaming\\\\npm"
    }
  }
  ```
- **Why the full path matters:** If the MCP server entry falls back to `"command": "npx ..."`, Windows may pick up an outdated global install (or none), causing `mcp-remote` to exit immediately and Cursor to show “No MCP resources found.”

Keep this note handy whenever you reinstall Node.js or move the workspace—update the paths above to match the installed location so Neon remains accessible.

