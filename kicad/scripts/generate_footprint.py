#!/usr/bin/env python3
"""
Generate RP2040-Zero KiCad footprint with all 29 GPIO pins.

Physical layout (WaveShare RP2040-Zero):
- Module: 18mm x 23.5mm
- USB-C at top
- Right side (10 THT pins, 2.54mm pitch): GP0-GP9
- Left side (10 THT pins, 2.54mm pitch): 5V, GND, 3V3, GP29-GP26, GP15-GP13
- Bottom edge (9 castellated SMD pads): GP16-GP23, GND

NOTE: Pin positions are approximate and MUST be verified against the physical
module with calipers before ordering PCBs. Print the footprint 1:1 and
place the real module on it to confirm alignment.

When back-mounted (component on B.Cu):
- The module is flipped, so left/right are mirrored
- Through-hole pads go through both layers
- Castellated pads are SMD on B.Cu only
"""

import os
import uuid as uuid_mod

def uid():
    return str(uuid_mod.uuid4())

# Module dimensions (mm) - VERIFY WITH PHYSICAL MEASUREMENT
MODULE_W = 18.0    # Width
MODULE_H = 23.5    # Height (USB-C at top = most negative Y)
ROW_SPACING = 15.24  # Distance between left and right pin rows
PIN_PITCH = 2.54    # Through-hole pin pitch
N_SIDE_PINS = 10    # Pins per side
N_BOTTOM_PADS = 9   # Castellated pads on bottom edge
BOTTOM_PAD_PITCH = 1.5  # Pitch of bottom castellated pads

# Origin: bottom-left corner of module outline, Y increases upward logically
# but in KiCad footprint coords, Y increases downward.
# We'll place origin at the center of pin 1 for convenience.
# Pin 1 is at top-right when looking from front (back-mounted = top-left from back view).

# For simplicity, use module bottom-left as (0, 0), top edge at y = -MODULE_H
# Pin columns at x = (MODULE_W - ROW_SPACING) / 2 and x = MODULE_W - margin
MARGIN = (MODULE_W - ROW_SPACING) / 2  # 1.38mm

# Right side pin positions (GP0-GP9), pin 1 at top
RIGHT_X = MODULE_W - MARGIN  # 16.62mm
# First pin Y: 1.27mm below top edge
FIRST_PIN_Y = -(MODULE_H - 1.27)  # -22.23mm from bottom origin

# Left side pin positions (5V, GND, 3V3, GP29-GP26, GP15-GP13)
LEFT_X = MARGIN  # 1.38mm

# Bottom castellated pad positions
# Centered on module width, starting from left
BOTTOM_Y = 0.0  # At bottom edge
bottom_total_span = (N_BOTTOM_PADS - 1) * BOTTOM_PAD_PITCH
bottom_start_x = (MODULE_W - bottom_total_span) / 2


