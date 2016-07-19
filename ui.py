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

# Interface for this addon.

import bmesh
from bpy.types import Panel

class ImportMDTrajectoryToolBar:
    bl_label = "Import Trajectory"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        scene = context.scene;
        import_md_trajectory = scene.import_md_trajectory

        layout = self.layout
        row = layout.row()
        row.label("File input")
        row = layout.row(align=True)
        row.prop(import_md_trajectory, "trajFile")
        row = layout.row(align=True)
        row.prop(import_md_trajectory, "topolFile")
        # Balls
        box = layout.box()
        row = box.row()
        row.label(text="Options")
        row = box.row()
        row.prop(import_md_trajectory, "subsetSelectionString")
        row = box.row()
        row.prop(import_md_trajectory, "smoothTrajectory")
        row = box.row()
        row.prop(import_md_trajectory, "timeFactorPerFrame")

        row = layout.row(align=True)
        row.operator("mesh.mdtraj_import", text="Import", icon='IMPORT')

class ImportMDTrajectoryToolBarObject(Panel, ImportMDTrajectoryToolBar):
    bl_category = "Import Trajectory"
    bl_idname = "MESH_PT_importmdtraj_object"
    bl_context = "objectmode"
