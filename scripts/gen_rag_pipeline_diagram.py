#!/usr/bin/env python3
"""
gen_rag_pipeline_diagram.py
Investor-pitch quality diagram: High-Fidelity RAG Pipeline — AEO.
Three-layer swimlane: Ingestion → Agentic Retrieval → Generative Synthesis.
Output: assets/rag_pipeline_diagram.png  (3200 × 1800 px @ 160 dpi)
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib import font_manager

# ─────────────────────────── font setup ───────────────────────────────────
for _fp in [
    '/usr/share/fonts/truetype/nanum/NanumSquareRoundR.ttf',
    '/usr/share/fonts/truetype/nanum/NanumSquareRoundB.ttf',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
]:
    if os.path.exists(_fp):
        font_manager.fontManager.addfont(_fp)
plt.rcParams['font.family'] = ['NanumSquareRound', 'Noto Sans CJK KR', 'DejaVu Sans']

# ─────────────────────────── design tokens ────────────────────────────────
BG          = '#0D1117'
CARD        = '#161B22'
CARD_HL     = '#1C2638'
GOLD        = '#F0C060'   # Layer 1 — Ingestion
GOLD_LANE   = '#1A1506'
GOLD_DIM    = '#7A5E1A'
TEAL        = '#3DD9C2'   # Layer 2 — Retrieval
TEAL_LANE   = '#051514'
TEAL_DIM    = '#1A6B62'
LOTUS       = '#B39DDB'   # Layer 3 — Synthesis
LOTUS_LANE  = '#120E1A'
LOTUS_DIM   = '#5A4A7A'
RED         = '#F87171'
SAGE        = '#7EC8A0'
WHITE       = '#F0F6FC'
MUTED       = '#8B949E'
DIM         = '#3D444D'
RULE        = '#21262D'

# ─────────────────────────── canvas ───────────────────────────────────────
FW, FH = 20.0, 11.25
fig, ax = plt.subplots(figsize=(FW, FH), dpi=160)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, FW)
ax.set_ylim(0, FH)
ax.axis('off')
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

# ─────────────────────────── layout grid ──────────────────────────────────
LABEL_X   = 0.12
LABEL_W   = 1.88
NODES_L   = LABEL_X + LABEL_W + 0.12   # 2.12
NODES_R   = 16.55
KPI_L     = 17.00
KPI_R     = FW - 0.14   # 19.86
KPI_CX    = (KPI_L + KPI_R) / 2
KPI_W     = KPI_R - KPI_L

N       = 5
NODE_W  = 2.58
NODE_H  = 1.34
_total  = NODES_R - NODES_L
_gap    = (_total - N * NODE_W) / (N - 1)
NODE_CX = [NODES_L + NODE_W / 2 + i * (NODE_W + _gap) for i in range(N)]

# Lane centres (y-axis, data coords, origin at bottom)
L1_CY  = 8.80   # Ingestion
L2_CY  = 6.25   # Retrieval
L3_CY  = 3.90   # Synthesis (raised to give table+banner room)
LANE_H = 2.20   # full lane height

# ─────────────────────────── primitives ───────────────────────────────────
def rbox(cx, cy, w, h, fc, ec, lw=1.2, r=0.12, z=2, alpha=1.0):
    p = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle=f'round,pad=0,rounding_size={r}',
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z, alpha=alpha,
    )
    ax.add_patch(p)


def node(cx, cy, title, sub1, sub2, color, highlight=False):
    fc = CARD_HL if highlight else CARD
    border_lw = 2.4 if highlight else 1.4
    rbox(cx, cy, NODE_W, NODE_H, fc, color, lw=border_lw, r=0.15, z=3)
    if highlight:
        ax.plot(
            [cx - NODE_W / 2 + 0.16, cx + NODE_W / 2 - 0.16],
            [cy + NODE_H / 2 - 0.08, cy + NODE_H / 2 - 0.08],
            color=color, lw=3.2, zorder=5, solid_capstyle='round'
        )
    title_color = color if highlight else WHITE
    ax.text(cx, cy + 0.30, title,
            ha='center', va='center', fontsize=12.5, fontweight='bold',
            color=title_color, zorder=4)
    ax.text(cx, cy + 0.02, sub1,
            ha='center', va='center', fontsize=10.5, color=WHITE, zorder=4)
    ax.text(cx, cy - 0.27, sub2,
            ha='center', va='center', fontsize=9.0, color=MUTED, zorder=4)


def h_arrow(cx_from, cx_to, cy, color):
    ax.annotate(
        '',
        xy=(cx_to - NODE_W / 2 - 0.06, cy),
        xytext=(cx_from + NODE_W / 2 + 0.06, cy),
        arrowprops=dict(arrowstyle='->', color=color, lw=1.7, mutation_scale=13),
        zorder=5
    )


def v_connector(x, y_top, y_bot, color, label):
    """Short vertical arrow bridging two lanes, with a text label."""
    ax.annotate(
        '',
        xy=(x, y_bot + 0.06),
        xytext=(x, y_top - 0.06),
        arrowprops=dict(
            arrowstyle='->', color=color, lw=2.4, mutation_scale=14,
        ),
        zorder=5
    )
    mid_y = (y_top + y_bot) / 2
    ax.text(x + 0.14, mid_y, label,
            ha='left', va='center', fontsize=9.5, color=color,
            fontstyle='italic', zorder=5)


def lane_eyebrow(cy, text, color):
    ax.text(NODES_L + 0.06, cy + LANE_H / 2 - 0.14, text,
            ha='left', va='top', fontsize=10.0, color=color, alpha=0.70,
            fontstyle='italic', zorder=4)


# ─────────────────────────── TITLE BAR ────────────────────────────────────
# Background panel
rbox(FW / 2, 10.80, FW, 0.92, BG, BG, lw=0, r=0, z=1)
ax.axhline(y=10.24, xmin=0.004, xmax=0.996, color=RULE, lw=1.4, zorder=2)

# Brand badge
rbox(1.00, 10.80, 1.68, 0.58, CARD, SAGE, lw=1.8, r=0.12, z=4)
ax.text(1.00, 10.81, 'aeogeo',
        ha='center', va='center', fontsize=14.5, fontweight='bold',
        color=SAGE, zorder=5)

# Main title
ax.text(FW / 2 + 0.6, 10.84,
        'High-Fidelity RAG Pipeline  —  Answer Engine Optimization (AEO)',
        ha='center', va='center', fontsize=19.0, fontweight='bold',
        color=WHITE, zorder=5)

# Sub-headline
ax.text(FW / 2 + 0.6, 10.44,
        'Prescription over Prediction  ·  Safety-First Matching  ·  <500 ms P95 Latency  ·  3.2× AI Citation Rate',
        ha='center', va='center', fontsize=11.5, color=MUTED, zorder=5)

# Step column headers
col_headers = [
    ('01', 'SOURCE'), ('02', 'PROCESS'),
    ('03', 'INDEX'),  ('04', 'MATCH'), ('05', 'OUTPUT'),
]
for i, (num, hint) in enumerate(col_headers):
    ax.text(NODE_CX[i], 10.10, f'{num}  {hint}',
            ha='center', va='center', fontsize=10.0, color=DIM,
            fontweight='bold', zorder=4)

# ─────────────────────────── LANE BACKGROUNDS ─────────────────────────────
for cy, bg_col in [(L1_CY, GOLD_LANE), (L2_CY, TEAL_LANE), (L3_CY, LOTUS_LANE)]:
    rbox(FW / 2, cy, FW, LANE_H + 0.08, bg_col, BG, lw=0, r=0.06, z=1, alpha=0.90)

# Lane separator dashed lines
for sep_y in [(L1_CY + L2_CY) / 2, (L2_CY + L3_CY) / 2]:
    ax.axhline(y=sep_y, xmin=0.004, xmax=0.996,
               color=RULE, lw=0.75, linestyle='--', alpha=0.6, zorder=2)

# ─────────────────────────── ACTOR LABEL COLUMN ───────────────────────────
actors = [
    (L1_CY, GOLD,  '01', 'INGESTION\n& KNOWLEDGE\nGRAPH',   'Operators / Providers'),
    (L2_CY, TEAL,  '02', 'AGENTIC\nRETRIEVAL\nENGINE',       'LangGraph + CrewAI'),
    (L3_CY, LOTUS, '03', 'GENERATIVE\nSYNTHESIS\n& AEO',     'Gemini 1.5 Pro / Ollama'),
]
for cy, color, num, title, sub in actors:
    rbox(LABEL_X + LABEL_W / 2, cy, LABEL_W, LANE_H - 0.30,
         CARD, color, lw=1.8, r=0.14, z=3)
    ax.text(LABEL_X + LABEL_W / 2, cy + 0.50, num,
            ha='center', va='center', fontsize=11.5, fontweight='bold',
            color=color, alpha=0.55, zorder=4)
    ax.text(LABEL_X + LABEL_W / 2, cy + 0.08, title,
            ha='center', va='center', fontsize=10.5, fontweight='bold',
            color=color, multialignment='center', linespacing=1.5, zorder=4)
    ax.text(LABEL_X + LABEL_W / 2, cy - 0.58, sub,
            ha='center', va='center', fontsize=8.5, color=MUTED,
            multialignment='center', linespacing=1.4, zorder=4)

# ─────────────────────────── LAYER 1 — Ingestion & Knowledge Graph ────────
lane_eyebrow(L1_CY,
             'Ground Truth — Thousands of Pose Assets  ·  OCR Tesseract+CV2  ·  Anatomical Intelligence Layer',
             GOLD)
L1 = [
    ('Asset Ingestion',        'Pose Library (1000+)',     'OCR Tesseract + CV2'),
    ('Knowledge Enrichment',   'Contraindication Flags',   'Kill-Switch Tags'),
    ('Vector Indexing',        'Pinecone Index',            'Anatomical Contexts'),
    ('Semantic Proximity',     'Physical Need → Cue Map',  'Pose ↔ Need Mapping'),
    ('Knowledge Graph',        'Prescription Model',        'Safety-First Index'),
]
for i, (t, s1, s2) in enumerate(L1):
    node(NODE_CX[i], L1_CY, t, s1, s2, GOLD, highlight=(i == 4))
    if i:
        h_arrow(NODE_CX[i - 1], NODE_CX[i], L1_CY, GOLD)

# ─────────────────────────── LAYER 2 — Agentic Retrieval Engine ───────────
lane_eyebrow(L2_CY,
             'LangGraph + CrewAI  ·  Researcher / Curator / Safety-Auditor Agents  ·  <500 ms P95 Latency',
             TEAL)
L2 = [
    ('NL Query Input',        '"Posture correction"',     '+ Herniated Disc flag'),
    ('Researcher Agent',      'PostGIS Geo-Index',         'Pose Library Pull'),
    ('Curator Agent',         'Need-Score Matrix',         'Cueing Expertise Match'),
    ('Safety Auditor',        'Kill-Switch Gatekeeper',    'Medical Check → Exclude'),
    ('Score & Rank',          'Weighted Match Score',      '0.4+0.3+0.3 Formula'),
]
for i, (t, s1, s2) in enumerate(L2):
    node(NODE_CX[i], L2_CY, t, s1, s2, TEAL, highlight=(i == 4))
    if i:
        h_arrow(NODE_CX[i - 1], NODE_CX[i], L2_CY, TEAL)

# ─────────────────────────── LAYER 3 — Generative Synthesis & AEO ─────────
lane_eyebrow(L3_CY,
             '3.2× AI Citation Rate  ·  AEO-Native JSON-LD  ·  Gemini 1.5 Pro  ·  Prescriptions over Predictions',
             LOTUS)
L3 = [
    ('LLM Synthesis',         'Gemini 1.5 Pro',           'Ollama (Local-First)'),
    ('Match Rationale',       '"Why this match:"',        'Anatomical Alignment'),
    ('Structured Answer',     'Prescription Record',       'Score + Explanation'),
    ('JSON-LD Record',        'Schema.org Markup',         'AEO-Native Format'),
    ('AI Distribution',       'Google AI Overviews',       'Naver Cue · SGE'),
]
for i, (t, s1, s2) in enumerate(L3):
    node(NODE_CX[i], L3_CY, t, s1, s2, LOTUS, highlight=(i == 4))
    if i:
        h_arrow(NODE_CX[i - 1], NODE_CX[i], L3_CY, LOTUS)

# ─────────────────────────── INTER-LAYER CONNECTORS ──────────────────────
# RAG Injection: Pinecone Index (L1 N4) → Researcher Agent (L2 N3)
# Rendered as a vertical connector at NODE_CX[3] between the two lanes.
v_connector(
    NODE_CX[3],
    L1_CY - LANE_H / 2,     # bottom edge of Lane 1
    L2_CY + LANE_H / 2,     # top edge of Lane 2
    GOLD,
    ' Knowledge\n Index'
)

# Grounded Synthesis: Safety Auditor (L2 N5) → LLM Synthesis (L3 N1)
# Rendered as a curved arc so the long left-to-right diagonal is clear.
ax.annotate(
    '',
    xy=(NODE_CX[0], L3_CY + NODE_H / 2 + 0.08),
    xytext=(NODE_CX[4], L2_CY - NODE_H / 2 - 0.08),
    arrowprops=dict(
        arrowstyle='->', color=TEAL, lw=1.9, mutation_scale=12,
        connectionstyle='arc3,rad=0.38',
        linestyle='dashed',
    ),
    zorder=5
)
# Arc label — positioned near the midpoint arc peak
ax.text(
    (NODE_CX[4] + NODE_CX[0]) / 2 + 1.80,
    (L2_CY + L3_CY) / 2 - 0.05,
    'Grounded\nContext',
    ha='center', va='center', fontsize=10.0, color=TEAL,
    fontstyle='italic', zorder=5
)

# ─────────────────────────── KPI PANEL ────────────────────────────────────
# Vertical divider
ax.axvline(x=KPI_L - 0.10, ymin=0.09, ymax=0.97,
           color=RULE, lw=0.9, zorder=2)

# Panel header
ax.text(KPI_CX, 10.43, 'KEY  METRICS',
        ha='center', va='center', fontsize=10.5, fontweight='bold',
        color=MUTED, zorder=4)
ax.axhline(y=10.28, xmin=KPI_L / FW, xmax=KPI_R / FW,
           color=RULE, lw=0.8, zorder=3)

kpi_data = [
    (L1_CY + 0.62, GOLD,  '20 Yrs',     'Expert Domain Data'),
    (L1_CY - 0.28, GOLD,  'RAG',        'Grounded Index'),
    (L2_CY + 0.62, TEAL,  '<500 ms',    'P95 Latency'),
    (L2_CY - 0.28, TEAL,  'CrewAI',     'Multi-Agent'),
    (L3_CY + 0.62, LOTUS, '3.2×',       'Citation Rate'),
    (L3_CY - 0.28, LOTUS, 'JSON-LD',    'AEO Native'),
]
for (ky, kc, kval, klabel) in kpi_data:
    rbox(KPI_CX, ky, KPI_W - 0.12, 0.70, CARD, kc, lw=1.3, r=0.12, z=3)
    ax.text(KPI_CX, ky + 0.13, kval,
            ha='center', va='center', fontsize=15.0, fontweight='bold',
            color=kc, zorder=4)
    ax.text(KPI_CX, ky - 0.18, klabel,
            ha='center', va='center', fontsize=9.5, color=MUTED, zorder=4)

# ─────────────────────────── STAKEHOLDER UX TABLE ─────────────────────────
# Compact three-row table below node area, above the safety banner
TABLE_TOP = L3_CY - LANE_H / 2 - 0.20   # top of table area
COL_W     = (NODES_R - NODES_L) / 3
HDR_H     = 0.44
ROW_H     = 0.38
ROW_GAP   = 0.06
HDR_CY    = TABLE_TOP - HDR_H / 2
headers   = ['Stakeholder', 'Core Expectation', 'UX Solution in Pipeline']
h_colors  = [GOLD, TEAL, LOTUS]
rows = [
    ('Users',      'Safety & Speed',       '<500 ms P95  ·  Safety Filters → Immediate Trust'),
    ('Providers',  'AI Discoverability',   'AEO JSON-LD  ·  3.2× AI Citation Rate'),
    ('Operators',  'Data Integrity',       'Agentic Orchestration  ·  Zero Hallucinations'),
]
# Header row
for j, (hdr, hc) in enumerate(zip(headers, h_colors)):
    hx = NODES_L + j * COL_W + COL_W / 2
    rbox(hx, HDR_CY, COL_W - 0.14, HDR_H, DIM, hc, lw=1.2, r=0.09, z=3)
    ax.text(hx, HDR_CY, hdr,
            ha='center', va='center', fontsize=10.5, fontweight='bold',
            color=WHITE, zorder=4)
# Data rows
row_colors = [GOLD, LOTUS, TEAL]
for ri, (r0, r1, r2) in enumerate(rows):
    ry = HDR_CY - HDR_H / 2 - ROW_GAP - ROW_H / 2 - ri * (ROW_H + ROW_GAP)
    for j, (cell, rc) in enumerate(zip([r0, r1, r2], row_colors)):
        cx_cell = NODES_L + j * COL_W + COL_W / 2
        rbox(cx_cell, ry, COL_W - 0.14, ROW_H, CARD, RULE, lw=0.7, r=0.07, z=3)
        ax.text(cx_cell, ry, cell,
                ha='center', va='center', fontsize=9.5, color=WHITE, zorder=4)

# ─────────────────────────── SAFETY INVARIANT BANNER ─────────────────────
SAFE_CY = 0.35
rbox(FW / 2, SAFE_CY, FW - 0.24, 0.62, '#180A0A', RED, lw=2.2, r=0.10, z=3)
ax.text(1.62, SAFE_CY + 0.14, '⚠  SAFETY INVARIANT',
        ha='left', va='center', fontsize=12.5, fontweight='bold',
        color=RED, zorder=5)
ax.text(1.62, SAFE_CY - 0.13,
        'kill_switch = TRUE poses excluded BEFORE scoring  ·  Severity: CAUTION | CRITICAL | MEDICAL_CLEARANCE',
        ha='left', va='center', fontsize=10.0, color=RED, alpha=0.85, zorder=5)
ax.text(FW - 0.50, SAFE_CY + 0.14,
        '"Prescription, not Prediction"',
        ha='right', va='center', fontsize=13.5, fontstyle='italic',
        color=GOLD, zorder=5)
ax.text(FW - 0.50, SAFE_CY - 0.13,
        'Every answer grounded in expert index — zero LLM hallucinations',
        ha='right', va='center', fontsize=9.5, color=MUTED, zorder=5)

# ─────────────────────────── SAVE (PNG + SVG) ─────────────────────────────
_assets = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
os.makedirs(_assets, exist_ok=True)

OUT_PNG = os.path.join(_assets, 'rag_pipeline_diagram.png')
OUT_SVG = os.path.join(_assets, 'rag_pipeline_diagram.svg')

plt.savefig(OUT_PNG, dpi=160, bbox_inches='tight', pad_inches=0.10, facecolor=BG)
print(f'Saved PNG → {OUT_PNG}')
plt.savefig(OUT_SVG, format='svg', bbox_inches='tight', pad_inches=0.10, facecolor=BG)
print(f'Saved SVG → {OUT_SVG}')
plt.close()
