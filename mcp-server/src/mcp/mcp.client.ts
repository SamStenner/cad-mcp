import { Injectable } from '@nestjs/common';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { FusionCADService } from 'src/fusion/fusion.service';
import {
  DrawCircleSchema,
  DrawRectangleSchema,
  ExtrudeSchema,
  FilletEdgesSchema,
  GetBodyInfoSchema,
  ApplyMaterialSchema,
} from 'src/fusion/schemas';

@Injectable()
export class McpClient {
  readonly server = new McpServer({ name: 'cad-mcp', version: '0.0.1' });

  constructor(private readonly fusion: FusionCADService) {
    this.server.registerTool(
      'draw-rectangle',
      {
        title: 'Draw Rectangle',
        description: 'Draw a rectangle',
        inputSchema: DrawRectangleSchema.shape,
      },
      async (params) => {
        const result = await this.fusion.drawRectangle(params);
        return {
          content: [{ type: 'text', text: JSON.stringify(result) }],
          structuredContent: result,
        };
      },
    );

    this.server.registerTool(
      'draw-circle',
      {
        title: 'Draw Circle',
        description: 'Draw a circle',
        inputSchema: DrawCircleSchema.shape,
      },
      async (params) => {
        const result = await this.fusion.drawCircle(params);
        return {
          content: [{ type: 'text', text: JSON.stringify(result) }],
          structuredContent: result,
        };
      },
    );

    this.server.registerTool(
      'extrude',
      {
        title: 'Extrude Profile',
        description: 'Extrude a profile to create a 3D feature',
        inputSchema: ExtrudeSchema.shape,
      },
      async (params) => {
        const result = await this.fusion.extrude(params);
        return {
          content: [{ type: 'text', text: JSON.stringify(result) }],
          structuredContent: result,
        };
      },
    );

    this.server.registerTool(
      'list-sketches',
      {
        title: 'List Sketches',
        description: 'List all sketches in the design',
      },
      async () => {
        const result = await this.fusion.listSketches();
        return {
          content: [{ type: 'text', text: JSON.stringify(result) }],
          structuredContent: result,
        };
      },
    );

    this.server.registerTool(
      'fillet-edges',
      {
        title: 'Fillet Edges',
        description: 'Fillet edges',
        inputSchema: FilletEdgesSchema.shape,
      },
      async (params) => {
        const result = await this.fusion.filletEdges(params);
        return {
          content: [{ type: 'text', text: JSON.stringify(result) }],
          structuredContent: result,
        };
      },
    );

    this.server.registerTool(
      'get-body-info',
      {
        title: 'Get Body Info',
        description: 'Get information about a body',
        inputSchema: GetBodyInfoSchema.shape,
      },
      async (params) => {
        const result = await this.fusion.getBodyInfo(params);
        return {
          content: [{ type: 'text', text: JSON.stringify(result) }],
          structuredContent: result,
        };
      },
    );

    this.server.registerTool(
      'apply-material',
      {
        title: 'Apply Material',
        description: 'Apply a material/appearance to a face',
        inputSchema: ApplyMaterialSchema.shape,
      },
      async (params) => {
        const result = await this.fusion.applyMaterial(params);
        return {
          content: [{ type: 'text', text: JSON.stringify(result) }],
          structuredContent: result,
        };
      },
    );

    this.server.registerTool(
      'list-materials',
      {
        title: 'List Materials',
        description: 'List all available materials/appearances',
      },
      async () => {
        const result = await this.fusion.listMaterials();
        return {
          content: [{ type: 'text', text: JSON.stringify(result) }],
          structuredContent: result,
        };
      },
    );
  }
}
