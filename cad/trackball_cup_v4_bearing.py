"""
TrackBall Cup v4 for OrthBall - M-BS10 Bearing Unit Version
============================================================
内径57mm, 外径67mm, 壁厚5mm
斜めカット10°, 底面オープン
エレコム M-BS10 ベアリングユニット ポケット x3 (120°間隔)

M-BS10 寸法 (公称): 幅8mm × 奥行7mm × 高さ4mm
※ スナップフィット穴の正確な寸法は実物計測後に調整してください
  → BEARING_* パラメータを変更するだけで穴サイズが変わります

使い方: Fusion 360 → Shift+S → スクリプト → + → このファイル → 実行
"""
import adsk.core, adsk.fusion, math


# ================================================================
# パラメータ (実物計測後にここだけ変更)
# ================================================================

# カップ基本形状
INNER_R = 2.85       # cm (内径57mm → 半径28.5mm)
OUTER_R = 3.35       # cm (外径67mm → 半径33.5mm)
TILT_DEG = 10        # 斜めカット角度
CUT_Z = 0.08         # cm (斜めカット面のZオフセット 0.8mm)
BOTTOM_Z = -2.0      # cm (底面カットZ座標 -20mm)

# M-BS10 ベアリングユニット ポケット寸法 (cm)
# ★ 実物が届いたらノギスで計測してここを修正 ★
BEARING_POCKET_DIAMETER = 0.72   # Φ7.2mm (本体円筒部の直径、仮値)
BEARING_POCKET_DEPTH = 0.40      # 4.0mm  (壁を貫通するポケット深さ)
BEARING_FLANGE_DIAMETER = 0.85   # Φ8.5mm (フランジ/耳部の直径、仮値)
BEARING_FLANGE_DEPTH = 0.10      # 1.0mm  (フランジが壁面に引っかかる段差)

# ベアリング配置 (緯度, 方位角) - 3箇所120°間隔
# 緯度: -55° = 赤道から55°下 (球の底面寄り)
# 方位角: 90°, 210°, 330° = 120°等間隔
BEARING_POSITIONS = [
    (-50, 90),     # 後方
    (-50, 210),    # 前方左
    (-50, 330),    # 前方右
]

# ================================================================


def create_sphere(rootComp, radius, operation):
    """半円アーク+直線でRevolveして球体を作る"""
    sketches = rootComp.sketches
    xzPlane = rootComp.xZConstructionPlane

    sk = sketches.add(xzPlane)

    arcs = sk.sketchCurves.sketchArcs
    arcs.addByThreePoints(
        adsk.core.Point3D.create(0, radius, 0),
        adsk.core.Point3D.create(radius, 0, 0),
        adsk.core.Point3D.create(0, -radius, 0)
    )

    lines = sk.sketchCurves.sketchLines
    lines.addByTwoPoints(
        adsk.core.Point3D.create(0, -radius, 0),
        adsk.core.Point3D.create(0, radius, 0)
    )

    prof = sk.profiles.item(0)

    revolves = rootComp.features.revolveFeatures
    yAxis = rootComp.yConstructionAxis

    revolveInput = revolves.createInput(prof, yAxis, operation)
    angle = adsk.core.ValueInput.createByReal(math.pi * 2)
    revolveInput.setAngleExtent(False, angle)
    return revolves.add(revolveInput)


