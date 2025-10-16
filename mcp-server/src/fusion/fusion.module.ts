import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { FusionCADService } from 'src/fusion/fusion.service';

@Module({
  imports: [ConfigModule],
  providers: [FusionCADService],
  exports: [FusionCADService],
})
export class FusionModule {}
