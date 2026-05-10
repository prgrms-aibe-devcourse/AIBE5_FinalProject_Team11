#!/usr/bin/env python3
"""
gen_rag_agentic_flow.py
Agentic RAG decision-loop flowchart — aeogeo brand palette.
Mirrors the 12-step LLM-agent flow pattern, adapted for the yoga matching pipeline.
Output: assets/rag_agentic_flow.png  +  assets/rag_agentic_flow.svg
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
from matplotlib import font_manager
import matplotlib.patheffects as pe

# ─────────────────────────── font setup ───────────────────────────────────
for _fp in [
    '/usr/share/fonts/truetype/nanum/NanumSquareRoundR.ttf',
    '/usr/share/fonts/truetype/nanum/NanumSquareRoundB.ttf',
]:
    if os.path.exists(_fp):
        font_manager.fontManager.addfont(_fp)
plt.rcParams['font.family'] = ['NanumSquareRound', 'DejaVu Sans']

# ─────────────────────────── palette ──────────────────────────────────────
BG       = '#0D1117'
CARD     = '#161B22'
GOLD     = '#F0C060'     # Ingestion / Query nodes
TEAL     = '#3DD9C2'     # Agent decision nodes
LOTUS    = '#B39DDB'     # Retrieval sources
SAGE     = '#7EC8A0'     # Final response
RED      = '#F87171'     # Kill-switch / No paths
WHITE    = '#F0F6FC'
MUTED    = '#8B949E'
DIM      = '#252B35'
BADGE    = '#1F6FEB'     # Step badge fill
RULE     = '#21262D'
ORANGE   = '#E8A468'     # Response / document nodes

# ─────────────────────────── canvas ───────────────────────────────────────
FW, FH = 22.0, 12.5
fig, ax = plt.subplots(figsize=(FW, FH), dpi=150)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, FW)
ax.set_ylim(0, FH)
ax.axis('off')
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

# ─────────────────────────── primitives ───────────────────────────────────
def rbox(cx, cy, w, h, fc, ec, lw=1.4, r=0.25, z=3):
    p = FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle=f'round,pad=0,rounding_size={r}',
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z,
    )
    ax.add_patch(p)
    return cx, cy


def agent_node(cx, cy, title, subtitle='', color=TEAL, w=2.80, h=1.20):
    """Rounded-rect agent node with dashed border (matching reference style)."""
    rbox(cx, cy, w, h, DIM, color, lw=1.6, r=0.28, z=3)
    # dashed outer ring effect — draw a second slightly larger box
    p2 = FancyBboxPatch(
        (cx - w/2 - 0.06, cy - h/2 - 0.06), w + 0.12, h + 0.12,
        boxstyle=f'round,pad=0,rounding_size=0.32',
        facecolor='none', edgecolor=color, linewidth=1.0,
        linestyle='dashed', zorder=3, alpha=0.45,
    )
    ax.add_patch(p2)
    if subtitle:
        ax.text(cx, cy + 0.18, title, ha='center', va='center',
                fontsize=11.5, fontweight='bold', color=WHITE, zorder=5)
        ax.text(cx, cy - 0.18, subtitle, ha='center', va='center',
                fontsize=9.5, color=color, zorder=5)
    else:
        ax.text(cx, cy, title, ha='center', va='center',
                fontsize=11.5, fontweight='bold', color=WHITE, zorder=5)


def oval_node(cx, cy, text, color=GOLD, w=1.60, h=0.80):
    """Oval input/output node."""
    from matplotlib.patches import Ellipse
    e = Ellipse((cx, cy), w, h, facecolor=color, edgecolor=color,
                linewidth=0, zorder=3, alpha=0.88)
    ax.add_patch(e)
    ax.text(cx, cy, text, ha='center', va='center',
            fontsize=10.5, fontweight='bold', color=BG, zorder=5)


def doc_node(cx, cy, title, subtitle='', color=ORANGE, w=2.00, h=1.20):
    """Document-shaped node (rect with folded corner hint)."""
    rbox(cx, cy, w, h, color, color, lw=0, r=0.18, z=3)
    # fold corner
    fold = 0.28
    fold_pts = [
        [cx + w/2 - fold, cy + h/2],
        [cx + w/2,        cy + h/2 - fold],
        [cx + w/2,        cy + h/2],
    ]
    from matplotlib.patches import Polygon
    poly = Polygon(fold_pts, closed=True, facecolor=BG, edgecolor=BG,
                   linewidth=0, zorder=4, alpha=0.55)
    ax.add_patch(poly)
    ax.text(cx, cy + (0.16 if subtitle else 0), title,
            ha='center', va='center', fontsize=10.5, fontweight='bold',
            color=BG, zorder=5)
    if subtitle:
        ax.text(cx, cy - 0.20, subtitle, ha='center', va='center',
                fontsize=8.5, color=BG, alpha=0.8, zorder=5)


def source_node(cx, cy, text, color=LOTUS, w=2.20, h=0.90):
    """Source pill (Vector DB, Internet, Tools)."""
    rbox(cx, cy, w, h, color, color, lw=0, r=0.40, z=3)
    ax.text(cx, cy, text, ha='center', va='center',
            fontsize=10.5, fontweight='bold', color=BG, zorder=5)


def badge(cx, cy, num):
    """Numbered step badge — filled circle."""
    c = Circle((cx, cy), 0.22, facecolor=BADGE, edgecolor=WHITE,
               linewidth=1.2, zorder=6)
    ax.add_patch(c)
    ax.text(cx, cy, str(num), ha='center', va='center',
            fontsize=9.0, fontweight='bold', color=WHITE, zorder=7)


def arrow(x0, y0, x1, y1, color=MUTED, style='->', lw=1.6,
          conn='arc3,rad=0.0', ls='solid', z=2):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(
                    arrowstyle=style, color=color, lw=lw,
                    mutation_scale=14, connectionstyle=conn,
                    linestyle=ls,
                ),
                zorder=z)


def label(x, y, text, color=WHITE, size=10.5, bold=False, ha='center'):
    ax.text(x, y, text, ha=ha, va='center', fontsize=size,
            fontweight='bold' if bold else 'normal', color=color, zorder=6)


# ═══════════════════════════════════════════════════════════════════════════
#  TITLE
# ═══════════════════════════════════════════════════════════════════════════
rbox(FW/2, 12.00, FW, 1.20, '#0D1117', '#0D1117', lw=0, r=0, z=1)
ax.axhline(y=11.36, xmin=0.006, xmax=0.994, color=RULE, lw=1.4, zorder=2)
rbox(1.18, 12.00, 1.90, 0.62, CARD, SAGE, lw=1.8, r=0.14, z=4)
ax.text(1.18, 12.00, 'aeogeo', ha='center', va='center',
        fontsize=15.0, fontweight='bold', color=SAGE, zorder=5)
ax.text(FW/2 + 0.8, 12.04,
        'Agentic RAG Decision Loop  —  High-Fidelity Yoga Matching Pipeline',
        ha='center', va='center', fontsize=20.0, fontweight='bold',
        color=WHITE, zorder=5)
ax.text(FW/2 + 0.8, 11.62,
        'LangGraph + CrewAI  ·  Query Rewrite  ·  Source Selection  ·  Kill-Switch Safety Gate  ·  Relevance Validation Loop',
        ha='center', va='center', fontsize=11.5, color=MUTED, zorder=5)

# ═══════════════════════════════════════════════════════════════════════════
#  NODE POSITIONS  (x, y in data coordinates, origin bottom-left)
#  Layout matches the reference image logic, adapted to aeogeo content.
#
#  Row 1 (top):    Query → Agent1(Rewrite) → Updated Query → Agent2(Need more?)
#  Row 2 (mid):    Agent4(Relevant?) ← Response ← Agent3(Synthesize) ← Agent2b(Src?)
#  Row 3 (low):    Final Response    Retrieved Context+Updated Query   Sources Box
# ═══════════════════════════════════════════════════════════════════════════

# ── Row 1 ──────────────────────────────────────────────────────────────────
# col positions
C1, C2, C3, C4, C5 = 1.60, 5.40, 8.80, 12.40, 17.00
R1, R2, R3, R4 = 10.20, 7.40, 4.70, 2.20

# ── Row 1: Query → Rewrite Agent → Updated Query → Detail Check Agent ──────
oval_node(C1, R1, 'Query', GOLD, w=1.50, h=0.80)
badge(C1 + 0.90, R1 + 0.44, 1)

agent_node(C2, R1, 'LLM Agent', 'Rewrite the initial query', TEAL, w=2.80, h=1.20)
badge(C2 + 1.60, R1 + 0.64, 2)

doc_node(C3, R1, 'Updated', 'Query', ORANGE, w=1.90, h=1.10)
badge(C3 + 1.06, R1 + 0.60, 3)

agent_node(C4, R1, 'LLM Agent', 'Need more details?', TEAL, w=2.80, h=1.20)
badge(C4 + 1.60, R1 + 0.64, 4)

# ── Row 2: Relevance Check ← Response ← Synthesize Agent ← Source Agent ──
agent_node(C1, R2, 'LLM Agent', 'Is the answer relevant?', TEAL, w=2.80, h=1.20)
badge(C1 + 1.60, R2 + 0.64, 10)

doc_node(C2 + 0.30, R2, 'Response', '', ORANGE, w=2.00, h=1.20)
badge(C2 + 0.30 + 1.10, R2 + 0.64, 9)

agent_node(C3, R2, 'LLM Agent', 'Synthesize answer', TEAL, w=2.80, h=1.20)
badge(C3 + 1.60, R2 + 0.64, 8)

agent_node(C4, R2, 'LLM Agent', 'Which source?', TEAL, w=2.80, h=1.20)
badge(C4 + 1.60, R2 + 0.64, 5)

# ── Row 3: Final Response | Context + Query box | Sources ──────────────────
# Final Response (green doc)
doc_node(C1, R3 - 0.20, 'Final', 'Response', SAGE, w=2.00, h=1.30)
badge(C1 + 1.10, R3 - 0.20 + 0.70, 11)

# Retrieved context / Updated query panel
CTX_CX, CTX_CY = C2 + 0.60, R3 - 0.10
rbox(CTX_CX, CTX_CY, 3.50, 2.60, DIM, LOTUS, lw=1.4, r=0.22, z=2)
ax.text(CTX_CX, CTX_CY + 0.92, 'Prompt', ha='center', va='center',
        fontsize=11.5, color=MUTED, zorder=4)
badge(CTX_CX + 1.85, CTX_CY + 0.92, 8)  # re-use step 8 prompt label

doc_node(CTX_CX - 0.30, CTX_CY + 0.18, 'Retrieved', 'context', LOTUS, w=2.00, h=1.10)
oval_node(CTX_CX + 0.50, CTX_CY - 0.80, 'Updated\nQuery', GOLD, w=1.80, h=0.90)
badge(CTX_CX + 1.85, CTX_CY + 0.18, 7)

# Sources panel (right)
SRC_CX, SRC_CY = C4 + 0.60, R3 - 0.10
rbox(SRC_CX, SRC_CY, 4.20, 2.60, DIM, MUTED, lw=1.4, r=0.22, z=2)
ax.text(SRC_CX, SRC_CY + 0.92, 'Knowledge Sources', ha='center', va='center',
        fontsize=11.5, fontweight='bold', color=WHITE, zorder=4)
badge(C4 + 1.60, R3 - 0.10 + 0.92, 6)

source_node(SRC_CX - 0.80, SRC_CY + 0.10, 'Pinecone\nVector DB', LOTUS, w=2.20, h=0.90)
source_node(SRC_CX + 0.90, SRC_CY + 0.10, 'Tools &\nAPIs', '#E8A0A0', w=1.80, h=0.90)
source_node(SRC_CX - 0.10, SRC_CY - 0.80, 'PostGIS +\nInternet', '#7EC8A0', w=2.20, h=0.90)

# ── No path loopback (step 12) ─────────────────────────────────────────────
badge(C1 - 1.10, R2 + 0.64, 12)
label(C1 - 0.68, R2 + 0.64, 'No', RED, size=13.0, bold=True)

# ═══════════════════════════════════════════════════════════════════════════
#  ARROWS
# ═══════════════════════════════════════════════════════════════════════════

# Row 1 horizontal
arrow(C1 + 0.76, R1,   C2 - 1.42, R1)   # 1→2
arrow(C2 + 1.42, R1,   C3 - 0.97, R1)   # 2→3
arrow(C3 + 0.97, R1,   C4 - 1.42, R1)   # 3→4

# Step 4 decision: No (down to synthesize), Yes (right to source agent)
arrow(C4, R1 - 0.62,  C3, R2 + 0.62, color=MUTED)   # No: Agent4 → Synthesize
label((C4 + C3)/2 + 0.40, (R1 + R2)/2 + 0.10, 'No', RED, bold=True)

arrow(C4 + 1.42, R1,  C5 - 0.10, R1, color=TEAL)    # Yes right
arrow(C5 - 0.10, R1,  C4 + 1.42, R2, conn='arc3,rad=-0.30', color=TEAL)  # down to row2
label(C4 + 2.30, (R1 + R2)/2 + 0.10, 'Yes', SAGE, bold=True)

# Row 2 horizontal (right to left — retrieval result flows back)
arrow(C4 - 1.42, R2,  C3 + 1.42, R2)    # 5→8 Source agent → Synthesize
arrow(C3 - 1.42, R2,  C2 + 0.30 + 1.02, R2)   # 8→9 Synthesize → Response
arrow(C2 + 0.30 - 1.02, R2, C1 + 1.42, R2)    # 9→10 Response → Relevance

# Step 6: source agent down to sources box
arrow(C4, R2 - 0.62,  SRC_CX, SRC_CY + 1.32)

# Step 7: sources → context box
arrow(SRC_CX - 2.12, SRC_CY,   CTX_CX + 1.77, CTX_CY,
      color=LOTUS, conn='arc3,rad=0.0')
label((SRC_CX - 2.12 + CTX_CX + 1.77)/2, SRC_CY + 0.24, '7', color=BADGE,
      size=9.5, bold=True)

# Context box → Synthesize agent
arrow(CTX_CX + 1.77, CTX_CY,  C3 - 1.42, R2,
      color=LOTUS, conn='arc3,rad=-0.15')

# Relevance check: Yes → Final Response
arrow(C1, R2 - 0.62,  C1, R3 - 0.20 + 0.67,  color=SAGE)
label(C1 + 0.38, (R2 + R3)/2 + 0.08, 'Yes', SAGE, bold=True)

# Relevance check: No → loop back up to Rewrite Agent (step 12 → step 1)
ax.annotate('', xy=(C2 - 1.42, R1),
            xytext=(C1 - 1.42, R2 + 0.62),
            arrowprops=dict(arrowstyle='->', color=RED, lw=1.8,
                            mutation_scale=14,
                            connectionstyle='arc3,rad=-0.55'),
            zorder=2)

# ═══════════════════════════════════════════════════════════════════════════
#  SAFETY INVARIANT BANNER
# ═══════════════════════════════════════════════════════════════════════════
SAFE_CY = 0.52
rbox(FW/2, SAFE_CY, FW - 0.28, 0.72, '#180A0A', RED, lw=2.2, r=0.12, z=3)
ax.text(1.80, SAFE_CY + 0.16, '⚠  SAFETY INVARIANT',
        ha='left', va='center', fontsize=13.0, fontweight='bold',
        color=RED, zorder=5)
ax.text(1.80, SAFE_CY - 0.14,
        'kill_switch = TRUE poses excluded BEFORE scoring  ·  Severity: CAUTION | CRITICAL | MEDICAL_CLEARANCE',
        ha='left', va='center', fontsize=10.5, color=RED, alpha=0.85, zorder=5)
ax.text(FW - 0.60, SAFE_CY + 0.16,
        '"Prescription, not Prediction"',
        ha='right', va='center', fontsize=14.5, fontstyle='italic',
        color=GOLD, zorder=5)
ax.text(FW - 0.60, SAFE_CY - 0.14,
        'Every answer grounded in expert Pose Library — zero LLM hallucinations',
        ha='right', va='center', fontsize=10.0, color=MUTED, zorder=5)

# ═══════════════════════════════════════════════════════════════════════════
#  SAVE
# ═══════════════════════════════════════════════════════════════════════════
_assets = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
os.makedirs(_assets, exist_ok=True)

OUT_PNG = os.path.join(_assets, 'rag_agentic_flow.png')
OUT_SVG = os.path.join(_assets, 'rag_agentic_flow.svg')

plt.savefig(OUT_PNG, dpi=150, bbox_inches='tight', pad_inches=0.12, facecolor=BG)
print(f'Saved PNG → {OUT_PNG}')
plt.savefig(OUT_SVG, format='svg', bbox_inches='tight', pad_inches=0.12, facecolor=BG)
print(f'Saved SVG → {OUT_SVG}')
plt.close()