def create_bearing_pocket(rootComp, shellBody, lat_deg, az_deg):
    """M-BS10用の段付き円筒ポケットを作成してカップからBoolean Cut"""
    sketches = rootComp.sketches
    extrudes = rootComp.features.extrudeFeatures
    combineFeatures = rootComp.features.combineFeatures
    moveFeatures = rootComp.features.moveFeatures

    lat = math.radians(lat_deg)
    az = math.radians(az_deg)

    # 内壁面上の位置
    px = INNER_R * math.cos(lat) * math.cos(az)
    py = INNER_R * math.cos(lat) * math.sin(az)
    pz = INNER_R * math.sin(lat)

    # 法線 (外向き = 球の中心からの方向)
    length = math.sqrt(px*px + py*py + pz*pz)
    nx, ny, nz = px/length, py/length, pz/length

    # --- 段付きカッターを原点に作成 ---

    # 1. フランジ部 (内壁面に引っかかる段差)
    #    Φ8.5mm x 1mm, Z = 0 ~ +1mm (内壁面側に張り出す)
    skF = sketches.add(rootComp.xYConstructionPlane)
    skF.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), BEARING_FLANGE_DIAMETER / 2)
    profF = skF.profiles.item(0)
    extF = extrudes.createInput(profF, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extF.setDistanceExtent(False, adsk.core.ValueInput.createByReal(BEARING_FLANGE_DEPTH))
    fFeat = extrudes.add(extF)
    fBody = fFeat.bodies.item(0)

    # 2. 本体部 (壁を貫通するメインのポケット)
    #    Φ7.2mm x 4mm, Z = 0 ~ -4mm (壁の外側へ向かう)
    skB = sketches.add(rootComp.xYConstructionPlane)
    skB.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), BEARING_POCKET_DIAMETER / 2)
    profB = skB.profiles.item(0)
    extB = extrudes.createInput(profB, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extB.setDistanceExtent(False, adsk.core.ValueInput.createByReal(-BEARING_POCKET_DEPTH))
    bFeat = extrudes.add(extB)
    bBody = bFeat.bodies.item(0)

    # フランジ+本体を結合
    tc = adsk.core.ObjectCollection.create()
    tc.add(bBody)
    ci = combineFeatures.createInput(fBody, tc)
    ci.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    combineFeatures.add(ci)

    # --- 回転: Z軸(0,0,1) → 法線(nx,ny,nz) ---
    bodiesToMove = adsk.core.ObjectCollection.create()
    bodiesToMove.add(fBody)

    cx = -ny
    cy = nx
    cz = 0.0
    cl = math.sqrt(cx*cx + cy*cy + cz*cz)

    if cl > 0.001:
        dot = nz
        rot_angle = math.acos(max(-1.0, min(1.0, dot)))
        ax, ay, az_v = cx/cl, cy/cl, cz/cl

        rotMatrix = adsk.core.Matrix3D.create()
        rotMatrix.setToRotation(
            rot_angle,
            adsk.core.Vector3D.create(ax, ay, az_v),
            adsk.core.Point3D.create(0, 0, 0))

        mi = moveFeatures.createInput2(bodiesToMove)
        mi.defineAsFreeMove(rotMatrix)
        moveFeatures.add(mi)

    # --- 平行移動 → 内壁面位置 ---
    bodiesToMove2 = adsk.core.ObjectCollection.create()
    bodiesToMove2.add(fBody)

    transMatrix = adsk.core.Matrix3D.create()
    transMatrix.translation = adsk.core.Vector3D.create(px, py, pz)

    mi2 = moveFeatures.createInput2(bodiesToMove2)
    mi2.defineAsFreeMove(transMatrix)
    moveFeatures.add(mi2)

    # --- Boolean Cut ---
    tc2 = adsk.core.ObjectCollection.create()
    tc2.add(fBody)
    ci2 = combineFeatures.createInput(shellBody, tc2)
    ci2.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    combineFeatures.add(ci2)


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface

    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        rootComp = design.rootComponent

        # ============================================================
        # 1. 外側の球体
        # ============================================================
        outerFeature = create_sphere(rootComp, OUTER_R,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # ============================================================
        # 2. 内側の球体 → Boolean Cut でシェル化
        # ============================================================
        innerFeature = create_sphere(rootComp, INNER_R,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        combineFeatures = rootComp.features.combineFeatures
        outerBody = outerFeature.bodies.item(0)
        innerBody = innerFeature.bodies.item(0)

        toolBodies = adsk.core.ObjectCollection.create()
        toolBodies.add(innerBody)
        combineInput = combineFeatures.createInput(outerBody, toolBodies)
        combineInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        combineFeatures.add(combineInput)

        shellBody = outerBody

        # ============================================================
        # 3. 斜めカット (10°)
        # ============================================================
        constructionPlanes = rootComp.constructionPlanes
        planeInput = constructionPlanes.createInput()
        planeInput.setByAngle(
            rootComp.xConstructionAxis,
            adsk.core.ValueInput.createByReal(math.radians(TILT_DEG)),
            rootComp.xYConstructionPlane
        )
        tiltPlane = constructionPlanes.add(planeInput)

        planeInput2 = constructionPlanes.createInput()
        planeInput2.setByOffset(
            tiltPlane,
            adsk.core.ValueInput.createByReal(CUT_Z)
        )
        cutPlane = constructionPlanes.add(planeInput2)

        extrudes = rootComp.features.extrudeFeatures
        sketches = rootComp.sketches

        skCut = sketches.add(cutPlane)
        skCut.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(-10, -10, 0),
            adsk.core.Point3D.create(10, 10, 0)
        )
        profCut = skCut.profiles.item(0)

        extCut = extrudes.createInput(profCut, adsk.fusion.FeatureOperations.CutFeatureOperation)
        extCut.setAllExtent(adsk.fusion.ExtentDirections.PositiveExtentDirection)
        extrudes.add(extCut)

        # ============================================================
        # 4. 底面カット (Z=-20mm以下を除去)
        # ============================================================
        planeInput3 = constructionPlanes.createInput()
        planeInput3.setByOffset(
            rootComp.xYConstructionPlane,
            adsk.core.ValueInput.createByReal(BOTTOM_Z)
        )
        bottomPlane = constructionPlanes.add(planeInput3)

        skBot = sketches.add(bottomPlane)
        skBot.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(-10, -10, 0),
            adsk.core.Point3D.create(10, 10, 0)
        )
        profBot = skBot.profiles.item(0)

        extBot = extrudes.createInput(profBot, adsk.fusion.FeatureOperations.CutFeatureOperation)
        extBot.setAllExtent(adsk.fusion.ExtentDirections.NegativeExtentDirection)
        extrudes.add(extBot)

        # ============================================================
        # 5. M-BS10 ベアリングユニット ポケット x3
        # ============================================================
        for lat_deg, az_deg in BEARING_POSITIONS:
            create_bearing_pocket(rootComp, shellBody, lat_deg, az_deg)

        # ============================================================
        # 完了
        # ============================================================
        app.activeViewport.fit()

        ui.messageBox(
            'トラックボールカップ v4 完成！\n\n'
            'M-BS10 ベアリングユニット対応\n'
            '内径: 57mm / 外径: 67mm / 壁厚: 5mm\n'
            f'傾斜: {TILT_DEG}° / ベアリングポケット: {len(BEARING_POSITIONS)}箇所\n\n'
            '★ M-BS10実物が届いたら BEARING_* パラメータを計測値に更新してください\n\n'
            'エクスポート: ファイル → エクスポート → STL')

    except Exception as e:
        if ui:
            ui.messageBox(f'エラー: {str(e)}\n\nLine: {e.__traceback__.tb_lineno}')
