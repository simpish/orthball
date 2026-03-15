// Orthball v1 - 3-Split Ortholinear Keyboard with Trackball
// Left Hand / Center Numpad / Right Hand + Trackball
// 2026-02-22
//
// Changes from default Cosmos Dactyl:
//   - Removed number row (row: -2) — moved to center numpad unit
//   - 3 rows only: row -1, 0, 1 (QWERTY, Home, Bottom)
//   - 6 columns maintained: -2.5, -1.5, -0.5, 0.5, 1.5, 2.5
//   - type: "mx-better" (3DP hotswap compatible)
//   - Keycap profile: MT3
//   - curvatureOfColumn: 17° (was 15°), curvatureOfRow: 5° (unchanged)
//   - Thumb cluster: 5 keys per side (unchanged from default Curved)
//   - Right hand: trackball space noted at column 3.5+ area
//   - Connectors: TRRS + USB-C, Microcontroller: kb2040-adafruit

const options: Options = {
  wallThickness: 4,
  wallShrouding: 0,
  wallXYOffset: 5,
  wallZOffset: 15,
  webThickness: 0,
  webMinThicknessFactor: 0.8,
  verticalClearance: 0.1,
  plateThickness: 3,
  keyBasis: "mt3",
  screwIndices: [-1, -1, -1, -1, -1, -1, -1],
  screwCountersink: true,
  screwSize: "M3",
  screwType: "screw insert",
  clearScrews: true,
  rounded: {},
  connectors: [
    { preset: "trrs" },
    { preset: "usb", size: "average" }
  ],
  connectorIndex: -1,
  microcontroller: "kb2040-adafruit",
  microcontrollerAngle: 0,
  fastenMicrocontroller: true,
  flipConnectors: false,
  shell: { type: "basic", lip: false }
}

// NOTE: Screws / the connector with
// negative indices are placed automatically.

/**
 * The planes used to position the clusters.
 * It's rotated by the tenting and x rotation
 */
const rightFingersPlane = new Trsf()
  .rotate(1.0222222222222221, [0, 0, 0], [1, 0, 0], false)
  .rotate(12, [0, 0, 0], [0, 1, 0], false)
  .rotate(0.2222222222222222, [0, 0, 0], [0, 0, 1], false)
  .translate(18, 35.6, -15.2)

const rightThumbsPlane = new Trsf()
  .rotate(-11.88888888888889, [0, 0, 0], [1, 0, 0])
  .rotate(-24.8, [0, 0, 0], [0, 1, 0])
  .rotate(34.44444444444444, [0, 0, 0], [0, 0, 1])
  .translate(-35.8, -25.6, -7.1)
  .transformBy(new Trsf()
    .translate(-18, -35.6, 15.2)
    .rotate(-0.2222222222222222, [0, 0, 0], [0, 0, 1])
    .rotate(-12, [0, 0, 0], [0, 1, 0])
    .rotate(-1.0222222222222221, [0, 0, 0], [1, 0, 0])
  )
  .transformBy(new Trsf()
    .rotate(1.0222222222222221, [0, 0, 0], [1, 0, 0], false)
    .rotate(12, [0, 0, 0], [0, 1, 0], false)
    .rotate(0.2222222222222222, [0, 0, 0], [0, 0, 1], false)
    .translate(18, 35.6, -15.2)
  )

const leftFingersPlane = new Trsf()
  .rotate(1.0222222222222221, [0, 0, 0], [1, 0, 0], false)
  .rotate(-12, [0, 0, 0], [0, 1, 0], false)
  .rotate(-0.2222222222222222, [0, 0, 0], [0, 0, 1], false)
  .translate(-18, 35.6, -15.2)

const leftThumbsPlane = new Trsf()
  .rotate(-11.88888888888889, [0, 0, 0], [1, 0, 0])
  .rotate(24.8, [0, 0, 0], [0, 1, 0])
  .rotate(-34.44444444444444, [0, 0, 0], [0, 0, 1])
  .translate(35.8, -25.6, -7.1)
  .transformBy(new Trsf()
    .translate(18, -35.6, 15.2)
    .rotate(0.2222222222222222, [0, 0, 0], [0, 0, 1])
    .rotate(12, [0, 0, 0], [0, 1, 0])
    .rotate(-1.0222222222222221, [0, 0, 0], [1, 0, 0])
  )
  .transformBy(new Trsf()
    .rotate(1.0222222222222221, [0, 0, 0], [1, 0, 0], false)
    .rotate(-12, [0, 0, 0], [0, 1, 0], false)
    .rotate(-0.2222222222222222, [0, 0, 0], [0, 0, 1], false)
    .translate(-18, 35.6, -15.2)
  )

