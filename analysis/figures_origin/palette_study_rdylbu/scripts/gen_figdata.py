# -*- coding: utf-8 -*-
"""Generate the demo dataset suite + the RdYlBu-Top palette for the Origin figure set.

Data are synthetic, generated from a fixed seed, in the HMPUR / polymer-melt
idiom so the figures exercise the same visual grammars as the reference image.
"""
import os
import struct
import numpy as np

OUT = r"C:\Users\ASUS\Documents\工作\Figures_RdYlBu_20260922\data"
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20260922)

# ---------------------------------------------------------------- palette ---
# 14 anchor stops read off the reference image (red -> yellow -> blue).
STOPS = ["#a5232a", "#c62f2a", "#d7312d", "#e35235", "#ef764f", "#fbb475",
         "#fde699", "#fef9b7", "#d2edf2", "#acd2e5", "#7dacd1", "#6090c1",
         "#4573b4", "#115fa4"]


def hex2rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def ramp(n):
    """n colours interpolated along the anchor stops, red first."""
    anchors = np.array([hex2rgb(s) for s in STOPS])
    t_a = np.linspace(0, 1, len(STOPS))
    t_n = np.linspace(0, 1, n)
    out = []
    for k in range(3):
        out.append(np.interp(t_n, t_a, anchors[:, k]))
    rgb = np.clip(np.round(np.array(out).T), 0, 255).astype(int)
    return ["#%02x%02x%02x" % tuple(c) for c in rgb]


def write_pal(path, n=256):
    """Microsoft RIFF PAL, the format Origin's own .pal files use."""
    cols = [hex2rgb(c) for c in ramp(n)]
    body = b"".join(struct.pack("BBBB", int(r), int(g), int(b), 0)
                    for r, g, b in cols)
    data = struct.pack("<HH", 0x0300, n) + body
    chunk = b"data" + struct.pack("<I", len(data)) + data
    riff = b"RIFF" + struct.pack("<I", 4 + len(chunk)) + b"PAL " + chunk
    with open(path, "wb") as f:
        f.write(riff)
    return len(riff)


for pdir in (r"D:\BaiduNetdiskDownload\Origin\Palettes", r"D:\Graph\Palettes"):
    try:
        os.makedirs(pdir, exist_ok=True)
        sz = write_pal(os.path.join(pdir, "RdYlBuTop.pal"))
        print("palette ->", os.path.join(pdir, "RdYlBuTop.pal"), sz, "bytes")
    except Exception as exc:                                   # noqa: BLE001
        print("palette FAILED", pdir, exc)

with open(os.path.join(OUT, "palette_hex.txt"), "w", encoding="utf-8") as f:
    for n in (6, 12, 14, 16, 18):
        f.write("%2d: %s\n" % (n, " ".join(ramp(n))))
print(open(os.path.join(OUT, "palette_hex.txt"), encoding="utf-8").read())


def save(name, header, cols):
    """cols: list of 1-D arrays, NaN-padded to equal length."""
    n = max(len(c) for c in cols)
    mat = np.full((n, len(cols)), np.nan)
    for j, c in enumerate(cols):
        mat[:len(c), j] = c
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(",".join(header) + "\n")
        for row in mat:
            f.write(",".join("" if np.isnan(v) else "%.6g" % v for v in row))
            f.write("\n")
    print(name, mat.shape)


def sig(z):
    return 1.0 / (1.0 + np.exp(-z))


# --------------------------------------------- DS1: chain-contour profile ---
NB = 16
x = np.linspace(0, 300, 301)
BND_A, BND_B = 45.0, 232.0
base = 0.10 + 0.46 * sig((x - 14) / 3.0) + 0.42 * sig((x - 70) / 55.0)
tail = np.where(x > BND_B, 0.36 * np.exp(-(x - BND_B) / 26.0) + 0.055, 1.0)
base = np.where(x > BND_B, base[np.argmin(abs(x - BND_B))] * tail, base)
amp = np.geomspace(34.0, 2.6, NB)
pk = np.geomspace(52.0, 9.0, NB)
line_cols, scat_cols = [], []
for k in range(NB):
    peak = pk[k] * np.exp(-0.5 * ((x - BND_B) / 5.4) ** 2)
    shoulder = 0.22 * pk[k] * np.exp(-0.5 * ((x - BND_B) / 17.0) ** 2)
    y = amp[k] * base + peak + shoulder
    y += rng.normal(0, 0.035 * amp[k] + 0.25, x.size)
    y = np.clip(y, 0, None)
    line_cols.append(y)
    s = np.full(x.size, np.nan)
    idx = rng.choice(np.arange(3, x.size - 3), 62, replace=False)
    s[idx] = np.clip(y[idx] * rng.normal(1.0, 0.26, idx.size)
                     + rng.normal(0, 0.9, idx.size), 0, None)
    scat_cols.append(s)
hdr = (["Contour"] + ["Bin%02d" % (k + 1) for k in range(NB)]
       + ["Pt%02d" % (k + 1) for k in range(NB)])
save("ds1_contour_profile.csv", hdr, [x] + line_cols + scat_cols)

