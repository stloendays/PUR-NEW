# RdYlBu 顶刊配色图集（Origin 2024 / originlab MCP）

> **这不是本文的证据。** 本目录是一次配色与图型的技法研究，数据全部是合成的，
> 放在这里只因为它和 `analysis/figures_origin/` 的出图工作共用同一条 Origin 通路，
> 调色板和脚本可以直接复用。它不参与 PUR-NEW 的任何科学主张，也不被正文或 SI 引用。
> 面板集本身见上一级的 `panels_v2/`。

2026-09-22 生成。共 14 张图，全部用参考图里那套红—黄—蓝发散配色，其中 4 张 3D，另有一张四面板组合图。

**数据是按 HMPUR / 聚氨酯热熔胶语境生成的合成数据集（固定种子 20260922），
用来撑满图形密度、做配色和模板的样板，不是任何一次真实计算或实验的结果。**
换成真数据时，把 `data/` 下对应的 CSV 替换成同样列结构的文件，重新导入
`RdYlBu_figure_set.opju` 里的同名工作表即可。

## 配色

从参考图逐个取色后插值得到的 14 个锚点：

```
#a5232a #c62f2a #d7312d #e35235 #ef764f #fbb475 #fde699
#fef9b7 #d2edf2 #acd2e5 #7dacd1 #6090c1 #4573b4 #115fa4
```

常用等分序列（红 → 蓝）：

| n | 色值 |
|---|---|
| 6 | `#a5232a #e8603f #fbc955 #79c4d8 #629cd1 #115fa4` |
| 12 | `#a5232a #c92f2b #db3d30 #ea6643 #f8a36b #fde196 #d2edf2 #acd2e5 #97c1dc #6b9ac7 #4a78b6 #115fa4` |
| 16 | `#a5232a #c22d2a #d2302c #de4532 #e96341 #f38b5c #fbbe7c #fde79b #fef8b5 #dbefe6 #b9dbe9 #93beda #71a1cb #5988be #3e70b2 #115fa4` |
| 18 | `#a5232a #be2c2a #cf302c #db3b2f #e45437 #ed704a #f69a65 #fcc682 #fde89d #fef7b3 #e2f1dd #c2e2ed #a4cbe1 #80aed2 #6998c6 #5382bb #396eb0 #115fa4` |

连续色标已经做成 Origin 调色板文件，256 级，装在两个位置（Origin 两处都会扫到）：

- `D:\BaiduNetdiskDownload\Origin\Palettes\RdYlBuTop.pal` —— 红→蓝
- `D:\BaiduNetdiskDownload\Origin\Palettes\RdYlBuTopR.pal` —— 蓝→红（高值为红，曲面/热图用这个）
- `BridgeRdBu.pal` —— 3 色，桥形图专用（增=红 / 减=蓝 / 合计=灰）
- 同名副本也在 `D:\Graph\Palettes\`

在 MCP 里调用时**名字必须带 `.pal` 后缀**，否则 originpro 会当成 colorlist 名处理、静默失效：
`set_plot_colormap(colormap="RdYlBuTopR.pal")`。

## 图

| 文件 | 图型 | 数据量 |
|---|---|---|
| `Fig1_contour_profile` | 16 条沿链坐标的剖面曲线 + 散点云 | 16 × 301 线 + 16 × 62 点 |
| `Fig2_hbond_vs_rate` | 按弛豫时间分 12 色的散点 + 线性拟合，X 对数轴 | 2600 点 |
| `Fig3_order_by_bin` | 18 组箱线图（含均值、离群点） | 7155 个观测 |
| `Fig4_viscosity_surface3d` | 3D 颜色映射曲面 | 41 × 33 = 1353 网格点 |
| `Fig5_opentime_bars3d` | 3D 柱 | 10 × 8 = 80 根 |
| `Fig6_modulus_scatter3d` | 3D 散点，按模量分 8 色 | 1600 点 |
| `Fig7_ftir_waterfall3d` | 3D 瀑布谱线 | 14 × 401 |
| `Fig8_relaxation_ridgeline` | 2D 偏移山脊图 | 12 × 400 |
| `Fig9_viscosity_contour` | 2D 等高线填充（与 Fig4 同一数据） | 1353 点 |
| `Fig10_descriptor_correlation` | 20 × 20 相关性热图，发散配色以 r = 0 为中点，块结构标注 | 400 个单元（由 400 样本算出） |
| `Fig11_ternary_composition` | 三元组成图，按黏度分 8 色 | 520 个配方 |
| `Fig12_cure_kinetics_bands` | 6 条动力学曲线 + 95% CI 上下界，直接标注温度 | 6 × 61 × 3 |
| `Fig13_viscosity_bridge` | 桥形（瀑布）贡献分解，增/减/合计三色 | 9 项 |
| `Fig14_composite_4panel` | 四面板组合图（a–d = Fig1/2/3/10），183 mm 双栏矢量 | — |

Fig1/2/3/10 内嵌的面板字母 a–d 是为 Fig14 组合图准备的；其余图不带面板字母。

每张图都有 `.png`（2400 px 宽）和 `.svg`（矢量，3D 的四张只有 PNG——OpenGL 图层导出的
SVG 是位图外壳）。`_overview.png` 是全部 14 张的总览。

版面统一按 Nature 双栏 183 mm，轴标题 12 pt、刻度 10 pt、标注 11 pt、面板字母 17 pt 粗体。

## 复现

```
scripts/gen_figdata.py          重新生成 data/ 下全部表（种子 20260922）
scripts/rasterize.sh <f.svg>    用 headless Chrome 把清理过的 SVG 光栅化成 PNG
scripts/compose_svg.py          把多张子图 SVG 嵌套拼成多面板图
scripts/strip_legend_from_svg.py  按包围盒删掉 Origin 删不掉的图例
palettes/*.pal                  三个 Origin 调色板，拷进 Origin 的 Palettes 目录即可
```

需要 numpy 的 Python 和本机 Origin 2024（经 originlab MCP 驱动）。
`scripts/` 里的脚本是这批图实际用的那几个，不是事后补写的。

## 已知限制

- Fig7 的两块背景平面是淡黄/淡青，是 glWater3D 模板自带的。Origin 的 3D 背景平面颜色
  没有 LabTalk 属性可写（写了返回成功但不生效），只能在 Plot Details → Planes 里改，
  或者改完另存成自己的模板。
- Fig4 / Fig5 / Fig6 的刻度标签偏小：3D 图层不吃 `set_graph_font`，也不吃
  `layer.x.label.pt` 之外的写法。轴标题已单独放大到 13 pt。
- 文字对象旁边那条渲染缺陷细线，是用 headless Chrome 重新光栅化清理过的 SVG 得到 PNG，
  不是直接用 Origin 导出的 PNG。
- Fig9 的图例在 Origin 里删不掉（`label -r Legend` / `set_legend(visible=False)` 都静默失效），
  是按包围盒从导出的 SVG 里剔除的；重新导出这张图需要再跑一次同样的剔除。
- Fig10 的两条轴刻度标签是手工放的文字对象：这台机器上 `layer.*.label.type` /
  `numDecPlaces` / `numericFormat` 一族属性全是静默空操作，改不动刻度数字格式。
- Fig11 三元图图层不渲染自由文字对象，所以颜色图例只能写在图注里：
  颜色 = 130 °C 下的 log10 η，蓝 2.4 → 红 5.0。
