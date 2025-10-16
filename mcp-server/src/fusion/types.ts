export type Point3D = {
  x: number;
  y: number;
  z: number;
};

export type EntityToken = {
  token: string;
};

export type SketchInfo = {
  index: number;
  token: string;
};

export type ProfileInfo = {
  token: string;
};

export type BodyInfo = {
  token: string;
};

export type Vertex = {
  token: string;
  x: number;
  y: number;
  z: number;
};

export type Edge = {
  token: string;
  length: number;
  startVertex: Vertex;
  endVertex: Vertex;
};

export type Face = {
  token: string;
  area: number;
  normal: Point3D;
};

export type BodyDetails = {
  token: string;
  name: string;
  volume: number;
  isSolid: boolean;
  isVisible: boolean;
};

export type DrawRectangleResult = {
  sketch: SketchInfo;
  profile: ProfileInfo | null;
};

export type DrawCircleResult = {
  sketch: SketchInfo;
  profile: ProfileInfo | null;
};

export type ExtrudeResult = {
  token: string;
  body: BodyInfo | null;
};

export type FilletEdgesResult = {
  token: string;
  edgeCount: number;
};

export type GetBodyInfoResult = {
  body: BodyDetails;
  edges: Edge[];
  faces: Face[];
  vertices: Vertex[];
};

export type ListSketchesResult = {
  sketches: {
    index: number;
    name: string;
    token: string;
    profileCount: number;
  }[];
};

export type ApplyMaterialResult = {
  faceToken: string;
  materialName: string;
  applied: boolean;
};

export type ListMaterialsResult = {
  materials: {
    name: string;
    id: string;
  }[];
  count: number;
};
