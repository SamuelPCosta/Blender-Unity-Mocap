import bpy
import json
import os
import time
import hashlib
from math import radians
from mathutils import Quaternion

json_file_path = r"C:\Users\Samur\AppData\LocalLow\DefaultCompany\VuforiaMocap\transformData.json"
# json_file_path = ""

last_hash = None
transform_data = {}
start = False
lastState = False
lastFrame = -1
INTERVAL = 5
INTERVAL_PREV = 2
msg = ""
strPath = ""
FPS = 1/24

def getEnd():
    global start, lastState, msg 
    if not start and lastState:
        print("Animation finished")
        msg = "capturing images..."
        bpy.ops.screen.animation_play() 
        
        return None
    return FPS

def startCapturing():
    global start, lastState, msg, lastFrame
    if start and not lastState:
        print("capturing images...")
        bpy.ops.screen.animation_play() 
        bpy.context.scene.frame_set(1)
        bpy.ops.screen.animation_play() 
        msg = "capturing images..."
        lastState = True
        lastFrame = -1
        bpy.app.timers.register(getEnd)
        return None
    return FPS

def startReading():
    global last_hash, transform_data, start, lastFrame, INTERVAL, INTERVAL_PREV, msg, lastState
    msg = "waiting for unity"
    print("Start")
    start = False
    bpy.app.timers.register(startCapturing)
    return None

def update_bones(scene, depsgraph):
    global last_hash, transform_data, start, lastFrame, INTERVAL, INTERVAL_PREV, msg, lastState, json_file_path
    current_hash = compute_file_hash(json_file_path)

    if current_hash != last_hash:
        transform_data = load_json_file()
        last_hash = current_hash
        start = transform_data.get("start")
        
    rig = bpy.data.objects.get("rig")
    if rig and rig.type == 'ARMATURE':
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.mode_set(mode='POSE')

        current_frame = bpy.context.scene.frame_current
        
        for bone_data in transform_data.get("bones", []):
            bone = rig.pose.bones.get(bone_data["name"])
            if bone and (current_frame % INTERVAL_PREV == 0 or current_frame % INTERVAL == 0):
                location = bone_data["Location"]
                bone.location = (
                    round(location["x"], 2),
                    round(location["y"], 2),
                    round(location["z"], 2)
                )

                rotation = bone_data["Rotation"]
                bone.rotation_quaternion = Quaternion((
                    round(rotation["w"], 2),
                    round(rotation["x"], 2),
                    round(rotation["y"], 2),
                    round(rotation["z"], 2)
                ))
                
                if current_frame >= lastFrame + INTERVAL:
                    bone.keyframe_insert(data_path="location", frame=current_frame, group=bone_data["name"])
                    bone.keyframe_insert(data_path="rotation_quaternion", frame=current_frame, group=bone_data["name"])
                    if bone_data == transform_data.get("bones", [])[-1]:
                        lastFrame = current_frame
                    

def compute_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def load_json_file():
    try:
        with open(json_file_path, 'r') as json_file:
            return json.load(json_file)
    except Exception as e:
        print(f"Error opening JSON: {e}")
        return {}

def mainMocap():
    global lastFrame
    bpy.context.scene.frame_set(1)
    if not bpy.context.screen.is_animation_playing:
        bpy.ops.screen.animation_play() 
    lastFrame = -1
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(update_bones)
    bpy.app.timers.register(startReading)

########################### PANEL ##############################

oldState = False
counter = 0
enable = True
timer = None

bl_info = {
    "name": "Mocap Vuforia 1.0.0",
    "blender": (2, 82, 0),
    "category": "Mocap Vuforia",
}

bl_info = {
    "name": "Mocap Vuforia",
    "description": "Single line explaining what this script exactly does.",
    "author": "Sam Costa",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Mocap Vuforia",
    "support": "COMMUNITY",
    "category": "Mocap Vuforia",
}

class Panel(bpy.types.Panel):
    bl_label = "Mocap Vuforia 1.0.0"
    bl_idname = "OBJECT_PT_Mocap_Vuforia"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mocap Vuforia'
    
    def redraw(self):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return None
        
    def draw(self, context):
        global msg, enable
        
        layout = self.layout
        
        row = layout.row()
        row.label(text="INSTRUCTIONS", icon='INFO')
        row = layout.row()
        row.label(text="1 - Select the json file")
        row = layout.row()
        row.label(text="      (Coming soon)")
        row = layout.row()
        row.label(text="2 - Press Start")
        row = layout.row()
        row.label(text="3 - Open the unity project")
        row = layout.row()
        row.label(text="4 - Raise your right hand")
        row = layout.row()
        row.label(text="5 - And then stand in A-Pose")
        row = layout.row()
        row.label(text="(Or T-pose depending on the model)")

#        # Bar for JSON file path display
#        row = layout.row()
#        row.prop(context.scene, "json_file_path", text="")
#        
#        # Button to browse the file
#        row = layout.row()
#        row.operator("object.file_browser", text="Browse JSON File")

        row = layout.row()
        row.operator("object.starter")
        row.enabled = enable
        
        row = layout.row()
        row.operator("object.restart_operator")
        
        row = layout.row()
        if oldState and not start:
            msg = "animation finished" 
            
        row.label(text="Status: " + msg, icon='REC')
        
        
class RestartOperator(bpy.types.Operator):
    bl_idname = "object.restart_operator"
    bl_label = "Stop / Restart"
    bl_description = "Restart the mocap process"

    def execute(self, context):
        global last_hash, transform_data, start, lastState, lastFrame, msg, enable
        last_hash = None
        transform_data = {}
        start = False
        lastState = False
        lastFrame = -1
        enable = True 
        msg = "restarted and ready!"
        
        bpy.app.handlers.frame_change_pre.clear()
         
        if bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_play() 
        bpy.context.scene.frame_set(1)
        
        rig = bpy.data.objects.get("rig")
        if rig and rig.type == 'ARMATURE':
            bpy.context.view_layer.objects.active = rig
            bpy.ops.object.mode_set(mode='POSE')

            for bone in rig.pose.bones:
                bone.location = (0.0, 0.0, 0.0)
                bone.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)

            bpy.ops.object.mode_set(mode='OBJECT')
        
        return {'FINISHED'}


class OBJECT_OT_FileBrowser(bpy.types.Operator):
    global json_file_path
    bl_idname = "object.file_browser"
    bl_label = "Browse File"
     
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    
    def execute(self, context):
        global json_file_path
        json_file_path = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class Starter(bpy.types.Operator):
    bl_idname = "object.starter"
    bl_label = "Start"
    bl_description = "Start the mocap process"
    
    def execute(self, context):
        global msg, enable
        if json_file_path != "" and json_file_path.endswith(".json"):
            self.report({'INFO'}, "Waiting for unity")
            enable = False
            mainMocap()
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Invalid File")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(Panel)
    bpy.utils.register_class(OBJECT_OT_FileBrowser)
    bpy.utils.register_class(Starter)
    bpy.utils.register_class(RestartOperator)

    bpy.types.Scene.json_file_path = bpy.props.StringProperty(name="JSON File Path", default=json_file_path)

def unregister():
    bpy.utils.unregister_class(Panel)
    bpy.utils.unregister_class(OBJECT_OT_FileBrowser)
    bpy.utils.unregister_class(Starter)
    bpy.utils.unregister_class(RestartOperator)

    del bpy.types.Scene.json_file_path

if __name__ == "__main__":
    register()