#!/usr/bin/env python3
"""
Convert OrthBall plate SVG outline + key positions to KiCad Edge.Cuts.

Parses orthball_plate_v7_outline.svg for the organic outer contour,
and orthball_keys_v7.json for key hole positions.

Coordinate pipeline:
  SVG path (raw) → apply SVG transform → display coords → mm → KiCad PCB coords

SVG inner transform: matrix(0.839222, 0, 0, -0.603249, 86.001784, 289.882793)
  display_x = 0.839222 * raw_x + 86.001784
  display_y = -0.603249 * raw_y + 289.882793

Display coords → mm (from orthball_keys_v7.json):
  x_mm = display_x * path_to_mm_scale (0.352569)
  y_mm = (y_flip_origin - display_y) * path_to_mm_scale

mm → KiCad:
  kx = x_mm + OFFSET_X
  ky = y_mm + OFFSET_Y  (no flip, matches SVG visual orientation)
"""

import json
import os
import re
import math

KEYS_JSON = os.path.join(os.path.dirname(__file__), "..", "..", "cad", "orthball_keys_v7.json")
OUTLINE_SVG = os.path.join(os.path.dirname(__file__), "..", "..", "cad", "orthball_plate_v7_outline.svg")
OUTPUT_PCB = os.path.join(os.path.dirname(__file__), "..", "orthball.kicad_pcb")

OFFSET_X = 10.0
OFFSET_Y = 10.0

MX_HOLE = 14.0
CHOC_HOLE = 13.8

# From orthball_keys_v7.json coordinate_system:
# JSON x_path/y_path and SVG raw path coords are in the SAME space.
# No SVG transform needed - convert raw coords directly to mm.
PATH_TO_MM = 0.352569
Y_FLIP_ORIGIN = 301.184


def load_keys():
    with open(KEYS_JSON, "r") as f:
        return json.load(f)


def svg_raw_to_kicad(x, y):
    """Convert SVG raw path coords → mm → KiCad PCB coords.

    Same coordinate space as JSON x_path/y_path. No SVG transform needed.
    x_mm = raw_x * scale
    y_mm = (y_flip_origin - raw_y) * scale
    """
    x_mm = x * PATH_TO_MM
    y_mm = (Y_FLIP_ORIGIN - y) * PATH_TO_MM
    return x_mm + OFFSET_X, y_mm + OFFSET_Y


def json_to_kicad(x_mm, y_mm):
    """Convert JSON mm coordinates to KiCad PCB coordinates."""
    return x_mm + OFFSET_X, y_mm + OFFSET_Y


# ---- SVG Path Parser ----

def parse_svg_path(d):
    """Parse SVG path data string into a list of (command, points) tuples."""
    # Tokenize: split into commands and numbers
    tokens = re.findall(r'[MmLlCcSsQqTtAaHhVvZz]|[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?', d)

    segments = []
    i = 0
    current_cmd = None

    while i < len(tokens):
        if tokens[i].isalpha():
            current_cmd = tokens[i]
            i += 1
        # Read numbers based on command type
        if current_cmd in ('M', 'L'):
            x, y = float(tokens[i]), float(tokens[i+1])
            segments.append((current_cmd, [(x, y)]))
            if current_cmd == 'M':
                current_cmd = 'L'  # implicit lineto after moveto
            i += 2
        elif current_cmd in ('m', 'l'):
            x, y = float(tokens[i]), float(tokens[i+1])
            segments.append((current_cmd, [(x, y)]))
            if current_cmd == 'm':
                current_cmd = 'l'
            i += 2
        elif current_cmd == 'C':
            x1, y1 = float(tokens[i]), float(tokens[i+1])
            x2, y2 = float(tokens[i+2]), float(tokens[i+3])
            x, y = float(tokens[i+4]), float(tokens[i+5])
            segments.append(('C', [(x1, y1), (x2, y2), (x, y)]))
            i += 6
        elif current_cmd == 'c':
            x1, y1 = float(tokens[i]), float(tokens[i+1])
            x2, y2 = float(tokens[i+2]), float(tokens[i+3])
            x, y = float(tokens[i+4]), float(tokens[i+5])
            segments.append(('c', [(x1, y1), (x2, y2), (x, y)]))
            i += 6
        elif current_cmd in ('Z', 'z'):
            segments.append(('Z', []))
            break
        elif current_cmd == 'H':
            x = float(tokens[i])
            segments.append(('H', [(x,)]))
            i += 1
        elif current_cmd == 'V':
            y = float(tokens[i])
            segments.append(('V', [(y,)]))
            i += 1
        else:
            i += 1  # skip unknown

    return segments


