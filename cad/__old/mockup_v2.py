"""
OrthBall v2 Mockup - Proper keyboard with individual keys
Fixes v1 issues:
- Individual key wells in 19.05mm grid
- Proper case/baseplate
- Left: 6x3 + 5 thumb = 23 keys
- Center: 3x4 = 12 keys
- Right: 6x3 + 5 thumb + 6 Choc + 55mm ball
"""

import cadquery as cq

# === Constants ===
MX_PITCH = 19.05
MX_KEY_SIZE = 13.5  # MX switch opening size
MX_KEY_WELL_DEPTH = 2.0  # depth of individual key well
CASE_HEIGHT = 20.0  # total height of case
CASE_WALL = 3.0  # wall thickness
CASE_BOTTOM = 2.5  # bottom plate thickness
TRACKBALL_DIA = 55.0
UNIT_GAP = 35.0  # gap between units

CHOC_PITCH = 18.0
CHOC_KEY_SIZE = 13.0


# === Helper: Create individual key wells on a grid ===
def create_key_grid(case_obj, cols, rows, x_offset=0, y_offset=0, pitch=MX_PITCH, well_size=MX_KEY_SIZE):
    """
    Cut individual key wells in a grid pattern.
    case_obj: CadQuery object to cut into
    cols, rows: number of columns and rows
    x_offset, y_offset: offset for the grid center
    Returns the modified object
    """
    result = case_obj
    for col in range(cols):
        for row in range(rows):
            x = (col - (cols - 1) / 2.0) * pitch + x_offset
            y = ((rows - 1) / 2.0 - row) * pitch + y_offset  # invert Y so row 0 is at top
            result = (
                result.faces(">Z").workplane()
                .center(x, y)
                .rect(well_size, well_size)
                .cutBlind(-MX_KEY_WELL_DEPTH)
            )
    return result


# === Left Hand Unit ===
# Main: 6 cols x 3 rows = 18 keys
# Thumb: 5 keys in a row
left_main_cols = 6
left_main_rows = 3
left_thumb_keys = 5

left_main_width = left_main_cols * MX_PITCH
left_main_depth = left_main_rows * MX_PITCH
thumb_width = left_thumb_keys * MX_PITCH
thumb_depth = MX_PITCH

# Case dimensions (add walls)
left_case_width = left_main_width + CASE_WALL * 2
left_case_depth = left_main_depth + thumb_depth + CASE_WALL * 2 + 8  # extra for thumb spacing

# Create left case
left_case = (
    cq.Workplane("XY")
    .box(left_case_width, left_case_depth, CASE_HEIGHT, centered=(True, True, False))
)

# Cut main key grid (top half)
main_y_offset = thumb_depth / 2 + 4  # shift up to make room for thumb
left_case = create_key_grid(left_case, left_main_cols, left_main_rows, y_offset=main_y_offset)

# Cut thumb key grid (bottom)
thumb_y_offset = -left_main_depth / 2 - 4
left_case = create_key_grid(left_case, left_thumb_keys, 1, y_offset=thumb_y_offset)


# === Center Numpad Unit ===
# 3 cols x 4 rows = 12 keys (flat)
center_cols = 3
center_rows = 4

center_width = center_cols * MX_PITCH
center_depth = center_rows * MX_PITCH

center_case_width = center_width + CASE_WALL * 2
center_case_depth = center_depth + CASE_WALL * 2

center_case = (
    cq.Workplane("XY")
    .box(center_case_width, center_case_depth, CASE_HEIGHT, centered=(True, True, False))
)

center_case = create_key_grid(center_case, center_cols, center_rows)


# === Right Hand Unit ===
# Main: 6 cols x 3 rows = 18 keys
# Thumb: 5 keys
# Choc: 6 keys (2 + 4 layout below trackball)
# Trackball: 55mm sphere

right_main_cols = 6
right_main_rows = 3
right_thumb_keys = 5

right_main_width = right_main_cols * MX_PITCH
right_main_depth = right_main_rows * MX_PITCH
right_thumb_width = right_thumb_keys * MX_PITCH
right_thumb_depth = MX_PITCH

# Right case needs extra width for trackball
trackball_area_width = TRACKBALL_DIA + 15
right_case_width = right_main_width + trackball_area_width + CASE_WALL * 2
right_case_depth = left_case_depth  # match left for symmetry

right_case = (
    cq.Workplane("XY")
    .box(right_case_width, right_case_depth, CASE_HEIGHT, centered=(True, True, False))
)

# Main key grid (left side of right unit)
key_area_x_offset = -(trackball_area_width / 2)
main_y_offset_r = thumb_depth / 2 + 4

right_case = create_key_grid(right_case, right_main_cols, right_main_rows,
                             x_offset=key_area_x_offset, y_offset=main_y_offset_r)

