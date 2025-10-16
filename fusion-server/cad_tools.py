import adsk.core, adsk.fusion
from typing import Any, Dict

class CADTools:
    
    def __init__(self, app: adsk.core.Application):
        self.app = app
    
    def _mm_to_cm(self, mm: float) -> float:
        return mm / 10.0
    
    def _design(self) -> adsk.fusion.Design:
        d = adsk.fusion.Design.cast(self.app.activeProduct)
        if not d:
            raise RuntimeError("No active Fusion design open")
        return d
    
    def draw_rectangle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        width_mm = params["width"]
        height_mm = params["height"]
        center_x_mm = params.get("centerX", 0)
        center_y_mm = params.get("centerY", 0)
        center_z_mm = params.get("centerZ", 0)

        width_cm = self._mm_to_cm(width_mm)
        height_cm = self._mm_to_cm(height_mm)
        center_x_cm = self._mm_to_cm(center_x_mm)
        center_y_cm = self._mm_to_cm(center_y_mm)
        center_z_cm = self._mm_to_cm(center_z_mm)
        
        design = self._design()
        root = design.rootComponent
        
        plane = root.xYConstructionPlane
        
        sketch = root.sketches.add(plane)
        
        half_w = width_cm / 2.0
        half_h = height_cm / 2.0
        center = adsk.core.Point3D.create(center_x_cm, center_y_cm, center_z_cm)
        corner = adsk.core.Point3D.create(center_x_cm + half_w, center_y_cm + half_h, center_z_cm)
        sketch.sketchCurves.sketchLines.addCenterPointRectangle(center, corner)
        
        sketch_index = root.sketches.count - 1
        sketch_token = sketch.entityToken
        
        profile_token = None
        if sketch.profiles.count > 0:
            profile_token = sketch.profiles.item(0).entityToken
        
        return {
            "sketch": {"index": sketch_index, "token": sketch_token},
            "profile": {"token": profile_token} if profile_token else None
        }

    def extrude(self, params: Dict[str, Any]) -> Dict[str, Any]:
        profile_token = params["profileToken"]
        distance_mm = params["distance"]
        operation_name = params.get("operation", "NewBodyFeatureOperation")
        
        distance_cm = self._mm_to_cm(distance_mm)
        
        design = self._design()
        root = design.rootComponent
        
        profile = design.findEntityByToken(profile_token)[0]
        
        operation = self._OPERATION_MAP.get(operation_name, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        extrudes = root.features.extrudeFeatures
        extrude_input = extrudes.createInput(profile, operation)
        
        distance_value = adsk.core.ValueInput.createByReal(distance_cm)
        extrude_input.setDistanceExtent(False, distance_value)
        
        extrude = extrudes.add(extrude_input)
        
        body_token = None
        if operation == adsk.fusion.FeatureOperations.NewBodyFeatureOperation and extrude.bodies.count > 0:
            body_token = extrude.bodies.item(0).entityToken
        
        return {
            "token": extrude.entityToken,
            "body": {"token": body_token} if body_token else None
        }

    def draw_circle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        radius_mm = params["radius"]
        center_x_mm = params.get("centerX", 0)
        center_y_mm = params.get("centerY", 0)
        center_z_mm = params.get("centerZ", 0)
        
        radius_cm = self._mm_to_cm(radius_mm)
        center_x_cm = self._mm_to_cm(center_x_mm)
        center_y_cm = self._mm_to_cm(center_y_mm)
        center_z_cm = self._mm_to_cm(center_z_mm)
        
        design = self._design()
        root = design.rootComponent
        
        plane = root.xYConstructionPlane
        
        sketch = root.sketches.add(plane)
        
        center = adsk.core.Point3D.create(center_x_cm, center_y_cm, center_z_cm)
        sketch.sketchCurves.sketchCircles.addByCenterRadius(center, radius_cm)
        
        sketch_index = root.sketches.count - 1
        sketch_token = sketch.entityToken
        
        profile_token = None
        if sketch.profiles.count > 0:
            profile_token = sketch.profiles.item(0).entityToken
        
        return {
            "sketch": {"index": sketch_index, "token": sketch_token},
            "profile": {"token": profile_token} if profile_token else None
        }

    def list_sketches(self, _params: Dict[str, Any]) -> Dict[str, Any]:
        design = self._design()
        root = design.rootComponent
        
        sketches = [
            {
                "index": i,
                "name": sketch.name,
                "token": sketch.entityToken,
                "profileCount": sketch.profiles.count
            }
            for i in range(root.sketches.count)
            for sketch in [root.sketches.item(i)]
        ]
        
        return {"sketches": sketches}

    def fillet_edges(self, params: Dict[str, Any]) -> Dict[str, Any]:
        edge_tokens = params["edgeTokens"]
        radius_mm = params["radius"]
        operation_name = params.get("operation", "NewBodyFeatureOperation")
        
        radius_cm = self._mm_to_cm(radius_mm)
        
        design = self._design()
        root = design.rootComponent
        
        edges = [design.findEntityByToken(token)[0] for token in edge_tokens]
        
        if not edges:
            raise ValueError("No valid edges found from provided tokens")
        
        fillets = root.features.filletFeatures
        fillet_input = fillets.createInput()
        
        edge_collection = adsk.core.ObjectCollection.create()
        for edge in edges:
            edge_collection.add(edge)
        
        fillet_input.edgeSetInputs.addConstantRadiusEdgeSet(edge_collection, adsk.core.ValueInput.createByReal(radius_cm), False)
        
        fillet_input.operation = self._OPERATION_MAP.get(operation_name, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        fillet = fillets.add(fillet_input)
        
        return {
            "token": fillet.entityToken,
            "edgeCount": len(edges)
        }

    def get_body_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        body_token = params["bodyToken"]
        
        design = self._design()
        
        entity = design.findEntityByToken(body_token)

        body = entity[0]
        
        body_info = {
            "token": body.entityToken,
            "name": body.name,
            "isSolid": body.isSolid,
            "isVisible": body.isVisible
        }
        
        edges = [
            {
                "token": edge.entityToken,
                "length": edge.length,
                "startVertex": {
                    "token": edge.startVertex.entityToken,
                    "x": edge.startVertex.geometry.x,
                    "y": edge.startVertex.geometry.y,
                    "z": edge.startVertex.geometry.z
                },
                "endVertex": {
                    "token": edge.endVertex.entityToken,
                    "x": edge.endVertex.geometry.x,
                    "y": edge.endVertex.geometry.y,
                    "z": edge.endVertex.geometry.z
                }
            }
            for i in range(body.edges.count)
            for edge in [body.edges.item(i)]
        ]
        
        faces = [
            {
                "token": face.entityToken,
                "area": face.area,
            }
            for i in range(body.faces.count)
            for face in [body.faces.item(i)]
        ]
        
        vertices = [
            {
                "token": vertex.entityToken,
                "x": vertex.geometry.x,
                "y": vertex.geometry.y,
                "z": vertex.geometry.z
            }
            for i in range(body.vertices.count)
            for vertex in [body.vertices.item(i)]
        ]
        
        return {
            "body": body_info,
            "edges": edges,
            "faces": faces,
            "vertices": vertices
        }

    def apply_material(self, params: Dict[str, Any]) -> Dict[str, Any]:
        face_token = params["faceToken"]
        material_name = params["materialName"]
        
        design = self._design()
        
        face = design.findEntityByToken(face_token)[0]
        
        material_lib = self.app.materialLibraries.itemByName("Fusion Appearance Library")
        if not material_lib:
            raise RuntimeError("Fusion Appearance Library not found")
        
        appearance = None
        for i in range(material_lib.appearances.count):
            app = material_lib.appearances.item(i)
            if app.name == material_name:
                appearance = app
                break
        
        if not appearance:
            raise ValueError(f"Material '{material_name}' not found in library")
        
        face.appearance = appearance
        
        return {
            "faceToken": face_token,
            "materialName": material_name,
            "applied": True
        }

    def list_materials(self, _params: Dict[str, Any]) -> Dict[str, Any]:
        material_lib = self.app.materialLibraries.itemByName("Fusion Appearance Library")
        if not material_lib:
            raise RuntimeError("Fusion Appearance Library not found")
        
        materials = []
        for i in range(material_lib.appearances.count):
            app = material_lib.appearances.item(i)
            materials.append({
                "name": app.name,
                "id": app.id
            })
        
        return {
            "materials": materials,
            "count": len(materials)
        }

    _OPERATION_MAP: Dict[str, adsk.fusion.FeatureOperations] = {
        "NewBodyFeatureOperation": adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        "JoinFeatureOperation": adsk.fusion.FeatureOperations.JoinFeatureOperation,
        "CutFeatureOperation": adsk.fusion.FeatureOperations.CutFeatureOperation,
        "IntersectFeatureOperation": adsk.fusion.FeatureOperations.IntersectFeatureOperation,
    }
