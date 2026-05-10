#!/usr/bin/env python3
"""
gen_hud_display.py
High-resolution portrait mockup of the Runner's Lunge HUD.

Output: assets/hud_display.png  (2160 × 4680 px @ 240 dpi)

Layout (top → bottom, figure units):
  0.00–0.14   Status bar  (session timer, latency, Pi connection)
  0.14–0.28   Alert Banner  (3 severity examples, stacked)
  0.28–0.70   Camera / Pose viewport  (skeleton + vector guides)
  0.70–0.80   Biometric gauges  (knee angle arc, stability bar, wobble)
  0.80–0.95   Bottom CTA panel  (hold timer, phase badge, cue text)
  0.95–1.00   Safe area / home indicator
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Arc, FancyArrowPatch, Circle, Wedge
from matplotlib.lines import Line2D
import numpy as np
import os

# ── Output ────────────────────────────────────────────────────────────────────
OUT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'hud_display.png')

# ── Canvas (portrait phone, 9:19.5) ──────────────────────────────────────────
FW, FH = 9.0, 19.5
DPI     = 240
fig, ax = plt.subplots(figsize=(FW, FH), dpi=DPI)
fig.patch.set_facecolor('#0D1117')
ax.set_facecolor('#0D1117')
ax.set_xlim(0, FW)
ax.set_ylim(0, FH)
ax.axis('off')

# ── Palette ───────────────────────────────────────────────────────────────────
BG       = '#0D1117'
CARD     = '#161B22'
CARD_HL  = '#1C2638'
CYAN     = '#00D4FF'
GREEN    = '#00CC77'
AMBER    = '#F59E0B'
RED      = '#FF3B30'
PURPLE   = '#A855F7'
DIM      = '#8B949E'
WHITE    = '#F0F6FC'
DARK_RED = '#3D0C0C'
DARK_GRN = '#0C2E1A'
DARK_AMB = '#2E1E05'

# ── Helper: rounded rectangle ────────────────────────────────────────────────

def rrect(x, y, w, h, color, alpha=1.0, ec='none', lw=0, zorder=2, radius=0.22):
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f'round,pad=0,rounding_size={radius}',
        facecolor=color, edgecolor=ec, linewidth=lw, alpha=alpha, zorder=zorder,
    )
    ax.add_patch(p)
    return p

def label(x, y, txt, fs=10, color=WHITE, weight='normal', ha='center', va='center',
          shadow=True, zorder=10, **kw):
    base = dict(fontsize=fs, ha=ha, va=va, fontweight=weight, zorder=zorder, **kw)
    if shadow:
        ax.text(x + 0.03, y - 0.03, txt, color='#00000088', **base)
    ax.text(x, y, txt, color=color, **base)

# ─────────────────────────────────────────────────────────────────────────────
# 1. PHONE BEZEL
# ─────────────────────────────────────────────────────────────────────────────
BEZEL_X, BEZEL_Y = 0.35, 0.22
BEZEL_W, BEZEL_H = FW - 0.70, FH - 0.44
rrect(BEZEL_X, BEZEL_Y, BEZEL_W, BEZEL_H,
      color='#1A1F26', ec='#30363D', lw=2.5, radius=0.55, zorder=1)
# Dynamic island
rrect(FW/2 - 0.5, BEZEL_Y + BEZEL_H - 0.38, 1.0, 0.26,
      color='#000', radius=0.13, zorder=3)

SCREEN_X = BEZEL_X + 0.08
SCREEN_Y = BEZEL_Y + 0.08
SCREEN_W = BEZEL_W - 0.16
SCREEN_H = BEZEL_H - 0.16

# Screen background (camera feed simulation — dark gradient)
rrect(SCREEN_X, SCREEN_Y, SCREEN_W, SCREEN_H,
      color='#0A0F14', radius=0.44, zorder=2)

# ─────────────────────────────────────────────────────────────────────────────
# 2. STATUS BAR
# ─────────────────────────────────────────────────────────────────────────────
SB_Y = SCREEN_Y + SCREEN_H - 0.90
label(SCREEN_X + 0.28, SB_Y, '00:02:37', fs=10, color=DIM, weight='bold', ha='left')
label(SCREEN_X + SCREEN_W/2, SB_Y, '●  Pi Connected  •  18 ms', fs=9.5, color=GREEN)
label(SCREEN_X + SCREEN_W - 0.15, SB_Y, '92%', fs=9.5, color=DIM, ha='right')

# Thin separator
ax.plot([SCREEN_X + 0.1, SCREEN_X + SCREEN_W - 0.1],
        [SB_Y - 0.32, SB_Y - 0.32],
        color='#21262D', lw=0.8, zorder=4)

# ─────────────────────────────────────────────────────────────────────────────
# 3. ALERT BANNERS (three severity examples, stacked)
# ─────────────────────────────────────────────────────────────────────────────
BANNER_X = SCREEN_X + 0.18
BANNER_W = SCREEN_W - 0.36

def banner(y, bg, ec_color, icon, txt, severity_lbl, fs=18):
    H = 1.15
    rrect(BANNER_X, y, BANNER_W, H, color=bg, ec=ec_color, lw=1.5, radius=0.22, zorder=6)
    # Icon
    label(BANNER_X + 0.38, y + H/2, icon, fs=fs + 4, color=ec_color, shadow=True, zorder=7)
    # Main text
    label(BANNER_X + BANNER_W/2 + 0.18, y + H/2 + 0.16,
          txt, fs=fs, color=ec_color, weight='black', zorder=7)
    # Severity badge
    rrect(BANNER_X + BANNER_W - 1.08, y + 0.10, 0.92, 0.36,
          color=ec_color, radius=0.10, zorder=8)
    label(BANNER_X + BANNER_W - 0.62, y + 0.28,
          severity_lbl, fs=7.5, color=BG, weight='bold', zorder=9)

BANNER_TOP = SB_Y - 1.50

# CRITICAL
banner(BANNER_TOP,
       bg=DARK_RED, ec_color=RED,
       icon='[X]', txt='STOP IMMEDIATELY',
       severity_lbl='CRITICAL', fs=17)

# WARNING
banner(BANNER_TOP - 1.32,
       bg=DARK_AMB, ec_color=AMBER,
       icon='>> ', txt='Watch your balance',
       severity_lbl='WARNING', fs=16)

# INFO
banner(BANNER_TOP - 2.64,
       bg=DARK_GRN, ec_color=GREEN,
       icon='OK', txt='Perfect depth',
       severity_lbl='INFO', fs=16)

# ─────────────────────────────────────────────────────────────────────────────
# 4. COLOUR WASH LABEL
# ─────────────────────────────────────────────────────────────────────────────
WASH_Y = BANNER_TOP - 3.80
rrect(BANNER_X, WASH_Y, BANNER_W, 0.80,
      color='#00CC7722', ec='#00CC7744', lw=1, radius=0.18, zorder=6)
label(SCREEN_X + SCREEN_W/2, WASH_Y + 0.40,
      '[WASH]  Peripheral Color Wash: full-screen green wash when form is correct',
      fs=8.5, color=GREEN, zorder=7)

# ─────────────────────────────────────────────────────────────────────────────
# 5. SKELETON / POSE VIEWPORT
# ─────────────────────────────────────────────────────────────────────────────
POSE_TOP    = WASH_Y - 0.25
POSE_BOTTOM = SCREEN_Y + 6.90
POSE_MID_X  = SCREEN_X + SCREEN_W / 2

# Background vignette
rrect(SCREEN_X + 0.08, POSE_BOTTOM, SCREEN_W - 0.16, POSE_TOP - POSE_BOTTOM,
      color='#080C10', radius=0.30, zorder=3, alpha=0.7)

# ── Stick-figure skeleton (Runner's Lunge, right foot forward) ────────────────
# Normalise to figure units;  figure height spans roughly 4.5 units in this zone
def sk(rx, ry):
    """Map relative skeleton coords [0,1] to figure coords."""
    px = SCREEN_X + 0.35 + rx * (SCREEN_W - 0.70)
    py = POSE_BOTTOM + 0.30 + ry * (POSE_TOP - POSE_BOTTOM - 0.50)
    return px, py

# Joint positions (approximate Runner's Lunge)
joints = {
    'head':    (0.48, 0.92),
    'neck':    (0.48, 0.83),
    'l_sh':    (0.36, 0.80),
    'r_sh':    (0.60, 0.80),
    'l_hip':   (0.40, 0.58),
    'r_hip':   (0.56, 0.58),
    'l_knee':  (0.26, 0.33),   # back knee, lower
    'r_knee':  (0.68, 0.50),   # front knee ~90°
    'l_ank':   (0.24, 0.08),
    'r_ank':   (0.74, 0.12),
    'l_elbow': (0.28, 0.65),
    'r_elbow': (0.70, 0.65),
    'l_wrist': (0.22, 0.50),
    'r_wrist': (0.76, 0.50),
    'mid_hip': (0.48, 0.58),
}

skeleton_edges = [
    ('head','neck'), ('neck','l_sh'), ('neck','r_sh'),
    ('l_sh','l_elbow'), ('l_elbow','l_wrist'),
    ('r_sh','r_elbow'), ('r_elbow','r_wrist'),
    ('neck','mid_hip'),
    ('mid_hip','l_hip'), ('mid_hip','r_hip'),
    ('l_hip','l_knee'), ('l_knee','l_ank'),
    ('r_hip','r_knee'), ('r_knee','r_ank'),
]

# Draw bones
for (a, b) in skeleton_edges:
    x0, y0 = sk(*joints[a])
    x1, y1 = sk(*joints[b])
    ax.plot([x0, x1], [y0, y1], color=CYAN, lw=2.8, alpha=0.85,
            solid_capstyle='round', zorder=8)

# Draw joints
for name, pos in joints.items():
    jx, jy = sk(*pos)
    c = Circle((jx, jy), 0.10,
                facecolor=CYAN if name not in ('r_knee', 'l_knee') else AMBER,
                edgecolor='#000', linewidth=0.8, zorder=9)
    ax.add_patch(c)

# ── HEAD circle
hx, hy = sk(*joints['head'])
ax.add_patch(Circle((hx, hy + 0.18), 0.22,
             facecolor='#1C2638', edgecolor=CYAN, linewidth=2.0, zorder=9))

# ── VECTOR GUIDES — "ideal rail" lines ──────────────────────────────────────
# Front shin guide: ankle → ideal knee position
ideal_r_knee = (0.68, 0.50)  # current
ideal_r_ank  = (0.74, 0.12)
gx0, gy0 = sk(*ideal_r_ank)
gx1, gy1 = sk(*ideal_r_knee)
# Extend guide upward by 15%
gx2 = gx1 + (gx1 - gx0) * 0.08
gy2 = gy1 + (gy1 - gy0) * 0.08
ax.annotate('', xy=(gx2, gy2), xytext=(gx0, gy0),
            arrowprops=dict(arrowstyle='->', color=GREEN, lw=2.0, alpha=0.7),
            zorder=7)

# Back shin guide: ankle → knee
bx0, by0 = sk(*joints['l_ank'])
bx1, by1 = sk(*joints['l_knee'])
ax.plot([bx0, bx1], [by0, by1],
        color=AMBER, lw=2.0, alpha=0.65, linestyle='--', zorder=7)

# Torso vertical guide
tx, ty0 = sk(0.48, 0.58)
_, ty1   = sk(0.48, 0.83)
ax.plot([tx, tx], [ty0, ty1],
        color=PURPLE, lw=1.8, alpha=0.60, linestyle=':', zorder=7)

# ── KNEE ANGLE ARC annotation (front knee) ───────────────────────────────────
rk_x, rk_y = sk(*joints['r_knee'])
angle_arc = Arc((rk_x, rk_y), 0.60, 0.60, angle=0,
                theta1=30, theta2=130, color=AMBER, lw=2.0, zorder=10)
ax.add_patch(angle_arc)
label(rk_x + 0.52, rk_y + 0.28, '91°', fs=10.5, color=AMBER, weight='bold', zorder=11)

# ── DIRECTIONAL ARROW cue (WARNING: watch knee) ──────────────────────────────
lk_x, lk_y = sk(*joints['l_knee'])
ax.annotate('', xy=(lk_x - 0.30, lk_y - 0.35), xytext=(lk_x - 0.04, lk_y - 0.02),
            arrowprops=dict(arrowstyle='->', color=AMBER, lw=2.2, alpha=0.90),
            zorder=11)
label(lk_x - 0.52, lk_y - 0.52, 'Lower', fs=9, color=AMBER, weight='bold', zorder=11)

# ── FLOOR LINE
fl_y = POSE_BOTTOM + 0.18
ax.plot([SCREEN_X + 0.25, SCREEN_X + SCREEN_W - 0.25],
        [fl_y, fl_y], color='#3A4550', lw=1.2, linestyle='--', zorder=5)

# ─────────────────────────────────────────────────────────────────────────────
# 6. BIOMETRIC GAUGES
# ─────────────────────────────────────────────────────────────────────────────
GAUGE_Y    = POSE_BOTTOM - 0.20
GAUGE_H    = 2.60
GAUGE_BOT  = GAUGE_Y - GAUGE_H
GAUGE_MID  = GAUGE_Y - GAUGE_H / 2

rrect(SCREEN_X + 0.08, GAUGE_BOT, SCREEN_W - 0.16, GAUGE_H,
      color=CARD, radius=0.26, zorder=4)

label(SCREEN_X + SCREEN_W / 2, GAUGE_Y - 0.30,
      'BIOMETRICS', fs=9, color=DIM, weight='bold', zorder=6, shadow=False)

# ── Arc gauge: Knee angle ─────────────────────────────────────────────────────
ARC_CX = SCREEN_X + 1.60
ARC_CY = GAUGE_Y - 1.60
ARC_R  = 0.78

# Background arc
ax.add_patch(Arc((ARC_CX, ARC_CY), ARC_R*2, ARC_R*2,
                  angle=0, theta1=0, theta2=180,
                  color='#21262D', lw=8, zorder=5))
# Value arc (91° ≈ 51% of 180°)
ax.add_patch(Arc((ARC_CX, ARC_CY), ARC_R*2, ARC_R*2,
                  angle=0, theta1=0, theta2=91,
                  color=GREEN, lw=8, zorder=6))
# Ideal marker at 90°
ix = ARC_CX + ARC_R * np.cos(np.radians(90))
iy = ARC_CY + ARC_R * np.sin(np.radians(90))
ax.plot([ARC_CX + (ARC_R-0.12)*np.cos(np.radians(90)),
         ARC_CX + (ARC_R+0.12)*np.cos(np.radians(90))],
        [ARC_CY + (ARC_R-0.12)*np.sin(np.radians(90)),
         ARC_CY + (ARC_R+0.12)*np.sin(np.radians(90))],
        color=CYAN, lw=2.0, zorder=7)

label(ARC_CX, ARC_CY - 0.08, '91°', fs=18, color=GREEN, weight='black', zorder=7)
label(ARC_CX, ARC_CY - 0.44, 'KNEE', fs=8.5, color=DIM, zorder=7, shadow=False)

# ── Stability bar ─────────────────────────────────────────────────────────────
SB_GX  = SCREEN_X + 3.30
SB_GY  = GAUGE_Y - 0.88
SB_GW  = 2.50
SB_GH  = 0.38
STAB   = 0.82   # 82%

rrect(SB_GX, SB_GY, SB_GW, SB_GH, color='#21262D', radius=0.12, zorder=5)
rrect(SB_GX, SB_GY, SB_GW * STAB, SB_GH, color=GREEN, radius=0.12, zorder=6)
label(SB_GX + SB_GW / 2, SB_GY + SB_GH / 2,
      f'Stability  {int(STAB*100)}%', fs=9, color=WHITE, weight='bold', zorder=7)

# ── Wobble bar ────────────────────────────────────────────────────────────────
WB_GY  = SB_GY - 0.70
WOBBLE = 0.08 / 0.15   # current / max = 53%
rrect(SB_GX, WB_GY, SB_GW, SB_GH, color='#21262D', radius=0.12, zorder=5)
rrect(SB_GX, WB_GY, SB_GW * WOBBLE, SB_GH, color=AMBER, radius=0.12, zorder=6)
label(SB_GX + SB_GW / 2, WB_GY + SB_GH / 2,
      f'Wobble  0.08 rad/s', fs=9, color=WHITE, weight='bold', zorder=7)

# ── Pi latency chip ───────────────────────────────────────────────────────────
LAT_X = SB_GX
LAT_Y = WB_GY - 0.74
rrect(LAT_X, LAT_Y, 1.14, 0.48, color=CARD_HL, ec=CYAN, lw=1, radius=0.14, zorder=5)
label(LAT_X + 0.57, LAT_Y + 0.24, '18 ms', fs=10, color=CYAN, weight='bold', zorder=6)
rrect(LAT_X + 1.24, LAT_Y, 1.18, 0.48, color=CARD_HL, ec=DIM, lw=0.8, radius=0.14, zorder=5)
label(LAT_X + 1.83, LAT_Y + 0.24, '30 fps', fs=10, color=DIM, weight='bold', zorder=6)

# ─────────────────────────────────────────────────────────────────────────────
# 7. BOTTOM CTA PANEL
# ─────────────────────────────────────────────────────────────────────────────
CTA_H   = 2.80
CTA_BOT = SCREEN_Y + 0.12
CTA_Y   = CTA_BOT + CTA_H

rrect(SCREEN_X + 0.08, CTA_BOT, SCREEN_W - 0.16, CTA_H,
      color='#0E1721', ec='#21262D', lw=1, radius=0.30, zorder=4)

# Phase badge
PH_X = SCREEN_X + 0.30
rrect(PH_X, CTA_BOT + CTA_H - 0.70, 1.70, 0.50,
      color=PURPLE, radius=0.14, zorder=6)
label(PH_X + 0.85, CTA_BOT + CTA_H - 0.45,
      'PHASE 3 · HOLD', fs=9, color=WHITE, weight='bold', zorder=7)

# Hold timer ring
HT_CX = SCREEN_X + SCREEN_W - 0.92
HT_CY = CTA_BOT + CTA_H - 0.50
ax.add_patch(Circle((HT_CX, HT_CY), 0.38,
             facecolor='#0D1117', edgecolor='#21262D', linewidth=4, zorder=5))
# Progress (hold 320 ms / 500 ms = 64%)
ax.add_patch(Wedge((HT_CX, HT_CY), 0.38, 90, 90 - 360*0.64,
             facecolor='none', width=0.12,
             edgecolor=GREEN, linewidth=0, zorder=6))
ax.add_patch(Arc((HT_CX, HT_CY), 0.76, 0.76, angle=90,
                  theta1=0, theta2=360*0.64, color=GREEN, lw=5, zorder=7))
label(HT_CX, HT_CY + 0.04, '320', fs=10, color=GREEN, weight='black', zorder=8)
label(HT_CX, HT_CY - 0.22, 'ms', fs=7.5, color=DIM, zorder=8, shadow=False)

# Main cue text (72pt equivalent at this figure scale)
label(SCREEN_X + SCREEN_W / 2, CTA_BOT + CTA_H - 1.38,
      'Perfect depth', fs=24, color=GREEN, weight='black', zorder=7)

# Korean cue sub-text
label(SCREEN_X + SCREEN_W / 2, CTA_BOT + CTA_H - 1.96,
      'Inhale, lengthen spine · breathe deeper',
      fs=11.5, color='#00CC7799', weight='bold', zorder=7)

# Debounce indicator
label(SCREEN_X + SCREEN_W / 2, CTA_BOT + 0.34,
      '[TTS]  Next cue in 1.7 s',
      fs=8.5, color=DIM, zorder=7, shadow=False)

# ─────────────────────────────────────────────────────────────────────────────
# 8. HOME INDICATOR
# ─────────────────────────────────────────────────────────────────────────────
rrect(FW/2 - 0.60, SCREEN_Y + 0.02, 1.20, 0.20,
      color='#30363D', radius=0.10, zorder=5)

# ─────────────────────────────────────────────────────────────────────────────
# 9. LEGEND / ANNOTATION PANEL (right margin)
# ─────────────────────────────────────────────────────────────────────────────
LEG_X = BEZEL_X + BEZEL_W + 0.10
LEG_TOP = FH - 0.50
LEG_ITEMS = [
    (CYAN,   'Skeleton overlay'),
    (GREEN,  'Vector guide rail\n(ideal position)'),
    (AMBER,  'Directional correction\narrow'),
    (PURPLE, 'Torso vertical guide'),
    (RED,    'CRITICAL strobe border'),
]
for i, (col, txt) in enumerate(LEG_ITEMS):
    ly = LEG_TOP - i * 1.15
    ax.add_patch(Circle((LEG_X + 0.14, ly), 0.10, facecolor=col, zorder=6))
    ax.text(LEG_X + 0.32, ly, txt, fontsize=7.8, color=DIM,
            va='center', zorder=6, linespacing=1.4)

# ─────────────────────────────────────────────────────────────────────────────
# 10. TITLE (above phone)
# ─────────────────────────────────────────────────────────────────────────────
ax.text(FW / 2, FH - 0.24,
        "Runner's Lunge HUD — Cue Overlay System",
        fontsize=14, fontweight='bold', color=WHITE,
        ha='center', va='center', zorder=10)
ax.text(FW / 2, FH - 0.68,
        'React Native  ·  Hailo-8 / Pi Inference  ·  Three Severity Levels',
        fontsize=9, color=DIM, ha='center', va='center', zorder=10)

# ─────────────────────────────────────────────────────────────────────────────
# 11. SAVE
# ─────────────────────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
plt.savefig(OUT, format='png', dpi=DPI,
            bbox_inches='tight', facecolor=fig.get_facecolor())
print(f'Saved → {os.path.abspath(OUT)}')
