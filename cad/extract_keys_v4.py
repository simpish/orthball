#!/usr/bin/env python3
"""Extract key positions from orthball_plate_v4.svg for KiCad PCB layout."""
import re, json, math

# SVG is in Affinity/Serif coordinate system with matrix(1,0,0,-1,0.238,380.456) transform
# This means Y is flipped. Actual Y = 380.456 - svg_y

# MX keys are 39.684 wide (≈40 SVG units), pitch ≈ 54.032 SVG units
# SVG unit to mm: the viewBox is 1111.181 wide, and keys are at 19.05mm pitch
# Key pitch in SVG: ~54 units → 19.05mm → 1 SVG unit ≈ 0.353mm

SCALE = 19.05 / 54.032  # SVG units to mm

# Parse all rect elements from the plate path (ページ1, first g group)
# MX keys: 39.684 wide squares (e.g., "614.966,251.492 to 575.282,291.176" = 39.684 x 39.684)
# Choc keys: smaller rounded rects with explicit C/L paths (e.g., 794.371 to 827.821 = 33.45 wide)

# MX key positions (center of each key) - extracted from SVG rect coordinates
# Format: (x_center, y_center) in SVG coords, then convert to mm
mx_keys = []
choc_keys = []
thumb_keys = []

# Parse from the SVG - MX keys are defined as "Mx,y Lx2,y2" rect patterns
# Let me extract all rect-like patterns from the path data

svg_rects = """
614.966,251.492 575.282,291.176
479.95,197.524 440.266,237.208
425.95,143.524 386.266,183.208
425.95,251.492 386.266,291.176
479.95,143.524 440.266,183.208
668.966,251.492 629.282,291.176
668.966,197.524 629.282,237.208
884.934,197.524 845.25,237.208
830.934,197.524 791.25,237.208
830.934,251.492 791.25,291.176
776.934,197.524 737.25,237.208
776.934,89.492 737.25,129.176
668.966,143.524 629.282,183.208
722.966,143.524 683.282,183.208
776.934,143.524 737.25,183.208
776.934,251.492 737.25,291.176
830.934,143.524 791.25,183.208
614.966,197.524 575.282,237.208
884.934,251.492 845.25,291.176
722.966,197.524 683.282,237.208
290.966,197.524 251.282,237.208
128.966,251.492 89.282,291.176
74.934,197.524 35.25,237.208
344.966,143.524 305.282,183.208
425.95,197.524 386.266,237.208
74.934,89.492 35.25,129.176
290.966,251.492 251.282,291.176
290.966,143.524 251.282,183.208
74.934,251.492 35.25,291.176
344.966,251.492 305.282,291.176
128.966,197.524 89.282,237.208
614.966,143.524 575.282,183.208
128.966,89.492 89.282,129.176
344.966,197.524 305.282,237.208
479.95,89.492 440.266,129.176
182.934,251.492 143.25,291.176
533.95,143.524 494.266,183.208
74.934,143.524 35.25,183.208
533.95,251.492 494.266,291.176
182.934,197.524 143.25,237.208
182.934,89.492 143.25,129.176
128.966,143.524 89.282,183.208
236.966,251.492 197.282,291.176
479.95,251.492 440.266,291.176
182.934,143.524 143.25,183.208
236.966,143.524 197.282,183.208
236.966,197.524 197.282,237.208
884.934,143.524 845.25,183.208
533.95,197.524 494.266,237.208
722.966,251.492 683.282,291.176
"""

# Choc keys (smaller, with rounded corners in the SVG path)
choc_rects = """
902.399,128.895 935.848,89.774
1010.229,128.895 1043.678,89.774
956.399,128.895 989.848,89.774
794.371,128.895 827.821,89.774
848.399,128.895 881.848,89.774
"""

# Thumb keys (rotated, defined with transform)
thumb_data = """
568.927,105.498 588.774,71.134 554.41,51.286 534.563,85.651
629.631,125.25 643.179,87.95 605.88,74.402 592.331,111.701
695.369,127.56 655.685,87.876
348.857,104.367 329.01,70.003 363.374,50.155 383.221,84.519
290.553,126.518 277.005,89.219 314.304,75.67 327.853,112.97
224.815,128.829 264.499,89.145
"""

# Y flip: actual_y = 380.456 - svg_y
Y_ORIGIN = 380.456

def parse_rect(line):
    parts = line.strip().split()
    if len(parts) != 2:
        return None
    x1, y1 = map(float, parts[0].split(','))
    x2, y2 = map(float, parts[1].split(','))
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    return cx, cy

keys = []
for line in svg_rects.strip().split('\n'):
    result = parse_rect(line)
    if result:
        cx, cy = result
        # Convert to mm (relative to origin)
        x_mm = cx * SCALE
        y_mm = (Y_ORIGIN - cy) * SCALE  # flip Y
        keys.append({"type": "MX", "x_mm": round(x_mm, 2), "y_mm": round(y_mm, 2), "svg_x": cx, "svg_y": cy})

chocs = []
for line in choc_rects.strip().split('\n'):
    result = parse_rect(line)
    if result:
        cx, cy = result
        x_mm = cx * SCALE
        y_mm = (Y_ORIGIN - cy) * SCALE
        chocs.append({"type": "Choc", "x_mm": round(x_mm, 2), "y_mm": round(y_mm, 2), "svg_x": cx, "svg_y": cy})

# Sort keys by position for readability
keys.sort(key=lambda k: (round(k['y_mm']/19, 0), k['x_mm']))
chocs.sort(key=lambda k: k['x_mm'])

output = {
    "info": "OrthBall V1 key positions extracted from v4 SVG",
    "scale": f"1 SVG unit = {SCALE:.4f} mm",
    "mx_keys": keys,
    "choc_keys": chocs,
    "total_mx": len(keys),
    "total_choc": len(chocs),
    "total": len(keys) + len(chocs)
}

print(json.dumps(output, indent=2))
