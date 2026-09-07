# Motion Preview — BVH Batch Renderer

A desktop application for batch rendering **BVH (Biovision Hierarchy)** motion-capture files into MP4 preview videos.

Motion Preview provides a simple graphical interface for importing multiple BVH files, configuring render settings, generating smooth skeletal visualizations in Blender, and automatically compiling rendered frames into video previews.

## Features

* Batch processing for multiple BVH files
* Add individual BVH files or scan entire folders
* Recursive folder scanning for `.bvh` files
* Multiple output resolutions
* Adjustable rendering speed through frame skipping
* Blender Workbench rendering mode
* Blender EEVEE rendering mode
* Automatic skeletal visualization
* Joint and bone geometry generation
* Grid floor visualization
* Automatic camera positioning based on character height
* Anti-jitter camera dolly system
* Automatic JPEG frame rendering
* Automatic MP4 video compilation
* Progress bar and timestamped application logs
* Temporary file cleanup after rendering
* Windows subprocess handling for background execution

---

## How It Works

The application follows this workflow:

```text
BVH Files
   │
   ▼
Motion Preview GUI
   │
   ├── Resolution Selection
   ├── Render Speed Selection
   └── Render Engine Selection
   │
   ▼
Temporary Blender Python Script
   │
   ▼
Blender BVH Import
   │
   ▼
Skeleton Visualization Generation
   │
   ├── Bones
   ├── Joints
   └── Grid Floor
   │
   ▼
Camera Setup
   │
   ▼
JPEG Frame Rendering
   │
   ▼
ImageIO / FFmpeg
   │
   ▼
MP4 Preview Video
```

---

# Requirements

## Python

The application requires Python 3.

## Required Python Packages

Install the following dependencies:

```bash
pip install customtkinter imageio imageio-ffmpeg
```

The script imports:

* `customtkinter`
* `imageio`
* Standard Python libraries including:

  * `os`
  * `sys`
  * `time`
  * `glob`
  * `shutil`
  * `threading`
  * `subprocess`
  * `tempfile`
  * `tkinter`

---

## Blender

The rendering process depends on Blender and its Python API (`bpy`).

The application generates a temporary Python script containing Blender API commands, including BVH import operations and rendering instructions.

The generated script uses:

```python
import bpy
```

and imports BVH files using:

```python
bpy.ops.import_anim.bvh()
```

Because the main application launches a Python subprocess using the current Python executable, the Python environment used to execute the generated script must provide access to Blender's `bpy` module.

---

# Installation

Clone or download this repository.

Install the Python dependencies:

```bash
pip install customtkinter imageio imageio-ffmpeg
```

Then run:

```bash
python bvh_batch_renderer.py
```

---

# User Interface

The application uses a dark CustomTkinter interface.

The window is divided into three primary areas:

```text
┌──────────────────────┬─────────────────────────────────┐
│                      │                                 │
│   SETTINGS SIDEBAR   │          FILE QUEUE             │
│                      │                                 │
│   Resolution         │   + Add Files                   │
│   Render Speed       │   + Add Folder                  │
│   Render Engine      │                                 │
│                      │   BVH File List                 │
│                      │                                 │
│                      │                     Clear List  │
│                      │                                 │
├──────────────────────┼─────────────────────────────────┤
│                      │                                 │
│  Start Batch Render  │  Progress Bar                   │
│                      │  Rendering Log                  │
│                      │                                 │
└──────────────────────┴─────────────────────────────────┘
```

---

# Adding BVH Files

## Add Files

Click:

```text
+ Add Files
```

You can select one or multiple `.bvh` files.

Duplicate files are ignored if they already exist in the rendering queue.

---

## Add Folder

Click:

```text
+ Add Folder
```

The application scans the selected folder recursively.

Every file ending with:

```text
.bvh
```

is added to the rendering queue.

This means BVH files inside subdirectories are also detected.

---

## Clear List

Click:

```text
Clear List
```

This removes all files from the current rendering queue.

---

# Render Settings

## Resolution

The following output resolutions are available:

| Resolution |
| ---------- |
| 1920×1080  |
| 1280×720   |
| 800×800    |
| 640×480    |
| 512×512    |
| 320×320    |
| 256×256    |

