"""Shared visual system for the composite main figures (Figs. 2-6; Fig. 1 carries its own copy).

183 mm wide pages, Arial 5.3-9 pt, ticks in, the pastel blue/green palette with one red
for the element each panel is about, live text in the SVG and TrueType in the PDF.
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

INK, MID, GRID = "#1B1B1B", "#6B6F76", "#E4E4E4"
FE, RU, OS = "#89AA7B", "#7789B7", "#9DACCB"
OTHER, RED = "#B3B8C0", "#EB6969"
TINT_G, TINT_B, PAPER = "#E4ECDE", "#E3E7F0", "#F0EEEF"
PALE_B, PALE_G, MID_G, LINE = "#C6CCDC", "#CBD7C3", "#ACBF9F", "#D6D6D6"
DARK_G, DARK_B = "#5E7A52", "#5A6480"

# Semantic palette for the main Figures 1-5. One meaning per hue, across all five:
#   blue   realization / rheological state / temperature response
#   orange thermal-hold failure / unstable response
#   green  validated outcome / retained direction
#   grey   null model / inactive / inadmissible / background
# Flat fills only; the one ramp (VOI) is sequential in lightness.
BLUE_XD, BLUE_D, BLUE, BLUE_M, BLUE_L, BLUE_XL = (
    "#1D3A5F", "#2F5B8A", "#4C7DB0", "#8EAFD2", "#CFDDEE", "#EEF3F9")
ORNG_D, ORNG, ORNG_M, ORNG_L, ORNG_XL = (
    "#A9501B", "#D9782F", "#EBAA78", "#F6D8C0", "#FCF1E8")
GRN_D, GRN, GRN_M, GRN_L, GRN_XL = (
    "#2F6B3F", "#4F9460", "#8DBE97", "#D2E7D6", "#EFF6F0")
GRY_D, GRY, GRY_M, GRY_L, GRY_XL = (
    "#4E535A", "#8A9098", "#B9BEC4", "#DDE0E3", "#F3F4F5")
VOI_RAMP = ["#F3F4F5", "#D6DCE4", "#A9B6C7", "#6F829C", "#3F5470", "#1F2E45"]


def tidy(ax, grid="y"):
    """Open axes: no top/right spine, a hairline grid behind the data."""
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if grid:
        ax.grid(axis=grid, color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)

RC = {
    "font.family": "Arial", "font.size": 7, "axes.linewidth": 0.6,
    "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK, "ytick.color": INK, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.major.size": 2.4, "ytick.major.size": 2.4, "xtick.minor.size": 1.3, "ytick.minor.size": 1.3,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.minor.width": 0.5, "ytick.minor.width": 0.5,
    "axes.labelsize": 7, "axes.labelpad": 2.0,
    "mathtext.fontset": "custom", "mathtext.rm": "Arial", "mathtext.it": "Arial:italic",
    "mathtext.bf": "Arial:bold", "mathtext.default": "regular",
    "svg.fonttype": "none", "pdf.fonttype": 42, "legend.frameon": False,
    "hatch.linewidth": 0.5,
}


class Page:
    """A figure laid out in millimetres from its bottom-left corner."""

    def __init__(self, w_mm, h_mm):
        plt.rcParams.update(RC)
        self.W, self.H = w_mm, h_mm
        self.fig = plt.figure(figsize=(w_mm / 25.4, h_mm / 25.4))

    def ax(self, x, y, w, h, **kw):
        return self.fig.add_axes([x / self.W, y / self.H, w / self.W, h / self.H], **kw)

    def canvas(self, x, y, w, h):
        """Axes with data units equal to millimetres, for schematics."""
        a = self.ax(x, y, w, h)
        a.set_xlim(0, w)
        a.set_ylim(0, h)
        a.set_aspect("equal")
        a.axis("off")
        return a

    def letter(self, ch, x, y):
        self.fig.text(x / self.W, y / self.H, ch, fontsize=9, fontweight="bold", va="top", ha="left")

    def title(self, text, x, y):
        self.fig.text(x / self.W, y / self.H, text, fontsize=7, fontweight="bold", va="top", ha="left")

    def save(self, here, stem):
        for ext in ("svg", "pdf", "png"):
            self.fig.savefig(os.path.join(here, "%s.%s" % (stem, ext)), dpi=600,
                             facecolor="white")
        print("wrote %s.{svg,pdf,png}  %.0f x %.0f mm" % (stem, self.W, self.H))


def crop_rgba(path, pad=6):
    img = mpimg.imread(path)
    a = img[:, :, 3] if img.shape[2] == 4 else (img[:, :, :3].min(axis=2) < 0.98).astype(float)
    ys, xs = np.where(a > 0.02)
    return img[max(ys.min() - pad, 0):ys.max() + pad, max(xs.min() - pad, 0):xs.max() + pad]


def boxed(ax):
    for s in ax.spines.values():
        s.set_linewidth(0.6)
    ax.tick_params(which="both", top=False, right=False)


def fmt_minus(s):
    return s.replace("-", "−")