// Shared curvature settings
const curvature = {
  spacingOfColumns: 21.5,
  spacingOfRows: 20.5,
  curvatureOfRow: 5,
  curvatureOfColumn: 17,
  arc: 0
}

/** Helper: make a finger key */
function fingerKey(
  column: number, row: number, letter: string,
  keycapRow: number, plane: any,
  home?: string
): Key {
  return {
    type: "mx-better",
    aspect: 1,
    cluster: "fingers",
    position: new Trsf()
      .placeOnMatrix({ column, row, ...curvature })
      .transformBy(plane),
    keycap: {
      ...(letter ? { letter } : {}),
      ...(home ? { home } : {}),
      row: keycapRow,
      profile: "mt3"
    }
  }
}

/** Helper: make a finger key with column offset (for middle/pinky columns) */
function fingerKeyOffset(
  column: number, row: number, letter: string,
  keycapRow: number, plane: any,
  offsetY: number, offsetZ: number,
  home?: string
): Key {
  return {
    type: "mx-better",
    aspect: 1,
    cluster: "fingers",
    position: new Trsf()
      .placeRow({
        row,
        spacingOfRows: 20.5,
        curvatureOfColumn: 17,
        arc: 0,
        columnForArc: column
      })
      .transformBy(new Trsf().translate(0, offsetY, offsetZ))
      .placeColumn({
        column,
        spacingOfColumns: 21.5,
        curvatureOfRow: 5
      })
      .transformBy(plane),
    keycap: {
      ...(letter ? { letter } : {}),
      ...(home ? { home } : {}),
      row: keycapRow,
      profile: "mt3"
    }
  }
}

// ============================================================
// LEFT HAND — 6 columns × 3 rows (no number row)
// Layout (left to right on left hand, columns 2.5 → -1.5):
//   Col 2.5: t g b  (inner index)
//   Col 1.5: r f v  (index)
//   Col 0.5: e d c  (middle, offset +2.8y -4z)
//   Col-0.5: w s x  (ring)
//   Col-1.5: q a z  (pinky, offset -13y +6z)
//   Col-2.5: (extra pinky — added for 6th column)
// ============================================================

const fingersLeft: Key[] = [
  // Column 2.5 (inner index) — rows -1, 0, 1
  fingerKey(2.5, -1, "t", 2, leftFingersPlane),
  fingerKey(2.5,  0, "g", 3, leftFingersPlane),
  fingerKey(2.5,  1, "b", 4, leftFingersPlane),

  // Column 1.5 (index) — rows -1, 0, 1
  fingerKey(1.5, -1, "r", 2, leftFingersPlane),
  fingerKey(1.5,  0, "f", 3, leftFingersPlane, "index"),
  fingerKey(1.5,  1, "v", 4, leftFingersPlane),

  // Column 0.5 (middle, offset) — rows -1, 0, 1
  fingerKeyOffset(0.5, -1, "e", 2, leftFingersPlane, 2.8, -4),
  fingerKeyOffset(0.5,  0, "d", 3, leftFingersPlane, 2.8, -4, "middle"),
  fingerKeyOffset(0.5,  1, "c", 4, leftFingersPlane, 2.8, -4),

  // Column -0.5 (ring) — rows -1, 0, 1
  fingerKey(-0.5, -1, "w", 2, leftFingersPlane),
  fingerKey(-0.5,  0, "s", 3, leftFingersPlane, "ring"),
  fingerKey(-0.5,  1, "x", 4, leftFingersPlane),

  // Column -1.5 (pinky, offset) — rows -1, 0, 1
  fingerKeyOffset(-1.5, -1, "q", 2, leftFingersPlane, -13, 6),
  fingerKeyOffset(-1.5,  0, "a", 3, leftFingersPlane, -13, 6, "pinky"),
  fingerKeyOffset(-1.5,  1, "z", 4, leftFingersPlane, -13, 6),

  // Column -2.5 (extra pinky) — rows -1, 0, 1
  // Using same offset pattern as pinky column
  fingerKeyOffset(-2.5, -1, "Tab", 2, leftFingersPlane, -13, 6),
  fingerKeyOffset(-2.5,  0, "Esc", 3, leftFingersPlane, -13, 6),
  fingerKeyOffset(-2.5,  1, "Sft", 4, leftFingersPlane, -13, 6),
]

