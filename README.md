# CAD MCP 🔧

Minimal MCP server that exposes CAD tools

Currently supports Fusion only.

## Demo Video

Watch the CAD MCP in action: [https://screen.studio/share/mTFQBOba](https://screen.studio/share/mTFQBOba)

## Getting Started

### Step 0: Preparing Fusion

The Fusion API works by installing an add-in, which is a folder containing a Python project. In our case, that is the `/fusion-server` directory in the root of this project. This needs to be added to Fusion before the MCP server can run. In Fusion, navigate to **Utilities** → **Add-Ins** → **Scripts and Add-Ins** → **+** → **Script or add-in from device**. Then select the `/fusion-server` directory. In the list of add-ins, `fusion-server` should now appear in the list with a checked toggle, indicating it is enabled.

For more help, watch this: [https://screen.studio/share/PqKagknA](https://screen.studio/share/PqKagknA)

### Step 1: Running the MCP Server

Now that the Fusion add-in has been enabled, we can start the MCP server. To do this, you need `pnpm` installed. Then, navigate to the `/mcp-server` directory.

To install the dependencies, run `pnpm i`

To start the server, run `pnpm start`

### Step 2: Using the MCP

You can now interact with the MCP using an MCP client of your choice. For example, in Cursor, just add this to your `mcp.json`:

```json
{
  "cad-mcp": {
    "url": "http://localhost:3000/mcp"
  }
}
```

Now you can interact with the MCP server via an LLM! 🚀

### Available Tools

The CAD MCP provides the following tools:

Core Tools:

- **draw-rectangle**: Draw a rectangle sketch
- **draw-circle**: Draw a circle sketch  
- **extrude**: Extrude a profile to create a 3D feature
- **fillet-edges**: Apply fillets to edges of a body
- **apply-material**: Apply a material/appearance to a specific face

Helper Tools:

- **get-body-info**: Get detailed information about a body (faces, edges, vertices)
- **list-sketches**: List all sketches in the design
- **list-materials**: List all available materials/appearances

### Quick Start Examples

- "Make a long box with round edges"
- "Make 3 skyscrapers of various heights"
- "Make a TARDIS"

TARDIS Example:

![TARDIS](/assets/tardis.gif)