def cubic_bezier_point(p0, p1, p2, p3, t):
    """Evaluate cubic bezier at parameter t."""
    u = 1 - t
    x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
    y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
    return x, y


def linearize_bezier(p0, p1, p2, p3, n_steps=16):
    """Convert cubic bezier to line segments."""
    points = []
    for i in range(n_steps + 1):
        t = i / n_steps
        points.append(cubic_bezier_point(p0, p1, p2, p3, t))
    return points


def svg_path_to_kicad_points(path_d):
    """Parse SVG path and convert all segments to KiCad coordinate points."""
    segments = parse_svg_path(path_d)
    kicad_lines = []  # list of (start, end) tuples in KiCad coords
    current = None
    start_point = None

    for cmd, pts in segments:
        if cmd == 'M':
            current = pts[0]
            start_point = current
        elif cmd == 'L':
            end = pts[0]
            p1 = svg_raw_to_kicad(*current)
            p2 = svg_raw_to_kicad(*end)
            kicad_lines.append((p1, p2))
            current = end
        elif cmd == 'C':
            cp1, cp2, end = pts
            bezier_pts = linearize_bezier(current, cp1, cp2, end, n_steps=20)
            for i in range(len(bezier_pts) - 1):
                p1 = svg_raw_to_kicad(*bezier_pts[i])
                p2 = svg_raw_to_kicad(*bezier_pts[i + 1])
                kicad_lines.append((p1, p2))
            current = end
        elif cmd == 'Z':
            if current and start_point and current != start_point:
                p1 = svg_raw_to_kicad(*current)
                p2 = svg_raw_to_kicad(*start_point)
                kicad_lines.append((p1, p2))

    return kicad_lines


def load_outline_svg():
    """Load and extract the path data from the outline SVG."""
    import xml.etree.ElementTree as ET
    tree = ET.parse(OUTLINE_SVG)
    root = tree.getroot()
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    # Find the path element
    for path_elem in root.iter('{http://www.w3.org/2000/svg}path'):
        d = path_elem.get('d')
        if d:
            return d
    raise RuntimeError("No path found in outline SVG")


# ---- Edge.Cuts Generators ----

def generate_rect_edgecuts(cx, cy, w, h, rotation_deg=0):
    """Generate Edge.Cuts lines for a rectangular hole."""
    if abs(rotation_deg) < 0.1:
        x1 = cx - w / 2
        y1 = cy - h / 2
        x2 = cx + w / 2
        y2 = cy + h / 2
        lines = [((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)),
                 ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))]
    else:
        angle = math.radians(rotation_deg)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        hw, hh = w / 2, h / 2
        corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        rotated = [(cx + x * cos_a - y * sin_a, cy + x * sin_a + y * cos_a)
                   for x, y in corners]
        lines = [(rotated[i], rotated[(i + 1) % 4]) for i in range(4)]

    result = []
    for (x1, y1), (x2, y2) in lines:
        result.append(f'''\t(gr_line
\t\t(start {x1:.4f} {y1:.4f})
\t\t(end {x2:.4f} {y2:.4f})
\t\t(stroke (width 0.1) (type solid))
\t\t(layer "Edge.Cuts")
\t)''')
    return "\n".join(result)


def lines_to_edgecuts(kicad_lines):
    """Convert list of ((x1,y1),(x2,y2)) to Edge.Cuts gr_line entries."""
    result = []
    for (x1, y1), (x2, y2) in kicad_lines:
        result.append(f'''\t(gr_line
\t\t(start {x1:.4f} {y1:.4f})
\t\t(end {x2:.4f} {y2:.4f})
\t\t(stroke (width 0.1) (type solid))
\t\t(layer "Edge.Cuts")
\t)''')
    return "\n".join(result)


# ---- Main PCB Generator ----

