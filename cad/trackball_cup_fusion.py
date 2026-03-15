"""
TrackBall Cup for OrthBall - Fusion 360 Script
=============================================
内径57mm, 外径67mm, 壁厚5mm
斜めカット10°, 底面オープン
BTU VCN311-7.5 ポケット x4

使い方: Fusion 360 → Shift+S → スクリプト → + → このファイル → 実行
"""
import adsk.core, adsk.fusion, math

def create_sphere(rootComp, radius, operation):
    """半円アーク+直線でRevolveして球体を作る"""
    sketches = rootComp.sketches
    xzPlane = rootComp.xZConstructionPlane

    sk = sketches.add(xzPlane)

    # 半円アーク (右半分): 上端→下端
    arcs = sk.sketchCurves.sketchArcs
    centerPt = adsk.core.Point3D.create(0, 0, 0)
    startPt = adsk.core.Point3D.create(radius, 0, 0)   # 右端(上)
    # 3点アーク: start, along, end
    arcs.addByThreePoints(
        adsk.core.Point3D.create(0, radius, 0),    # 上
        adsk.core.Point3D.create(radius, 0, 0),    # 右
        adsk.core.Point3D.create(0, -radius, 0)    # 下
    )

    # 閉じるための直線 (下端→上端, 回転軸上)
    lines = sk.sketchCurves.sketchLines
    lines.addByTwoPoints(
        adsk.core.Point3D.create(0, -radius, 0),
        adsk.core.Point3D.create(0, radius, 0)
    )

    prof = sk.profiles.item(0)

    # Y軸周りにRevolve 360°
    revolves = rootComp.features.revolveFeatures
    yAxis = rootComp.yConstructionAxis

    revolveInput = revolves.createInput(prof, yAxis, operation)
    angle = adsk.core.ValueInput.createByReal(math.pi * 2)
    revolveInput.setAngleExtent(False, angle)
    return revolves.add(revolveInput)


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface

    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        rootComp = design.rootComponent

        # 単位はcm
        inner_r = 2.85    # 28.5mm → 内径57mm
        outer_r = 3.35    # 33.5mm → 外径67mm
        tilt_deg = 10
        cut_z = 0.08      # 0.8mm
        bottom_z = -2.0   # -20mm

        # BTU寸法 (cm)
        btu_flange_r = 0.46    # Φ9.2mm/2 (9mm + 0.2mm tolerance)
        btu_flange_h = 0.1     # 1mm
        btu_body_r = 0.38      # Φ7.6mm/2 (7.5mm + 0.1mm tolerance)
        btu_body_h = 0.4       # 4mm

        # ============================================================
        # 1. 外側の球体
        # ============================================================
        outerFeature = create_sphere(rootComp, outer_r,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # ============================================================
        # 2. 内側の球体 → Boolean Cut
        # ============================================================
        innerFeature = create_sphere(rootComp, inner_r,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # Shell = Outer - Inner
        combineFeatures = rootComp.features.combineFeatures
        outerBody = outerFeature.bodies.item(0)
        innerBody = innerFeature.bodies.item(0)

        toolBodies = adsk.core.ObjectCollection.create()
        toolBodies.add(innerBody)
        combineInput = combineFeatures.createInput(outerBody, toolBodies)
        combineInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        combineFeatures.add(combineInput)

        shellBody = outerBody  # これがシェル

        # ============================================================
        # 3. 斜めカット (10°)
        # ============================================================
        # XY平面をX軸周りにtilt_deg回転した構築平面
        constructionPlanes = rootComp.constructionPlanes
        planeInput = constructionPlanes.createInput()
        planeInput.setByAngle(
            rootComp.xConstructionAxis,
            adsk.core.ValueInput.createByReal(math.radians(tilt_deg)),
            rootComp.xYConstructionPlane
        )
        tiltPlane = constructionPlanes.add(planeInput)

        # 傾斜平面をZ方向にオフセット
        planeInput2 = constructionPlanes.createInput()
        planeInput2.setByOffset(
            tiltPlane,
            adsk.core.ValueInput.createByReal(cut_z)
        )
        cutPlane = constructionPlanes.add(planeInput2)

        # カット用の大きい四角形
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
            adsk.core.ValueInput.createByReal(bottom_z)
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
        # 5. BTU ポケット x4
        # ============================================================
        btu_positions = [
            (-55, 90),    # Bottom back
            (-55, 210),   # Bottom front-left
            (-55, 330),   # Bottom front-right
            (-5,  90),    # Equator back
        ]

        for lat_deg, az_deg in btu_positions:
            lat = math.radians(lat_deg)
            az = math.radians(az_deg)

            # 内壁面上の位置
            px = inner_r * math.cos(lat) * math.cos(az)
            py = inner_r * math.cos(lat) * math.sin(az)
            pz = inner_r * math.sin(lat)

            # 法線 (外向き)
            length = math.sqrt(px*px + py*py + pz*pz)
            nx, ny, nz = px/length, py/length, pz/length

            # --- BTUカッター（フランジ+ボディ）を原点に作成 ---
            # フランジ: Φ9.2mm x 1mm, Z=0~+1mm
            skF = sketches.add(rootComp.xYConstructionPlane)
            skF.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(0, 0, 0), btu_flange_r)
            profF = skF.profiles.item(0)
            extF = extrudes.createInput(profF, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            extF.setDistanceExtent(False, adsk.core.ValueInput.createByReal(btu_flange_h))
            fFeat = extrudes.add(extF)
            fBody = fFeat.bodies.item(0)

            # ボディ: Φ7.6mm x 4mm, Z=0~-4mm
            skB = sketches.add(rootComp.xYConstructionPlane)
            skB.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(0, 0, 0), btu_body_r)
            profB = skB.profiles.item(0)
            extB = extrudes.createInput(profB, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            extB.setDistanceExtent(False, adsk.core.ValueInput.createByReal(-btu_body_h))
            bFeat = extrudes.add(extB)
            bBody = bFeat.bodies.item(0)

            # フランジ+ボディを結合
            tc = adsk.core.ObjectCollection.create()
            tc.add(bBody)
            ci = combineFeatures.createInput(fBody, tc)
            ci.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
            combineFeatures.add(ci)

            # --- 回転: Z軸(0,0,1) → 法線(nx,ny,nz) ---
            moveFeatures = rootComp.features.moveFeatures
            bodiesToMove = adsk.core.ObjectCollection.create()
            bodiesToMove.add(fBody)

            # 回転軸 = Z × N
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

        # ============================================================
        # 完了
        # ============================================================
        app.activeViewport.fit()

        ui.messageBox(
            'トラックボールカップ完成！\n\n'
            '内径: 57mm / 外径: 67mm / 壁厚: 5mm\n'
            '傾斜: 10° / BTUポケット: 4箇所\n\n'
            'エクスポート: ファイル → エクスポート → STL')

    except Exception as e:
        if ui:
            ui.messageBox(f'エラー: {str(e)}\n\nLine: {e.__traceback__.tb_lineno}')