# -------------------------------------------------- DS2: scatter + fit ------
N2 = 2600
u = rng.normal(size=N2)
v = rng.normal(size=N2)
rho = 0.42
hb = 10 ** (0.30 + 0.45 * u)
rate = 0.118 + 0.048 * (rho * u + np.sqrt(1 - rho ** 2) * v)
rate = np.clip(rate, 0.004, 0.298)
lx = np.log10(hb)
R = float(np.corrcoef(lx, rate)[0, 1])
b, a = np.polyfit(lx, rate, 1)
t = R * np.sqrt(N2 - 2) / np.sqrt(1 - R ** 2)
logp = float(np.log10(2.0) - t * t / 2.0 / np.log(10) - np.log10(t * np.sqrt(2 * np.pi)))
xf = np.linspace(lx.min(), lx.max(), 120)
yf = a + b * xf
tau = np.log10(1.0 / rate)          # half-life-like colour variable
save("ds2_scatter_fit.csv",
     ["HBindex", "DecayRate", "LogTau", "FitX", "FitY"],
     [hb, rate, tau, 10 ** xf, yf])
print("DS2  R=%.3f  slope=%.4f  t=%.1f  log10(p)~%.0f" % (R, b, t, logp))

# ------------------------------------------------- DS3: boxes by bin --------
NBOX = 18
centres = np.geomspace(9.2, 1.9, NBOX)
box_cols = []
for k in range(NBOX):
    n = int(rng.integers(320, 460))
    vals = centres[k] * np.exp(rng.normal(0, 0.42, n)) + rng.normal(0, 0.35, n)
    vals = np.clip(vals, 0.02, None)
    box_cols.append(vals)
save("ds3_box_bins.csv", ["Bin%02d" % (k + 1) for k in range(NBOX)], box_cols)
print("DS3  total n =", sum(len(c) for c in box_cols))

# ------------------------------------------------- DS4: XYZ surface ---------
T = np.linspace(90, 150, 41)
H = np.linspace(16, 48, 33)
TT, HH = np.meshgrid(T, H, indexing="ij")
tT = (TT - 90) / 60.0
tH = (HH - 16) / 32.0
Z = (3.62 - 1.42 * tT + 1.18 * tH + 0.92 * tH ** 2 - 0.55 * tT * tH
     + 0.20 * np.sin(3.1 * np.pi * tH) * np.exp(-2.0 * tT)
     + 0.16 * np.exp(-((tT - 0.25) ** 2 + (tH - 0.72) ** 2) / 0.02))
save("ds4_surface.csv", ["Temperature", "HardSeg", "LogEta"],
     [TT.ravel(), HH.ravel(), Z.ravel()])
print("DS4  z range %.2f .. %.2f" % (Z.min(), Z.max()))

# ------------------------------------------------- DS5: 3D bars -------------
cat = np.arange(1, 11) * 0.02          # catalyst loading, wt%
ext = np.arange(1, 9)                  # chain-extender index
CC, EE = np.meshgrid(cat, ext, indexing="ij")
OT = (46 - 190 * (CC - 0.02) - 1.5 * (EE - 1) ** 1.35
      + 12 * np.exp(-((CC - 0.06) / 0.035) ** 2) + rng.normal(0, 0.9, CC.shape))
OT = np.clip(OT, 2.0, None)
save("ds5_bars3d.csv", ["Catalyst", "Extender", "OpenTime"],
     [CC.ravel(), EE.ravel(), OT.ravel()])

# ------------------------------------------------- DS6: 3D scatter ----------
N6 = 1400
hs = rng.uniform(16, 48, N6)
ann = 10 ** rng.uniform(-1.0, 1.9, N6)
mod = (18 + 2.55 * (hs - 16) ** 1.18 * (1 + 0.32 * np.log10(ann + 0.2))
       + rng.normal(0, 22, N6))
mod = np.clip(mod, 5, None)
save("ds6_scatter3d.csv", ["HardSeg", "AnnealTime", "Modulus"], [hs, ann, mod])

# ------------------------------------------------- DS7: FTIR spectra --------
wn = np.linspace(1640, 1790, 401)
times = np.array([0, 0.25, 0.5, 1, 2, 4, 6, 9, 12, 18, 24, 36, 48, 72], float)
spec_cols = []
for j, tt in enumerate(times):
    f = tt / times.max()
    a_hb = 0.28 + 0.62 * (1 - np.exp(-3.1 * f))       # H-bonded C=O 1703
    a_fr = 0.86 - 0.47 * (1 - np.exp(-2.6 * f))       # free C=O 1733
    a_ur = 0.20 + 0.30 * f                            # urea/amide shoulder 1660
    y = (a_hb * np.exp(-0.5 * ((wn - 1702.5 + 1.4 * f) / 9.5) ** 2)
         + a_fr * np.exp(-0.5 * ((wn - 1732.0) / 8.2) ** 2)
         + a_ur * np.exp(-0.5 * ((wn - 1659.0) / 12.5) ** 2)
         + 0.035 + 0.00022 * (wn - 1640)
         + rng.normal(0, 0.0035, wn.size))
    spec_cols.append(y)
save("ds7_spectra.csv", ["Wavenumber"] + ["t%04.1fh" % v for v in times],
     [wn] + spec_cols)

# ------------------------------------------------- DS8: ridgeline -----------
lt = np.linspace(-1.2, 3.4, 320)
NR = 12
ridge = []
for k in range(NR):
    f = k / (NR - 1.0)
    m1, m2 = -0.35 + 1.55 * f, 1.35 + 1.30 * f
    w1, w2 = 0.30 + 0.10 * f, 0.36 + 0.14 * f
    a2 = 0.25 + 0.72 * f
    y = (np.exp(-0.5 * ((lt - m1) / w1) ** 2)
         + a2 * np.exp(-0.5 * ((lt - m2) / w2) ** 2))
    y = y / y.max() + rng.normal(0, 0.006, lt.size)
    ridge.append(y)
save("ds8_ridgeline.csv", ["LogTau"] + ["F%02d" % (k + 1) for k in range(NR)],
     [lt] + ridge)

print("\nall datasets written to", OUT)
