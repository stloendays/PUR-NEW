"""Skeletal-formula primitives for the composite figures.

Drawn rather than rendered: the structures here are repeat units and linkages, which
chemistry journals show as 2D skeletal formulae, not as 3D atom renders. Everything is
in millimetres on a Page.canvas, so a bond length is the same on every panel.

Only structures with a public, unambiguous formula are drawn atom-for-atom. A supplier
polyol whose exact backbone is not public is drawn as a labelled generic block instead
of a guessed structure.
"""
import math

from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyBboxPatch

INK = "#1B1B1B"
BOND_W = 0.9
L = 2.6                                   # standard bond length, mm


def _line(ax, p, q, w=BOND_W, color=INK, ls="-", z=3):
    ax.add_line(Line2D([p[0], q[0]], [p[1], q[1]], lw=w, color=color,
                       linestyle=ls, solid_capstyle="round", zorder=z))


def bond(ax, p, q, order=1, color=INK, w=BOND_W, off=0.34):
    """Single, double or triple bond between two points."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    n = math.hypot(dx, dy)
    ux, uy = -dy / n, dx / n
    if order == 1:
        _line(ax, p, q, w, color)
    elif order == 2:
        for s in (+off / 2, -off / 2):
            _line(ax, (p[0] + ux * s, p[1] + uy * s), (q[0] + ux * s, q[1] + uy * s), w, color)
    else:
        _line(ax, p, q, w, color)
        for s in (+off, -off):
            _line(ax, (p[0] + ux * s, p[1] + uy * s), (q[0] + ux * s, q[1] + uy * s), w, color)


def atom(ax, p, text, size=5.6, color=INK, ha="center", va="center", pad=0.0):
    """A heteroatom label. Carbon is implicit, as in any skeletal formula."""
    ax.text(p[0], p[1] + pad, text, fontsize=size, color=color, ha=ha, va=va,
            zorder=5, bbox=dict(boxstyle="round,pad=0.10", fc="white", ec="none"))


def zig(start, n, d=L, up_first=True, angle=30.0):
    """n points of a zig-zag chain from start, alternating above and below the axis."""
    a = math.radians(angle)
    pts, x, y, up = [start], start[0], start[1], up_first
    for _ in range(n):
        x += d * math.cos(a)
        y += d * math.sin(a) * (1 if up else -1)
        pts.append((x, y))
        up = not up
    return pts


def chain(ax, pts, orders=None, color=INK, w=BOND_W):
    orders = orders or [1] * (len(pts) - 1)
    for i in range(len(pts) - 1):
        bond(ax, pts[i], pts[i + 1], orders[i], color, w)


def benzene(ax, c, r=L * 0.92, rot=0.0, color=INK, w=BOND_W, inner=True):
    """A phenylene ring. Returns its six vertices, para pair first."""
    v = [(c[0] + r * math.cos(math.radians(rot + 60 * k)),
          c[1] + r * math.sin(math.radians(rot + 60 * k))) for k in range(6)]
    for k in range(6):
        bond(ax, v[k], v[(k + 1) % 6], 1, color, w)
    if inner:
        ax.add_patch(Circle(c, r * 0.55, fill=False, lw=w * 0.85, ec=color, zorder=3))
    return v


def carbonyl(ax, c, up=True, color=INK, w=BOND_W, label="O"):
    """C=O drawn from a backbone carbon at c."""
    tip = (c[0], c[1] + (L * 0.86 if up else -L * 0.86))
    bond(ax, c, tip, 2, color, w)
    atom(ax, (tip[0], tip[1] + (0.55 if up else -0.55)), label, color=color)
    return tip


def hbond(ax, p, q, color="#EB6969", w=1.0):
    """A hydrogen bond, dotted, the one interaction this paper is actually about."""
    _line(ax, p, q, w, color, ls=(0, (1.0, 1.3)), z=4)


def block(ax, x, y, w, h, text, sub=None, fc="#E3E7F0", ec="#5A6480", lw=0.7,
          fs=6.0, fs_sub=5.2):
    """A labelled generic block, for a component whose exact backbone is not public."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.0,rounding_size=0.8",
                                fc=fc, ec=ec, lw=lw, zorder=2))
    ax.text(x + w / 2, y + h / 2 + (0.9 if sub else 0), text, fontsize=fs, ha="center",
            va="center", color=INK, zorder=4, fontweight="bold")
    if sub:
        ax.text(x + w / 2, y + h / 2 - 1.5, sub, fontsize=fs_sub, ha="center", va="center",
                color="#6B6F76", zorder=4)
