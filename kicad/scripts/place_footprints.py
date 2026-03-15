#!/usr/bin/env python3
"""
Place footprints on the OrthBall V1 PCB based on orthball_keys_v7.json.

This script reads the generated .kicad_pcb file and adds footprint
placements for all components:
- 51 MX switches (front side, with key holes)
- 5 Choc switches (front side)
- 56 diodes (back side, SOD-123)
- 1 RP2040-Zero (back side, USB-C at PCB edge)
- 1 PMW3360 header (back side, near trackball)
- 1 OLED header (back side, at OLED opening)
- 6 M2 mounting holes

Coordinate transform (JSON → KiCad PCB):
  JSON: origin at bottom-left, Y increases upward
  KiCad: origin at top-left, Y increases downward
  kicad_x = json_x + OFFSET_X
  kicad_y = json_y + OFFSET_Y  (no flip - matches SVG visual orientation)

Usage:
  python3 place_footprints.py

This will modify orthball.kicad_pcb in place, adding footprints.
Make sure to run svg_to_edgecuts.py first to generate the base PCB.
"""

import json
import os
import re
import math
import uuid as uuid_mod

KEYS_JSON = os.path.join(os.path.dirname(__file__), "..", "..", "cad", "orthball_keys_v7.json")
PCB_FILE = os.path.join(os.path.dirname(__file__), "..", "orthball.kicad_pcb")

OFFSET_X = 10.0
OFFSET_Y = 10.0

# Diode offset from switch center (mm)
DIODE_OFFSET_X = 0.0
DIODE_OFFSET_Y = 5.5  # Below the switch in KiCad coords (positive = down)


def uid():
    return str(uuid_mod.uuid4())


def load_keys():
    with open(KEYS_JSON, "r") as f:
        return json.load(f)


def json_to_kicad(x_mm, y_mm):
    """Convert JSON coords to KiCad. No Y flip - matches SVG visual orientation."""
    return x_mm + OFFSET_X, y_mm + OFFSET_Y


def generate_footprint_entry(ref, fp_lib, x, y, rotation=0, layer="F.Cu", value=""):
    """Generate a footprint placement entry for the PCB file."""
    return f'''\t(footprint "{fp_lib}"
\t\t(layer "{layer}")
\t\t(uuid "{uid()}")
\t\t(at {x:.4f} {y:.4f} {rotation:.1f})
\t\t(property "Reference" "{ref}"
\t\t\t(at 0 -2 0)
\t\t\t(layer "{layer.replace('.Cu', '.SilkS')}")
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(property "Value" "{value}"
\t\t\t(at 0 2 0)
\t\t\t(layer "{layer.replace('.Cu', '.Fab')}")
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t)'''