# Thumb key grid
thumb_y_offset_r = -right_main_depth / 2 - 4
right_case = create_key_grid(right_case, right_thumb_keys, 1,
                             x_offset=key_area_x_offset, y_offset=thumb_y_offset_r)

# Trackball socket
# Ball center is set so ~60% is exposed above the case top
trackball_r = TRACKBALL_DIA / 2.0
expose_fraction = 0.60
ball_center_z = CASE_HEIGHT - trackball_r * (2 * expose_fraction - 1)

# Position trackball on the right side of the case
trackball_x = right_case_width / 2 - trackball_area_width / 2
trackball_y = right_case_depth / 2 - TRACKBALL_DIA / 2 - 10  # near top-right

trackball_sphere = (
    cq.Workplane("XY")
    .transformed(offset=(trackball_x, trackball_y, ball_center_z))
    .sphere(trackball_r + 0.5)  # slightly larger for clearance
)
right_case = right_case.cut(trackball_sphere)

# Visual trackball (the actual ball)
trackball = (
    cq.Workplane("XY")
    .transformed(offset=(trackball_x, trackball_y, ball_center_z))
    .sphere(trackball_r - 0.3)
)

# Choc 6 keys below trackball
# Layout: 2 keys on top row, 4 keys on bottom row
choc_top_cols = 2
choc_bot_cols = 4

choc_y_base = trackball_y - trackball_r - CHOC_PITCH  # below ball

# Top 2 choc keys
right_case = create_key_grid(right_case, choc_top_cols, 1,
                             x_offset=trackball_x, y_offset=choc_y_base,
                             pitch=CHOC_PITCH, well_size=CHOC_KEY_SIZE)

# Bottom 4 choc keys
choc_y_bot = choc_y_base - CHOC_PITCH
right_case = create_key_grid(right_case, choc_bot_cols, 1,
                             x_offset=trackball_x, y_offset=choc_y_bot,
                             pitch=CHOC_PITCH, well_size=CHOC_KEY_SIZE)


# === Assemble all units ===
# Position units in a row: left - center - right

# Calculate positions (center unit at origin)
center_x = 0
left_x = -(center_case_width / 2 + UNIT_GAP + left_case_width / 2)
right_x = center_case_width / 2 + UNIT_GAP + right_case_width / 2

left_placed = left_case.translate((left_x, 0, 0))
center_placed = center_case.translate((center_x, 0, 0))
right_placed = right_case.translate((right_x, 0, 0))
trackball_placed = trackball.translate((right_x, 0, 0))

# Combine all
assembly = left_placed.union(center_placed).union(right_placed).union(trackball_placed)


# === Export STEP ===
cq.exporters.export(assembly, "cad/mockup_v2.step")
print("✓ Exported cad/mockup_v2.step")

# === Export STL ===
cq.exporters.export(assembly, "cad/mockup_v2.stl")
print("✓ Exported cad/mockup_v2.stl")

# === Export SVG projections ===
# # Top view
# svg_top = (
#     cq.exporters.export(assembly, "cad/mockup_v2_top.svg",
#                        opt={'width': 800, 'height': 400,
#                             'marginLeft': 50, 'marginTop': 50,
#                             'projectionDir': (0, 0, 1)})
# )
# print("✓ Exported cad/mockup_v2_top.svg")

# # Front view
# svg_front = (
#     cq.exporters.export(assembly, "cad/mockup_v2_front.svg",
#                        opt={'width': 800, 'height': 300,
#                             'marginLeft': 50, 'marginTop': 50,
#                             'projectionDir': (0, 1, 0)})
# )
# print("✓ Exported cad/mockup_v2_front.svg")

# # Isometric view
# svg_iso = (
#     cq.exporters.export(assembly, "cad/mockup_v2_iso.svg",
#                        opt={'width': 800, 'height': 600,
#                             'marginLeft': 50, 'marginTop': 50,
#                             'projectionDir': (1, -1, 0.5)})
# )
# print("✓ Exported cad/mockup_v2_iso.svg")

print("\n=== OrthBall v2 Mockup Complete ===")
print(f"Left:   {left_main_cols}x{left_main_rows} + {left_thumb_keys} thumb = {left_main_cols*left_main_rows + left_thumb_keys} keys")
print(f"Center: {center_cols}x{center_rows} = {center_cols*center_rows} keys")
print(f"Right:  {right_main_cols}x{right_main_rows} + {right_thumb_keys} thumb + 6 Choc + 55mm ball = {right_main_cols*right_main_rows + right_thumb_keys + 6} keys + ball")
print(f"Total:  {(left_main_cols*left_main_rows + left_thumb_keys) + (center_cols*center_rows) + (right_main_cols*right_main_rows + right_thumb_keys + 6)} keys + trackball")
