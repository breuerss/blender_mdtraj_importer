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

import bpy
from bpy.types import Operator
from importlib import reload
from . import exceptions
from . import importer
reload(importer)
reload(exceptions)
#
# ------
# Export

class MDTrajectoryImport(Operator):
    """Import MD Trajectory to scene"""
    bl_idname = "mesh.mdtraj_import"
    bl_label = "Import MD Trajectory"

    def execute(self, context):


        import_md_trajectory = context.scene.import_md_trajectory
        MDImporter = importer.MDTrajectoryImporter(context,
                bpy.path.abspath(import_md_trajectory.trajFile),
                bpy.path.abspath(import_md_trajectory.topolFile),
                import_md_trajectory.subsetSelectionString,
                import_md_trajectory.groupName,
                import_md_trajectory.smoothTrajectory,
                import_md_trajectory.cyclicTrajectory,
                import_md_trajectory.timeFactorPerFrame)

        try:
            MDImporter.import_trajectory()
        except exceptions.ErrorMessageException as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        #info = []
        #ret = export.write_mesh(context, info, self.report)
        #report.update(*info)

        #if ret:
        return {'FINISHED'}
        #else:
        #    return {'CANCELLED'}