// Left thumb cluster — 5 keys (unchanged from default Curved)
const thumbsLeft: Key[] = [
  {
    type: "mx-better",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(17.8, [0, 0, 0], [1, 0, 0])
      .rotate(-3.2888888888888888, [0, 0, 0], [0, 1, 0])
      .rotate(8.2, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, 3.5)
      .placeOnMatrix({
        column: -0.4, row: -0.34,
        spacingOfColumns: 20, spacingOfRows: 20,
        curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0
      })
      .transformBy(leftThumbsPlane),
    keycap: { home: "thumb", row: 5, profile: "mt3" }
  },
  {
    type: "mx-better",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(17.8, [0, 0, 0], [1, 0, 0])
      .rotate(-3.2888888888888888, [0, 0, 0], [0, 1, 0])
      .rotate(8.2, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, -4.2)
      .placeOnMatrix({
        column: -0.29, row: 0.67,
        spacingOfColumns: 20, spacingOfRows: 20,
        curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0
      })
      .transformBy(leftThumbsPlane),
    keycap: { home: "thumb", row: 5, profile: "mt3" }
  },
  {
    type: "mx-better",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(15.11111111111111, [0, 0, 0], [1, 0, 0])
      .rotate(-16, [0, 0, 0], [0, 1, 0])
      .rotate(21.8, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, 0.4)
      .placeOnMatrix({
        column: -1.43, row: -0.06,
        spacingOfColumns: 20, spacingOfRows: 20,
        curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0
      })
      .transformBy(leftThumbsPlane),
    keycap: { row: 5, profile: "mt3" }
  },
  {
    type: "mx-better",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(18.2, [0, 0, 0], [1, 0, 0])
      .rotate(7.111111111111111, [0, 0, 0], [0, 1, 0])
      .rotate(1, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, 3.1)
      .placeOnMatrix({
        column: 0.64, row: -0.44,
        spacingOfColumns: 20, spacingOfRows: 20,
        curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0
      })
      .transformBy(leftThumbsPlane),
    keycap: { row: 5, profile: "mt3" }
  },
  {
    type: "mx-better",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(18.31111111111111, [0, 0, 0], [1, 0, 0])
      .rotate(9.088888888888889, [0, 0, 0], [0, 1, 0])
      .rotate(1.488888888888889, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, -5.3)
      .placeOnMatrix({
        column: 0.75, row: 0.58,
        spacingOfColumns: 20, spacingOfRows: 20,
        curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0
      })
      .transformBy(leftThumbsPlane),
    keycap: { row: 5, profile: "mt3" }
  }
]

// ============================================================
// RIGHT HAND — 6 columns × 3 rows (mirrored)
// Layout (left to right on right hand, columns -2.5 → 1.5):
//   Col-2.5: y h n  (inner index)
//   Col-1.5: u j m  (index)
//   Col-0.5: i k ,  (middle, offset +2.8y -4z)
//   Col 0.5: o l .  (ring)
//   Col 1.5: p ; /  (pinky, offset -13y +6z)
//   Col 2.5: extra pinky (added for 6th column)
//
// TRACKBALL: Positioned outside column 2.5 (approx column 3.5+)
//   on the pinky side. See comment below for placement.
// ============================================================

const fingersRight: Key[] = [
  // Column -2.5 (inner index) — rows -1, 0, 1
  fingerKey(-2.5, -1, "y", 2, rightFingersPlane),
  fingerKey(-2.5,  0, "h", 3, rightFingersPlane),
  fingerKey(-2.5,  1, "n", 4, rightFingersPlane),

  // Column -1.5 (index) — rows -1, 0, 1
  fingerKey(-1.5, -1, "u", 2, rightFingersPlane),
  fingerKey(-1.5,  0, "j", 3, rightFingersPlane, "index"),
  fingerKey(-1.5,  1, "m", 4, rightFingersPlane),

  // Column -0.5 (middle, offset) — rows -1, 0, 1
  fingerKeyOffset(-0.5, -1, "i", 2, rightFingersPlane, 2.8, -4),
  fingerKeyOffset(-0.5,  0, "k", 3, rightFingersPlane, 2.8, -4, "middle"),
  fingerKeyOffset(-0.5,  1, ",", 4, rightFingersPlane, 2.8, -4),

  // Column 0.5 (ring) — rows -1, 0, 1
  fingerKey(0.5, -1, "o", 2, rightFingersPlane),
  fingerKey(0.5,  0, "l", 3, rightFingersPlane, "ring"),
  fingerKey(0.5,  1, ".", 4, rightFingersPlane),

  // Column 1.5 (pinky, offset) — rows -1, 0, 1
  fingerKeyOffset(1.5, -1, "p", 2, rightFingersPlane, -13, 6),
  fingerKeyOffset(1.5,  0, ";", 3, rightFingersPlane, -13, 6, "pinky"),
  fingerKeyOffset(1.5,  1, "/", 4, rightFingersPlane, -13, 6),

  // Column 2.5 (extra pinky) — rows -1, 0, 1
  fingerKeyOffset(2.5, -1, "[", 2, rightFingersPlane, -13, 6),
  fingerKeyOffset(2.5,  0, "'", 3, rightFingersPlane, -13, 6),
  fingerKeyOffset(2.5,  1, "\\", 4, rightFingersPlane, -13, 6),
]

