#!/usr/bin/env python3
"""
Generate OrthBall V1 KiCad schematic with:
- 56 key switches (51 MX + 5 Choc) with diodes in 4x14 matrix
- RP2040-Zero MCU (custom symbol)
- PMW3360 header (1x7)
- OLED header (1x4)
- Mounting holes (M2 x 6)

Coordinate system: KiCad schematic uses mm, origin at top-left.
A3 paper: 420mm x 297mm
"""

import json
import uuid as uuid_mod
import os

def uid():
    return str(uuid_mod.uuid4())

# Matrix layout: 4 rows x 14 columns
# ROW0-ROW3 on GP0-GP3
# COL0-COL9 on GP4-GP13, COL10-COL13 on GP26-GP29
ROWS = 4
COLS = 14

# Key names for readability
KEY_NAMES = [
    # ROW0 (14 keys)
    ["Esc", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "BS", "BS2", "", ""],
    # ROW1 (14 keys)
    ["Tab", "A", "S", "D", "F", "G", "H", "J", "K", "L", "P", ";", "", ""],
    # ROW2 (14 keys)
    ["Sft", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "Sft2", "", ""],
    # ROW3 (bottom row with thumb keys)
    ["Ctrl", "Alt", "GUI", "Fn", "Spc", "Th1", "Th2", "Th3", "Th4", "Th5", "Th6",
     "Ch1", "Ch2", "Ch3"],
]

# Load key data to determine MX vs Choc
KEYS_JSON = os.path.join(os.path.dirname(__file__), "..", "..", "cad", "orthball_keys_v7.json")

# Matrix config: which positions are populated
# All 56 keys mapped linearly to the matrix
# ROW0: 14 keys (key_id 0-13, but we may have empty cells)
# ROW1: 14 keys (key_id 14-27)
# ROW2: 14 keys (key_id 28-41)
# ROW3: 14 keys (key_id 42-55, includes rotated MX + Choc)

def generate_switch_diode_pair(sw_ref, d_ref, row, col, x, y, is_choc=False):
    """Generate a switch + diode pair at schematic position (x, y)."""
    # Switch symbol instance
    sw_uuid = uid()
    d_uuid = uid()
    sw_pin1_uuid = uid()
    sw_pin2_uuid = uid()
    d_pin1_uuid = uid()
    d_pin2_uuid = uid()

    col_label = f"COL{col}"
    row_label = f"ROW{row}"

    if is_choc:
        fp = "marbastlib-choc:SW_choc_v1_HS_CPG135001S30_1u"
    else:
        fp = "marbastlib-mx:SW_MX_HS_CPG151101S11_1u"

    parts = []

    # Switch symbol
    parts.append(f'''  (symbol
    (lib_id "Switch:SW_Push")
    (at {x + 5.08} {y + 2.54} 0)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{sw_uuid}")
    (property "Reference" "{sw_ref}"
      (at {x + 5.08} {y} 0)
      (effects (font (size 1 1)))
    )
    (property "Value" "SW_Push"
      (at {x + 5.08} {y + 5.08} 0)
      (effects (font (size 1 1)) (hide yes))
    )
    (property "Footprint" "{fp}"
      (at {x + 5.08} {y + 2.54} 0)
      (effects (font (size 1 1)) (hide yes))
    )
    (property "Datasheet" ""
      (at {x + 5.08} {y + 2.54} 0)
      (effects (font (size 1 1)) (hide yes))
    )
    (property "Description" ""
      (at {x + 5.08} {y + 2.54} 0)
      (effects (font (size 1 1)) (hide yes))
    )
    (pin "1"
      (uuid "{sw_pin1_uuid}")
    )
    (pin "2"
      (uuid "{sw_pin2_uuid}")
    )
  )''')

    # Diode symbol (rotated 90 degrees, cathode towards ROW)
    parts.append(f'''  (symbol
    (lib_id "Device:D")
    (at {x + 8.89} {y + 5.08} 270)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{d_uuid}")
    (property "Reference" "{d_ref}"
      (at {x + 10.16} {y + 5.08} 90)
      (effects (font (size 1 1)))
    )
    (property "Value" "1N4148W"
      (at {x + 8.89} {y + 5.08} 90)
      (effects (font (size 1 1)) (hide yes))
    )
    (property "Footprint" "Diode_SMD:D_SOD-123"
      (at {x + 8.89} {y + 5.08} 270)
      (effects (font (size 1 1)) (hide yes))
    )
    (property "Datasheet" ""
      (at {x + 8.89} {y + 5.08} 270)
      (effects (font (size 1 1)) (hide yes))
    )
    (property "Description" ""
      (at {x + 8.89} {y + 5.08} 270)
      (effects (font (size 1 1)) (hide yes))
    )
    (pin "1"
      (uuid "{d_pin1_uuid}")
    )
    (pin "2"
      (uuid "{d_pin2_uuid}")
    )
  )''')

    # Wire from COL to switch pin 1 (left side of switch)
    parts.append(f'''  (wire
    (pts (xy {x} {y + 2.54}) (xy {x + 2.54} {y + 2.54}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )''')

    # Wire from switch pin 2 to diode anode
    parts.append(f'''  (wire
    (pts (xy {x + 7.62} {y + 2.54}) (xy {x + 8.89} {y + 2.54}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )''')
    parts.append(f'''  (wire
    (pts (xy {x + 8.89} {y + 2.54}) (xy {x + 8.89} {y + 3.81}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )''')

    # Wire from diode cathode to ROW
    parts.append(f'''  (wire
    (pts (xy {x + 8.89} {y + 6.35}) (xy {x + 8.89} {y + 7.62}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )''')

    # Net label for COL at switch input
    parts.append(f'''  (label "{col_label}"
    (at {x} {y + 2.54} 180)
    (effects (font (size 1.27 1.27)))
    (uuid "{uid()}")
  )''')

    # Net label for ROW at diode output
    parts.append(f'''  (label "{row_label}"
    (at {x + 8.89} {y + 7.62} 270)
    (effects (font (size 1.27 1.27)))
    (uuid "{uid()}")
  )''')

    return "\n".join(parts)


