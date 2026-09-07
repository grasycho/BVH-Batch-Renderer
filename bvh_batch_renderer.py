import os
import sys
import time
import glob
import shutil
import threading
import subprocess
import tempfile
import customtkinter as ctk
from tkinter import filedialog, messagebox
import imageio.v2 as imageio

# Set up the modern dark UI theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MotionPreviewApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Motion Preview - Smooth Spline Batch Renderer")
        self.geometry("950x680")
        self.minsize(800, 500)

        self.files_to_render = []

        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_main_area()
        self._build_log_area()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

        self.logo = ctk.CTkLabel(self.sidebar, text="Motion Preview", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Resolution Dropdown
        self.lbl_res = ctk.CTkLabel(self.sidebar, text="Resolution:", anchor="w")
        self.lbl_res.grid(row=1, column=0, padx=20, pady=(15, 0), sticky="w")
        self.resolution_menu = ctk.CTkOptionMenu(
            self.sidebar, 
            values=["1920x1080", "1280x720", "800x800", "640x480", "512x512", "320x320", "256x256"]
        )
        self.resolution_menu.set("640x480")
        self.resolution_menu.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Speed Dropdown (Frame Step)
        self.lbl_speed = ctk.CTkLabel(self.sidebar, text="Render Speed (Frame Step):", anchor="w")
        self.lbl_speed.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.speed_menu = ctk.CTkOptionMenu(
            self.sidebar, 
            values=[
                "Max Speed (Render 1 in 5 frames)", 
                "Ultra Fast (Render 1 in 4 frames)", 
                "Draft (Render 1 in 3 frames)", 
                "Normal (Render 1 in 2 frames)", 
                "High Quality (Render All)"
            ]
        )
        self.speed_menu.set("Max Speed (Render 1 in 5 frames)")
        self.speed_menu.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Render Engine Dropdown
        self.lbl_engine = ctk.CTkLabel(self.sidebar, text="Render Engine:", anchor="w")
        self.lbl_engine.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.engine_menu = ctk.CTkOptionMenu(self.sidebar, values=["Workbench (Fast Solid)", "EEVEE (Shaded)"])
        self.engine_menu.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Start Button
        self.render_btn = ctk.CTkButton(self.sidebar, text="Start Batch Render", 
                                        command=self.start_render_thread, 
                                        fg_color="#1f6b29", hover_color="#144d1c", height=40)
        self.render_btn.grid(row=8, column=0, padx=20, pady=(20, 20), sticky="s")

    def _build_main_area(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=(10, 5))
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Toolbar
        self.top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        
        self.btn_add_files = ctk.CTkButton(self.top_bar, text="+ Add Files", command=self.add_files, width=100)
        self.btn_add_files.pack(side="left", padx=(0, 10))

        self.btn_add_folder = ctk.CTkButton(self.top_bar, text="+ Add Folder", command=self.add_folder, width=100)
        self.btn_add_folder.pack(side="left", padx=10)

        self.btn_clear = ctk.CTkButton(self.top_bar, text="Clear List", command=self.clear_list, 
                                       fg_color="#8c2727", hover_color="#5e1a1a", width=100)
        self.btn_clear.pack(side="right")

        self.file_listbox = ctk.CTkTextbox(self.main_frame, state="disabled")
        self.file_listbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    def _build_log_area(self):
        self.bottom_frame = ctk.CTkFrame(self, height=150)
        self.bottom_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=(5, 10))
        self.bottom_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(self.bottom_frame)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.progress_bar.set(0)

        self.log_box = ctk.CTkTextbox(self.bottom_frame, height=80, state="disabled", fg_color="#141414", text_color="#00ff66", font=("Consolas", 12))
        self.log_box.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

    # --- UI Interactions ---

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def update_file_list(self):
        self.file_listbox.configure(state="normal")
        self.file_listbox.delete("1.0", "end")
        for f in self.files_to_render:
            self.file_listbox.insert("end", f"{f}\n")
        self.file_listbox.configure(state="disabled")

    def add_files(self):
        files = filedialog.askopenfilenames(title="Select BVH Files", filetypes=[("BVH Files", "*.bvh")])
        for f in files:
            if f not in self.files_to_render:
                self.files_to_render.append(f)
        self.update_file_list()
        self.log(f"Added {len(files)} files.")

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder with BVH Files")
        if folder:
            count = 0
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith('.bvh'):
                        full_path = os.path.join(root, file)
                        if full_path not in self.files_to_render:
                            self.files_to_render.append(full_path)
                            count += 1
            self.update_file_list()
            self.log(f"Scanned folder, added {count} files.")

    def clear_list(self):
        self.files_to_render.clear()
        self.update_file_list()
        self.log("Queue cleared.")

    # --- Core Rendering Logic ---

    def generate_bpy_script(self, bvh_path, temp_dir, res_x, res_y, engine, frame_step):
        bvh_path = bvh_path.replace("\\", "/")
        temp_dir = temp_dir.replace("\\", "/")
        
        return f"""import bpy
import math
import sys

bpy.ops.wm.read_factory_settings(use_empty=True)

if bpy.data.worlds:
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (0.04, 0.04, 0.04, 1)

light_data = bpy.data.lights.new(name="Sun", type='SUN')
light_data.energy = 2.0
light_obj = bpy.data.objects.new(name="Sun", object_data=light_data)
light_obj.rotation_euler = (math.radians(45), math.radians(45), 0)
bpy.context.collection.objects.link(light_obj)

try:
    bpy.ops.import_anim.bvh(filepath="{bvh_path}", update_scene_fps=True, update_scene_duration=True)
except Exception as e:
    print("Error loading BVH:", e)
    sys.exit(1)

armature = next((obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE'), None)

if armature:
    bpy.context.view_layer.update()
    
    max_z = 0.1
    root_bone = None
    
    for bone in armature.pose.bones:
        if bone.parent is None:
            root_bone = bone
            
        head_z = (armature.matrix_world @ bone.head).z
        tail_z = (armature.matrix_world @ bone.tail).z
        max_z = max(max_z, head_z, tail_z)

    char_height = max_z
    cam_dist = char_height * 1.3 

    # --- GRID FLOOR ---
    bpy.ops.mesh.primitive_grid_add(size=char_height * 10, x_subdivisions=40, y_subdivisions=40)
    grid = bpy.context.active_object
    grid.location = (0, 0, 0)
    
    bpy.ops.object.modifier_add(type='WIREFRAME')
    grid.modifiers["Wireframe"].thickness = char_height * 0.002
    
    mat_grid = bpy.data.materials.new(name="GridMat")
    mat_grid.use_nodes = True
    bsdf_grid = mat_grid.node_tree.nodes.get("Principled BSDF")
    if bsdf_grid:
        bsdf_grid.inputs['Base Color'].default_value = (0.3, 0.3, 0.3, 1.0)
    grid.data.materials.append(mat_grid)

    # --- SPLINE & JOINT GEOMETRY ---
    mat_visuals = bpy.data.materials.new(name="VisualMat")
    mat_visuals.use_nodes = True
    bsdf_vis = mat_visuals.node_tree.nodes.get("Principled BSDF")
    if bsdf_vis:
        bsdf_vis.inputs['Base Color'].default_value = (0.85, 0.85, 0.85, 1.0)
        bsdf_vis.inputs['Roughness'].default_value = 0.4

    bpy.ops.mesh.primitive_uv_sphere_add(radius=char_height * 0.012)
    base_joint = bpy.context.active_object
    base_joint.data.materials.append(mat_visuals)

    bpy.ops.mesh.primitive_cylinder_add(radius=char_height * 0.003, depth=1)
    base_bone = bpy.context.active_object
    base_bone.data.materials.append(mat_visuals)

    for v in base_bone.data.vertices:
        orig_y = v.co.y
        orig_z = v.co.z
        v.co.y = orig_z + 0.5 
        v.co.z = -orig_y      

    for bone in armature.pose.bones:
        ob_bone = base_bone.copy()
        bpy.context.collection.objects.link(ob_bone)
        
        const_loc = ob_bone.constraints.new('COPY_LOCATION')
        const_loc.target = armature
        const_loc.subtarget = bone.name
        
        const_rot = ob_bone.constraints.new('COPY_ROTATION')
        const_rot.target = armature
        const_rot.subtarget = bone.name
        
        length = bone.length if bone.length > (char_height * 0.001) else (char_height * 0.01)
        ob_bone.scale = (1, length, 1)
        
        ob_joint = base_joint.copy()
        bpy.context.collection.objects.link(ob_joint)
        const_j = ob_joint.constraints.new('COPY_LOCATION')
        const_j.target = armature
        const_j.subtarget = bone.name
        
        if len(bone.children) == 0:
            ob_tail = base_joint.copy()
            bpy.context.collection.objects.link(ob_tail)
            const_t = ob_tail.constraints.new('COPY_LOCATION')
            const_t.target = armature
            const_t.subtarget = bone.name
            const_t.head_tail = 1.0 

    base_joint.hide_render = True
    base_bone.hide_render = True
    
    # --- ANTI-JITTER DOLLY CAMERA SYSTEM ---
    cam_data = bpy.data.cameras.new('PreviewCam')
    cam_data.lens = 35
    cam = bpy.data.objects.new('PreviewCam', cam_data)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    
    # 1. The "Dolly" - Follows the character horizontally, but ignores vertical jumping/footsteps
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    dolly_empty = bpy.context.active_object
    const_dolly = dolly_empty.constraints.new(type='COPY_LOCATION')
    const_dolly.target = armature
    if root_bone:
        const_dolly.subtarget = root_bone.name
    const_dolly.use_z = False # Critical fix for grid shaking
    
    # 2. The "Target" - Follows the character exactly (including jumps) for the camera to look at
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    look_empty = bpy.context.active_object
    const_look = look_empty.constraints.new(type='COPY_LOCATION')
    const_look.target = armature
    if root_bone:
        const_look.subtarget = root_bone.name

    # Parent the camera to the stable dolly, pointing at the true target
    cam.parent = dolly_empty
    cam.location = (0, -cam_dist, cam_dist * 0.3) 
    
    track = cam.constraints.new(type='TRACK_TO')
    track.target = look_empty
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

scene = bpy.context.scene
scene.render.engine = '{engine}'
scene.render.resolution_x = {res_x}
scene.render.resolution_y = {res_y}
scene.render.resolution_percentage = 100
scene.frame_step = {frame_step}

scene.render.image_settings.file_format = 'JPEG'
scene.render.image_settings.quality = 90
scene.render.filepath = "{temp_dir}/frame_"

bpy.ops.render.render(animation=True)
sys.exit(0)
"""

    def compile_video(self, frame_dir, output_path, fps=30):
        search_pattern = os.path.join(frame_dir, "*.jpg")
        frames = sorted(glob.glob(search_pattern))
        
        if not frames:
            self.log("Compilation failed: No frames found.")
            return False
            
        try:
            # We output at 30fps. If frame_step is high, it creates a fast timelapse effect automatically.
            writer = imageio.get_writer(output_path, fps=fps, codec='libx264', macro_block_size=None)
            for frame_file in frames:
                writer.append_data(imageio.imread(frame_file))
            writer.close()
            return True
        except Exception as e:
            self.log(f"FFmpeg compilation error: {str(e)}")
            return False

    def start_render_thread(self):
        if not self.files_to_render:
            messagebox.showwarning("Empty Queue", "Please add some BVH files or a folder first.")
            return
            
        self.render_btn.configure(state="disabled", text="Processing...")
        threading.Thread(target=self.batch_process, daemon=True).start()

    def batch_process(self):
        python_exe = sys.executable 
        total = len(self.files_to_render)
        self.progress_bar.set(0)
        
        res = self.resolution_menu.get().split("x")
        res_x, res_y = int(res[0]), int(res[1])
        engine = "BLENDER_WORKBENCH" if "Fast" in self.engine_menu.get() else "BLENDER_EEVEE"

        # Determine frame step (always outputs a solid 30fps container)
        speed_choice = self.speed_menu.get()
        if "5" in speed_choice:
            frame_step = 5
        elif "4" in speed_choice:
            frame_step = 4
        elif "3" in speed_choice:
            frame_step = 3
        elif "2" in speed_choice:
            frame_step = 2
        else:
            frame_step = 1

        for idx, file_path in enumerate(self.files_to_render):
            filename = os.path.basename(file_path)
            self.log(f"Rendering frames: {filename}")
            
            output_path = os.path.splitext(file_path)[0] + "_preview.mp4"
            
            temp_frame_dir = tempfile.mkdtemp()
            script_content = self.generate_bpy_script(file_path, temp_frame_dir, res_x, res_y, engine, frame_step)
            
            fd, temp_script_path = tempfile.mkstemp(suffix=".py")
            with os.fdopen(fd, 'w') as f:
                f.write(script_content)
                
            try:
                cmd = [python_exe, temp_script_path]
                startupinfo = None
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                           text=True, startupinfo=startupinfo)
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    self.log(f"Compiling sequence...")
                    if self.compile_video(temp_frame_dir, output_path, fps=30):
                        self.log(f"Success -> {os.path.basename(output_path)}")
                else:
                    self.log(f"Error rendering {filename}. See console.")
                    print(f"--- BPY ERROR ---\n{stdout}\n{stderr}")
                    
            except Exception as e:
                self.log(f"Execution failed: {str(e)}")
            finally:
                os.remove(temp_script_path)
                shutil.rmtree(temp_frame_dir, ignore_errors=True) 
                
            self.progress_bar.set((idx + 1) / total)

        self.log("Batch processing complete.")
        self.render_btn.configure(state="normal", text="Start Batch Render")


if __name__ == "__main__":
    app = MotionPreviewApp()
    app.mainloop()