def generate_pcb():
    data = load_keys()
    keys = data["keys"]

    edgecuts = []

    # Outer contour from SVG
    print("Parsing outline SVG...")
    path_d = load_outline_svg()
    outline_lines = svg_path_to_kicad_points(path_d)
    print(f"  {len(outline_lines)} line segments from SVG outline")
    edgecuts.append(lines_to_edgecuts(outline_lines))

    # Key holes from JSON
    for k in keys:
        cx, cy = json_to_kicad(k["x_mm"], k["y_mm"])
        if k["type"] == "oled":
            edgecuts.append(generate_rect_edgecuts(
                cx, cy, k["width_mm"], k["height_mm"], k.get("rotation_deg", 0)
            ))
        elif k["type"] == "choc":
            edgecuts.append(generate_rect_edgecuts(
                cx, cy, CHOC_HOLE, CHOC_HOLE, k.get("rotation_deg", 0)
            ))
        else:  # mx
            edgecuts.append(generate_rect_edgecuts(
                cx, cy, MX_HOLE, MX_HOLE, k.get("rotation_deg", 0)
            ))

    edgecuts_str = "\n".join(edgecuts)

    pcb = f'''(kicad_pcb
\t(version 20240108)
\t(generator "orthball_gen")
\t(generator_version "9.0")
\t(general
\t\t(thickness 1.6)
\t\t(legacy_teardrops no)
\t)
\t(paper "A3")
\t(layers
\t\t(0 "F.Cu" signal)
\t\t(31 "B.Cu" signal)
\t\t(32 "B.Adhes" user "B.Adhesive")
\t\t(33 "F.Adhes" user "F.Adhesive")
\t\t(34 "B.Paste" user)
\t\t(35 "F.Paste" user)
\t\t(36 "B.SilkS" user "B.Silkscreen")
\t\t(37 "F.SilkS" user "F.Silkscreen")
\t\t(38 "B.Mask" user "B.Mask")
\t\t(39 "F.Mask" user "F.Mask")
\t\t(40 "Dwgs.User" user "User.Drawings")
\t\t(41 "Cmts.User" user "User.Comments")
\t\t(42 "Eco1.User" user "User.Eco1")
\t\t(43 "Eco2.User" user "User.Eco2")
\t\t(44 "Edge.Cuts" user)
\t\t(45 "Margin" user)
\t\t(46 "B.CrtYd" user "B.Courtyard")
\t\t(47 "F.CrtYd" user "F.Courtyard")
\t\t(48 "B.Fab" user "B.Fabrication")
\t\t(49 "F.Fab" user "F.Fabrication")
\t\t(50 "User.1" user)
\t\t(51 "User.2" user)
\t)
\t(setup
\t\t(pad_to_mask_clearance 0)
\t\t(allow_soldermask_bridges_in_footprints no)
\t\t(pcbplotparams
\t\t\t(layerselection 0x00010fc_ffffffff)
\t\t\t(plot_on_all_layers_selection 0x0000000_00000000)
\t\t\t(disableapertmacros no)
\t\t\t(usegerberextensions no)
\t\t\t(usegerberattributes yes)
\t\t\t(usegerberadvancedattributes yes)
\t\t\t(creategerberjobfile yes)
\t\t\t(svgprecision 4)
\t\t\t(excludeedgelayer yes)
\t\t\t(plotframeref no)
\t\t\t(viasonmask no)
\t\t\t(mode 1)
\t\t\t(useauxorigin no)
\t\t\t(hpglpennumber 1)
\t\t\t(hpglpenspeed 20)
\t\t\t(hpglpendiameter 15.000000)
\t\t\t(pdf_front_fp_property_popups yes)
\t\t\t(pdf_back_fp_property_popups yes)
\t\t\t(dxf_units_type 0)
\t\t\t(plotvalue yes)
\t\t\t(plotreference yes)
\t\t\t(plotfptext yes)
\t\t\t(plotinvisibletext no)
\t\t\t(sketchpadsonfab no)
\t\t\t(subtractmaskfromsilk no)
\t\t\t(outputformat 1)
\t\t\t(mirror no)
\t\t\t(drillshape 1)
\t\t\t(scaleselection 1)
\t\t\t(outputdirectory "gerber/")
\t\t)
\t)
\t(net 0 "")
{edgecuts_str}
)
'''
    return pcb


def main():
    pcb = generate_pcb()
    with open(OUTPUT_PCB, "w") as f:
        f.write(pcb)
    print(f"Generated PCB: {OUTPUT_PCB}")


if __name__ == "__main__":
    main()