// TRACKBALL PLACEMENT (Right hand, outside column 2.5)
// ─────────────────────────────────────────────────────
// The trackball will be positioned approximately at:
//   column: ~3.5, row: ~0 (home row height)
//   on the right hand unit, outside the pinky column.
//
// Cosmos supports trackball types like "trackball-btcpi"
// (34mm BTU/BTCPI trackball) and others. To add one:
//
// Uncomment and add to fingersRight array:
// {
//   type: "trackball-btcpi",  // or "trackball-veichu", etc.
//   aspect: 1,
//   cluster: "fingers",
//   size: { diameter: 34 },
//   position: new Trsf()
//     .placeOnMatrix({
//       column: 3.5,
//       row: 0,
//       ...curvature,
//     })
//     .transformBy(rightFingersPlane),
// }
//
// Note: The actual trackball mount will be designed separately
// using CadQuery with Choc switches (6 keys around trackball).
// This Cosmos model defines the main key matrix only.

// Right thumb cluster — 5 keys (mirrored from left)
const thumbsRight: Key[] = [
  {
    type: "mx-better",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(17.8, [0, 0, 0], [1, 0, 0])
      .rotate(3.2888888888888888, [0, 0, 0], [0, 1, 0])
      .rotate(-8.2, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, 3.5)
      .placeOnMatrix({
        column: 0.4, row: -0.34,
        spacingOfColumns: 20, spacingOfRows: 20,
        curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0
      })
      .transformBy(rightThumbsPlane),
    keycap: { home: "thumb", row: 5, profile: "mt3" }
  },
  {
    type: "mx-better",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(17.8, [0, 0, 0], [1, 0, 0])
      .rotate(3.2888888888888888, [0, 0, 0], [0, 1, 0])
      .rotate(-8.2, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, -4.2)
      .placeOnMatrix({
        column: 0.29, row: 0.67,
        spacingOfColumns: 20, spacingOfRows: 20,
        curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0
      })
      .transformBy(rightThumbsPlane),
    keycap: { home: "thumb", row: 5, profile: "mt3" }
  },
  {
    type: "mx-better",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(15.11111111111111, [0, 0, 0], [1, 0, 0])
      .rotate(16, [0, 0, 0], [0, 1, 0])
      .rotate(-21.8, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, 0.4)
      .placeOnMatrix({
        column: 1.43, row: -0.06,
        spacingOfColumns: 20, spacingOfRows: 20,
        curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0
      })
      .transformBy(rightThumbsPlane),
    keycap: { row: 5, profile: "mt3" }
  },
  {
    type: "mx-better",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(18.2, [0, 0, 0], [1, 0, 0])
      .rotate(-7.111111111111111, [0, 0, 0], [0, 1, 0])
      .rotate(-1, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, 3.1)
      .placeOnMatrix({
        column: -0.64, row: -0.44,
        spacingOfColumns: 20, spacingOfRows: 20,
        curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0
      })
      .transformBy(rightThumbsPlane),
    keycap: { row: 5, profile: "mt3" }
  },
  {
    type: "mx-better",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(18.31111111111111, [0, 0, 0], [1, 0, 0])
      .rotate(-9.088888888888889, [0, 0, 0], [0, 1, 0])
      .rotate(-1.488888888888889, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, -5.3)
      .placeOnMatrix({
        column: -0.75, row: 0.58,
        spacingOfColumns: 20, spacingOfRows: 20,
        curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0
      })
      .transformBy(rightThumbsPlane),
    keycap: { row: 5, profile: "mt3" }
  }
]

export default {
  left: {
    ...options,
    keys: [...fingersLeft, ...thumbsLeft],
    flipConnectors: true
  },
  right: {
    ...options,
    keys: [...fingersRight, ...thumbsRight],
  },
}
