import z from 'zod';

export const DrawRectangleSchema = z.object({
  width: z.number().describe('Width in millimeters'),
  height: z.number().describe('Height in millimeters'),
  centerX: z.number().optional().describe('X coordinate in millimeters'),
  centerY: z.number().optional().describe('Y coordinate in millimeters'),
  centerZ: z.number().optional().describe('Z coordinate in millimeters'),
});

export type DrawRectangleParams = z.infer<typeof DrawRectangleSchema>;

export const DrawCircleSchema = z.object({
  radius: z.number().describe('Radius in millimeters'),
  centerX: z.number().optional().describe('X coordinate in millimeters'),
  centerY: z.number().optional().describe('Y coordinate in millimeters'),
  centerZ: z.number().optional().describe('Z coordinate in millimeters'),
});

export type DrawCircleParams = z.infer<typeof DrawCircleSchema>;

const OperationSchema = z.enum([
  'NewBodyFeatureOperation',
  'JoinFeatureOperation',
  'CutFeatureOperation',
  'IntersectFeatureOperation',
]);

export type Operation = z.infer<typeof OperationSchema>;

export const ExtrudeSchema = z.object({
  profileToken: z
    .string()
    .describe('The entity token of the profile to extrude'),
  distance: z.number().describe('Extrusion distance in millimeters'),
  operation: OperationSchema.optional().describe('Type of operation'),
});

export type ExtrudeParams = z.infer<typeof ExtrudeSchema>;

export const FilletEdgesSchema = z.object({
  bodyToken: z.string().describe('The entity token of the body to fillet'),
  radius: z.number().describe('Radius in millimeters'),
  operation: OperationSchema.optional().describe('Type of operation'),
});

export type FilletEdgesParams = z.infer<typeof FilletEdgesSchema>;

export const GetBodyInfoSchema = z.object({
  bodyToken: z
    .string()
    .describe('The entity token of the body to get info about'),
});

export type GetBodyInfoParams = z.infer<typeof GetBodyInfoSchema>;

export const ApplyMaterialSchema = z.object({
  faceToken: z
    .string()
    .describe('The entity token of the face to apply material to'),
  materialName: z
    .string()
    .describe('The name of the material/appearance to apply'),
});

export type ApplyMaterialParams = z.infer<typeof ApplyMaterialSchema>;
