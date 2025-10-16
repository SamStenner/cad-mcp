import { Controller, Post, Req, Res } from '@nestjs/common';
import { McpClient } from './mcp.client';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import type { Request, Response } from 'express';

@Controller('mcp')
export class McpController {
  constructor(private readonly mcp: McpClient) {}

  @Post()
  async handle(@Req() req: Request, @Res() res: Response) {
    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
      enableJsonResponse: true,
    });
    res.on('close', () => void transport.close());
    await this.mcp.server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  }
}