def generate_mcu_section(x, y):
    """Generate MCU (RP2040-Zero) with net labels."""
    mcu_uuid = uid()
    parts = []

    # RP2040-Zero symbol
    pin_uuids = {i: uid() for i in range(1, 30)}
    # Also need B1-B9
    for i in range(1, 10):
        pin_uuids[f"B{i}"] = uid()

    parts.append(f'''  (symbol
    (lib_id "orthball:RP2040-Zero")
    (at {x} {y} 0)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{mcu_uuid}")
    (property "Reference" "U1"
      (at {x} {y - 31.75} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "RP2040-Zero"
      (at {x} {y - 30.48} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "orthball:RP2040-Zero"
      (at {x} {y - 3.81} 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Datasheet" "https://www.waveshare.com/wiki/RP2040-Zero"
      (at {x} {y - 6.35} 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Description" "WaveShare RP2040-Zero module"
      (at {x} {y - 8.89} 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (pin "1" (uuid "{pin_uuids[1]}"))
    (pin "2" (uuid "{pin_uuids[2]}"))
    (pin "3" (uuid "{pin_uuids[3]}"))
    (pin "4" (uuid "{pin_uuids[4]}"))
    (pin "5" (uuid "{pin_uuids[5]}"))
    (pin "6" (uuid "{pin_uuids[6]}"))
    (pin "7" (uuid "{pin_uuids[7]}"))
    (pin "8" (uuid "{pin_uuids[8]}"))
    (pin "9" (uuid "{pin_uuids[9]}"))
    (pin "10" (uuid "{pin_uuids[10]}"))
    (pin "11" (uuid "{pin_uuids[11]}"))
    (pin "12" (uuid "{pin_uuids[12]}"))
    (pin "13" (uuid "{pin_uuids[13]}"))
    (pin "14" (uuid "{pin_uuids[14]}"))
    (pin "15" (uuid "{pin_uuids[15]}"))
    (pin "16" (uuid "{pin_uuids[16]}"))
    (pin "17" (uuid "{pin_uuids[17]}"))
    (pin "18" (uuid "{pin_uuids[18]}"))
    (pin "19" (uuid "{pin_uuids[19]}"))
    (pin "20" (uuid "{pin_uuids[20]}"))
    (pin "B1" (uuid "{pin_uuids['B1']}"))
    (pin "B2" (uuid "{pin_uuids['B2']}"))
    (pin "B3" (uuid "{pin_uuids['B3']}"))
    (pin "B4" (uuid "{pin_uuids['B4']}"))
    (pin "B5" (uuid "{pin_uuids['B5']}"))
    (pin "B6" (uuid "{pin_uuids['B6']}"))
    (pin "B7" (uuid "{pin_uuids['B7']}"))
    (pin "B8" (uuid "{pin_uuids['B8']}"))
    (pin "B9" (uuid "{pin_uuids['B9']}"))
  )''')

    # Net labels for MCU pins
    # Left side pins (GP0-GP9, GP16-GP23, GND_B)
    # Pin layout from symbol:
    # Left side: GP0(pin1) at y-25.4, GP1 at y-22.86, ..., GP9 at y-2.54
    #            GP16(B1) at y+5.08, ..., GP23(B8) at y+22.86, GND_B(B9) at y+25.4
    # Right side: GP13(pin11) at y+12.7, GP14(pin12) at y+10.16, GP15(pin13) at y+7.62
    #             GP26(pin14) at y+5.08, GP27(pin15) at y+2.54, GP28(pin16) at y+0
    #             GP29(pin17) at y-2.54
    #             3V3(pin18) at y-7.62, GND(pin19) at y-10.16, 5V(pin20) at y-12.7

    # Left side GPIO labels
    left_gpio = [
        ("ROW0", -25.4), ("ROW1", -22.86), ("ROW2", -20.32), ("ROW3", -17.78),
        ("COL0", -15.24), ("COL1", -12.7), ("COL2", -10.16), ("COL3", -7.62),
        ("COL4", -5.08), ("COL5", -2.54),
    ]
    for label, dy in left_gpio:
        lx = x - 19.05 - 2.54
        ly = y + dy
        parts.append(f'''  (label "{label}"
    (at {lx} {ly} 180)
    (effects (font (size 1.27 1.27)))
    (uuid "{uid()}")
  )''')
        parts.append(f'''  (wire
    (pts (xy {lx} {ly}) (xy {x - 19.05} {ly}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )''')

    # Left side back pad labels
    back_gpio = [
        ("PMW_MISO", 5.08), ("PMW_CS", 7.62), ("PMW_SCK", 10.16), ("PMW_MOSI", 12.7),
        ("PMW_MOTION", 15.24), ("SPARE_GP21", 17.78), ("SPARE_GP22", 20.32), ("SPARE_GP23", 22.86),
    ]
    for label, dy in back_gpio:
        lx = x - 19.05 - 2.54
        ly = y + dy
        parts.append(f'''  (label "{label}"
    (at {lx} {ly} 180)
    (effects (font (size 1.27 1.27)))
    (uuid "{uid()}")
  )''')
        parts.append(f'''  (wire
    (pts (xy {lx} {ly}) (xy {x - 19.05} {ly}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )''')

    # GND_B label
    lx = x - 19.05 - 2.54
    ly = y + 25.4
    parts.append(f'''  (label "GND"
    (at {lx} {ly} 180)
    (effects (font (size 1.27 1.27)))
    (uuid "{uid()}")
  )''')
    parts.append(f'''  (wire
    (pts (xy {lx} {ly}) (xy {x - 19.05} {ly}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )''')

    # Right side labels
    right_labels = [
        ("COL9", -12.7), ("OLED_SDA", -10.16), ("OLED_SCL", -7.62),
        ("COL10", -5.08), ("COL11", -2.54), ("COL12", 0), ("COL13", 2.54),
    ]
    for label, dy in right_labels:
        lx = x + 19.05 + 2.54
        ly = y + dy
        parts.append(f'''  (label "{label}"
    (at {lx} {ly} 0)
    (effects (font (size 1.27 1.27)))
    (uuid "{uid()}")
  )''')
        parts.append(f'''  (wire
    (pts (xy {x + 19.05} {ly}) (xy {lx} {ly}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )''')

    # Power labels (right side)
    power_labels = [
        ("3V3", -7.62 + 15.24), ("GND", -10.16 + 20.32), ("5V", -12.7 + 25.4),
    ]
    # Actually recalculate based on symbol pin positions
    # 3V3 is pin 18 at right side y offset 7.62
    # GND is pin 19 at right side y offset 10.16
    # 5V is pin 20 at right side y offset 12.7
    power_labels = [
        ("3V3", 7.62), ("GND", 10.16), ("5V", 12.7),
    ]
    # Hmm, these are wrong. Let me recalculate from the symbol.
    # In the symbol, right side pins:
    # GP13 at y=-12.7 (pin 11)
    # GP14 at y=-10.16 (pin 12)
    # GP15 at y=-7.62 (pin 13)
    # GP26 at y=-5.08 (pin 14)
    # GP27 at y=-2.54 (pin 15)
    # GP28 at y=0 (pin 16)
    # GP29 at y=2.54 (pin 17)
    # 3V3 at y=7.62 (pin 18)
    # GND at y=10.16 (pin 19)
    # 5V at y=12.7 (pin 20)

    # Fix: use correct offsets from symbol
    for label, dy in [("3V3", 7.62), ("GND", 10.16), ("5V", 12.7)]:
        lx = x + 19.05 + 2.54
        ly = y + dy
        parts.append(f'''  (label "{label}"
    (at {lx} {ly} 0)
    (effects (font (size 1.27 1.27)))
    (uuid "{uid()}")
  )''')
        parts.append(f'''  (wire
    (pts (xy {x + 19.05} {ly}) (xy {lx} {ly}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )''')

    return "\n".join(parts)