Default:

```text
640×480
```

---

## Render Speed

Render speed is controlled by Blender's frame stepping.

Available options:

| Setting      | Frame Step |
| ------------ | ---------: |
| Max Speed    |          5 |
| Ultra Fast   |          4 |
| Draft        |          3 |
| Normal       |          2 |
| High Quality |          1 |

### How Frame Stepping Works

For example:

```text
Frame Step = 1
```

renders every animation frame.

```text
Frame Step = 2
```

renders every second frame.

```text
Frame Step = 5
```

renders one out of every five frames.

The final video is still compiled at:

```text
30 FPS
```

Therefore, larger frame steps create a faster, time-lapse-style motion preview.

---

# Render Engines

The application provides two Blender rendering modes.

## Workbench

```text
Workbench (Fast Solid)
```

Internally:

```python
BLENDER_WORKBENCH
```

This mode is intended for fast preview rendering.

---

## EEVEE

```text
EEVEE (Shaded)
```

Internally:

```python
BLENDER_EEVEE
```

This mode provides a shaded rendering option.

---

# BVH Rendering Pipeline

For every BVH file in the queue, the application performs the following steps.

## 1. Create Temporary Workspace

A temporary directory is created for rendered frames.

A temporary Python script is also created for Blender processing.

---

## 2. Reset Blender Scene

The generated Blender script resets the scene using:

```python
bpy.ops.wm.read_factory_settings(use_empty=True)
```

This starts the rendering process with an empty scene.

---

## 3. Configure Background

The world background is configured with a dark color:

```text
RGB: 0.04, 0.04, 0.04
```

This provides a dark environment for the motion preview.

---

## 4. Create a Sun Light

A directional sun light is added to the scene.

The light:

* Uses a `SUN` light type
* Has an energy value of `2.0`
* Is rotated approximately 45 degrees on two axes

---

## 5. Import the BVH Animation

The BVH file is imported using Blender's BVH importer.

The importer automatically updates:

* Scene FPS
* Animation duration

If BVH loading fails, the Blender process exits with an error.

---

# Automatic Skeleton Visualization

The application creates custom geometry to visualize the imported armature.

Instead of directly rendering the imported skeleton, it creates separate visual objects that follow the armature bones.

---

## Joint Geometry

A UV sphere is created as the base joint object.

The joint radius is proportional to the detected character height.

Each bone receives a joint visualization.

Leaf bones also receive an additional joint at their tail position.

---

## Bone Geometry

A cylinder is created as the base bone object.

The cylinder is transformed and then duplicated for every bone in the armature.

Each visual bone receives constraints that connect it to the corresponding armature bone.

The visualization uses:

```text
COPY_LOCATION
```

and:

```text
COPY_ROTATION
```

constraints.

The bone geometry scales according to the actual bone length.

Very small bones receive a minimum fallback length.

---

## Material

The skeleton visualization uses a Principled BSDF material.

Default values include:

```text
Base Color: Light Gray
Roughness: 0.4
```

The visual geometry is therefore rendered as a clean, light-colored motion skeleton.

---

# Grid Floor

A grid floor is automatically generated underneath the character.

The grid size is proportional to the detected character height.

The process:

1. Creates a grid mesh.
2. Positions it at the world origin.
3. Adds a Wireframe modifier.
4. Applies a dark gray material.

The grid thickness also scales according to character height.

This provides visual reference for movement and locomotion.

---

# Automatic Character Height Detection

The application analyzes the armature to estimate character height.

For every pose bone, it checks:

* Bone head position
* Bone tail position

The highest Z-coordinate is used to estimate the maximum character height.

This value is then used to calculate:

* Camera distance
* Grid size
* Grid line thickness
* Joint size
* Bone radius
* Minimum bone length

This allows the preview scene to automatically scale to different BVH characters.

---

# Anti-Jitter Camera System

One of the primary rendering features is the camera setup designed to reduce unwanted vertical camera movement.

The system uses two Empty objects.

## Dolly Empty

The Dolly Empty follows the armature's root bone.

However, its Z-axis movement is disabled.

