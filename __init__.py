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

bl_info = {
    "name": "Import MD Trajectory",
    "category": "Mesh",
    "description": "Loading MD trajectories from files that are supported by mdtraj",
    "author": "Sebastian Breuers",
    "version": (1, 0),
    "blender": (2, 60, 0),
    "location": "3D View -> Toolbox",
    "warning": ""
}

if "bpy" in locals():
    import importlib
    importlib.reload(ui)
    importlib.reload(operators)
else:
    import bpy
    from bpy.props import (
            StringProperty,
            BoolProperty,
            IntProperty,
            PointerProperty,
            )

    from bpy.types import (
            Operator,
            AddonPreferences,
            PropertyGroup,
            )

    from bpy.utils import (
            register_class,
            unregister_class
            )

    from . import (
            ui,
            operators,
            )

import math

class ImportMDSettings(PropertyGroup):
    trajExt = ''.join([
            "*.xtc, *.pdb.gz, *.hoomdxml, *.restrt, *.h5, *.lammpstrj, *.xml",
            ", *.inpcrd, *.mdcrd, *.xyz.gz, *.stk, *.xyz, *.crd, *.lh5, *.dtr, *.nc",
            ", *.hdf5, *.pdb, *.dcd, *.rst7, *.mol2, *.netcdf, *.trr, *.gro, *.ncdf",
            ", *.ncrst, *.binpos, *.arc"
            ])
    trajFile = StringProperty(
            name="Trajectory file",
            description="Trajectory to be loaded",
            default="//",
            subtype='FILE_PATH'
            )

    topolExt = "*.pdb, *.pdb.gz, *.h5, *.lh5, *.prmtop, *.parm7, *.psf, *.mol2, *.hoomdxml, *.gro, *.arc, *.hdf5"
    topolFile = StringProperty(
            name="Topology file",
            description="Topology suitable for the trajectory",
            default="//",
            subtype='FILE_PATH'
            )
    subsetSelectionString = StringProperty(
            name="Subset",
            description="Subset of trajectory to be loaded",
            default='protein'
            )

    smoothTrajectory = IntProperty(
        name = "Smoothen trajectory",
        default=10,
        description = "Interpolate trajectory to avoid high frequency movements",
        )

    cyclicTrajectory = BoolProperty(
            name = "Make cyclic",
            default = True,
            description = "Make the imported trajectory cyclic"
            )

    timeFactorPerFrame = IntProperty(
        name = "Time",
        default=1,
        min=1,
        description = "Time distance between frames"
        )

    groupName = StringProperty(
            name = "Group name",
            default = "MD Trajectory",
            description = "The name that should be assigned to the created group"
            )


classes = (
    ui.ImportMDTrajectoryToolBarObject,
    operators.MDTrajectoryImport,
    ImportMDSettings,
    )
def register():
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.import_md_trajectory = PointerProperty(type=ImportMDSettings)


def unregister():
    for cls in classes:
        unregister_class(cls)

    del bpy.types.Scene.import_md_trajectory
