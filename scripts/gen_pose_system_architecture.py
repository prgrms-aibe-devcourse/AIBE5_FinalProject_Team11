#!/usr/bin/env python3
"""
gen_pose_system_architecture.py
Distributed Biometric Pose Evaluation System — Runner's Lunge.

4-swimlane architecture:
  Pipeline A  Mobile Edge        (cyan)   — Camera · Downscaler · IMU · WS Client
  Pipeline B  Inference Bridge   (green)  — WS Stream · Pi OS · Hailo-8 · 3D Extractor
  Pipeline C  Biometric Logic    (purple) — Knee Angle · Stability Eval · State Machine
  Pipeline D  Feedback / HUD     (orange) — JSON Return · SVG Overlay · Voice Synthesis

Plus:
  Calibration gateway  (red)   — inclinometer pre-session gate
  Pi cluster sidebar   (green) — spans lanes B + C right-side
  Cloud backend footer (gray)  — yoga-api Spring Boot

Style: dark theme matching assets/infrastructure_diagram.svg
Output: assets/pose_system_architecture.svg
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib import font_manager

# ── Korean / system font setup ────────────────────────────────────────────
for _fp in [
    '/usr/share/fonts/truetype/nanum/NanumSquareRoundR.ttf',
    '/usr/share/fonts/truetype/nanum/NanumSquareRoundB.ttf',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
]:
    if os.path.exists(_fp):
        font_manager.fontManager.addfont(_fp)
plt.rcParams['font.family'] = ['NanumSquareRound', 'Noto Sans CJK KR', 'DejaVu Sans']

# ── Palette — dark theme (matches infrastructure_diagram.svg) ─────────────
BG       = '#0D1117'
CARD     = '#161B22'
CARD_HL  = '#1C2638'
CYAN     = '#00D4FF'   # Pipeline A — Mobile Edge
GREEN    = '#00CC77'   # Pipeline B — Inference Bridge
PURPLE   = '#A855F7'   # Pipeline C — Biometric Logic
ORANGE   = '#F59E0B'   # Pipeline D — Feedback / HUD
RED      = '#FF7B72'   # Calibration gateway
GRAY     = '#8B949E'   # Cloud backend
GOLD     = '#F0C060'   # Formula / annotation text
WHITE    = '#E6EDF3'   # Primary text
DIM      = '#7D8590'   # Secondary text
PI_BG    = '#0D1F12'   # Pi cluster background
CAL_BG   = '#1A0B0B'   # Calibration band background

# ── Canvas ────────────────────────────────────────────────────────────────
FW, FH = 22, 15
fig, ax = plt.subplots(figsize=(FW, FH), dpi=150)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, FW)
ax.set_ylim(0, FH)
ax.axis('off')
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

# ── Layout constants ──────────────────────────────────────────────────────
LABEL_X  = 0.15
LABEL_W  = 1.90
NODE_W   = 2.50
NODE_H   = 1.15
N        = 4                                    # nodes per swimlane
_left    = LABEL_X + LABEL_W + 0.20            # first node left edge
_right   = 14.70                               # last node right edge (Pi cluster starts ~15.0)
_gap     = (_right - _left - N * NODE_W) / (N - 1)
NODE_CX  = [_left + NODE_W / 2 + i * (NODE_W + _gap) for i in range(N)]

# Y centers (bottom → top)
CLOUD_Y  = 1.10     # cloud backend footer center
LANE_D   = 3.10     # Pipeline D — Feedback/HUD
LANE_C   = 5.40     # Pipeline C — Biometric Logic
LANE_B   = 7.90     # Pipeline B — Inference Bridge
LANE_A   = 10.40    # Pipeline A — Mobile Edge
CAL_Y    = 12.30    # Calibration gateway center
TITLE_Y  = 13.80    # Title

# Pi cluster geometry (right side, spans B + C)
PI_X     = 15.10
PI_W     = 6.65
PI_H     = 5.20
PI_CY    = (LANE_B + LANE_C) / 2 + 0.15       # vertical center between B and C

LANE_H   = 1.85    # swimlane band half-height for the group rectangle

# ── Helpers ───────────────────────────────────────────────────────────────
def rbox(cx, cy, w, h, fc, ec, lw=1.2, r=0.14, alpha=1.0):
    p = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle=f'round,pad=0,rounding_size={r}',
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=2, alpha=alpha,
    )
    ax.add_patch(p)


def node(cx, cy, text, ec, highlight=False, w=None, h=None, fontsize=11.5):
    nw = w or NODE_W
    nh = h or NODE_H
    rbox(cx, cy, nw, nh, CARD_HL if highlight else CARD, ec,
         lw=1.6 if highlight else 1.1)
    ax.text(cx, cy, text, ha='center', va='center',
            fontsize=fontsize, color=WHITE, multialignment='center',
            linespacing=1.45, zorder=3)


def arr(x0, x1, cy, color, lw=1.7, style='->', ls='solid'):
    ax.annotate('',
        xy=(x1 - (w := NODE_W) / 2 - 0.07, cy),
        xytext=(x0 + w / 2 + 0.07, cy),
        arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                        linestyle=ls),
        zorder=4)


def varr(x, y0, y1, color, lw=1.5, ls='solid', label=''):
    """Vertical arrow from y0 down to y1."""
    ax.annotate('',
        xy=(x, y1 + NODE_H / 2 + 0.07),
        xytext=(x, y0 - NODE_H / 2 - 0.07),
        arrowprops=dict(arrowstyle='->', color=color, lw=lw,
                        linestyle=ls),
        zorder=4)
    if label:
        ax.text(x + 0.12, (y0 + y1) / 2, label,
                fontsize=9.5, color=color, va='center', zorder=5)


def lane_band(cy, color, label_top, label_btm=''):
    """Draw the swimlane group rectangle and label column."""
    # band rect
    rbox(FW / 2 - 0.15, cy, FW - 0.30, LANE_H * 2 + 0.20,
         BG, color, lw=1.4, r=0.20, alpha=0.0)  # transparent fill — border only
    # left fill with slight tint
    rbox(FW / 2 - 0.15, cy, FW - 0.30, LANE_H * 2 + 0.20,
         color, color, lw=0, r=0.20, alpha=0.04)
    # label box
    rbox(LABEL_X + LABEL_W / 2, cy, LABEL_W, LANE_H * 2,
         CARD_HL, color, lw=1.4)
    ax.text(LABEL_X + LABEL_W / 2, cy + 0.22, label_top,
            ha='center', va='center', fontsize=11, fontweight='bold',
            color=color, zorder=3)
    if label_btm:
        ax.text(LABEL_X + LABEL_W / 2, cy - 0.28, label_btm,
                ha='center', va='center', fontsize=9.5, color=DIM, zorder=3)


# ═════════════════════════════════════════════════════════════════════════
# TITLE
# ═════════════════════════════════════════════════════════════════════════
ax.text(FW / 2, TITLE_Y,
        'Distributed Biometric Pose System  —  Runner\'s Lunge',
        ha='center', va='center', fontsize=22, fontweight='bold',
        color=WHITE, zorder=5)
ax.text(FW / 2, TITLE_Y - 0.55,
        'Edge Client (Phone + Watch)  ·  Compute Node (Raspberry Pi 4 + Hailo-8)  ·  Cloud Backend (yoga-api)',
        ha='center', va='center', fontsize=12, color=DIM, zorder=5)
ax.axhline(y=TITLE_Y - 0.85, xmin=0.01, xmax=0.99,
           color='#30363D', linewidth=1.2, zorder=2)

# ═════════════════════════════════════════════════════════════════════════
# CALIBRATION GATEWAY BANNER
# ═════════════════════════════════════════════════════════════════════════
rbox(FW / 2, CAL_Y, FW - 0.30, 1.0, CAL_BG, RED, lw=1.8, r=0.16)
ax.text(FW / 2, CAL_Y + 0.20,
        '⚙  Phase 0 — Setup Calibration  (runs before every session)',
        ha='center', va='center', fontsize=13, fontweight='bold',
        color=RED, zorder=5)
ax.text(FW / 2, CAL_Y - 0.22,
        'react-native-sensors Accelerometer  ·  '
        r'θ_tilt = atan2(√(x²+z²), |y|) × 180/π  ·  '
        'Target: θ_tilt < 5° sustained 2 s  →  APPROVED  ✓',
        ha='center', va='center', fontsize=10.5, color=DIM, zorder=5)

# Calibration → Pipeline A arrow
varr(NODE_CX[0], CAL_Y - 0.50, LANE_A + 0.62, RED, lw=1.4,
     ls='dashed', label='APPROVED')

# ═════════════════════════════════════════════════════════════════════════
# PIPELINE A — Mobile Edge
# ═════════════════════════════════════════════════════════════════════════
lane_band(LANE_A, CYAN, 'Pipeline A', 'Mobile Edge')

A_NODES = [
    'React Native\nVision Camera\nJPEG @ 60%',
    'Frame Downscaler\n+ frameId (UUID)\ncapturedAt stamp',
    'IMU Sync\nWatch accel/gyro\nBT / HealthKit',
    'WebSocket Client\nauto-reconnect\n3 s fallback → Lite',
]
for i, txt in enumerate(A_NODES):
    node(NODE_CX[i], LANE_A, txt, CYAN, highlight=(i == 3))
    if i:
        arr(NODE_CX[i - 1], NODE_CX[i], LANE_A, CYAN)

# A[3] → Pi cluster (right)
ax.annotate('',
    xy=(PI_X - 0.10, LANE_A),
    xytext=(NODE_CX[3] + NODE_W / 2 + 0.07, LANE_A),
    arrowprops=dict(arrowstyle='->', color=CYAN, lw=1.5,
                    linestyle='dashed'),
    zorder=4)
ax.text(PI_X - 0.22, LANE_A + 0.22, 'WS stream\n(LAN)', fontsize=9.5,
        color=CYAN, ha='right', va='center', zorder=5)

# A[3] → B[0] vertical (WS stream downward)
varr(NODE_CX[3], LANE_A, LANE_B, GREEN, lw=1.4, ls='dashed', label='')

# ═════════════════════════════════════════════════════════════════════════
# PI CLUSTER SIDEBAR  (spans A bottom → C top)
# ═════════════════════════════════════════════════════════════════════════
rbox(PI_X + PI_W / 2, PI_CY, PI_W, PI_H, PI_BG, GREEN, lw=1.8, r=0.22)
ax.text(PI_X + PI_W / 2, PI_CY + PI_H / 2 - 0.35,
        'Compute Node  —  Raspberry Pi 4',
        ha='center', va='center', fontsize=12, fontweight='bold',
        color=GREEN, zorder=4)
ax.text(PI_X + PI_W / 2, PI_CY + PI_H / 2 - 0.72,
        '4 GB RAM  ·  Python 3.11  ·  FastAPI',
        ha='center', va='center', fontsize=10, color=DIM, zorder=4)

# Pi sub-nodes
PI_SUB_W = PI_W - 0.60
PI_SUB_H = 0.90
PI_SUB_X = PI_X + PI_W / 2
pi_sub_tops = [PI_CY + 0.95, PI_CY - 0.05, PI_CY - 1.05]
pi_sub_labels = [
    'WebSocket Server\nFastAPI /ws/pose\nasyncio frame queue',
    'MoveNet Thunder\nTFLite · Hailo-8\n20 TOPS accelerator',
    '3D Landmark\nExtractor\n{x,y,z,vis} × 33',
]
for i, (py, txt) in enumerate(zip(pi_sub_tops, pi_sub_labels)):
    node(PI_SUB_X, py, txt, GREEN, highlight=(i == 2),
         w=PI_SUB_W, h=PI_SUB_H, fontsize=10.5)
    if i:
        ax.annotate('',
            xy=(PI_SUB_X, py + PI_SUB_H / 2 + 0.05),
            xytext=(PI_SUB_X, pi_sub_tops[i - 1] - PI_SUB_H / 2 - 0.05),
            arrowprops=dict(arrowstyle='->', color=GREEN, lw=1.4),
            zorder=4)

# Pi returns landmarks back to Pipeline B node 3 (3D extractor → lane_b last node)
ax.annotate('',
    xy=(NODE_CX[3] + NODE_W / 2 + 0.07, LANE_B),
    xytext=(PI_X - 0.10, LANE_B - 0.30),
    arrowprops=dict(arrowstyle='->', color=GREEN, lw=1.5,
                    connectionstyle='arc3,rad=0.15'),
    zorder=4)
ax.text(NODE_CX[3] + NODE_W / 2 + 0.16, LANE_B + 0.28,
        'JSON landmarks', fontsize=9.5, color=GREEN, ha='left', va='center', zorder=5)

# ═════════════════════════════════════════════════════════════════════════
# PIPELINE B — Inference Bridge
# ═════════════════════════════════════════════════════════════════════════
lane_band(LANE_B, GREEN, 'Pipeline B', 'Inference Bridge')

B_NODES = [
    'WebSocket / RTSP\nLAN frame stream\nPhone → Pi :8765',
    'Raspberry Pi OS\nFastAPI WS server\nasyncio queue',
    'Hailo-8 Accel.\n20 TOPS\nMoveNet Thunder',
    '3D Landmark\nExtractor\n{x,y,z,vis}×33',
]
for i, txt in enumerate(B_NODES):
    node(NODE_CX[i], LANE_B, txt, GREEN, highlight=(i == 3))
    if i:
        arr(NODE_CX[i - 1], NODE_CX[i], LANE_B, GREEN)

# B[3] → C[0] vertical
varr(NODE_CX[3], LANE_B, LANE_C, PURPLE, lw=1.5, label='3D lmks')

# ═════════════════════════════════════════════════════════════════════════
# LANE SEPARATOR + FORMULA
# ═════════════════════════════════════════════════════════════════════════
sep_bc = (LANE_B + LANE_C) / 2
ax.axhline(y=sep_bc, xmin=0.01, xmax=0.67,
           color='#30363D', linewidth=0.6, linestyle='--', alpha=0.6, zorder=1)

# Latency compensation annotation (between B and C)
ax.text(FW * 0.35, sep_bc + 0.08,
        'Latency compensation: pos(t) = lerp(Lₙ₋₁, Lₙ, Δt)  ·  freeze if piLatencyMs > 200 ms',
        ha='center', va='center', fontsize=10, color=GOLD,
        style='italic', zorder=3)

# ═════════════════════════════════════════════════════════════════════════
# PIPELINE C — Biometric Logic
# ═════════════════════════════════════════════════════════════════════════
lane_band(LANE_C, PURPLE, 'Pipeline C', 'Biometric Logic')

# Only 3 nodes for this lane — center them in the same x zone
C3_GAP  = (_right - _left - 3 * NODE_W) / 2
C3_CX   = [_left + NODE_W / 2 + i * (NODE_W + C3_GAP) for i in range(3)]

C_NODES = [
    'Knee Angle\narccos(KH·KA / |KH||KA|)\n3D vectors',
    'Stability Eval\nComplementary filter\nα·ω_gyro + (1-α)·RMS_vis',
    'State Machine\nIDLE → START → LOW\n→ COMPLETE',
]
for i, txt in enumerate(C_NODES):
    node(C3_CX[i], LANE_C, txt, PURPLE, highlight=(i == 2))
    if i:
        ax.annotate('',
            xy=(C3_CX[i] - NODE_W / 2 - 0.07, LANE_C),
            xytext=(C3_CX[i - 1] + NODE_W / 2 + 0.07, LANE_C),
            arrowprops=dict(arrowstyle='->', color=PURPLE, lw=1.7),
            zorder=4)

# Threshold formula annotation
ax.text((C3_CX[0] + C3_CX[2]) / 2, LANE_C - LANE_H + 0.28,
        'THRESHOLD_MET:  θ_knee ≤ 90°  ∧  wobble < 0.15 rad/s  ∧  hold 500 ms',
        ha='center', va='center', fontsize=10, color=GOLD,
        style='italic', zorder=3)

# C[2] → D[0] vertical
varr(C3_CX[2], LANE_C, LANE_D, ORANGE, lw=1.5, label='state evt')

# ═════════════════════════════════════════════════════════════════════════
# LANE SEPARATOR
# ═════════════════════════════════════════════════════════════════════════
sep_cd = (LANE_C + LANE_D) / 2
ax.axhline(y=sep_cd, xmin=0.01, xmax=0.67,
           color='#30363D', linewidth=0.6, linestyle='--', alpha=0.6, zorder=1)

# ═════════════════════════════════════════════════════════════════════════
# PIPELINE D — Feedback / HUD
# ═════════════════════════════════════════════════════════════════════════
lane_band(LANE_D, ORANGE, 'Pipeline D', 'Feedback / HUD')

D3_GAP = C3_GAP
D3_CX  = [_left + NODE_W / 2 + i * (NODE_W + D3_GAP) for i in range(3)]

D_NODES = [
    'JSON Return\n{frameId, landmarks}\nlatency buffer / lerp',
    'RN SVG Overlay\nreact-native-svg\nReanimated shared vals',
    'Voice Synthesis\nTTS coaching cues\n"Hold steady"',
]
for i, txt in enumerate(D_NODES):
    node(D3_CX[i], LANE_D, txt, ORANGE, highlight=(i == 2))
    if i:
        ax.annotate('',
            xy=(D3_CX[i] - NODE_W / 2 - 0.07, LANE_D),
            xytext=(D3_CX[i - 1] + NODE_W / 2 + 0.07, LANE_D),
            arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.7),
            zorder=4)

# D[1] → Cloud footer
ax.annotate('',
    xy=(D3_CX[1], CLOUD_Y + 0.48 + 0.07),
    xytext=(D3_CX[1], LANE_D - NODE_H / 2 - 0.07),
    arrowprops=dict(arrowstyle='->', color=GRAY, lw=1.4,
                    linestyle='dashed'),
    zorder=4)
ax.text(D3_CX[1] + 0.14, (LANE_D + CLOUD_Y) / 2,
        'POST /sessions\n(on COMPLETE)',
        fontsize=9.5, color=GRAY, va='center', zorder=5)

# ═════════════════════════════════════════════════════════════════════════
# CLOUD BACKEND FOOTER
# ═════════════════════════════════════════════════════════════════════════
rbox(FW / 2, CLOUD_Y, FW - 0.30, 0.96, '#0D1117', GRAY, lw=1.5, r=0.16)
ax.text(FW / 2, CLOUD_Y + 0.22,
        '☁  Cloud Backend  —  yoga-api  (Spring Boot 3.x  ·  Java 21)',
        ha='center', va='center', fontsize=13, fontweight='bold',
        color=GRAY, zorder=5)
ax.text(FW / 2, CLOUD_Y - 0.21,
        'POST /api/v1/sessions  ·  JWT Bearer auth  ·  '
        'Payload: {poseId, repCount, avgKneeAngle, avgWobbleScore, piLatencyMs}  ·  '
        'Offline queue: react-native-mmkv',
        ha='center', va='center', fontsize=10, color=DIM, zorder=5)

# ═════════════════════════════════════════════════════════════════════════
# LEGEND
# ═════════════════════════════════════════════════════════════════════════
LEGEND_Y = 0.32
items = [
    (CYAN,   'Pipeline A — Mobile Edge (Camera · IMU · WS Client)'),
    (GREEN,  'Pipeline B — Inference Bridge (Pi · Hailo-8 · MoveNet)'),
    (PURPLE, 'Pipeline C — Biometric Logic (Trigonometry · Fusion · FSM)'),
    (ORANGE, 'Pipeline D — Feedback / HUD (Overlay · TTS)'),
    (RED,    'Calibration Gateway (inclinometer, pre-session)'),
    (GRAY,   'Cloud Backend — yoga-api Spring Boot'),
]
col_w = FW / len(items)
for k, (col, lbl) in enumerate(items):
    cx = col_w * k + col_w / 2
    ax.add_patch(plt.Rectangle(
        (cx - col_w / 2 + 0.25, LEGEND_Y - 0.12), 0.30, 0.24,
        facecolor=col, edgecolor='none', zorder=4,
    ))
    ax.text(cx - col_w / 2 + 0.65, LEGEND_Y,
            lbl, fontsize=9.5, color=DIM, va='center', zorder=5)
# ═════════════════════════════════════════════════════════════════════════
# SAVE
# ═════════════════════════════════════════════════════════════════════════
OUT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'assets', 'pose_system_architecture.svg')
)
plt.savefig(OUT, format='svg', bbox_inches='tight', pad_inches=0.12, facecolor=BG)
print(f'Saved → {OUT}')
plt.close()