This means the camera:

* Follows horizontal character movement
* Does not follow vertical jumping
* Remains visually stable relative to the grid

---

## Look Target

A second Empty follows the root bone normally.

Unlike the Dolly Empty, it follows vertical movement.

The camera tracks this object.

This means:

```text
Camera Position
    ↓
Stable Horizontal Dolly

Camera Direction
    ↓
Animated Character Target
```

The result is a camera that:

* Follows the character horizontally
* Looks toward vertical movement
* Avoids excessive camera shaking caused by jumps or footsteps

---

# Camera Configuration

The generated camera uses:

```text
Lens: 35mm
```

The camera distance is calculated dynamically based on character height.

The camera is positioned approximately:

```text
X = 0
Y = -Character Height × 1.3
Z = Camera Distance × 0.3
```

The camera uses a:

```text
TRACK_TO
```

constraint targeting the animated look target.

---

# Frame Rendering

The scene renders animation frames as JPEG files.

Settings include:

```text
Format: JPEG
Quality: 90
```

The frames are written to a temporary directory.

Example:

```text
/tmp/render-session/
    frame_0001.jpg
    frame_0002.jpg
    frame_0003.jpg
    ...
```

The temporary directory is removed after processing is complete.

---

# Video Compilation

After Blender finishes rendering, the application searches the temporary directory for:

```text
*.jpg
```

frames.

The frames are sorted and compiled into an MP4 video using ImageIO.

The video writer uses:

```text
Codec: libx264
FPS: 30
```

The application attempts to use FFmpeg through ImageIO's video writing backend.

---

# Output Files

Each output video is created next to the original BVH file.

For example:

```text
walk_cycle.bvh
```

becomes:

```text
walk_cycle_preview.mp4
```

The output naming format is:

```text
<original_filename>_preview.mp4
```

---

# Batch Processing

The application processes files sequentially.

For each file:

1. Create temporary frame directory.
2. Generate temporary Blender Python script.
3. Start the rendering subprocess.
4. Render animation frames.
5. Compile JPEG frames into MP4.
6. Delete temporary files.
7. Update the progress bar.
8. Continue with the next BVH file.

The process runs inside a background thread so the GUI does not intentionally perform the batch processing directly from the main event loop.

---

# Progress Tracking

The application includes a progress bar.

Progress is calculated as:

```text
Processed Files / Total Files
```

For example:

```text
1 of 5 files → 20%
3 of 5 files → 60%
5 of 5 files → 100%
```

---

# Application Log

A log panel displays timestamped messages.

Example:

```text
[12:30:15] Added 5 files.
[12:30:20] Rendering frames: walk.bvh
[12:31:10] Compiling sequence...
[12:31:15] Success -> walk_preview.mp4
[12:31:16] Batch processing complete.
```

The log records events such as:

* Files added
* Folder scans
* Queue clearing
* Rendering start
* Video compilation
* Successful output generation
* Rendering errors
* Compilation errors

---

# Error Handling

## Empty Queue

If no BVH files are added, the application displays a warning.

```text
Please add some BVH files or a folder first.
```

---

## BVH Import Errors

If Blender cannot import a BVH file, the generated Blender script:

1. Prints the error.
2. Exits with a non-zero status code.

The main application then logs a rendering error.

---

## Video Compilation Errors

If no JPEG frames are found:

```text
Compilation failed: No frames found.
```

is logged.

If the ImageIO/FFmpeg process fails, the exception is logged.

---

# Temporary File Cleanup

After each BVH file is processed, the application removes:

* The temporary Blender Python script
* The temporary frame directory
* Rendered JPEG frames

Temporary files are cleaned up in a `finally` block.

This ensures cleanup is attempted even when rendering fails.

---

# Project Structure

A minimal project structure:

```text
motion-preview/
│
├── bvh_batch_renderer.py
│
└── README.md
```

---

# Main Application Components

## `MotionPreviewApp`

The primary application class.

```python
class MotionPreviewApp(ctk.CTk):
```

This class manages:

* Application window
* Sidebar settings
* BVH file queue
* Progress tracking
* Log output
* Rendering workflow

---

