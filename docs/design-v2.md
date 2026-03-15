# OrthBall V1 Design Spec v2

*Updated: 2026-02-23*

## 方針転換

当初の3分割構想から、**まず1体型で動くもの**を作る方針に変更。
On the 17をベースに、トラックボールを55mmに大型化する。

## コンセプト

**On the 17クローン + 55mmトラックボール + 3Dプリントケース**

成功したらV2で分割化を検討。

## V1 スペック

| 項目 | 仕様 |
|------|------|
| ベース | On the 17 |
| レイアウト | 一体型オルソリニア（左右6×4 + サム6 + Choc6）|
| スイッチ（メイン） | MX互換 ホットスワップ |
| スイッチ（トラックボール横） | Choc v1 × 6個 |
| トラックボール | **55mm**（Perixx PERIPRO-303） |
| ボール支持 | BTU 3点（BOSCH Rexroth 8mm）or セラミック球 |
| センサー | PMW3360（独立センサーPCB） |
| マイコン | RP2040（Pro Micro RP2040） |
| ケース | **3Dプリント** |
| ファームウェア | QMK + Vial |
| 接続 | USB-C 有線 |
| ケース形状 | 底辺が弓なりにカーブするエルゴ形状 |

## キーレイアウト（v4 SVGベース）

```
左手 6列×4行     右手 6列×4行        トラックボール
┌─┬─┬─┬─┬─┬─┐  ┌─┬─┬─┬─┬─┬─┐    ╭───╮
│ │ │ │ │ │ │  │ │ │ │ │ │ │    │55mm│
├─┼─┼─┼─┼─┼─┤  ├─┼─┼─┼─┼─┼─┤    │   │
│ │ │ │ │ │ │  │ │ │ │ │ │ │    ╰───╯
├─┼─┼─┼─┼─┼─┤  ├─┼─┼─┼─┼─┼─┤
│ │ │ │ │ │ │  │ │ │ │ │ │ │
├─┼─┼─┼─┼─┼─┤  ├─┼─┼─┼─┤ │ │  [C][C][C][C][C][C]
│ │ │ │ │ │ │  │ │ │ │ │         Choc×6
└─┴─┴─┴─┘      └─┴─┴─┴─┘
      ╲T T T╱  ╲T T T╱  ← サムキー（扇状）
```

- MXキー: 50個（左右各24 + 最下行2個）
- Chocキー: 6個（トラックボール下、横一列）
- サムキー: 6個（左右各3、扇状に角度付き）
- **合計: 62キー**

## On the 17からの変更点

1. **トラックボール 34mm → 55mm**
   - カップ形状再設計（深さ約22mm、60-70%露出）
   - BTUベアリング検討（55mmならサイズ的に余裕）
   - センサー距離調整（ボール表面から2.4mm）
   - トラックボール部のケース高さが増える

2. **ケース: アクリル積層 → 3Dプリント**
   - トラックボール部の曲面が自由に作れる
   - 一体成型でカップ＋ケース統合可能
   - 底辺のエルゴカーブも実現可能

3. **PCB設計**
   - センサーPCBは独立基板（Charybdis方式参考）
   - メインPCBはOn the 17ベースで改変
   - On the 17のKiCadデータは非公開 → ゼロから設計

## 高さ計算

### MXキー側
| パーツ | 厚み |
|--------|------|
| ボトムプレート | 1.5-2mm |
| 空間（配線） | 4-5mm |
| PCB | 1.6mm |
| PCB〜プレート間 | 5mm |
| スイッチプレート | 1.5mm |
| MXスイッチ（上部） | 6.6mm |
| キーキャップ | 7-8mm |
| **合計** | **約28-30mm** |

### トラックボール側
- 55mmボール、60%露出 → カップ深さ約22mm
- ボール天面はキーキャップより約19mm高い
- ケースのトラックボール部分は盛り上がり形状

## ベアリング方式調査結果

| 方式 | 特徴 | 推奨度 |
|------|------|--------|
| セラミック球（2-3mm） | 安い、簡単、実績多 | ★★★ 最初はこれ |
| ローラーベアリング | 軽い動き出し、方向性あり | ★★ |
| BTU（8mm BOSCH Rexroth） | 最滑らか、55mmに最適 | ★★★ V1後半で検討 |

### 参考オープンソース
- **Adept Anyball mod**: 55mm BTU対応、BOSCH Rexroth 8mm使用
  https://github.com/adept-anyball/mod
- **Charybdis PMW3360 PCB**: センサー基板設計（KiCad、CC-BY-NC-SA）
  https://github.com/Bastardkb/charybdis-pmw-3360-sensor-pcb
- **kepeoのトラックボールケース設計記事**
  https://kepeo.hatenablog.com/entry/2024/09/08/134648

## 開発環境

| ツール | バージョン | 場所 |
|--------|-----------|------|
| KiCad | 9.0.7 | Mac `/Applications/KiCad/` |
| Blender | 4.2.3 LTS | Mac `/Applications/Blender.app` |
| Affinity Designer | - | Mac（SVGレイアウト設計用） |
| CadQuery | venv | Mac `/Users/shudai/Space/keyboard/orthball/.venv/` |
| QMK | - | 未セットアップ |
| 3Dプリンタ | - | 自宅 |

## ファイル構成

```
orthball/
├── docs/
│   ├── design-v1.md      # 旧3分割設計（参考用）
│   ├── design-v2.md      # ← このファイル
│   └── product-vision.md  # 製品ビジョン
├── cad/
│   ├── orthball_plate_v4.svg  # ★ 最新レイアウト（Affinity製）
│   ├── orthball_unified_v1.svg/pdf  # 統合図面
│   ├── extract_keys_v4.py  # キー座標抽出スクリプト
│   └── (旧ファイル群)
├── .venv/                 # Python仮想環境
└── .claude/agents/        # Claude Code用エージェント設定
```

## V2 構想（将来）

- 2分割 or 3分割化
- 各スプリットにPro Micro RP2040
- TRRS接続（左右2分割）
- テンキー = 独立USBマクロパッド（案3）
- BLE化: nice!nano差し替え or XIAO BLE
- ZMK + BLE（PMW3360対応成熟後）

## 現在の進捗

### 完了 ✅
- [x] 設計方針決定（一体型、On the 17ベース）
- [x] キーレイアウトv4確定（Affinity Designer）
- [x] トラックボールベアリング方式調査
- [x] 高さ計算
- [x] KiCad 9.0.7 インストール（Mac）
- [x] キー座標抽出スクリプト作成
- [x] design-v2.md 作成

### 次のステップ 📋
1. **v4 SVGからキー座標を最終確定**（MX 50 + Choc 6 + サム6）
2. **KiCad MCPセットアップ** or Pythonスクリプトでフットプリント自動配置
3. **回路図作成**（RP2040 + PMW3360 + キーマトリクス）
4. **PCBレイアウト生成**
5. **トラックボールカップ3Dモデリング**（Blender or CadQuery）
6. **55mmボール購入**（Perixx PERIPRO-303）
7. **カップ3Dプリント → 物理検証**
8. **ケース3Dモデリング**
9. **QMK/Vialファームウェア**（On the 17参考）
10. **PCB発注**（JLCPCB等）

### ブロッカー ⚠️
- On the 17のKiCadデータは非公開 → PCBはゼロから設計
- CadQuery on Mac venvがSegfault → Blender推奨
