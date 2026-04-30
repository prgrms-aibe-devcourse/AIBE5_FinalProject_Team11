#!/usr/bin/env python3
"""
gen_arch_diagram.py  v2
Professional 3-pipeline architecture diagram.
All elements contained within bounds, evenly spaced.
Output: assets/architecture_diagram.png
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib import font_manager
import os

# ── Korean fonts ──────────────────────────────────────────────────────────
for _fp in [
    '/usr/share/fonts/truetype/nanum/NanumSquareRoundR.ttf',
    '/usr/share/fonts/truetype/nanum/NanumSquareRoundB.ttf',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
]:
    if os.path.exists(_fp):
        font_manager.fontManager.addfont(_fp)
plt.rcParams['font.family'] = ['NanumSquareRound', 'Noto Sans CJK KR', 'DejaVu Sans']

# ── Palette ──────────────────────────────────────────────────────────────
BG    = '#0F170B'
CARD  = '#192312'
CARD2 = '#1F2B18'
SAGE  = '#7CB87A'
EARTH = '#C4866A'
LOTUS = '#B5A4C9'
RED   = '#E07070'
GOLD  = '#D4A853'
DIM   = '#9FAF8C'
WHITE = '#F0EDE6'
RULE  = '#3A6030'

# ── Canvas ────────────────────────────────────────────────────────────────
FW, FH = 16, 9
fig, ax = plt.subplots(figsize=(FW, FH), dpi=150)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, FW)
ax.set_ylim(0, FH)
ax.axis('off')
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

# ── Layout constants ──────────────────────────────────────────────────────
# lane label: x=0.15, width=1.55
# 5 nodes fill x=1.85 to 15.75, evenly spaced
LABEL_X  = 0.15
LABEL_W  = 1.55
NODE_W   = 2.42
NODE_H   = 1.10
N        = 5
_left    = LABEL_X + LABEL_W + 0.15          # first node left edge
_right   = 15.75                              # last node right edge
_total   = _right - _left                     # total horizontal space
_gap     = (_total - N * NODE_W) / (N - 1)   # gap between nodes
NODE_CX  = [_left + NODE_W/2 + i*(NODE_W + _gap) for i in range(N)]

LANE_Y   = [6.65, 4.40, 2.15]   # center y for pipelines A, B, C


def rbox(cx, cy, w, h, fc, ec, lw=1.2, r=0.14):
    p = FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle=f'round,pad=0,rounding_size={r}',
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=2
    )
    ax.add_patch(p)


def node(cx, cy, text, ec, highlight=False):
    rbox(cx, cy, NODE_W, NODE_H, CARD2 if highlight else CARD, ec,
         lw=1.5 if highlight else 1.1)
    ax.text(cx, cy, text, ha='center', va='center',
            fontsize=8.5, color=WHITE, multialignment='center',
            linespacing=1.4, zorder=3)


def arr(x0, x1, cy, color):
    ax.annotate('',
        xy=(x1 - NODE_W/2 - 0.06, cy),
        xytext=(x0 + NODE_W/2 + 0.06, cy),
        arrowprops=dict(arrowstyle='->', color=color, lw=1.7),
        zorder=4)


# ── Title ────────────────────────────────────────────────────────────────
ax.text(FW/2, 8.58,
        'Yogaman.club  ·  기술 아키텍처  —  3개 파이프라인',
        ha='center', va='center', fontsize=17, fontweight='bold',
        color=WHITE, zorder=3)
ax.axhline(y=8.22, xmin=0.015, xmax=0.985,
           color=RULE, linewidth=1.5, zorder=2)

# ── Lane separators (subtle dashes) ──────────────────────────────────────
for sep in [(LANE_Y[0]+LANE_Y[1])/2, (LANE_Y[1]+LANE_Y[2])/2]:
    ax.axhline(y=sep, xmin=0.01, xmax=0.99,
               color=RULE, linewidth=0.55, linestyle='--', alpha=0.45, zorder=1)

# ── Pipeline A  —  포즈 매칭 ────────────────────────────────────────────
cy = LANE_Y[0]
rbox(LABEL_X + LABEL_W/2, cy, LABEL_W, NODE_H, CARD2, SAGE, lw=1.4)
ax.text(LABEL_X + LABEL_W/2, cy, 'Pipeline A\n포즈 매칭',
        ha='center', va='center', fontsize=8.5, fontweight='bold',
        color=SAGE, multialignment='center', linespacing=1.4, zorder=3)

A = [
    'yoga repo\n(poses_db)',
    'enrich_poses.py\nbenefit tags\nkill_switch flag',
    'PostgreSQL\npose_contraindications\n(severity · kill_sw)',
    'Spring Boot\n매칭 엔진\n(REST API)',
    'Top-K Poses\nmatch.yogaman.club\n+ JSON-LD 자동 생성',
]
for i, txt in enumerate(A):
    node(NODE_CX[i], cy, txt, SAGE, highlight=(i == 4))
    if i: arr(NODE_CX[i-1], NODE_CX[i], cy, SAGE)

# ── Pipeline B  —  스튜디오 매칭 ────────────────────────────────────────
cy = LANE_Y[1]
rbox(LABEL_X + LABEL_W/2, cy, LABEL_W, NODE_H, CARD2, EARTH, lw=1.4)
ax.text(LABEL_X + LABEL_W/2, cy, 'Pipeline B\n스튜디오 매칭',
        ha='center', va='center', fontsize=8.5, fontweight='bold',
        color=EARTH, multialignment='center', linespacing=1.4, zorder=3)

B = [
    'User Input\nneed · lat/lon · km',
    'NeedFit Score\n(필요 태그 겹침)',
    'Proximity Score\nHaversine 거리',
    'Specialization\nScore (전문화)',
    'Ranked Studios\nScore = 0.4+0.3+0.3\nStreamlit Demo',
]
for i, txt in enumerate(B):
    node(NODE_CX[i], cy, txt, EARTH, highlight=(i == 4))
    if i: arr(NODE_CX[i-1], NODE_CX[i], cy, EARTH)

# Score formula annotation (below Pipeline B, above Pipeline C separator)
ax.text(FW/2, (LANE_Y[1] + LANE_Y[2])/2 + 0.08,
        'Score  =  NeedFit × 0.40  +  Proximity × 0.30  +  Specialization × 0.30',
        ha='center', va='center', fontsize=8, color=GOLD,
        style='italic', zorder=3)

# ── Pipeline C  —  RAG 챗봇 (Elbee) ────────────────────────────────────
cy = LANE_Y[2]
rbox(LABEL_X + LABEL_W/2, cy, LABEL_W, NODE_H, CARD2, LOTUS, lw=1.4)
ax.text(LABEL_X + LABEL_W/2, cy, 'Pipeline C\nRAG 챗봇',
        ha='center', va='center', fontsize=8.5, fontweight='bold',
        color=LOTUS, multialignment='center', linespacing=1.4, zorder=3)

C = [
    'screenshots/\n(교재 이미지)',
    'ocr_pipeline.py\nTesseract + cv2\n→ 텍스트 추출',
    'GeoDataStore\nkeyword index\n(TF-proxy)',
    'Elbee RAG\nOllama Mistral\n→ OpenAI fallback',
    'Streamed Answer\nelbee.yogaman.club\n+ Person JSON-LD',
]
for i, txt in enumerate(C):
    node(NODE_CX[i], cy, txt, LOTUS, highlight=(i == 4))
    if i: arr(NODE_CX[i-1], NODE_CX[i], cy, LOTUS)

# ── Kill-Switch banner ───────────────────────────────────────────────────
KS_Y, KS_H = 0.18, 0.88
rbox(FW/2, KS_Y + KS_H/2, FW - 0.30, KS_H, '#1A0A0A', RED, lw=2.0, r=0.10)
ax.text(FW/2, KS_Y + KS_H/2,
        '⚠   Kill-Switch 불변식  —  kill_switch = TRUE 포즈는 점수 계산 이전에 완전 제외'
        '     severity:  CAUTION  |  CRITICAL  |  MEDICAL_CLEARANCE',
        ha='center', va='center', fontsize=9.5, fontweight='bold',
        color=RED, zorder=3)

# ── Save ─────────────────────────────────────────────────────────────────
OUT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'assets', 'architecture_diagram.png')
)
plt.savefig(OUT, dpi=150, bbox_inches='tight', pad_inches=0.12, facecolor=BG)
print(f'Saved → {OUT}')
plt.close()
