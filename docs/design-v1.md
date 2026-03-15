# OrthBall v1 設計書

## キー配列（KLEベース）

元の配列をそのまま左右分割 + 中央テンキーに分ける。

### 全体レイアウト（元KLE）

```
Row1: Esc    Q      W      E      R      T    |  &7    *8    (9   |  Y      U      I      O      BS     BS
Row2: Tab    A      S      D      F      G    |  $4    %5    *6   |  H      J      K      L      P      ;
Row3: *Shift Z      X      C      V      B    |  !1    @2    #3   |  N      M      <      >      ?/     Shift*
Row4: *Alt   *Win   Space  Esc    *Alt   Space|  Space *Ctrl      |  Enter  *Shift F24    Enter  *Win
      Space  Space  L(2)                      |                   |  L(3)          *Win
```

### 左手ユニット（6列 × 4行）

```
Esc      Q(L4)   W       E       R       T
Tab(*C)  A       S       D       F       G
*Shift   Z       X       C       V       B
*Alt     *Win    Space   Esc     *Alt    Space
Space    Space   L(2)                    *Ctrl
```

- 4行目は最下段修飾キー + サムクラスタ
- MX + 3DP Hotswap
- 立体（Curvatureあり）

### 中央テンキー（3列 × 4行 = 12キー）

```
&7    *8    (9
$4    %5    *6
!1    @2    #3
0     .     ,
```

- 最下段: 0, ., ,（Enterなし）
- MX
- フラット（Curvatureなし）
- USB-CでPC接続（マスター）
- TRRSで左右に分岐

### 右手ユニット（6列 × 4行 + トラックボール + Choc6キー）

```
Y       U       I       O       BS      BS
H       J       K       L       P       ;
N       M       <       >       ?/      Shift*
Enter   *Shift  F24     Enter   *Win
L(3)            *Win
```

右端外側:
```
        ● 55mm TrackBall
        ┌────┬────┐
        │Btn4│Btn5│  Choc（戻る/進む）
        ├──┬──┼──┬──┤
        │B1│Sc│B2│B3│  Choc（左クリ/Scroll/右クリ/中クリ）
        └──┴──┴──┴──┘
```

- MX + 3DP Hotswap（メイン部）
- 立体（Curvatureあり）
- トラックボール: 55mm, PMW3360
- Choc 6キー: 別途CadQueryで設計

## Cosmos設定値

- Keycaps: MT3
- Switches: MX (mx-better)
- Row Curvature: 5°
- Column Curvature: 17°
- Tenting Angle: 12°
- Thumb Cluster: Curved, 3-5キー

## 接続方式

```
左手 ── TRRS ── 中央テンキー ── TRRS ── 右手
                      │
                   USB-C
                      │
                     PC
```

## スイッチ構成

| 部位 | スイッチ | Hotswap |
|------|-----------|----------|
| 左手メイン | MX | 3DP Hotswap |
| 中央テンキー | MX | 3DP Hotswap |
| 右手メイン | MX | 3DP Hotswap |
| 右手ボール周り | Choc | Direct Solder |

## 次のステップ

1. Cosmos Expertコードをこの配列に合わせて修正
2. 3Dプレビューで確認
3. 中央テンキーは別途CadQueryで設計
4. Chocボタン部はCadQueryで設計

*Created: 2026-02-22*
*Status: v1 配列確定*
