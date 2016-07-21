# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
#
import bpy

import mdtraj as md
from mdtraj.core.element import *

class MDTrajectoryImporter: 
    defaultColor = (0.080, 0.005, 0.182, 1);
    colorMap = {
            'hydrogen': (1, 1, 1, 1),
            'nitrogen': (0.026, 0.322, 0.8, 1),
            'carbon': (0.337, 0.378, 0.387, 1),
            'oxygen': (0.8, 0.006, 0.037, 1),
            'sulfur': (0.8, 0.006, 0.037, 1),
            }

    elements = [Element.getByAtomicNumber(i) for i in range(116)]

    def __init__ (self,
            context = bpy.context,
            trajFile = '',
            topolFile = '',
            subsetSelectionString = '',
            smoothTrajectory = True,
            timeFactorPerFrame = 1):
        self.context = context;
        self.trajFile = trajFile;
        self.topolFile = topolFile;
        self.subsetSelectionString = subsetSelectionString;
        self.smoothTrajectory = smoothTrajectory;
        self.timeFactorPerFrame = timeFactorPerFrame;

    def createMeshForPositions (self, positions, element):
        atom_vertices = [];
        for position in positions:
            atom_vertices.append(position);

        atomMesh = bpy.data.meshes.new("Mesh_" + element.symbol);
        atomMesh.from_pydata(atom_vertices, [], []);
        atomMesh.update();

        mesh = bpy.data.objects.new(element.name, atomMesh);
        mesh.dupli_type = 'VERTS'
        return mesh;

    def insert_keyframe (self, fcurves, frame, positions):
        for fcu, val in zip(fcurves, positions):
            fcu.keyframe_points.insert(frame, val, {'FAST'})

    def addKeyframesToMeshFromPositions (self, mesh, frames) :
        action = bpy.data.actions.new("MeshAnimation");

        mesh.animation_data_create();
        mesh.animation_data.action = action;

        data_path = "vertices[%d].co"

        for v in mesh.vertices:
            fcurves = [action.fcurves.new(data_path % v.index, i) for i in range(3)]
            for frameIndex, frame in enumerate(frames):
                self.insert_keyframe(fcurves, frameIndex, frame[v.index]);

    def assignValuesToMaterial (self, material, properties):
        for inputType, value in properties.items():
            material.inputs[inputType].default_value = value

    def createMaterialForElement (self, element):
        material = bpy.data.materials.new(name=element.name)
        material.use_nodes = True

        # Remove default
        nodes = material.node_tree.nodes;
        nodes.remove(nodes.get('Diffuse BSDF'))

        # Create base color
        material_baseColor = nodes.new('ShaderNodeBsdfToon')
        self.assignValuesToMaterial(material_baseColor, {
            'Color': self.colorMap.get(element.name, self.defaultColor),
            'Size': 0.7,
            'Smooth': 0.2
            })

        # Create rim color
        material_rim = nodes.new('ShaderNodeBsdfToon')
        self.assignValuesToMaterial(material_rim, {
            'Color': (0, 0, 0, 1),
            'Size': 0.7,
            'Smooth': 0.2
            })

        # Create rim positioner
        material_fresnel = nodes.new('ShaderNodeFresnel')
        self.assignValuesToMaterial(material_fresnel, {
            'IOR': 0.9
            })

        # Create mix node
        material_mix = nodes.new('ShaderNodeMixShader')

        # Bring them together
        material_output = nodes.get('Material Output')
        links = material.node_tree.links
        links.new(material_output.inputs['Surface'], material_mix.outputs['Shader'])
        links.new(material_mix.inputs[0], material_fresnel.outputs['Fac'])
        links.new(material_mix.inputs[1], material_baseColor.outputs['BSDF'])
        links.new(material_mix.inputs[2], material_rim.outputs['BSDF'])

        return material;


    def getMaterialForElement (self, element):
        material = bpy.data.materials.get(element.name);
        if not material:
            material = self.createMaterialForElement(element)

        return material;

    def getAtomRepresentation (self, element):

        bpy.ops.surface.primitive_nurbs_surface_sphere_add(
            view_align=False, enter_editmode=False,
            location=(0,0,0), rotation=(0.0, 0.0, 0.0))

        ball = self.context.scene.objects.active

        ball.scale  = (element.radius,) * 3

        ball.name = "Ball_" + element.name
        ball.active_material = self.getMaterialForElement(element);

        return ball;

    def addObjectsToGroup (self, objectNames, groupName):
        bpy.ops.object.select_all(action = 'DESELECT')
        for name in objectNames:
            obj = bpy.data.objects[name]
            for child in obj.children:
                if child.parent == obj:
                    child.select = True
            obj.select = True

        print('Making animation curves cyclic');
        for window in self.context.window_manager.windows:
            screen = window.screen

            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    area.type = 'GRAPH_EDITOR'
                    override = {'window': window, 'screen': screen, 'area': area}
                    bpy.ops.graph.extrapolation_type(override, type = 'MAKE_CYCLIC')
                    area.type = 'VIEW_3D'
                    break

        bpy.ops.group.create(name = groupName)

    def createRepresentationForBlender (self, subsetTrajectory, element, createdObjects):
        print('Operate on element %s.' % element.name);
        indices = subsetTrajectory.topology.select('element %s' % element.symbol);
        if len(indices) != 0:
            positions = subsetTrajectory.atom_slice(indices).xyz;

            meshObject = self.createMeshForPositions(positions[0], element);
            self.context.scene.objects.link(meshObject)
            ball = self.getAtomRepresentation(element);
            ball.parent = meshObject

            self.addKeyframesToMeshFromPositions(meshObject.data, positions[1:]);
            createdObjects.append(meshObject.name);

    def getPreparedTrajectoryFromFiles (self, trajFile, topolFile, subsetString, smoothen):
        print('Loading trajectory from %s with topology %s.' % (trajFile, topolFile));
        subsetTrajectory = md.load(trajFile, top = topolFile);

        if subsetString:
            print('Create subset.');
            subsetIndices = subsetTrajectory.topology.select(subsetString);
            subsetTrajectory = subsetTrajectory.atom_slice(subsetIndices);

        print('Center trajectory');
        subsetTrajectory.center_coordinates();

        if smoothen:
            print('Smoothen trajectory.');
            subsetTrajectory.smooth(4, inplace=True);

        return subsetTrajectory;

    def import_trajectory (self):
        print('Nnew')
        subsetTrajectory = self.getPreparedTrajectoryFromFiles(
                self.trajFile,
                self.topolFile,
                self.subsetSelectionString,
                self.smoothTrajectory
                );

        createdObjects = [];
        for element in self.elements:
            self.createRepresentationForBlender(subsetTrajectory, element, createdObjects);

        self.addObjectsToGroup (createdObjects, 'My trajectory');