## `_build_sidebar()`

Creates the settings sidebar.

Includes:

* Resolution selector
* Render speed selector
* Render engine selector
* Start Batch Render button

---

## `_build_main_area()`

Creates the file queue interface.

Includes:

* Add Files button
* Add Folder button
* Clear List button
* File list display

---

## `_build_log_area()`

Creates the processing status area.

Includes:

* Progress bar
* Timestamped log panel

---

## `generate_bpy_script()`

Generates a temporary Blender Python script for each BVH file.

The generated script handles:

* Scene initialization
* BVH importing
* Lighting
* Grid creation
* Skeleton visualization
* Material creation
* Camera setup
* Render configuration
* Animation rendering

---

## `compile_video()`

Compiles rendered JPEG frames into an MP4 video.

Uses:

```python
imageio.get_writer()
```

with:

```text
libx264
```

as the requested codec.

---

## `batch_process()`

Controls the complete batch rendering workflow.

This method:

* Reads UI settings
* Determines resolution
* Determines render engine
* Converts speed settings into frame steps
* Processes each BVH file
* Creates temporary resources
* Launches the rendering subprocess
* Compiles videos
* Cleans temporary files
* Updates progress

---

# Usage Example

## Step 1: Launch the Application

```bash
python bvh_batch_renderer.py
```

## Step 2: Add BVH Files

Click:

```text
+ Add Files
```

or:

```text
+ Add Folder
```

## Step 3: Configure Settings

Example:

```text
Resolution:
1280x720

Render Speed:
Normal (Render 1 in 2 frames)

Render Engine:
Workbench (Fast Solid)
```

## Step 4: Start Processing

Click:

```text
Start Batch Render
```

## Step 5: Find Your Videos

Output videos are created next to the original BVH files:

```text
walk.bvh
walk_preview.mp4

run.bvh
run_preview.mp4
```

---

# Performance Considerations

Rendering performance depends on several factors:

* Number of BVH files
* Number of animation frames
* Selected resolution
* Frame step
* Selected Blender render engine
* Character skeleton complexity
* Hardware performance

For faster previews, consider using:

```text
320x320
```

or:

```text
640x480
```

with:

```text
Max Speed (Render 1 in 5 frames)
```

and:

```text
Workbench (Fast Solid)
```

For more complete motion previews, use:

```text
High Quality (Render All)
```

which renders every animation frame.

---

# Notes and Limitations

## Blender Python Environment

The generated rendering script requires access to:

```python
bpy
```

The exact method for providing Blender's Python API depends on the Blender and Python environment being used.

## Sequential Processing

Files are processed one at a time.

The application does not currently render multiple BVH files in parallel.

## Fixed Video Frame Rate

Compiled MP4 videos are always written at:

```text
30 FPS
```

## JPEG Intermediate Frames

Each animation is first rendered as JPEG images before video compilation.

## Output Location

Videos are written beside their corresponding BVH source files.

---

# Future Improvements

Potential improvements could include:

* Blender executable path selection
* Automatic Blender installation detection
* Custom output directory selection
* Custom output FPS
* Custom video quality settings
* Custom camera angles
* Background color controls
* Skeleton color customization
* Transparent background rendering
* Parallel batch processing
* Render cancellation
* Per-file error reporting in the UI
* Drag-and-drop BVH support
* Persistent application settings
* Output format selection
* GIF export
* Preview thumbnails

---

# License

No license is currently defined in the source code.

If you plan to distribute this project, consider adding a license such as:

* MIT License
* Apache License 2.0
* GPL-3.0

---

# Author

Created as a BVH motion preview and batch rendering tool using:

* Python
* CustomTkinter
* Blender Python API
* ImageIO
* FFmpeg-compatible video encoding

---

## Technical Summary

**Input**

```text
BVH Motion Capture Files
```

**Processing**

```text
Python GUI
    ↓
Temporary Blender Script
    ↓
BVH Import
    ↓
Procedural Skeleton Visualization
    ↓
Stable Dolly Camera
    ↓
JPEG Frame Rendering
    ↓
ImageIO / libx264
```

**Output**

```text
MP4 Motion Preview Videos
```