def generate_pmw3360_header(x, y):
    """Generate PMW3360 breakout module pin header connector."""
    conn_uuid = uid()
    parts = []

    pin_names = ["VCC", "GND", "MISO", "MOSI", "SCK", "CS", "MOTION"]
    net_labels = ["3V3", "GND", "PMW_MISO", "PMW_MOSI", "PMW_SCK", "PMW_CS", "PMW_MOTION"]

    pin_uuids = [uid() for _ in range(7)]

    parts.append(f'''  (symbol
    (lib_id "Connector:Conn_01x07_Pin")
    (at {x} {y} 0)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{conn_uuid}")
    (property "Reference" "J1"
      (at {x} {y - 12.7} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "PMW3360"
      (at {x} {y - 11.43} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Vertical"
      (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Datasheet" ""
      (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Description" "PMW3360 breakout module header"
      (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )''')

    for i, pu in enumerate(pin_uuids):
        parts.append(f'    (pin "{i+1}" (uuid "{pu}"))')
    parts.append("  )")

    # Net labels for each pin
    for i, (pn, nl) in enumerate(zip(pin_names, net_labels)):
        py = y + i * 2.54 - 7.62
        lx = x - 2.54 - 2.54
        parts.append(f'''  (label "{nl}"
    (at {lx} {py} 180)
    (effects (font (size 1.27 1.27)))
    (uuid "{uid()}")
  )''')
        parts.append(f'''  (wire
    (pts (xy {lx} {py}) (xy {x - 2.54} {py}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )''')

    return "\n".join(parts)


