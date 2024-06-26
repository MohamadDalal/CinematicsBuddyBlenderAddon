import bpy
import addon_utils
from pathlib import Path
from math import pi, tan
from .parseFile import readCinematicsBuddyFile

# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

# Source: https://blender.stackexchange.com/a/26906
class FileLoaderProperty(bpy.types.PropertyGroup):

    path: bpy.props.StringProperty(
        name="Cinematics Buddy File Path",
        description="Path to animation file",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')
        
class OBJECT_OT_BakkesCinBuddy_load_file(bpy.types.Operator):
    bl_idname = "object.bakkescinbuddy_load_file"
    bl_label = "Execute"
    bl_options = {'REGISTER', 'UNDO'}
        
    
    def execute(self, context):
        print("Execute")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        file_path = context.scene.BakkesCinematicBuddyFileSelector.path
        for mod in addon_utils.modules():
            if mod.bl_info.get("name") == "Bakkes Cinematics Buddy Loader":
                print(mod.bl_info.get("name"))
                addon_path = Path(mod.__file__).parent
        try:
            recordingMetadata, frames = readCinematicsBuddyFile(file_path)
            print(recordingMetadata)
            print("Number of loaded frames: ", frames.__len__())
            # TODO: I think I need to make this into a proper plugin in order to not need absolute paths
            stadiumObj = bpy.data.objects.get("RL_STADIUM_PROXY", None)
            ballObj = bpy.data.objects.get("RL_BALL_PROXY", None)
            if stadiumObj is None:
                stadiumScene = bpy.ops.import_scene.fbx( filepath = str(addon_path / "models/StadiumProxy.FBX"))
                stadiumObj = bpy.data.objects["RL_STADIUM_PROXY"]
            if ballObj is None:
                ballScene = bpy.ops.import_scene.fbx( filepath =  str(addon_path / "models/BallProxy.FBX"))
                ballObj = bpy.data.objects["RL_BALL_PROXY"]
                ballObj.rotation_mode = 'QUATERNION'
            # Source: https://www.youtube.com/watch?v=uDtEkjbD_-g&ab_channel=CGPython and Copilot
            cameraObj = bpy.data.objects.get(recordingMetadata.cameraName, None)
            if cameraObj is not None:
                cameraObj.name = "Old_"+cameraObj.name
            bpy.context.scene.frame_end = max(bpy.context.scene.frame_end, recordingMetadata.numFrames)
            bpy.ops.object.camera_add()
            cameraObj = bpy.context.active_object
            cameraData = cameraObj.data
            cameraObj.rotation_mode = 'QUATERNION'
            cameraData.lens_unit = 'MILLIMETERS'
            cameraData.lens = frames[0]["CM"]["F"]
            cameraObj.name = recordingMetadata.cameraName
            for frame_num, frame in enumerate(frames):
                ballObj.location = frame["B"]["L"]
                ballObj.rotation_quaternion = frame["B"]["R"]
                ballObj.keyframe_insert(data_path="location", frame=frame_num)
                ballObj.keyframe_insert(data_path="rotation_quaternion", frame=frame_num)
                cameraObj.location = frame["CM"]["L"]
                cameraObj.rotation_mode = 'QUATERNION'
                cameraObj.rotation_quaternion = frame["CM"]["R"]
                cameraObj.rotation_mode = 'XYZ'
                cameraObj.rotation_euler[0] += pi/2
                cameraObj.rotation_euler[2] -= pi/2
                # Source https://www.reddit.com/r/blenderhelp/comments/c3u94n/how_to_keyframe_camera_fovfocal_length/
                cameraData.lens = (cameraData.sensor_width/2)/tan(frame["CM"]["F"]*pi/360)
                cameraObj.keyframe_insert(data_path="location", frame=frame_num)
                cameraObj.keyframe_insert(data_path="rotation_euler", frame=frame_num)
                cameraData.keyframe_insert(data_path="lens", frame=frame_num)
            return {'FINISHED'}
        except Exception as e:
            #raise(e)
            print("Failed to open file")
            return {'CANCELLED'}
    


# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class OBJECT_PT_BakkesCinBuddy_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_bakkesCinBuddyPanel"
    bl_label = "Bakkes CinBuddy Loader"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Tools"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        col = layout.column(align=True)
        col.prop(scn.BakkesCinematicBuddyFileSelector, "path", text="File")
        col.operator("object.bakkescinbuddy_load_file", text="Load file")