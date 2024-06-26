bl_info = {
    "name": "Bakkes Cinematics Buddy Loader",
    "description": "Loads exported animation from the Bakkes mod pluggin Cinematics Buddy",
    "author": "GO_AWAY_77",
    "version": (0, 1),
    "blender": (4, 0, 0),
    "location": "View3D > UI > Tools",
    "warning": "Only imports camera and ball animations so far, and only works with 60 FPS.", # used for warning icon and text in addons panel
    "support": "COMMUNITY",
    "category": "Import-Export",
}

import bpy
from .blenderOperator import *

# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------
    
classes = (
    FileLoaderProperty,
    OBJECT_PT_BakkesCinBuddy_panel,
    OBJECT_OT_BakkesCinBuddy_load_file
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.BakkesCinematicBuddyFileSelector = bpy.props.PointerProperty(type=FileLoaderProperty)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.BakkesCinematicBuddyFileSelector


if __name__ == "__main__":
    register()