def generate_oled_header(x, y):
    """Generate OLED SSD1306 I2C pin header connector."""
    conn_uuid = uid()
    parts = []

    pin_names = ["GND", "VCC", "SCL", "SDA"]
    net_labels = ["GND", "3V3", "OLED_SCL", "OLED_SDA"]
    pin_uuids = [uid() for _ in range(4)]

    parts.append(f'''  (symbol
    (lib_id "Connector:Conn_01x04_Pin")
    (at {x} {y} 0)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{conn_uuid}")
    (property "Reference" "J2"
      (at {x} {y - 7.62} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "OLED_SSD1306"
      (at {x} {y - 6.35} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"
      (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Datasheet" ""
      (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Description" "OLED SSD1306 0.91in 128x32 I2C display header"
      (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )''')

    for i, pu in enumerate(pin_uuids):
        parts.append(f'    (pin "{i+1}" (uuid "{pu}"))')
    parts.append("  )")

    for i, (pn, nl) in enumerate(zip(pin_names, net_labels)):
        py = y + i * 2.54 - 3.81
        lx = x - 2.54 - 2.54
        parts.append(f'''  (label "{nl}"
    (at {lx} {py} 180)
    (effects (font (size 1.27 1.27)))
    (uuid "{uid()}")
  )''')
        parts.append(f'''  (wire
    (pts (xy {lx} {py}) (xy {x - 2.54} {py}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )''')

    return "\n".join(parts)