def generate_footprint():
    lines = []

    lines.append(f'''(footprint "RP2040-Zero"
\t(version 20241229)
\t(generator "orthball_gen")
\t(generator_version "9.0")
\t(layer "B.Cu")
\t(descr "WaveShare RP2040-Zero, 18x23.5mm, 20 THT + 9 castellated, back-mounted. VERIFY DIMENSIONS WITH PHYSICAL MODULE.")
\t(tags "RP2040 Zero WaveShare microcontroller")
\t(property "Reference" "U1"
\t\t(at {MODULE_W/2:.2f} {-MODULE_H/2:.2f} 0)
\t\t(layer "B.SilkS")
\t\t(uuid "{uid()}")
\t\t(effects (font (size 1 1) (thickness 0.15)) (justify mirror))
\t)
\t(property "Value" "RP2040-Zero"
\t\t(at {MODULE_W/2:.2f} {-MODULE_H/2 + 2:.2f} 0)
\t\t(layer "B.Fab")
\t\t(uuid "{uid()}")
\t\t(effects (font (size 1 1) (thickness 0.15)) (justify mirror))
\t)
\t(property "Footprint" "orthball:RP2040-Zero"
\t\t(at 0 0 0)
\t\t(layer "B.Fab")
\t\t(hide yes)
\t\t(uuid "{uid()}")
\t\t(effects (font (size 1.27 1.27) (thickness 0.15)))
\t)
\t(property "Datasheet" "https://www.waveshare.com/wiki/RP2040-Zero"
\t\t(at 0 0 0)
\t\t(layer "B.Fab")
\t\t(hide yes)
\t\t(uuid "{uid()}")
\t\t(effects (font (size 1.27 1.27) (thickness 0.15)))
\t)
\t(property "Description" "WaveShare RP2040-Zero, back-mounted, 29 GPIO"
\t\t(at 0 0 0)
\t\t(layer "B.Fab")
\t\t(hide yes)
\t\t(uuid "{uid()}")
\t\t(effects (font (size 1.27 1.27) (thickness 0.15)))
\t)
\t(attr through_hole)''')

    # Module outline on B.SilkS
    corners = [(0, 0), (MODULE_W, 0), (MODULE_W, -MODULE_H), (0, -MODULE_H)]
    for i in range(4):
        x1, y1 = corners[i]
        x2, y2 = corners[(i+1) % 4]
        lines.append(f'''\t(fp_line
\t\t(start {x1:.2f} {y1:.2f})
\t\t(end {x2:.2f} {y2:.2f})
\t\t(stroke (width 0.12) (type solid))
\t\t(layer "B.SilkS")
\t\t(uuid "{uid()}")
\t)''')

    # Courtyard
    margin = 0.5
    crt = [(-margin, margin), (MODULE_W + margin, margin),
           (MODULE_W + margin, -MODULE_H - margin), (-margin, -MODULE_H - margin)]
    for i in range(4):
        x1, y1 = crt[i]
        x2, y2 = crt[(i+1) % 4]
        lines.append(f'''\t(fp_line
\t\t(start {x1:.2f} {y1:.2f})
\t\t(end {x2:.2f} {y2:.2f})
\t\t(stroke (width 0.05) (type solid))
\t\t(layer "B.CrtYd")
\t\t(uuid "{uid()}")
\t)''')

    # USB-C outline on Fab layer (at top of module)
    usbc_w = 9.0
    usbc_h = 1.5
    usbc_x1 = (MODULE_W - usbc_w) / 2
    usbc_x2 = usbc_x1 + usbc_w
    usbc_y1 = -MODULE_H
    usbc_y2 = -MODULE_H - usbc_h
    for (x1, y1, x2, y2) in [
        (usbc_x1, usbc_y1, usbc_x2, usbc_y1),
        (usbc_x2, usbc_y1, usbc_x2, usbc_y2),
        (usbc_x2, usbc_y2, usbc_x1, usbc_y2),
        (usbc_x1, usbc_y2, usbc_x1, usbc_y1),
    ]:
        lines.append(f'''\t(fp_line
\t\t(start {x1:.2f} {y1:.2f})
\t\t(end {x2:.2f} {y2:.2f})
\t\t(stroke (width 0.1) (type solid))
\t\t(layer "B.Fab")
\t\t(uuid "{uid()}")
\t)''')

    # USB-C label
    lines.append(f'''\t(fp_text user "USB-C"
\t\t(at {MODULE_W/2:.2f} {-MODULE_H - usbc_h/2:.2f} 0)
\t\t(layer "B.Fab")
\t\t(uuid "{uid()}")
\t\t(effects (font (size 0.8 0.8) (thickness 0.1)) (justify mirror))
\t)''')

    # Pin 1 marker
    lines.append(f'''\t(fp_text user "1"
\t\t(at {RIGHT_X + 2:.2f} {FIRST_PIN_Y:.2f} 0)
\t\t(layer "B.Fab")
\t\t(uuid "{uid()}")
\t\t(effects (font (size 0.8 0.8) (thickness 0.12)) (justify mirror))
\t)''')

    # Reference on Fab
    lines.append(f'''\t(fp_text user "${{REFERENCE}}"
\t\t(at {MODULE_W/2:.2f} {-MODULE_H/2:.2f} 0)
\t\t(unlocked yes)
\t\t(layer "B.Fab")
\t\t(uuid "{uid()}")
\t\t(effects (font (size 1 1) (thickness 0.15)) (justify mirror))
\t)''')

    # ============================================================
    # Through-hole pads
    # ============================================================
    # Right side: pins 1-10 (GP0-GP9), top to bottom
    # Pin mapping:
    #   Pin 1 = GP0, Pin 2 = GP1, ..., Pin 10 = GP9
    right_pin_names = [f"GP{i}" for i in range(10)]
    for i in range(N_SIDE_PINS):
        pin_num = i + 1
        py = FIRST_PIN_Y + i * PIN_PITCH
        lines.append(f'''\t(pad "{pin_num}" thru_hole circle
\t\t(at {RIGHT_X:.2f} {py:.2f})
\t\t(size 1.8 1.8)
\t\t(drill 1.0)
\t\t(layers "*.Cu" "*.Mask")
\t\t(remove_unused_layers no)
\t\t(uuid "{uid()}")
\t)''')

    # Left side: pins 11-20, bottom to top
    # Pin mapping (bottom to top):
    #   Pin 11 = GP13, Pin 12 = GP14, Pin 13 = GP15
    #   Pin 14 = GP26, Pin 15 = GP27, Pin 16 = GP28, Pin 17 = GP29
    #   Pin 18 = 3V3, Pin 19 = GND, Pin 20 = 5V
    for i in range(N_SIDE_PINS):
        pin_num = 11 + i
        # Bottom to top: first pin (11) at bottom, last pin (20) at top
        py = FIRST_PIN_Y + (N_SIDE_PINS - 1 - i) * PIN_PITCH
        lines.append(f'''\t(pad "{pin_num}" thru_hole circle
\t\t(at {LEFT_X:.2f} {py:.2f})
\t\t(size 1.8 1.8)
\t\t(drill 1.0)
\t\t(layers "*.Cu" "*.Mask")
\t\t(remove_unused_layers no)
\t\t(uuid "{uid()}")
\t)''')

    # ============================================================
    # Bottom castellated SMD pads (B1-B9)
    # ============================================================
    # These are on B.Cu only, at the bottom edge of the module
    # Pin mapping:
    #   B1 = GP16, B2 = GP17, B3 = GP18, B4 = GP19, B5 = GP20
    #   B6 = GP21, B7 = GP22, B8 = GP23, B9 = GND
    for i in range(N_BOTTOM_PADS):
        pad_name = f"B{i + 1}"
        px = bottom_start_x + i * BOTTOM_PAD_PITCH
        lines.append(f'''\t(pad "{pad_name}" smd rect
\t\t(at {px:.2f} {BOTTOM_Y:.2f})
\t\t(size 1.0 2.0)
\t\t(layers "B.Cu" "B.Mask")
\t\t(uuid "{uid()}")
\t)''')

    lines.append("\t(embedded_fonts no)")
    lines.append(")")

    return "\n".join(lines)


def main():
    output_path = os.path.join(
        os.path.dirname(__file__), "..", "libs", "orthball.pretty", "RP2040-Zero.kicad_mod"
    )
    footprint = generate_footprint()
    with open(output_path, "w") as f:
        f.write(footprint)
    print(f"Generated footprint: {output_path}")
    print(f"  Module: {MODULE_W}mm x {MODULE_H}mm")
    print(f"  THT pins: 2 x {N_SIDE_PINS} (pitch {PIN_PITCH}mm, row spacing {ROW_SPACING}mm)")
    print(f"  Bottom SMD pads: {N_BOTTOM_PADS} (pitch {BOTTOM_PAD_PITCH}mm)")
    print()
    print("  *** IMPORTANT: Verify dimensions with physical RP2040-Zero module! ***")
    print("  *** Print at 1:1 scale and place module on printout to confirm.    ***")


if __name__ == "__main__":
    main()
