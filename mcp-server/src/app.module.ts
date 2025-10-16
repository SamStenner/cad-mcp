import { Module } from '@nestjs/common';
import { McpModule } from './mcp/mcp.module';
import { ConfigModule } from '@nestjs/config';

@Module({
  imports: [McpModule, ConfigModule.forRoot()],
})
export class AppModule {}