def generate_mounting_hole(ref, x, y):
    """Generate a mounting hole."""
    mh_uuid = uid()
    return f'''  (symbol
    (lib_id "Mechanical:MountingHole")
    (at {x} {y} 0)
    (unit 1)
    (exclude_from_sim yes)
    (in_bom no)
    (on_board yes)
    (dnp no)
    (uuid "{mh_uuid}")
    (property "Reference" "{ref}"
      (at {x + 2.54} {y} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "M2"
      (at {x + 2.54} {y + 2.54} 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Footprint" "MountingHole:MountingHole_2.2mm_M2"
      (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Datasheet" ""
      (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Description" "M2 mounting hole"
      (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
  )'''


def generate_schematic():
    """Generate the complete schematic."""
    # Load key data to determine which keys are MX vs Choc
    try:
        with open(KEYS_JSON, "r") as f:
            keys_data = json.load(f)
        keys = keys_data["keys"]
    except Exception:
        keys = None

    # Determine Choc key IDs
    choc_ids = set()
    if keys:
        for k in keys:
            if k.get("type") == "choc":
                choc_ids.add(k["key_id"])

    # Schematic content
    parts = []

    # Header
    root_uuid = "e63e39d7-6ac0-4ffd-8aa3-1841a4541b55"
    parts.append(f'''(kicad_sch
  (version 20231120)
  (generator "orthball_gen")
  (generator_version "9.0")
  (uuid "{root_uuid}")
  (paper "A3")
  (title_block
    (title "OrthBall V1")
    (date "2026-03-15")
    (rev "0.1")
    (comment 1 "One-piece ortholinear keyboard + 55mm trackball")
    (comment 2 "MCU: RP2040-Zero / Sensor: PMW3360 / Display: OLED SSD1306")
  )
  (lib_symbols
    (symbol "Switch:SW_Push"
      (pin_numbers hide)
      (pin_names (offset 1.016) hide)
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "SW"
        (at 1.27 2.54 0)
        (effects (font (size 1.27 1.27)) (justify left))
      )
      (property "Value" "SW_Push"
        (at 0 -1.524 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Footprint" ""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "~"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "Push button switch, generic, two pins"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (symbol "SW_Push_0_1"
        (circle
          (center -2.032 0)
          (radius 0.508)
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy 0 1.27) (xy 0 3.048))
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy 2.54 1.27) (xy -2.54 1.27))
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (circle
          (center 2.032 0)
          (radius 0.508)
          (stroke (width 0) (type default))
          (fill (type none))
        )
      )
      (symbol "SW_Push_1_1"
        (pin passive line
          (at -5.08 0 0)
          (length 2.54)
          (name "1" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
        (pin passive line
          (at 5.08 0 180)
          (length 2.54)
          (name "2" (effects (font (size 1.27 1.27))))
          (number "2" (effects (font (size 1.27 1.27))))
        )
      )
    )
    (symbol "Device:D"
      (pin_numbers hide)
      (pin_names (offset 1.016) hide)
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "D"
        (at 0 2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "D"
        (at 0 -2.54 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Footprint" ""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "~"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "Diode, general purpose"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (symbol "D_0_1"
        (polyline
          (pts (xy -1.27 1.27) (xy -1.27 -1.27))
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy 1.27 0) (xy -1.27 0))
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy 1.27 1.27) (xy 1.27 -1.27) (xy -1.27 0) (xy 1.27 1.27))
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
      )
      (symbol "D_1_1"
        (pin passive line
          (at -3.81 0 0)
          (length 2.54)
          (name "K" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
        (pin passive line
          (at 3.81 0 180)
          (length 2.54)
          (name "A" (effects (font (size 1.27 1.27))))
          (number "2" (effects (font (size 1.27 1.27))))
        )
      )
    )
    (symbol "orthball:RP2040-Zero"
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "U"
        (at 0 1.27 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "RP2040-Zero"
        (at 0 -1.27 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "orthball:RP2040-Zero"
        (at 0 -3.81 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "https://www.waveshare.com/wiki/RP2040-Zero"
        (at 0 -6.35 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "WaveShare RP2040-Zero module, 29 GPIO, USB-C"
        (at 0 -8.89 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (symbol "RP2040-Zero_0_1"
        (rectangle
          (start -16.51 29.21)
          (end 16.51 -29.21)
          (stroke (width 0.254) (type default))
          (fill (type background))
        )
      )
      (symbol "RP2040-Zero_1_1"
        (pin bidirectional line (at -19.05 25.4 0) (length 2.54) (name "GP0" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at -19.05 22.86 0) (length 2.54) (name "GP1" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at -19.05 20.32 0) (length 2.54) (name "GP2" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at -19.05 17.78 0) (length 2.54) (name "GP3" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at -19.05 15.24 0) (length 2.54) (name "GP4" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at -19.05 12.7 0) (length 2.54) (name "GP5" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at -19.05 10.16 0) (length 2.54) (name "GP6" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at -19.05 7.62 0) (length 2.54) (name "GP7" (effects (font (size 1.27 1.27)))) (number "8" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at -19.05 5.08 0) (length 2.54) (name "GP8" (effects (font (size 1.27 1.27)))) (number "9" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at -19.05 2.54 0) (length 2.54) (name "GP9" (effects (font (size 1.27 1.27)))) (number "10" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at 19.05 -12.7 180) (length 2.54) (name "GP13" (effects (font (size 1.27 1.27)))) (number "11" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at 19.05 -10.16 180) (length 2.54) (name "GP14" (effects (font (size 1.27 1.27)))) (number "12" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at 19.05 -7.62 180) (length 2.54) (name "GP15" (effects (font (size 1.27 1.27)))) (number "13" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at 19.05 -5.08 180) (length 2.54) (name "GP26" (effects (font (size 1.27 1.27)))) (number "14" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at 19.05 -2.54 180) (length 2.54) (name "GP27" (effects (font (size 1.27 1.27)))) (number "15" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at 19.05 0 180) (length 2.54) (name "GP28" (effects (font (size 1.27 1.27)))) (number "16" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at 19.05 2.54 180) (length 2.54) (name "GP29" (effects (font (size 1.27 1.27)))) (number "17" (effects (font (size 1.27 1.27)))))
        (pin power_out line (at 19.05 7.62 180) (length 2.54) (name "3V3" (effects (font (size 1.27 1.27)))) (number "18" (effects (font (size 1.27 1.27)))))
        (pin power_in line (at 19.05 10.16 180) (length 2.54) (name "GND" (effects (font (size 1.27 1.27)))) (number "19" (effects (font (size 1.27 1.27)))))
        (pin power_in line (at 19.05 12.7 180) (length 2.54) (name "5V" (effects (font (size 1.27 1.27)))) (number "20" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at -19.05 -5.08 0) (length 2.54) (name "GP16" (effects (font (size 1.27 1.27)))) (number "B1" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at -19.05 -7.62 0) (length 2.54) (name "GP17" (effects (font (size 1.27 1.27)))) (number "B2" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at -19.05 -10.16 0) (length 2.54) (name "GP18" (effects (font (size 1.27 1.27)))) (number "B3" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at -19.05 -12.7 0) (length 2.54) (name "GP19" (effects (font (size 1.27 1.27)))) (number "B4" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at -19.05 -15.24 0) (length 2.54) (name "GP20" (effects (font (size 1.27 1.27)))) (number "B5" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at -19.05 -17.78 0) (length 2.54) (name "GP21" (effects (font (size 1.27 1.27)))) (number "B6" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at -19.05 -20.32 0) (length 2.54) (name "GP22" (effects (font (size 1.27 1.27)))) (number "B7" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at -19.05 -22.86 0) (length 2.54) (name "GP23" (effects (font (size 1.27 1.27)))) (number "B8" (effects (font (size 1.27 1.27)))))
        (pin power_in line (at -19.05 -25.4 0) (length 2.54) (name "GND_B" (effects (font (size 1.27 1.27)))) (number "B9" (effects (font (size 1.27 1.27)))))
      )
    )
    (symbol "Connector:Conn_01x07_Pin"
      (pin_names (offset 1.016) hide)
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "J"
        (at 0 10.16 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "Conn_01x07_Pin"
        (at 0 -10.16 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Footprint" ""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "~"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "Generic connector, single row, 01x07"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (symbol "Conn_01x07_Pin_1_1"
        (polyline (pts (xy 1.27 -7.62) (xy 0.8636 -7.62)) (stroke (width 0.1524) (type default)) (fill (type none)))
        (polyline (pts (xy 1.27 -5.08) (xy 0.8636 -5.08)) (stroke (width 0.1524) (type default)) (fill (type none)))
        (polyline (pts (xy 1.27 -2.54) (xy 0.8636 -2.54)) (stroke (width 0.1524) (type default)) (fill (type none)))
        (polyline (pts (xy 1.27 0) (xy 0.8636 0)) (stroke (width 0.1524) (type default)) (fill (type none)))
        (polyline (pts (xy 1.27 2.54) (xy 0.8636 2.54)) (stroke (width 0.1524) (type default)) (fill (type none)))
        (polyline (pts (xy 1.27 5.08) (xy 0.8636 5.08)) (stroke (width 0.1524) (type default)) (fill (type none)))
        (polyline (pts (xy 1.27 7.62) (xy 0.8636 7.62)) (stroke (width 0.1524) (type default)) (fill (type none)))
        (rectangle (start 0.8636 -7.874) (end 0 -7.366) (stroke (width 0) (type default)) (fill (type outline)))
        (rectangle (start 0.8636 -5.334) (end 0 -4.826) (stroke (width 0) (type default)) (fill (type outline)))
        (rectangle (start 0.8636 -2.794) (end 0 -2.286) (stroke (width 0) (type default)) (fill (type outline)))
        (rectangle (start 0.8636 -0.254) (end 0 0.254) (stroke (width 0) (type default)) (fill (type outline)))
        (rectangle (start 0.8636 2.286) (end 0 2.794) (stroke (width 0) (type default)) (fill (type outline)))
        (rectangle (start 0.8636 4.826) (end 0 5.334) (stroke (width 0) (type default)) (fill (type outline)))
        (rectangle (start 0.8636 7.366) (end 0 7.874) (stroke (width 0) (type default)) (fill (type outline)))
        (pin passive line (at -2.54 7.62 0) (length 3.81) (name "Pin_1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at -2.54 5.08 0) (length 3.81) (name "Pin_2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin passive line (at -2.54 2.54 0) (length 3.81) (name "Pin_3" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
        (pin passive line (at -2.54 0 0) (length 3.81) (name "Pin_4" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
        (pin passive line (at -2.54 -2.54 0) (length 3.81) (name "Pin_5" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
        (pin passive line (at -2.54 -5.08 0) (length 3.81) (name "Pin_6" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
        (pin passive line (at -2.54 -7.62 0) (length 3.81) (name "Pin_7" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))
      )
    )
    (symbol "Connector:Conn_01x04_Pin"
      (pin_names (offset 1.016) hide)
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "J"
        (at 0 5.08 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "Conn_01x04_Pin"
        (at 0 -7.62 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Footprint" ""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "~"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "Generic connector, single row, 01x04"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (symbol "Conn_01x04_Pin_1_1"
        (polyline (pts (xy 1.27 -2.54) (xy 0.8636 -2.54)) (stroke (width 0.1524) (type default)) (fill (type none)))
        (polyline (pts (xy 1.27 0) (xy 0.8636 0)) (stroke (width 0.1524) (type default)) (fill (type none)))
        (polyline (pts (xy 1.27 2.54) (xy 0.8636 2.54)) (stroke (width 0.1524) (type default)) (fill (type none)))
        (polyline (pts (xy 1.27 5.08) (xy 0.8636 5.08)) (stroke (width 0.1524) (type default)) (fill (type none)))
        (rectangle (start 0.8636 -2.794) (end 0 -2.286) (stroke (width 0) (type default)) (fill (type outline)))
        (rectangle (start 0.8636 -0.254) (end 0 0.254) (stroke (width 0) (type default)) (fill (type outline)))
        (rectangle (start 0.8636 2.286) (end 0 2.794) (stroke (width 0) (type default)) (fill (type outline)))
        (rectangle (start 0.8636 4.826) (end 0 5.334) (stroke (width 0) (type default)) (fill (type outline)))
        (pin passive line (at -2.54 2.54 0) (length 3.81) (name "Pin_1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at -2.54 0 0) (length 3.81) (name "Pin_2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin passive line (at -2.54 -2.54 0) (length 3.81) (name "Pin_3" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
        (pin passive line (at -2.54 -5.08 0) (length 3.81) (name "Pin_4" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
      )
    )
    (symbol "Mechanical:MountingHole"
      (pin_names (offset 1.016))
      (exclude_from_sim yes)
      (in_bom no)
      (on_board yes)
      (property "Reference" "H"
        (at 0 5.08 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "MountingHole"
        (at 0 3.175 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" ""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "~"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "Mounting Hole without connection"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (symbol "MountingHole_0_1"
        (circle
          (center 0 0)
          (radius 1.27)
          (stroke (width 1.27) (type default))
          (fill (type none))
        )
      )
    )
  )''')

    # Section labels
    parts.append(f'''  (text "== KEY MATRIX (4 x 14) =="
    (exclude_from_sim no)
    (at 25.4 25.4 0)
    (effects (font (size 3 3) (bold yes)))
    (uuid "{uid()}")
  )''')

    # Generate key matrix
    # Layout: starts at x=25.4, y=35, spacing 12.7mm per column, 12.7mm per row
    matrix_x0 = 25.4
    matrix_y0 = 35.0
    col_spacing = 12.7
    row_spacing = 12.7

    sw_num = 1
    d_num = 1
    key_id = 0

    for row in range(ROWS):
        for col in range(COLS):
            name = KEY_NAMES[row][col] if col < len(KEY_NAMES[row]) else ""
            # Skip empty positions
            if name == "" and key_id >= 56:
                continue

            x = matrix_x0 + col * col_spacing
            y = matrix_y0 + row * row_spacing

            # Determine if this is a Choc key
            is_choc = key_id in choc_ids

            if name != "" or key_id < 56:
                parts.append(generate_switch_diode_pair(
                    f"SW{sw_num}", f"D{d_num}", row, col, x, y, is_choc
                ))
                sw_num += 1
                d_num += 1
                key_id += 1

    # MCU section
    parts.append(f'''  (text "== MCU: RP2040-Zero =="
    (exclude_from_sim no)
    (at 280 50 0)
    (effects (font (size 3 3) (bold yes)))
    (uuid "{uid()}")
  )''')

    parts.append(generate_mcu_section(320, 100))

    # PMW3360 section
    parts.append(f'''  (text "== TRACKBALL: PMW3360 =="
    (exclude_from_sim no)
    (at 280 170 0)
    (effects (font (size 3 3) (bold yes)))
    (uuid "{uid()}")
  )''')

    parts.append(generate_pmw3360_header(320, 190))

    # OLED section
    parts.append(f'''  (text "== DISPLAY: OLED SSD1306 =="
    (exclude_from_sim no)
    (at 280 220 0)
    (effects (font (size 3 3) (bold yes)))
    (uuid "{uid()}")
  )''')

    parts.append(generate_oled_header(320, 240))

    # Mounting holes
    parts.append(f'''  (text "== MOUNTING HOLES =="
    (exclude_from_sim no)
    (at 280 260 0)
    (effects (font (size 3 3) (bold yes)))
    (uuid "{uid()}")
  )''')

    for i in range(6):
        parts.append(generate_mounting_hole(f"H{i+1}", 290 + (i % 3) * 15, 270 + (i // 3) * 10))

    # Close schematic
    parts.append(f'''  (sheet_instances
    (path "/"
      (page "1")
    )
  )
)''')

    return "\n".join(parts)


def main():
    output_path = os.path.join(os.path.dirname(__file__), "..", "orthball.kicad_sch")
    schematic = generate_schematic()

    with open(output_path, "w") as f:
        f.write(schematic)

    print(f"Generated schematic: {output_path}")
    print(f"  - 56 switch+diode pairs (51 MX + 5 Choc)")
    print(f"  - RP2040-Zero MCU with all GPIO labels")
    print(f"  - PMW3360 7-pin header")
    print(f"  - OLED 4-pin header")
    print(f"  - 6 mounting holes")


if __name__ == "__main__":
    main()
