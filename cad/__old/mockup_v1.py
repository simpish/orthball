import cadquery as cq

# === Constants ===
MX_PITCH = 19.05
CASE_HEIGHT = 17.0
CASE_WALL = 3.0
CASE_BOTTOM = 2.0
KEY_RECESS_DEPTH = 1.5
TRACKBALL_DIA = 55.0
UNIT_GAP = 30.0

# === Helper: create a case box with key area recess ===
def make_case(width, depth, key_cols, key_rows, extra_features=None):
    key_w = key_cols * MX_PITCH
    key_d = key_rows * MX_PITCH
    case = (
        cq.Workplane("XY")
        .box(width, depth, CASE_HEIGHT, centered=(True, True, False))
    )
    # recess for key area (centered)
    case = (
        case.faces(">Z").workplane()
        .rect(key_w, key_d)
        .cutBlind(-KEY_RECESS_DEPTH)
    )
    return case

# === Left Hand Unit ===
# 6col x 3row + thumb cluster (5 keys in a row below)
left_key_w = 6 * MX_PITCH  # 114.3
left_key_d = 3 * MX_PITCH  # 57.15
thumb_w = 5 * MX_PITCH      # 95.25
thumb_d = 1 * MX_PITCH      # 19.05

left_width = left_key_w + CASE_WALL * 2
left_depth = left_key_d + thumb_d + CASE_WALL * 2 + 5  # extra space for thumb

left = (
    cq.Workplane("XY")
    .box(left_width, left_depth, CASE_HEIGHT, centered=(True, True, False))
)
# Main key recess
left = (
    left.faces(">Z").workplane()
    .center(0, thumb_d / 2 + 2)
    .rect(left_key_w, left_key_d)
    .cutBlind(-KEY_RECESS_DEPTH)
)
# Thumb cluster recess
left = (
    left.faces(">Z").workplane()
    .center(0, -(left_key_d / 2) - 2)
    .rect(thumb_w, thumb_d)
    .cutBlind(-KEY_RECESS_DEPTH)
)

# === Center Numpad Unit ===
center_key_w = 3 * MX_PITCH  # 57.15
center_key_d = 4 * MX_PITCH  # 76.2
center_width = center_key_w + CASE_WALL * 2
center_depth = center_key_d + CASE_WALL * 2

center = make_case(center_width, center_depth, 3, 4)

# === Right Hand Unit ===
# 6col x 3row + thumb(5) + trackball + choc 6 keys
right_key_w = 6 * MX_PITCH
right_key_d = 3 * MX_PITCH
trackball_r = TRACKBALL_DIA / 2.0

# Right unit needs extra width for trackball area
trackball_area_w = TRACKBALL_DIA + 10  # some margin
right_width = right_key_w + trackball_area_w + CASE_WALL * 2
right_depth = left_depth  # same as left for symmetry

right = (
    cq.Workplane("XY")
    .box(right_width, right_depth, CASE_HEIGHT, centered=(True, True, False))
)

# Main key recess (shifted left to make room for trackball)
key_offset_x = -(trackball_area_w / 2)
right = (
    right.faces(">Z").workplane()
    .center(key_offset_x, thumb_d / 2 + 2)
    .rect(right_key_w, right_key_d)
    .cutBlind(-KEY_RECESS_DEPTH)
)

# Thumb cluster recess
right = (
    right.faces(">Z").workplane()
    .center(key_offset_x, -(right_key_d / 2) - 2)
    .rect(thumb_w, thumb_d)
    .cutBlind(-KEY_RECESS_DEPTH)
)

# Trackball socket - cut a spherical cavity, ball exposed 65%
# Ball center is below the top surface
expose_frac = 0.65
ball_center_z = CASE_HEIGHT - trackball_r * (2 * expose_frac - 1)
trackball_x = right_width / 2 - trackball_area_w / 2
trackball_y = right_depth / 2 - TRACKBALL_DIA / 2 - 5  # top-right area

trackball_sphere = (
    cq.Workplane("XY")
    .transformed(offset=(trackball_x, trackball_y, ball_center_z))
    .sphere(trackball_r)
)
right = right.cut(trackball_sphere)

# Trackball (the ball itself) - visual
ball = (
    cq.Workplane("XY")
    .transformed(offset=(trackball_x, trackball_y, ball_center_z))
    .sphere(trackball_r - 0.5)  # slightly smaller to sit in socket
)

# Choc 6 keys recess below trackball (2 top + 4 bottom)
choc_pitch = 18.0  # Choc spacing
choc_w_top = 2 * choc_pitch
choc_w_bot = 4 * choc_pitch
choc_h = 16.0  # single row height

# Top 2 choc keys
right = (
    right.faces(">Z").workplane()
    .center(trackball_x, trackball_y - trackball_r - choc_h / 2 - 3)
    .rect(choc_w_top, choc_h)
    .cutBlind(-KEY_RECESS_DEPTH)
)
# Bottom 4 choc keys  
right = (
    right.faces(">Z").workplane()
    .center(trackball_x, trackball_y - trackball_r - choc_h - choc_h / 2 - 6)
    .rect(choc_w_bot, choc_h)
    .cutBlind(-KEY_RECESS_DEPTH)
)

# === Arrange units on desk ===
# Left unit on the left, center in middle, right on the right
left_total_w = left_width
center_total_w = center_width
right_total_w = right_width

# Positions (x centers)
left_x = -(left_total_w / 2 + UNIT_GAP + center_total_w / 2 + UNIT_GAP + right_total_w / 2) / 2
# Simpler: place center at origin
center_x = 0
left_x = -(center_total_w / 2 + UNIT_GAP + left_total_w / 2)
right_x = center_total_w / 2 + UNIT_GAP + right_total_w / 2

left_placed = left.translate((left_x, 0, 0))
center_placed = center.translate((center_x, 0, 0))
right_placed = right.translate((right_x, 0, 0))
ball_placed = ball.translate((right_x, 0, 0))

# === Combine and export ===
assembly = left_placed.union(center_placed).union(right_placed).union(ball_placed)

cq.exporters.export(assembly, "cad/mockup_v1.step")
print("Exported cad/mockup_v1.step successfully!")
