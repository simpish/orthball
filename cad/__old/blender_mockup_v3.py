import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Constants
MX_PITCH = 19.05  # MX key pitch in mm
CHOC_PITCH_X = 18.0  # Choc horizontal pitch
CHOC_PITCH_Y = 17.0  # Choc vertical pitch
PLATE_THICKNESS = 1.5  # Switch plate thickness
CASE_WALL = 3.0  # Case wall thickness
CASE_BOTTOM = 3.0  # Case bottom thickness
CASE_DEPTH = 12.0  # Case internal depth

# Colors
COLOR_CASE = (0.2, 0.2, 0.25, 1.0)  # Dark grey
COLOR_KEYCAP = (0.7, 0.7, 0.75, 1.0)  # Light grey
COLOR_BALL = (0.8, 0.1, 0.1, 1.0)  # Red
COLOR_CHOC = (0.95, 0.95, 0.98, 1.0)  # White
COLOR_BEARING = (0.75, 0.75, 0.8, 1.0)  # Silver
COLOR_PLATE = (0.3, 0.3, 0.3, 1.0)  # Dark metal
COLOR_PCB = (0.1, 0.3, 0.15, 1.0)  # Dark green PCB

def create_material(name, color):
    """Create a simple material with color"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        if 'Metallic' in bsdf.inputs:
            bsdf.inputs['Metallic'].default_value = 0.3
        if 'Roughness' in bsdf.inputs:
            bsdf.inputs['Roughness'].default_value = 0.5
    return mat

def create_keycap(location, size=(17, 17, 8), material=None):
    """Create a keycap with tapered top (trapezoid shape)"""
    # Create base shape
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    cap = bpy.context.active_object
    cap.scale = (size[0]/2, size[1]/2, size[2]/2)
    cap.location.z += size[2]/2

    # Enter edit mode to taper the top
    bpy.context.view_layer.objects.active = cap
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    # Select and scale top face vertices
    for v in cap.data.vertices:
        if v.co.z > 0:  # Top vertices
            v.select = True

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.resize(value=(0.85, 0.85, 1.0))
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add bevel modifier for rounded edges
    bevel = cap.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.5
    bevel.segments = 3

    if material:
        if not cap.data.materials:
            cap.data.materials.append(material)
        else:
            cap.data.materials[0] = material
    return cap

def create_pcb_layer(width, depth, offset=(0, 0, 0), mat=None):
    """Create a PCB layer below the switch plate"""
    pcb_thickness = 1.6  # Standard PCB thickness
    pcb_z = offset[2] - pcb_thickness/2 - 3  # Below the plate

    bpy.ops.mesh.primitive_cube_add(size=1, location=(offset[0], offset[1], pcb_z))
    pcb = bpy.context.active_object
    pcb.name = "PCB"
    pcb.scale = (width/2, depth/2, pcb_thickness/2)
    if mat:
        pcb.data.materials.append(mat)
    return pcb

def create_simple_case(width, depth, offset=(0, 0, 0), mat=None):
    """Create a simple case box with walls"""
    # Bottom
    bpy.ops.mesh.primitive_cube_add(size=1, location=(offset[0], offset[1], offset[2] - CASE_DEPTH/2))
    bottom = bpy.context.active_object
    bottom.scale = (width/2, depth/2, CASE_BOTTOM/2)
    if mat:
        bottom.data.materials.append(mat)

    # Front wall
    bpy.ops.mesh.primitive_cube_add(size=1)
    wall = bpy.context.active_object
    wall.scale = (width/2, CASE_WALL/2, CASE_DEPTH/2)
    wall.location = (offset[0], offset[1] - depth/2 + CASE_WALL/2, offset[2] - CASE_DEPTH/2)
    if mat:
        wall.data.materials.append(mat)

    # Back wall
    bpy.ops.mesh.primitive_cube_add(size=1)
    wall = bpy.context.active_object
    wall.scale = (width/2, CASE_WALL/2, CASE_DEPTH/2)
    wall.location = (offset[0], offset[1] + depth/2 - CASE_WALL/2, offset[2] - CASE_DEPTH/2)
    if mat:
        wall.data.materials.append(mat)

    # Left wall
    bpy.ops.mesh.primitive_cube_add(size=1)
    wall = bpy.context.active_object
    wall.scale = (CASE_WALL/2, depth/2, CASE_DEPTH/2)
    wall.location = (offset[0] - width/2 + CASE_WALL/2, offset[1], offset[2] - CASE_DEPTH/2)
    if mat:
        wall.data.materials.append(mat)

    # Right wall
    bpy.ops.mesh.primitive_cube_add(size=1)
    wall = bpy.context.active_object
    wall.scale = (CASE_WALL/2, depth/2, CASE_DEPTH/2)
    wall.location = (offset[0] + width/2 - CASE_WALL/2, offset[1], offset[2] - CASE_DEPTH/2)
    if mat:
        wall.data.materials.append(mat)

    return bottom

def create_plate_with_holes(width, depth, key_positions, offset=(0, 0, 0), mat=None, hole_size=14.0):
    """Create a switch plate with cutout holes at key positions"""
    # Create main plate
    bpy.ops.mesh.primitive_cube_add(size=1, location=offset)
    plate = bpy.context.active_object
    plate.name = "SwitchPlate"
    plate.scale = (width/2, depth/2, PLATE_THICKNESS/2)

    # Create holes at each key position using boolean difference
    for pos in key_positions:
        # Create a cube for the hole
        hole_x = offset[0] + pos[0]
        hole_y = offset[1] + pos[1]
        hole_z = offset[2]

        bpy.ops.mesh.primitive_cube_add(size=1, location=(hole_x, hole_y, hole_z))
        hole = bpy.context.active_object
        hole.scale = (hole_size/2, hole_size/2, PLATE_THICKNESS)  # Taller than plate to ensure cut through

        # Add boolean modifier to plate
        bool_mod = plate.modifiers.new(name="Boolean", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = hole

        # Apply modifier
        bpy.context.view_layer.objects.active = plate
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)

        # Delete the hole object
        bpy.data.objects.remove(hole, do_unlink=True)

    if mat:
        if not plate.data.materials:
            plate.data.materials.append(mat)
        else:
            plate.data.materials[0] = mat

    return plate

def create_trackball_with_cup(ball_diameter, offset=(0, 0, 0), mat_ball=None, mat_cup=None, mat_bearing=None):
    """Create trackball, cup, and bearings"""
    cup_depth = ball_diameter * 0.35

    # Create cup as a simple bowl shape
    bpy.ops.mesh.primitive_uv_sphere_add(radius=ball_diameter/2 + 1.5, location=(offset[0], offset[1], offset[2] - cup_depth/3), segments=32, ring_count=16)
    cup = bpy.context.active_object
    cup.scale = (1, 1, 0.6)  # Flatten to make bowl shape
    if mat_cup:
        cup.data.materials.append(mat_cup)

    # Create ball
    ball_z = offset[2] + ball_diameter * 0.2  # Raised so it's 60% visible
    bpy.ops.mesh.primitive_uv_sphere_add(radius=ball_diameter/2, location=(offset[0], offset[1], ball_z), segments=32, ring_count=32)
    ball = bpy.context.active_object
    if mat_ball:
        ball.data.materials.append(mat_ball)

    # Create BTU bearings (3 points at 120 degrees)
    bearings = []
    bearing_radius = 1.5
    bearing_distance = ball_diameter/2 - 5

    for i in range(3):
        angle = i * 120 * math.pi / 180
        x = offset[0] + bearing_distance * math.cos(angle)
        y = offset[1] + bearing_distance * math.sin(angle)
        z = offset[2] - cup_depth * 0.3

        bpy.ops.mesh.primitive_uv_sphere_add(radius=bearing_radius, location=(x, y, z), segments=16, ring_count=16)
        bearing = bpy.context.active_object
        if mat_bearing:
            bearing.data.materials.append(mat_bearing)
        bearings.append(bearing)

    return ball, cup, bearings

# Create materials
mat_case = create_material("Case", COLOR_CASE)
mat_keycap = create_material("Keycap", COLOR_KEYCAP)
mat_plate = create_material("Plate", COLOR_PLATE)
mat_ball = create_material("Ball", COLOR_BALL)
mat_choc = create_material("Choc", COLOR_CHOC)
mat_bearing = create_material("Bearing", COLOR_BEARING)
mat_pcb = create_material("PCB", COLOR_PCB)

# === LEFT UNIT ===
left_width = 6 * MX_PITCH + 10
left_depth = 4 * MX_PITCH + 10
left_x = -left_width/2 - 70

create_simple_case(left_width, left_depth, (left_x, 0, 0), mat_case)
create_pcb_layer(left_width - 2*CASE_WALL, left_depth - 2*CASE_WALL, (left_x, 0, 0), mat_pcb)

# Collect all key positions for this unit
left_key_positions = []

# Main keys (6x3)
for row in range(3):
    for col in range(6):
        x = (col - 2.5) * MX_PITCH
        y = (row - 1) * MX_PITCH + MX_PITCH/2
        left_key_positions.append((x, y))

# Thumb keys (5 keys below)
thumb_y = -1.5 * MX_PITCH - MX_PITCH/2
for i in range(5):
    x = (i - 2) * MX_PITCH
    left_key_positions.append((x, thumb_y))

# Create plate with holes
create_plate_with_holes(left_width - 2*CASE_WALL, left_depth - 2*CASE_WALL,
                        left_key_positions, (left_x, 0, 0), mat_plate)

# Create keycaps above the holes
for row in range(3):
    for col in range(6):
        x = left_x + (col - 2.5) * MX_PITCH
        y = (row - 1) * MX_PITCH + MX_PITCH/2
        z = PLATE_THICKNESS
        create_keycap((x, y, z), material=mat_keycap)

for i in range(5):
    x = left_x + (i - 2) * MX_PITCH
    create_keycap((x, thumb_y, PLATE_THICKNESS), material=mat_keycap)

# === CENTER NUMPAD ===
center_width = 3 * MX_PITCH + 10
center_depth = 4 * MX_PITCH + 10
center_x = 0

create_simple_case(center_width, center_depth, (center_x, 0, 0), mat_case)
create_pcb_layer(center_width - 2*CASE_WALL, center_depth - 2*CASE_WALL, (center_x, 0, 0), mat_pcb)

# Collect key positions
center_key_positions = []
for row in range(4):
    for col in range(3):
        x = (col - 1) * MX_PITCH
        y = (row - 1.5) * MX_PITCH
        center_key_positions.append((x, y))

# Create plate with holes
create_plate_with_holes(center_width - 2*CASE_WALL, center_depth - 2*CASE_WALL,
                        center_key_positions, (center_x, 0, 0), mat_plate)

# Create keycaps
for row in range(4):
    for col in range(3):
        x = center_x + (col - 1) * MX_PITCH
        y = (row - 1.5) * MX_PITCH
        z = PLATE_THICKNESS
        create_keycap((x, y, z), material=mat_keycap)

# === RIGHT UNIT ===
right_width = 160
right_depth = 100
right_x = center_width/2 + right_width/2 + 30

create_simple_case(right_width, right_depth, (right_x, 0, 0), mat_case)
create_pcb_layer(right_width - 2*CASE_WALL, right_depth - 2*CASE_WALL, (right_x, 0, 0), mat_pcb)

# Collect all key positions for right unit
right_key_positions = []

# Main keys (6x3)
main_x_offset = -35
for row in range(3):
    for col in range(6):
        x = main_x_offset + (col - 2.5) * MX_PITCH
        y = (row - 1) * MX_PITCH + MX_PITCH/2
        right_key_positions.append((x, y))

# Thumb keys (5 keys)
thumb_y = -1.5 * MX_PITCH - MX_PITCH/2
for i in range(5):
    x = main_x_offset + (i - 2) * MX_PITCH
    right_key_positions.append((x, thumb_y))

# Choc keys below trackball
ball_x_offset = 30
ball_y_offset = 20
choc_x_offset = ball_x_offset
choc_y_offset = ball_y_offset - 45

# Top 2 Choc keys (13mm holes for Choc switches)
for i in range(2):
    x = choc_x_offset + (i - 0.5) * CHOC_PITCH_X
    y = choc_y_offset
    right_key_positions.append((x, y))

# Bottom 4 Choc keys
for i in range(4):
    x = choc_x_offset + (i - 1.5) * CHOC_PITCH_X
    y = choc_y_offset - CHOC_PITCH_Y
    right_key_positions.append((x, y))

# Create plate with holes (mix of MX 14mm and Choc 13mm - using 14mm for all for simplicity)
create_plate_with_holes(right_width - 2*CASE_WALL, right_depth - 2*CASE_WALL,
                        right_key_positions, (right_x, 0, 0), mat_plate, hole_size=14.0)

# Create keycaps - Main keys
main_x = right_x + main_x_offset
for row in range(3):
    for col in range(6):
        x = main_x + (col - 2.5) * MX_PITCH
        y = (row - 1) * MX_PITCH + MX_PITCH/2
        z = PLATE_THICKNESS
        create_keycap((x, y, z), material=mat_keycap)

# Thumb keys
for i in range(5):
    x = main_x + (i - 2) * MX_PITCH
    create_keycap((x, thumb_y, PLATE_THICKNESS), material=mat_keycap)

# Trackball (right upper area)
ball_x = right_x + ball_x_offset
ball_y = ball_y_offset
ball_z = 0
ball, cup, bearings = create_trackball_with_cup(55, (ball_x, ball_y, ball_z), mat_ball, mat_case, mat_bearing)

# Choc keys below trackball
choc_x = right_x + choc_x_offset
choc_y = choc_y_offset

# Top 2 Choc keys
for i in range(2):
    x = choc_x + (i - 0.5) * CHOC_PITCH_X
    y = choc_y
    z = PLATE_THICKNESS
    create_keycap((x, y, z), size=(16, 16, 5), material=mat_choc)

# Bottom 4 Choc keys
for i in range(4):
    x = choc_x + (i - 1.5) * CHOC_PITCH_X
    y = choc_y - CHOC_PITCH_Y
    z = PLATE_THICKNESS
    create_keycap((x, y, z), size=(16, 16, 5), material=mat_choc)

# === LIGHTING ===
# Sun light
bpy.ops.object.light_add(type='SUN', location=(100, -100, 200))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), 0, math.radians(45))

# Fill light
bpy.ops.object.light_add(type='AREA', location=(-100, 100, 150))
area = bpy.context.active_object
area.data.energy = 1000
area.data.size = 150

# === CAMERAS ===
# Isometric view
bpy.ops.object.camera_add(location=(300, -300, 200))
camera_iso = bpy.context.active_object
camera_iso.name = "Camera_Iso"
camera_iso.rotation_euler = (math.radians(60), 0, math.radians(45))
camera_iso.data.type = 'ORTHO'
camera_iso.data.ortho_scale = 400

# Top view
bpy.ops.object.camera_add(location=(0, 0, 400))
camera_top = bpy.context.active_object
camera_top.name = "Camera_Top"
camera_top.rotation_euler = (0, 0, 0)
camera_top.data.type = 'ORTHO'
camera_top.data.ortho_scale = 450

# Detail view - trackball closeup
bpy.ops.object.camera_add(location=(ball_x + 100, ball_y - 100, ball_z + 80))
camera_detail = bpy.context.active_object
camera_detail.name = "Camera_Detail"
camera_detail.rotation_euler = (math.radians(55), 0, math.radians(45))
camera_detail.data.type = 'ORTHO'
camera_detail.data.ortho_scale = 120

# === RENDER SETUP ===
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.95, 0.95, 0.95, 1.0)  # Light grey background

# === RENDER ALL VIEWS ===
print("Rendering isometric view...")
scene.camera = camera_iso
scene.render.filepath = '/Users/shudai/Space/keyboard/orthball/cad/mockup_v3_iso.png'
bpy.ops.render.render(write_still=True)

print("Rendering top view...")
scene.camera = camera_top
scene.render.filepath = '/Users/shudai/Space/keyboard/orthball/cad/mockup_v3_top.png'
bpy.ops.render.render(write_still=True)

print("Rendering detail view...")
scene.camera = camera_detail
scene.render.filepath = '/Users/shudai/Space/keyboard/orthball/cad/mockup_v3_detail.png'
bpy.ops.render.render(write_still=True)

print("All renders complete!")
