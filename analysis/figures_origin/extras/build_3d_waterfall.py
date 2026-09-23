"""PUR-NEW 3D waterfall: the measured temperature sweep, all seven realizations.

Drives the new plot3d helpers (the same code the new MCP tools call) against
the running Origin. Data is data/temperature_sweeps.csv as measured -- a
complete 7 x 6 grid, no interpolation and no model.
"""
from __future__ import annotations

import csv
import os
import sys
from collections import defaultdict
from contextlib import suppress

sys.path.insert(0, r"D:\Tools\originlab-mcp\src")

import originpro as op  # noqa: E402

from originlab_mcp.tools.plot3d import (  # noqa: E402
    layer_is_3d,
    plot_via_template,
)

OUT = os.path.dirname(os.path.abspath(__file__))
SRC = r"D:\Research\PUR-NEW\data\temperature_sweeps.csv"

# 顺序让 E2 家族相邻，深度方向上就能看出"同配方四次实现"的散布
ORDER = [
    ("E1 +P", "#1F4E79"),
    ("E1 R01 day-1", "#4A7FB5"),
    ("E2 R01", "#14524F"),
    ("E2 R02", "#1F7A78"),
    ("E2 R02 day-1", "#46A8A0"),
    ("E2 R03", "#84C9C0"),
    ("E3 R03", "#6B4C9A"),
]


def rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return f"color({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)})"


def load() -> tuple[list[float], dict[str, list[float]]]:
    temps: list[float] = []
    series: dict[str, dict[float, float]] = defaultdict(dict)
    with open(SRC, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rid = row["formulation_id"] + " " + row["run_label"]
            if row["retest_after_1d"].lower() == "true":
                rid += " day-1"
            t = float(row["temperature_c"])
            series[rid][t] = float(row["viscosity_reported"])
            if t not in temps:
                temps.append(t)
    temps.sort()
    return temps, {k: [v[t] for t in temps] for k, v in series.items()}


with suppress(Exception):
    op.attach()
op.set_show(True)
op.lt_exec("@GVC=0;")          # 否则导出是深灰底

temps, series = load()
missing = [name for name, _ in ORDER if name not in series]
if missing:
    raise SystemExit(f"源数据里没有这些实现: {missing}")

book = op.new_book("w", lname="PURNEW3D")
wks = book[0]
wks.from_list(0, temps, "Temperature", "\\+(o)C")
for i, (name, _) in enumerate(ORDER):
    wks.from_list(i + 1, series[name], name, "mPa\\(183)s")

roles = {0: "X"}
roles.update({i + 1: "Y" for i in range(len(ORDER))})
graph = plot_via_template(
    op, wks, list(range(len(ORDER) + 1)), "glWater3D", roles=roles)
print("graph:", graph, "is_3d:", layer_is_3d(op, graph))

op.lt_exec(f"win -a {graph};")
op.lt_exec("Layer.Plot.Ungroup();")          # 不拆组，逐条颜色无效

gr = op.find_graph(graph)
gl = gr[0]
for i, (_, hex_color) in enumerate(ORDER):
    gl.plot_list()[i].color = hex_color      # 线色
    op.lt_exec(f"layer.plot = {i + 1};")
    op.lt_exec(f"set %C -cf {rgb(hex_color)};")   # 墙面填充
    op.lt_exec("set %C -w 800;")

# 纵轴保持线性：瀑布是靠偏移把曲线错开的，取对数会把偏移量一起压掉，
# 轴范围会被拉到 1E-7 那种地方。
op.lt_exec('xb.text$ = "Temperature (\+(o)C)";')
op.lt_exec('yl.text$ = "Viscosity (mPa\(183)s)";')
# 深度轴的刻度标签已经把七个实现的名字写全了，标题是多余的，删掉。
op.lt_exec('zf.text$ = " ";')   # zf 才是深度轴标题（zl/zb 不存在）

op.lt_exec("page.width = 6300; page.height = 4700;")   # 160 x 119 mm
op.lt_exec("layer -3d m RD;")                # 复位到模板默认视角，可复现

gp = op.find_graph(graph)
gp.save_fig(os.path.join(OUT, "purnew_3d.png"), width=1800)
gp.save_fig(os.path.join(OUT, "purnew_3d.svg"), width=1800)
print("exported")