def main():
    data = load_keys()
    keys = data["keys"]
    trackballs = data.get("trackballs", [])
    print(f"Keys: {len([k for k in keys if k['type'] != 'oled'])} switches")

    footprints = []
    # Note: KiCad PCB S-expression does not support ;; comments

    sw_num = 1
    d_num = 1
    oled_entry = None

    for k in keys:
        if k["type"] == "oled":
            # OLED position - place header nearby
            ox, oy = json_to_kicad(k["x_mm"], k["y_mm"])
            oled_entry = (ox, oy)
            continue

        cx, cy = json_to_kicad(k["x_mm"], k["y_mm"])
        rot = -k.get("rotation_deg", 0)  # Negate for KiCad convention

        if k["type"] == "choc":
            fp_lib = "marbastlib-choc:SW_choc_v1_HS_CPG135001S30_1u"
        else:
            fp_lib = "marbastlib-mx:SW_MX_HS_CPG151101S11_1u"

        footprints.append(generate_footprint_entry(
            f"SW{sw_num}", fp_lib, cx, cy, rot, "F.Cu", "SW_Push"
        ))

        # Diode placed on back side, offset from switch center
        # Rotate diode offset by switch rotation
        rad = math.radians(k.get("rotation_deg", 0))
        dx = DIODE_OFFSET_X * math.cos(rad) - DIODE_OFFSET_Y * math.sin(rad)
        dy = DIODE_OFFSET_X * math.sin(rad) + DIODE_OFFSET_Y * math.cos(rad)
        # Note: in KiCad, positive Y is down, so we don't negate dy for the offset
        diode_x = cx + dx
        diode_y = cy + dy  # dy is already in KiCad direction

        footprints.append(generate_footprint_entry(
            f"D{d_num}", "Diode_SMD:D_SOD-123", diode_x, diode_y, rot, "B.Cu", "1N4148W"
        ))

        sw_num += 1
        d_num += 1

    # RP2040-Zero: place at top center of PCB, back side
    # USB-C should face the top edge
    mcu_x = OFFSET_X + 150  # Approximate center-ish position
    mcu_y = OFFSET_Y + 5    # Near top edge
    footprints.append(generate_footprint_entry(
        "U1", "orthball:RP2040-Zero", mcu_x, mcu_y, 0, "B.Cu", "RP2040-Zero"
    ))

    # PMW3360 header: near trackball opening
    if trackballs:
        tb = trackballs[0]
        tb_x, tb_y = json_to_kicad(tb["x_mm"], tb["y_mm"])
        pmw_x = tb_x - 30  # Left of trackball
        pmw_y = tb_y
    else:
        pmw_x = OFFSET_X + 330
        pmw_y = OFFSET_Y + 50

    footprints.append(generate_footprint_entry(
        "J1", "Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Vertical",
        pmw_x, pmw_y, 0, "B.Cu", "PMW3360"
    ))

    # OLED header: at OLED opening
    if oled_entry:
        oled_x, oled_y = oled_entry
    else:
        oled_x = OFFSET_X + 160
        oled_y = OFFSET_Y + 80

    footprints.append(generate_footprint_entry(
        "J2", "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
        oled_x, oled_y + 10, 0, "B.Cu", "OLED_SSD1306"
    ))

    # Mounting holes: 6 positions at corners and center
    # Estimate board extents
    all_x = [k["x_mm"] for k in keys]
    all_y = [k["y_mm"] for k in keys]
    board_x1, board_x2 = min(all_x) - 5, max(all_x) + 20
    board_y1, board_y2 = min(all_y) - 5, max(all_y) + 10

    mount_positions = [
        (board_x1 + 5, board_y1 + 5),    # Bottom-left
        (board_x2 - 5, board_y1 + 5),    # Bottom-right
        (board_x1 + 5, board_y2 - 5),    # Top-left
        (board_x2 - 5, board_y2 - 5),    # Top-right
        ((board_x1 + board_x2) / 2, board_y1 + 5),  # Bottom-center
        ((board_x1 + board_x2) / 2, board_y2 - 5),  # Top-center
    ]

    for i, (mx, my) in enumerate(mount_positions):
        kx, ky = json_to_kicad(mx, my)
        footprints.append(generate_footprint_entry(
            f"H{i+1}", "MountingHole:MountingHole_2.2mm_M2",
            kx, ky, 0, "F.Cu", "M2"
        ))

    # Insert footprints into PCB file
    footprints_str = "\n".join(footprints)

    with open(PCB_FILE, "r") as f:
        pcb_content = f.read()

    # Insert before the closing parenthesis
    pcb_content = pcb_content.rstrip()
    if pcb_content.endswith(")"):
        pcb_content = pcb_content[:-1] + "\n" + footprints_str + "\n)\n"

    with open(PCB_FILE, "w") as f:
        f.write(pcb_content)

    print(f"Placed footprints in: {PCB_FILE}")
    print(f"  - {sw_num - 1} switches")
    print(f"  - {d_num - 1} diodes")
    print(f"  - 1 RP2040-Zero MCU")
    print(f"  - 1 PMW3360 header")
    print(f"  - 1 OLED header")
    print(f"  - 6 mounting holes")
    print()
    print("Next steps:")
    print("  1. Open orthball.kicad_pcb in KiCad")
    print("  2. Import netlist from schematic")
    print("  3. Adjust footprint positions as needed")
    print("  4. Route traces")


if __name__ == "__main__":
    main()
