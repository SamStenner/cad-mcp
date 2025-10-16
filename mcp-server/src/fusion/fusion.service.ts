import { Injectable } from '@nestjs/common';
import { RPCClient } from './rpc.client';
import { ConfigService } from '@nestjs/config';
import {
  DrawCircleParams,
  DrawRectangleParams,
  ExtrudeParams,
  FilletEdgesParams,
  GetBodyInfoParams,
  ApplyMaterialParams,
} from './schemas';
import {
  DrawCircleResult,
  DrawRectangleResult,
  ExtrudeResult,
  FilletEdgesResult,
  GetBodyInfoResult,
  ListSketchesResult,
  ApplyMaterialResult,
  ListMaterialsResult,
} from './types';

type FusionCADServiceConfig = {
  FUSION_SERVER_PORT: number;
  FUSION_SERVER_HOST: string;
};

@Injectable()
export class FusionCADService {
  private readonly rpc: RPCClient;

  constructor(configService: ConfigService<FusionCADServiceConfig>) {
    const port = parseInt(configService.get('FUSION_SERVER_PORT') ?? '8765');
    const host = configService.get('FUSION_SERVER_HOST') ?? '127.0.0.1';
    this.rpc = new RPCClient(port, host);
  }

  public drawRectangle = async (
    params: DrawRectangleParams,
  ): Promise<DrawRectangleResult> => this.rpc.send('draw_rectangle', params);

  public extrude = (params: ExtrudeParams): Promise<ExtrudeResult> =>
    this.rpc.send('extrude', params);

  public drawCircle = (params: DrawCircleParams): Promise<DrawCircleResult> =>
    this.rpc.send('draw_circle', params);

  public listSketches = (): Promise<ListSketchesResult> =>
    this.rpc.send('list_sketches');

  public filletEdges = async ({
    bodyToken,
    radius,
    operation,
  }: FilletEdgesParams): Promise<FilletEdgesResult> => {
    const body = await this.getBodyInfo({ bodyToken });
    const edgeTokens = body.edges.map((edge) => edge.token);
    return this.rpc.send('fillet_edges', { edgeTokens, radius, operation });
  };

  public getBodyInfo = (
    params: GetBodyInfoParams,
  ): Promise<GetBodyInfoResult> => this.rpc.send('get_body_info', params);

  public applyMaterial = (
    params: ApplyMaterialParams,
  ): Promise<ApplyMaterialResult> => this.rpc.send('apply_material', params);

  public listMaterials = (): Promise<ListMaterialsResult> =>
    this.rpc.send('list_materials');
}
