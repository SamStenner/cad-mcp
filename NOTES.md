# Notes

## Design Decisions

I broke the task down into two parts, creating an MCP server and interacting with a CAD program.

I am much more familiar with NodeJS/Typescript backends than Python, so decided that it would be best to use a lightweight NestJS server for my MCP server.
I realize that most CAD API's don't have Typescript support, but a simple RPC wrapper will allow me to call Python from Node, so I considered that to be acceptable. If I were primarily a Python developer, I would have chosen just Python for this task.

## Choice of CAD Program

Solidworks is Windows only, so that was immediately out. FreeCAD looked like the simplest, whereas Fusion looked more powerful. Both FreeCAD and Fusion used Python, although Fusion needs slightly more work to get the add-in installed. Fusion looked like a richer interface that might be better at helping me visually debug any issues. I decided to go with Fusion, but would be willing to fall back to FreeCAD if I ran into issues.

## MCP Server Architecture

I decided to use NestJS because I like the opinionated choices it makes with controllers, services and modules. It keeps the different concerns separated nicely, and encourages injectable patterns. This would mean that adding support for other CAD programs under the same API would be quite straightforward. In fact, I initially designed the `FusionService` to implement a general interface for the tools, but decided that it added unnecessary re-direction at this stage. I felt that for this demo it's best to keep it simple.

## Fusion Add-In

In order to interact with Fusion's API, I needed to make a small 'Add-in', which is basically just a Python program that imports the Fusion Python SDK, and is then installed via Fusion's UI. Once this worked, I was able to send requests to Fusion from Node. This was probably more complex than if I'd gone with FreeCADs API, which is just a Python package, but I hoped that the free visualization and flexibility that Fusion provides would make it worth it.

## Tool Definitions

I initially wanted to define all my tools on the Typescript side as I'm more familiar with Typescript. However, interacting with Fusion's API so granularly via RPC would introduce high complexity, so I decided to define the tools in Python, and let my MCP server make simple RPC requests to Python, where the 'heavy-lifting' would happen. I felt this was a more idiomatic way of doing cross-language requests. If I were to support additional CAD programs, I would probably maintain this principle.

## Tool Choices

1. I started with just one simple tool, `draw-rectangle`. This allowed me to make sure I had a simple end-to-end flow working. I created a tool on the MCP side called `draw-rectangle`, used RPC to forward the request + parameters to the python side, and ensured it created a rectangle in the Fusion UI. When I saw the model appear in the Fusion UI without any UI-specific work required, I felt confident in my choice of using Fusion as it made it easy to prototype and validate my code quickly.
2. Then I added more parameters, such as width/height and X/Y/Z coordinates.
3. Once this worked, I added `draw-circle` to provide more variety in my testing.
4. As suggested by the task spec, I added `extrude` so that 3D shapes could be made, as well as `fillet-edges`.
5. I also made `get-body-info` in case the LLM wants to know information about the bodies it's already made.
6. Finally, I added `list-materials` and `apply-material` to make the models more visually interesting

## Arguments & Validation

I knew that the MCP server for NodeJS used Zod for schema validation. This would make validating inputs/outputs very simple, and would automatically handle any errors and convert them into the appropriate responses that the LLM could understand. I also ensured that errors that happened on the Python side would be correctly piped back to Typescript so that it was easier to debug issues.

## Limitations

Currently, the output is available only on the server side. This means that whilst the client that uses the MCP server is able to modify/control the 3D model, the artifact remains on the server that is running the CAD software. I think it would be useful to be able to access the artifact, either by uploading it somewhere, returning it in the MCP response as base64, or even providing screenshots.

Adding new tools requires defining the tool in the MCP server, and then also defining it in the python server. This can also lead to type drifting, as there's no strong coupling between the functions. If I had more time I would use code-gen to automatically generate the functions/types in both Python and Typescript, making development faster and safer. We did a lot of this at Cosine.

The current tools are quite limited (e.g. can only use the built in materials), and can only operate in one space. Given more time, it would be good to be able to manage projects, change project, delete objects, move objects, etc.

## Known Issues

- No input validation on Python side (relies on TypeScript validation)
- No strong types on the Python side
- The fusion tokens are quite long strings, which can fill up the LLMs context window quickly if the whole sketch is requested.

## Interesting Files

A lot of the code is just boiler plate for running an MCP server, setting up NestJS, RPC, etc. The files that actually contain relevant code are:

- [fusion-server/cad_tools.py](fusion-server/cad_tools.py) (tool logic implementation)
- [fusion-server/fusion_bridge.py](fusion-server/fusion_bridge.py) (python server + addin bridge)
- [mcp-server/src/mcp/mcp.client.ts](mcp-server/src/mcp/mcp.client.ts) (mcp tools definitions)
- [mcp-server/src/fusion/schemas.ts](mcp-server/src/fusion/schemas.ts) (mcp tool schema definitions)
- [mcp-server/src/mcp/mcp.controller.ts](mcp-server/src/mcp/mcp.controller.ts) (mcp endpoint)
