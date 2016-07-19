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

# <pep8-80 compliant>

# Export wrappers and integration with external tools.

import bpy
import mdtraj as md
from mdtraj.core.element import *

def createMeshForPositions (positions, element):
    atom_vertices = [];
    for position in positions:
        atom_vertices.append(position);

    atomMesh = bpy.data.meshes.new("Mesh_" + element.symbol);
    atomMesh.from_pydata(atom_vertices, [], []);
    atomMesh.update();

    mesh = bpy.data.objects.new(element.name, atomMesh);
    mesh.dupli_type = 'VERTS'
    return mesh;

def insert_keyframe(fcurves, frame, positions):
    for fcu, val in zip(fcurves, positions):
        fcu.keyframe_points.insert(frame, val, {'FAST'})

def addKeyframesToMeshFromPositions (mesh, frames) :
    action = bpy.data.actions.new("MeshAnimation");

    mesh.animation_data_create();
    mesh.animation_data.action = action;

    data_path = "vertices[%d].co"

    for v in mesh.vertices:
        fcurves = [action.fcurves.new(data_path % v.index, i) for i in range(3)]
        for frameIndex, frame in enumerate(frames):
            insert_keyframe(fcurves, frameIndex, frame[v.index]);

def getMaterialForElement (element):
    return bpy.data.materials[element.name];

def getAtomRepresentation (element):

    bpy.ops.surface.primitive_nurbs_surface_sphere_add(
        view_align=False, enter_editmode=False,
        location=(0,0,0), rotation=(0.0, 0.0, 0.0))

    ball = bpy.context.scene.objects.active

    ball.scale  = (element.radius,) * 3

    ball.name = "Ball_" + element.name
    ball.active_material = getMaterialForElement(element);
    
    return ball;

def addObjectsToGroup (objectNames, groupName):
    bpy.ops.object.select_all(action = 'DESELECT')  
    for name in objectNames:
        bpy.data.objects[name].select = True

    bpy.ops.group.create(name = groupName)
    
def createRepresentationForBlender(subsetTrajectory, element, createdObjects):
    print('Operate on element %s.' % element.name);
    indices = subsetTrajectory.topology.select('element %s' % element.symbol);
    positions = subsetTrajectory.atom_slice(indices).xyz;

    meshObject = createMeshForPositions(positions[0], element);
    bpy.context.scene.objects.link(meshObject)
    ball = getAtomRepresentation(element);
    ball.parent = meshObject

    addKeyframesToMeshFromPositions(meshObject.data, positions[1:]);
    createdObjects.append(meshObject.name);

def getPreparedTrajectoryFromFiles(trajFile, topolFile, subsetString, smooth):
    print('Loading trajectory from %s with topology %s.' % (trajFile, topolFile));
    subsetTrajectory = md.load_xtc(trajFile, top = topolFile);

    if subsetString:
        print('Create subset.');
        subsetIndices = subsetTrajectory.topology.select(subsetString);
        subsetTrajectory = subsetTrajectory.atom_slice(subsetIndices);

    print('Center trajectory');
    subsetTrajectory.center_coordinates();

    if smooth:
        print('Smoothen trajectory.');
        subsetTrajectory.smooth(2, inplace=True);

    return subsetTrajectory;

def import_trajectory (context):
    scene = context.scene
    import_md_trajectory = scene.import_md_trajectory
    trajFile = bpy.path.abspath(import_md_trajectory.trajFile)
    topolFile = bpy.path.abspath(import_md_trajectory.topolFile)
    subsetSelectionString = import_md_trajectory.subsetSelectionString
    smoothTrajectory = import_md_trajectory.smoothTrajectory
    timeFactorPerFrame = import_md_trajectory.timeFactorPerFrame

    subsetTrajectory = getPreparedTrajectoryFromFiles(trajFile, topolFile, subsetSelectionString, smoothTrajectory);

    elements = [
            hydrogen,
            carbon,
            oxygen,
            nitrogen
    ];

    createdObjects = [];
    for element in elements:
        createRepresentationForBlender(subsetTrajectory, element, createdObjects);

    addObjectsToGroup (createdObjects, 'My trajectory');
