import { Module } from '@nestjs/common';
import { McpController } from './mcp.controller';
import { McpClient } from './mcp.client';
import { FusionModule } from 'src/fusion/fusion.module';

@Module({
  imports: [FusionModule],
  controllers: [McpController],
  providers: [McpClient],
})
export class McpModule {}
