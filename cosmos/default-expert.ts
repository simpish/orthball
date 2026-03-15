// Cosmos Expert Mode - デフォルト（リセット状態）
// 2026-02-22 保存
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
