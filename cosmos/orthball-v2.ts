// Orthball v2 - Ortholinear + Trackball
// 6col × 3row per hand, MX 3DP Hotswap, Trackball on right
// 2026-02-22

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

// Planes (from Cosmos default - tenting 12°)
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

// Curvature settings
const curvature = {
  spacingOfColumns: 21.5,
  spacingOfRows: 20.5,
  curvatureOfRow: 5,
  curvatureOfColumn: 17,
  arc: 0
}

// Helper: standard ortho key (no column offset)
function orthoKey(
  column: number, row: number, letter: string,
  keycapRow: number, plane: any, home?: string
): Key {
  return {
    type: "mx-hotswap",
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

// ============================================================
// LEFT HAND — 6 columns × 3 rows (ortholinear, no offsets)
//   Col -2.5: Esc  Tab  Shift  (outer pinky)
//   Col -1.5: Q    A    Z      (pinky)
//   Col -0.5: W    S    X      (ring)
//   Col  0.5: E    D    C      (middle)
//   Col  1.5: R    F    V      (index)
//   Col  2.5: T    G    B      (inner)
// ============================================================
const fingersLeft: Key[] = [
  // Col -2.5 (outer pinky)
  orthoKey(-2.5, -1, "Esc", 2, leftFingersPlane),
  orthoKey(-2.5,  0, "Tab", 3, leftFingersPlane),
  orthoKey(-2.5,  1, "Sft", 4, leftFingersPlane),

  // Col -1.5 (pinky)
  orthoKey(-1.5, -1, "q", 2, leftFingersPlane),
  orthoKey(-1.5,  0, "a", 3, leftFingersPlane, "pinky"),
  orthoKey(-1.5,  1, "z", 4, leftFingersPlane),

  // Col -0.5 (ring)
  orthoKey(-0.5, -1, "w", 2, leftFingersPlane),
  orthoKey(-0.5,  0, "s", 3, leftFingersPlane, "ring"),
  orthoKey(-0.5,  1, "x", 4, leftFingersPlane),

  // Col 0.5 (middle)
  orthoKey(0.5, -1, "e", 2, leftFingersPlane),
  orthoKey(0.5,  0, "d", 3, leftFingersPlane, "middle"),
  orthoKey(0.5,  1, "c", 4, leftFingersPlane),

  // Col 1.5 (index)
  orthoKey(1.5, -1, "r", 2, leftFingersPlane),
  orthoKey(1.5,  0, "f", 3, leftFingersPlane, "index"),
  orthoKey(1.5,  1, "v", 4, leftFingersPlane),

  // Col 2.5 (inner)
  orthoKey(2.5, -1, "t", 2, leftFingersPlane),
  orthoKey(2.5,  0, "g", 3, leftFingersPlane),
  orthoKey(2.5,  1, "b", 4, leftFingersPlane),
]

// Left thumb cluster — 5 keys
const thumbsLeft: Key[] = [
  {
    type: "mx-hotswap",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(17.8, [0, 0, 0], [1, 0, 0])
      .rotate(-3.29, [0, 0, 0], [0, 1, 0])
      .rotate(8.2, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, 3.5)
      .placeOnMatrix({ column: -0.4, row: -0.34, spacingOfColumns: 20, spacingOfRows: 20, curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0 })
      .transformBy(leftThumbsPlane),
    keycap: { letter: "Spc", home: "thumb", row: 5, profile: "mt3" }
  },
  {
    type: "mx-hotswap",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(17.8, [0, 0, 0], [1, 0, 0])
      .rotate(-3.29, [0, 0, 0], [0, 1, 0])
      .rotate(8.2, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, -4.2)
      .placeOnMatrix({ column: -0.29, row: 0.67, spacingOfColumns: 20, spacingOfRows: 20, curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0 })
      .transformBy(leftThumbsPlane),
    keycap: { letter: "Spc", home: "thumb", row: 5, profile: "mt3" }
  },
  {
    type: "mx-hotswap",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(15.11, [0, 0, 0], [1, 0, 0])
      .rotate(-16, [0, 0, 0], [0, 1, 0])
      .rotate(21.8, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, 0.4)
      .placeOnMatrix({ column: -1.43, row: -0.06, spacingOfColumns: 20, spacingOfRows: 20, curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0 })
      .transformBy(leftThumbsPlane),
    keycap: { letter: "Alt", row: 5, profile: "mt3" }
  },
  {
    type: "mx-hotswap",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(18.2, [0, 0, 0], [1, 0, 0])
      .rotate(7.11, [0, 0, 0], [0, 1, 0])
      .rotate(1, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, 3.1)
      .placeOnMatrix({ column: 0.64, row: -0.44, spacingOfColumns: 20, spacingOfRows: 20, curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0 })
      .transformBy(leftThumbsPlane),
    keycap: { letter: "Win", row: 5, profile: "mt3" }
  },
  {
    type: "mx-hotswap",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(18.31, [0, 0, 0], [1, 0, 0])
      .rotate(9.09, [0, 0, 0], [0, 1, 0])
      .rotate(1.49, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, -5.3)
      .placeOnMatrix({ column: 0.75, row: 0.58, spacingOfColumns: 20, spacingOfRows: 20, curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0 })
      .transformBy(leftThumbsPlane),
    keycap: { letter: "L2", row: 5, profile: "mt3" }
  }
]

// ============================================================
// RIGHT HAND — 6 columns × 3 rows + TRACKBALL
//   Col -2.5: Y    H    N      (inner)
//   Col -1.5: U    J    M      (index)
//   Col -0.5: I    K    ,      (middle)
//   Col  0.5: O    L    .      (ring)
//   Col  1.5: BS   P    /      (pinky)
//   Col  2.5: BS   ;    Sft    (outer pinky)
//   Col  3.5: ● TRACKBALL
// ============================================================
const fingersRight: Key[] = [
  // Col -2.5 (inner)
  orthoKey(-2.5, -1, "y", 2, rightFingersPlane),
  orthoKey(-2.5,  0, "h", 3, rightFingersPlane),
  orthoKey(-2.5,  1, "n", 4, rightFingersPlane),

  // Col -1.5 (index)
  orthoKey(-1.5, -1, "u", 2, rightFingersPlane),
  orthoKey(-1.5,  0, "j", 3, rightFingersPlane, "index"),
  orthoKey(-1.5,  1, "m", 4, rightFingersPlane),

  // Col -0.5 (middle)
  orthoKey(-0.5, -1, "i", 2, rightFingersPlane),
  orthoKey(-0.5,  0, "k", 3, rightFingersPlane, "middle"),
  orthoKey(-0.5,  1, ",", 4, rightFingersPlane),

  // Col 0.5 (ring)
  orthoKey(0.5, -1, "o", 2, rightFingersPlane),
  orthoKey(0.5,  0, "l", 3, rightFingersPlane, "ring"),
  orthoKey(0.5,  1, ".", 4, rightFingersPlane),

  // Col 1.5 (pinky)
  orthoKey(1.5, -1, "BS", 2, rightFingersPlane),
  orthoKey(1.5,  0, "p", 3, rightFingersPlane, "pinky"),
  orthoKey(1.5,  1, "/", 4, rightFingersPlane),

  // Col 2.5 (outer pinky)
  orthoKey(2.5, -1, "BS", 2, rightFingersPlane),
  orthoKey(2.5,  0, ";", 3, rightFingersPlane),
  orthoKey(2.5,  1, "Sft", 4, rightFingersPlane),

  // TRACKBALL — column 3.5, centered on home row
  {
    type: "trackball",
    aspect: 1,
    cluster: "fingers",
    position: new Trsf()
      .placeOnMatrix({
        column: 3.5,
        row: 0,
        ...curvature,
      })
      .transformBy(rightFingersPlane),
    keycap: { row: 3, profile: "mt3" }
  },
]

// Right thumb cluster — 5 keys (mirrored)
const thumbsRight: Key[] = [
  {
    type: "mx-hotswap",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(17.8, [0, 0, 0], [1, 0, 0])
      .rotate(3.29, [0, 0, 0], [0, 1, 0])
      .rotate(-8.2, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, 3.5)
      .placeOnMatrix({ column: 0.4, row: -0.34, spacingOfColumns: 20, spacingOfRows: 20, curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0 })
      .transformBy(rightThumbsPlane),
    keycap: { letter: "Ent", home: "thumb", row: 5, profile: "mt3" }
  },
  {
    type: "mx-hotswap",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(17.8, [0, 0, 0], [1, 0, 0])
      .rotate(3.29, [0, 0, 0], [0, 1, 0])
      .rotate(-8.2, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, -4.2)
      .placeOnMatrix({ column: 0.29, row: 0.67, spacingOfColumns: 20, spacingOfRows: 20, curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0 })
      .transformBy(rightThumbsPlane),
    keycap: { letter: "Sft", home: "thumb", row: 5, profile: "mt3" }
  },
  {
    type: "mx-hotswap",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(15.11, [0, 0, 0], [1, 0, 0])
      .rotate(16, [0, 0, 0], [0, 1, 0])
      .rotate(-21.8, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, 0.4)
      .placeOnMatrix({ column: 1.43, row: -0.06, spacingOfColumns: 20, spacingOfRows: 20, curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0 })
      .transformBy(rightThumbsPlane),
    keycap: { letter: "Win", row: 5, profile: "mt3" }
  },
  {
    type: "mx-hotswap",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(18.2, [0, 0, 0], [1, 0, 0])
      .rotate(-7.11, [0, 0, 0], [0, 1, 0])
      .rotate(-1, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, 3.1)
      .placeOnMatrix({ column: -0.64, row: -0.44, spacingOfColumns: 20, spacingOfRows: 20, curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0 })
      .transformBy(rightThumbsPlane),
    keycap: { letter: "L3", row: 5, profile: "mt3" }
  },
  {
    type: "mx-hotswap",
    aspect: 1,
    cluster: "thumbs",
    position: new Trsf()
      .rotate(18.31, [0, 0, 0], [1, 0, 0])
      .rotate(-9.09, [0, 0, 0], [0, 1, 0])
      .rotate(-1.49, [0, 0, 0], [0, 0, 1])
      .translate(0, 0, -5.3)
      .placeOnMatrix({ column: -0.75, row: 0.58, spacingOfColumns: 20, spacingOfRows: 20, curvatureOfRow: 0, curvatureOfColumn: 0, arc: 0 })
      .transformBy(rightThumbsPlane),
    keycap: { letter: "F24", row: 5, profile: "mt3" }
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
