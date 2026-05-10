#!/usr/bin/env python3
"""
gen_hud_landscape.py
Immersive landscape HUD overlay — Runner's Lunge
Output: assets/hud_landscape.svg  (1920×1080 SVG)

Paradigm: futuristic spatial glass panels over a photorealistic sunset scene.
No matplotlib — pure SVG string construction for crisp vector output at any scale.
"""
import os, math, textwrap

OUT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'hud_landscape.svg')

W, H = 1920, 1080

# ── Palette ───────────────────────────────────────────────────────────────────
CYAN      = '#00D4FF'
GREEN     = '#00CC77'
AMBER     = '#F59E0B'
RED       = '#FF3B30'
PURPLE    = '#A855F7'
DIM       = '#8B949E'
WHITE     = '#F0F6FC'
PANEL_BG  = 'rgba(10,18,30,0.72)'
PANEL_BG2 = 'rgba(10,18,30,0.55)'
GLASS_STK = CYAN

# ── SVG primitives ────────────────────────────────────────────────────────────

def g(content, **attrs):
    a = ' '.join(f'{k.replace("_","-")}="{v}"' for k, v in attrs.items())
    return f'<g {a}>{content}</g>'

def rect(x, y, w, h, fill=PANEL_BG, stroke=CYAN, sw=1.5, rx=14, ry=14,
         opacity=1, filter_='', extra=''):
    f = f'filter="url(#{filter_})"' if filter_ else ''
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
            f'rx="{rx}" ry="{ry}" opacity="{opacity}" {f} {extra}/>')

def text(x, y, txt, fs=16, fill=WHITE, weight='normal', anchor='middle',
         family='Inter,Arial,sans-serif', opacity=1, dy=0, extra=''):
    return (f'<text x="{x}" y="{y}" dy="{dy}" font-size="{fs}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}" '
            f'font-family="{family}" opacity="{opacity}" {extra}>{txt}</text>')

def line(x1, y1, x2, y2, stroke=CYAN, sw=1.5, dash='', opacity=0.7):
    d = f'stroke-dasharray="{dash}"' if dash else ''
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}" {d}/>')

def circle(cx, cy, r, fill='none', stroke=CYAN, sw=2):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')

def arc_path(cx, cy, r, start_deg, end_deg, stroke=CYAN, sw=8,
             fill='none', linecap='round'):
    """SVG arc from start_deg to end_deg (clockwise from 12 o'clock)."""
    s = math.radians(start_deg - 90)
    e = math.radians(end_deg   - 90)
    large = 1 if (end_deg - start_deg) > 180 else 0
    x1, y1 = cx + r * math.cos(s), cy + r * math.sin(s)
    x2, y2 = cx + r * math.cos(e), cy + r * math.sin(e)
    return (f'<path d="M {x1:.1f} {y1:.1f} A {r} {r} 0 {large} 1 {x2:.1f} {y2:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linecap="{linecap}"/>')

def polyline(pts, stroke=CYAN, sw=2.5, fill='none', opacity=0.85, dash=''):
    pstr = ' '.join(f'{x},{y}' for x,y in pts)
    d = f'stroke-dasharray="{dash}"' if dash else ''
    return (f'<polyline points="{pstr}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" opacity="{opacity}" stroke-linejoin="round" '
            f'stroke-linecap="round" {d}/>')

def badge(x, y, w, h, label_txt, bg, tc=WHITE, fs=13, rx=8):
    return (rect(x, y, w, h, fill=bg, stroke='none', sw=0, rx=rx, ry=rx)
            + text(x + w/2, y + h/2 + fs*0.36, label_txt, fs=fs, fill=tc, weight='700'))

def panel_header(x, y, w, title, color=CYAN, fs=15):
    return (line(x+14, y+1, x+w-14, y+1, stroke=color, sw=1, opacity=0.4)
            + text(x+16, y+22, title, fs=fs, fill=color, weight='700', anchor='start'))

def corner_ticks(x, y, w, h, color=CYAN, size=18, sw=1.5):
    """Futuristic corner brackets."""
    s = size
    parts = [
        # TL
        f'M {x},{y+s} L {x},{y} L {x+s},{y}',
        # TR
        f'M {x+w-s},{y} L {x+w},{y} L {x+w},{y+s}',
        # BL
        f'M {x},{y+h-s} L {x},{y+h} L {x+s},{y+h}',
        # BR
        f'M {x+w-s},{y+h} L {x+w},{y+h} L {x+w},{y+h-s}',
    ]
    return ''.join(
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"/>'
        for d in parts
    )

# ── Defs (filters, gradients, animations) ────────────────────────────────────

DEFS = """
<defs>
  <!-- Glow filters -->
  <filter id="glow-cyan" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="4" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glow-red" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="6" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glow-green" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="3" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="softshadow">
    <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#000" flood-opacity="0.6"/>
  </filter>
  <filter id="blur-bg">
    <feGaussianBlur stdDeviation="2"/>
  </filter>

  <!-- Sunset gradient background -->
  <linearGradient id="sunset" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%"   stop-color="#0D0A1A"/>
    <stop offset="30%"  stop-color="#1A0E2E"/>
    <stop offset="60%"  stop-color="#2D1B0E"/>
    <stop offset="85%"  stop-color="#3D2408"/>
    <stop offset="100%" stop-color="#1A0A05"/>
  </linearGradient>

  <!-- Floor gradient -->
  <linearGradient id="floor-grad" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%"  stop-color="#2A1A0A" stop-opacity="0.9"/>
    <stop offset="100%" stop-color="#0D0806" stop-opacity="1"/>
  </linearGradient>

  <!-- Window light bloom -->
  <radialGradient id="window-bloom" cx="72%" cy="35%" r="40%">
    <stop offset="0%"  stop-color="#FF8C3A" stop-opacity="0.28"/>
    <stop offset="60%" stop-color="#FF5500" stop-opacity="0.08"/>
    <stop offset="100%" stop-color="#000" stop-opacity="0"/>
  </radialGradient>

  <!-- Panel glass gradient -->
  <linearGradient id="glass-grad" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%"   stop-color="#FFFFFF" stop-opacity="0.06"/>
    <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0.01"/>
  </linearGradient>

  <!-- Skeleton mesh gradient -->
  <radialGradient id="mesh-glow" cx="50%" cy="45%" r="50%">
    <stop offset="0%"  stop-color="#00D4FF" stop-opacity="0.25"/>
    <stop offset="100%" stop-color="#00D4FF" stop-opacity="0"/>
  </radialGradient>

  <!-- Spine gradient -->
  <linearGradient id="spine-grad" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%"   stop-color="#A855F7"/>
    <stop offset="50%"  stop-color="#00D4FF"/>
    <stop offset="100%" stop-color="#00CC77"/>
  </linearGradient>

  <!-- Red strobe animation -->
  <animate id="strobe" attributeName="opacity"
    values="1;0.15;1;0.15;1" dur="0.7s" repeatCount="indefinite"/>

  <!-- Pulse animation for kill-switch border -->
  <style>
    .strobe { animation: strobe 0.7s infinite; }
    @keyframes strobe { 0%,100%{opacity:1} 50%{opacity:0.18} }
    .pulse-green { animation: pulse-g 1.4s infinite; }
    @keyframes pulse-g { 0%,100%{opacity:0.7} 50%{opacity:1} }
    .pulse-cyan  { animation: pulse-c 2s infinite; }
    @keyframes pulse-c { 0%,100%{opacity:0.5} 50%{opacity:1} }
    .scan-line   { animation: scan 3s linear infinite; }
    @keyframes scan { from{transform:translateY(-200px)} to{transform:translateY(1300px)} }
  </style>

  <!-- Mat texture gradient -->
  <linearGradient id="mat-grad" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%"   stop-color="#1A2A20" stop-opacity="0.95"/>
    <stop offset="50%"  stop-color="#1E3226" stop-opacity="0.98"/>
    <stop offset="100%" stop-color="#152218" stop-opacity="0.95"/>
  </linearGradient>

  <!-- Holographic grid pattern -->
  <pattern id="holo-grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <line x1="40" y1="0" x2="0" y2="40" stroke="#00D4FF" stroke-width="0.3" opacity="0.15"/>
    <line x1="0"  y1="0" x2="40" y2="40" stroke="#00D4FF" stroke-width="0.3" opacity="0.08"/>
  </pattern>
</defs>
"""

# ─────────────────────────────────────────────────────────────────────────────
# SCENE BACKGROUND
# ─────────────────────────────────────────────────────────────────────────────

BG_SCENE = f"""
<!-- ── Background scene ── -->
<rect width="{W}" height="{H}" fill="url(#sunset)"/>

<!-- Floor plane -->
<ellipse cx="960" cy="{H}" rx="1400" ry="340"
         fill="url(#floor-grad)" opacity="0.95"/>

<!-- Yoga mat -->
<ellipse cx="860" cy="830" rx="420" ry="55"
         fill="url(#mat-grad)" opacity="0.92"/>
<ellipse cx="860" cy="830" rx="418" ry="53"
         fill="none" stroke="#2E4A38" stroke-width="2" opacity="0.6"/>

<!-- Window ambient bloom (simulated sunset light) -->
<rect width="{W}" height="{H}" fill="url(#window-bloom)"/>

<!-- Ambient floor reflection -->
<ellipse cx="860" cy="870" rx="300" ry="28"
         fill="#FF6622" opacity="0.06"/>

<!-- Atmospheric haze -->
<rect width="{W}" height="{H}"
      fill="url(#holo-grid)" opacity="0.40"/>

<!-- Subtle scan line -->
<rect class="scan-line" x="0" y="0" width="{W}" height="3"
      fill="{CYAN}" opacity="0.06"/>
"""

# ─────────────────────────────────────────────────────────────────────────────
# 3-D HOLOGRAPHIC WIREFRAME SKELETON — Runner's Lunge (right foot forward)
# All coords hand-tuned to sit on mat at ~860,830
# ─────────────────────────────────────────────────────────────────────────────

# Joint world positions (px)  — perspective-projected
SK = {
    'head':    (870, 290),
    'neck':    (868, 345),
    'r_sh':    (940, 380),
    'l_sh':    (790, 395),
    'r_elb':   (980, 460),
    'l_elb':   (745, 468),
    'r_wri':   (1008, 530),
    'l_wri':   (718, 534),
    'r_hip':   (900, 530),
    'l_hip':   (810, 540),
    'mid_hip': (855, 534),
    # Front (right) leg
    'r_knee':  (990, 680),
    'r_ank':   (1060, 790),
    # Back (left) leg
    'l_knee':  (710, 700),
    'l_ank':   (660, 820),
}

BONES = [
    ('head','neck'),
    ('neck','r_sh'), ('neck','l_sh'),
    ('r_sh','r_elb'), ('r_elb','r_wri'),
    ('l_sh','l_elb'), ('l_elb','l_wri'),
    ('neck','mid_hip'),
    ('mid_hip','r_hip'), ('mid_hip','l_hip'),
    ('r_hip','r_knee'), ('r_knee','r_ank'),
    ('l_hip','l_knee'), ('l_knee','l_ank'),
]

# Mesh triangles (just the front-facing face panels for wireframe look)
MESH_TRIS = [
    ('neck','r_sh','mid_hip'),
    ('neck','l_sh','mid_hip'),
    ('r_sh','r_elb','mid_hip'),
    ('l_sh','l_elb','mid_hip'),
    ('mid_hip','r_hip','r_knee'),
    ('mid_hip','l_hip','l_knee'),
    ('r_hip','r_knee','r_ank'),
    ('l_hip','l_knee','l_ank'),
]

def tri_path(a, b, c):
    ax,ay = SK[a]; bx,by = SK[b]; cx,cy = SK[c]
    return f'M {ax},{ay} L {bx},{by} L {cx},{cy} Z'

mesh_glow_circle = (
    f'<ellipse cx="860" cy="540" rx="200" ry="280" fill="url(#mesh-glow)" opacity="0.9"/>'
)

mesh_tris = ''.join(
    f'<path d="{tri_path(a,b,c)}" fill="{CYAN}" fill-opacity="0.04" '
    f'stroke="{CYAN}" stroke-width="0.6" opacity="0.55"/>'
    for a,b,c in MESH_TRIS
)

bones_svg = ''.join(
    polyline([SK[a], SK[b]], stroke=CYAN, sw=2.2, opacity=0.82)
    for a,b in BONES
)

joints_svg = ''.join(
    f'<circle cx="{x}" cy="{y}" r="5" fill="{CYAN}" opacity="0.9" filter="url(#glow-cyan)"/>'
    for x,y in SK.values()
)

# Head
hx, hy = SK['head']
head_svg = (f'<circle cx="{hx}" cy="{hy-22}" r="28" '
            f'fill="rgba(0,212,255,0.08)" stroke="{CYAN}" stroke-width="1.8" '
            f'filter="url(#glow-cyan)" opacity="0.85"/>')

# Glowing spine (neck → mid_hip)
nx,ny = SK['neck']; mx,my = SK['mid_hip']
spine_svg = (
    f'<line x1="{nx}" y1="{ny}" x2="{mx}" y2="{my}" '
    f'stroke="url(#spine-grad)" stroke-width="5" opacity="0.80" '
    f'filter="url(#glow-cyan)" stroke-linecap="round"/>'
)

# ── VECTOR GUIDE RAILS ────────────────────────────────────────────────────────
# Front shin ideal rail (ankle → extended knee direction)
rk = SK['r_knee']; ra = SK['r_ank']
front_rail = (
    polyline([ra, rk, (rk[0]+(rk[0]-ra[0])*0.12, rk[1]+(rk[1]-ra[1])*0.12)],
             stroke=GREEN, sw=2.5, opacity=0.65, dash='8 5')
    + f'<polygon points="{rk[0]-7},{rk[1]-14} {rk[0]+7},{rk[1]-14} {rk[0]},{rk[1]-28}" '
      f'fill="{GREEN}" opacity="0.75"/>'
)
# Back shin correction rail
lk = SK['l_knee']; la = SK['l_ank']
back_rail = polyline([la, lk], stroke=AMBER, sw=2.2, opacity=0.60, dash='6 4')

# Torso vertical guide
torso_rail = polyline(
    [(SK['mid_hip'][0], SK['mid_hip'][1]), (SK['mid_hip'][0], SK['neck'][1])],
    stroke=PURPLE, sw=1.8, opacity=0.55, dash='4 4'
)

# ── KNEE ANGLE ARC ────────────────────────────────────────────────────────────
rkx,rky = SK['r_knee']
knee_arc = (
    arc_path(rkx, rky, 52, 295, 395, stroke=AMBER, sw=3.5)
    + text(rkx+64, rky-10, '91°', fs=20, fill=AMBER, weight='800')
)

# ── DIRECTIONAL CORRECTION ARROW (back knee) ──────────────────────────────────
lkx,lky = SK['l_knee']
dir_arrow = (
    f'<line x1="{lkx}" y1="{lky}" x2="{lkx-52}" y2="{lky+58}" '
    f'stroke="{AMBER}" stroke-width="2.5" opacity="0.85" '
    f'marker-end="url(#arr-amber)"/>'
    + text(lkx-74, lky+82, 'Lower', fs=18, fill=AMBER, weight='800')
)

SKELETON = f"""
<!-- ── 3-D Holographic Skeleton ── -->
<g filter="url(#softshadow)">
  {mesh_glow_circle}
  {mesh_tris}
  {torso_rail}
  {front_rail}
  {back_rail}
  {spine_svg}
  {bones_svg}
  {joints_svg}
  {head_svg}
  {knee_arc}
  {dir_arrow}
</g>
"""

# ─────────────────────────────────────────────────────────────────────────────
# GLASS PANELS
# ─────────────────────────────────────────────────────────────────────────────

def glass_panel(x, y, w, h, stroke=CYAN, sw=1.5, extra_class=''):
    return (
        # Blurred background layer
        rect(x, y, w, h, fill='rgba(6,12,22,0.65)', stroke='none', sw=0, rx=16, ry=16)
        # Glass sheen
        + rect(x, y, w, 40, fill='url(#glass-grad)', stroke='none', sw=0, rx=16, ry=0)
        # Border
        + rect(x, y, w, h, fill='none', stroke=stroke, sw=sw, rx=16, ry=16,
               extra=f'class="{extra_class}"' if extra_class else '')
        # Corner ticks
        + corner_ticks(x, y, w, h, color=stroke, size=14, sw=1.2)
    )

# ─────────────────────────────────────────────────────────────────────────────
# 1. TOP-CENTER KILL-SWITCH BANNER (pulsing red)
# ─────────────────────────────────────────────────────────────────────────────
KS_X, KS_Y, KS_W, KS_H = 540, 22, 840, 76

KILL_SWITCH = f"""
<!-- ── Kill-Switch Banner ── -->
<g class="strobe">
  {glass_panel(KS_X, KS_Y, KS_W, KS_H, stroke=RED, sw=2.5)}
  <rect x="{KS_X}" y="{KS_Y}" width="{KS_W}" height="{KS_H}"
        fill="rgba(255,59,48,0.10)" rx="16"/>
</g>
<!-- Icon + text always visible regardless of strobe -->
{badge(KS_X+14, KS_Y+18, 96, 40, 'CRITICAL', RED, tc=WHITE, fs=12, rx=6)}
{text(KS_X+KS_W//2+30, KS_Y+24, 'STOP IMMEDIATELY — KNEE STRESS DETECTED',
      fs=23, fill=RED, weight='900', extra='filter="url(#glow-red)"')}
{text(KS_X+KS_W//2+30, KS_Y+52, 'Knee shear exceeds 20°  ·  Abort pose immediately',
      fs=14, fill='#FF9990', weight='500')}
{line(KS_X+14, KS_Y+KS_H-1, KS_X+KS_W-14, KS_Y+KS_H-1, stroke=RED, sw=0.8)}
"""

# ─────────────────────────────────────────────────────────────────────────────
# 2. LEFT PANEL — Current Pose + Phase
# ─────────────────────────────────────────────────────────────────────────────
LP_X, LP_Y, LP_W, LP_H = 28, 118, 310, 360

LEFT_PANEL = f"""
<!-- ── Left: Pose Info ── -->
{glass_panel(LP_X, LP_Y, LP_W, LP_H)}
{panel_header(LP_X, LP_Y, LP_W, 'CURRENT POSE')}
{text(LP_X+LP_W//2, LP_Y+74, "Runner's Lunge", fs=22, fill=WHITE, weight='800')}
{text(LP_X+LP_W//2, LP_Y+100, 'Anjaneyasana — Right Forward', fs=13, fill=DIM)}
{line(LP_X+20, LP_Y+114, LP_X+LP_W-20, LP_Y+114, stroke=CYAN, sw=0.5, opacity=0.3)}

{text(LP_X+24, LP_Y+138, 'Front Knee Angle', fs=12, fill=DIM, anchor='start')}
{text(LP_X+LP_W-16, LP_Y+138, '91°', fs=18, fill=GREEN, weight='800', anchor='end',
      extra='filter="url(#glow-green)"')}

{text(LP_X+24, LP_Y+168, 'Torso Lean', fs=12, fill=DIM, anchor='start')}
{text(LP_X+LP_W-16, LP_Y+168, '8°', fs=18, fill=GREEN, weight='800', anchor='end')}

{text(LP_X+24, LP_Y+198, 'Back Knee Height', fs=12, fill=DIM, anchor='start')}
{text(LP_X+LP_W-16, LP_Y+198, 'LOW', fs=16, fill=AMBER, weight='800', anchor='end')}

{line(LP_X+20, LP_Y+216, LP_X+LP_W-20, LP_Y+216, stroke=CYAN, sw=0.5, opacity=0.3)}

{text(LP_X+LP_W//2, LP_Y+240, 'PHASE  3 / 5', fs=13, fill=DIM)}
{badge(LP_X+LP_W//2-70, LP_Y+258, 140, 34, 'HOLD PHASE', PURPLE, fs=13)}

{text(LP_X+LP_W//2, LP_Y+320, 'Alignment', fs=12, fill=DIM)}
{text(LP_X+LP_W//2, LP_Y+340, 'Spine lengthening, hips level', fs=12, fill=WHITE)}
"""

# ─────────────────────────────────────────────────────────────────────────────
# 3. LEFT-LOWER PANEL — Warning cue
# ─────────────────────────────────────────────────────────────────────────────
WP_X, WP_Y, WP_W, WP_H = 28, 494, 310, 108

WARN_PANEL = f"""
<!-- ── Warning panel ── -->
{glass_panel(WP_X, WP_Y, WP_W, WP_H, stroke=AMBER, sw=1.5)}
<rect x="{WP_X}" y="{WP_Y}" width="{WP_W}" height="{WP_H}"
      fill="rgba(245,158,11,0.08)" rx="16"/>
{badge(WP_X+14, WP_Y+16, 90, 30, 'WARNING', AMBER, tc='#000', fs=11, rx=5)}
{text(WP_X+WP_W//2, WP_Y+58, 'Back knee lower', fs=22, fill=AMBER, weight='900')}
{text(WP_X+WP_W//2, WP_Y+84, 'Drop left knee toward the mat', fs=12, fill='#C8860A')}
"""

# ─────────────────────────────────────────────────────────────────────────────
# 4. LEFT-LOWER-2 PANEL — Info / Encouragement
# ─────────────────────────────────────────────────────────────────────────────
IP_X, IP_Y, IP_W, IP_H = 28, 616, 310, 96

INFO_PANEL = f"""
<!-- ── Info / encouragement panel ── -->
<g class="pulse-green">
{glass_panel(IP_X, IP_Y, IP_W, IP_H, stroke=GREEN, sw=1.5)}
<rect x="{IP_X}" y="{IP_Y}" width="{IP_W}" height="{IP_H}"
      fill="rgba(0,204,119,0.07)" rx="16"/>
</g>
{badge(IP_X+14, IP_Y+16, 66, 28, 'INFO', GREEN, tc='#000', fs=11, rx=5)}
{text(IP_X+IP_W//2, IP_Y+54, 'Perfect depth', fs=22, fill=GREEN, weight='900',
      extra='filter="url(#glow-green)"')}
{text(IP_X+IP_W//2, IP_Y+78, 'Inhale · lengthen · breathe deeper', fs=12, fill='#009955')}
"""

# ─────────────────────────────────────────────────────────────────────────────
# 5. RIGHT PANEL — Biometrics
# ─────────────────────────────────────────────────────────────────────────────
RP_X, RP_Y, RP_W, RP_H = 1582, 118, 310, 600

# Knee angle arc gauge
ARC_CX, ARC_CY, ARC_R = RP_X + 155, RP_Y + 210, 90
knee_bg_arc   = arc_path(ARC_CX, ARC_CY, ARC_R, 135, 405, stroke='#21262D', sw=12)
knee_val_arc  = arc_path(ARC_CX, ARC_CY, ARC_R, 135, 135+270*0.506, stroke=GREEN, sw=12)
knee_ideal_mk = (
    f'<line x1="{ARC_CX + (ARC_R-16)*math.cos(math.radians(-90)):.1f}" '
    f'y1="{ARC_CY + (ARC_R-16)*math.sin(math.radians(-90)):.1f}" '
    f'x2="{ARC_CX + (ARC_R+16)*math.cos(math.radians(-90)):.1f}" '
    f'y2="{ARC_CY + (ARC_R+16)*math.sin(math.radians(-90)):.1f}" '
    f'stroke="{CYAN}" stroke-width="3"/>'
)

RIGHT_PANEL = f"""
<!-- ── Right: Biometrics ── -->
{glass_panel(RP_X, RP_Y, RP_W, RP_H)}
{panel_header(RP_X, RP_Y, RP_W, 'BIOMETRICS')}

<!-- Knee arc gauge -->
{knee_bg_arc}
{knee_val_arc}
{knee_ideal_mk}
{text(ARC_CX, ARC_CY-8, '91°', fs=36, fill=GREEN, weight='900',
      extra='filter="url(#glow-green)"')}
{text(ARC_CX, ARC_CY+28, 'FRONT KNEE', fs=11, fill=DIM)}
{text(ARC_CX, ARC_CY+46, 'Target: 90°', fs=11, fill=DIM)}

{line(RP_X+20, RP_Y+316, RP_X+RP_W-20, RP_Y+316, stroke=CYAN, sw=0.5, opacity=0.3)}

<!-- Stability bar -->
{text(RP_X+20, RP_Y+342, 'Stability', fs=13, fill=DIM, anchor='start')}
{text(RP_X+RP_W-20, RP_Y+342, '82%', fs=13, fill=GREEN, weight='700', anchor='end')}
{rect(RP_X+20, RP_Y+354, RP_W-40, 14, fill='#21262D', stroke='none', sw=0, rx=7)}
{rect(RP_X+20, RP_Y+354, int((RP_W-40)*0.82), 14, fill=GREEN, stroke='none', sw=0, rx=7)}

<!-- Wobble bar -->
{text(RP_X+20, RP_Y+388, 'Wobble', fs=13, fill=DIM, anchor='start')}
{text(RP_X+RP_W-20, RP_Y+388, '0.08 r/s', fs=13, fill=AMBER, weight='700', anchor='end')}
{rect(RP_X+20, RP_Y+400, RP_W-40, 14, fill='#21262D', stroke='none', sw=0, rx=7)}
{rect(RP_X+20, RP_Y+400, int((RP_W-40)*0.53), 14, fill=AMBER, stroke='none', sw=0, rx=7)}

{line(RP_X+20, RP_Y+428, RP_X+RP_W-20, RP_Y+428, stroke=CYAN, sw=0.5, opacity=0.3)}

<!-- Pi latency chip -->
{text(RP_X+20, RP_Y+452, 'Pi Latency', fs=13, fill=DIM, anchor='start')}
{text(RP_X+RP_W-20, RP_Y+452, '18 ms', fs=15, fill=CYAN, weight='800', anchor='end')}

{text(RP_X+20, RP_Y+480, 'Inference FPS', fs=13, fill=DIM, anchor='start')}
{text(RP_X+RP_W-20, RP_Y+480, '30 fps', fs=15, fill=CYAN, weight='800', anchor='end')}

{text(RP_X+20, RP_Y+510, 'Model', fs=13, fill=DIM, anchor='start')}
{text(RP_X+RP_W-20, RP_Y+510, 'MoveNet/Hailo', fs=13, fill=DIM, anchor='end')}

{line(RP_X+20, RP_Y+526, RP_X+RP_W-20, RP_Y+526, stroke=CYAN, sw=0.5, opacity=0.3)}

{text(RP_X+RP_W//2, RP_Y+556, 'Session Timer', fs=12, fill=DIM)}
{text(RP_X+RP_W//2, RP_Y+584, '00:02:37', fs=24, fill=WHITE, weight='800')}
"""

# ─────────────────────────────────────────────────────────────────────────────
# 6. BOTTOM BAR — Hold timer + cue text + upcoming
# ─────────────────────────────────────────────────────────────────────────────
BB_X, BB_Y, BB_W, BB_H = 28, 740, 1864, 100

# Hold ring
HR_CX, HR_CY, HR_R = 220, BB_Y+50, 38
hold_ring = (
    arc_path(HR_CX, HR_CY, HR_R, 0, 360, stroke='#21262D', sw=8)
    + arc_path(HR_CX, HR_CY, HR_R, 0, 360*0.64, stroke=GREEN, sw=8)
    + text(HR_CX, HR_CY+6, '320', fs=18, fill=GREEN, weight='900')
    + text(HR_CX, HR_CY+22, 'ms', fs=10, fill=DIM)
)

BOTTOM_BAR = f"""
<!-- ── Bottom bar ── -->
{glass_panel(BB_X, BB_Y, BB_W, BB_H, stroke=CYAN, sw=1)}

<!-- Hold timer -->
{badge(BB_X+16, BB_Y+14, 120, 28, 'HOLD 500 ms', GREEN, tc='#000', fs=11, rx=5)}
{hold_ring}

{line(BB_X+270, BB_Y+16, BB_X+270, BB_Y+BB_H-16, stroke=CYAN, sw=0.5, opacity=0.3)}

<!-- Main cue text (72pt visual weight) -->
{text(BB_X+BB_W//2, BB_Y+44, 'Perfect depth', fs=42, fill=GREEN, weight='900',
      extra='filter="url(#glow-green)"')}
{text(BB_X+BB_W//2, BB_Y+76, 'Inhale · lengthen spine · breathe deeper', fs=16, fill='#00CC7799')}

{line(BB_X+BB_W-300, BB_Y+16, BB_X+BB_W-300, BB_Y+BB_H-16, stroke=CYAN, sw=0.5, opacity=0.3)}

<!-- Debounce indicator -->
{text(BB_X+BB_W-140, BB_Y+44, 'Next cue', fs=12, fill=DIM)}
{text(BB_X+BB_W-140, BB_Y+70, '1.7 s', fs=22, fill=CYAN, weight='800')}
"""

# ─────────────────────────────────────────────────────────────────────────────
# 7. TOP STATUS BAR
# ─────────────────────────────────────────────────────────────────────────────
STATUS = f"""
<!-- ── Status bar ── -->
{text(48, 16, 'Pi  CONNECTED', fs=12, fill=GREEN, weight='700', anchor='start')}
{circle(36, 10, 5, fill=GREEN, stroke='none')}
{text(W//2, 16, "RUNNER'S LUNGE HUD  ·  Cue Overlay System  v1.0", fs=13, fill=DIM, weight='600')}
{text(W-48, 16, '00:02:37', fs=12, fill=DIM, anchor='end')}
"""

# ─────────────────────────────────────────────────────────────────────────────
# 8. LEGEND (bottom-right corner)
# ─────────────────────────────────────────────────────────────────────────────
LG_X, LG_Y = 1350, 756
LEGEND_ITEMS = [
    (CYAN,   'Skeleton overlay'),
    (GREEN,  'Ideal vector rail'),
    (AMBER,  'Correction arrow'),
    (PURPLE, 'Torso guide'),
    (RED,    'Kill-switch border'),
]
legend_svg = ''
for i, (col, lbl) in enumerate(LEGEND_ITEMS):
    ly = LG_Y + i * 18
    legend_svg += (
        f'<circle cx="{LG_X}" cy="{ly+6}" r="5" fill="{col}"/>'
        + text(LG_X+14, ly+10, lbl, fs=11, fill=DIM, anchor='start')
    )

# ─────────────────────────────────────────────────────────────────────────────
# 9. COLOUR WASH OVERLAY — green (INFO state shown)
# ─────────────────────────────────────────────────────────────────────────────
COLOR_WASH = f"""
<!-- ── Peripheral green colour wash (INFO) ── -->
<rect width="{W}" height="{H}"
      fill="rgba(0,204,119,0.045)" pointer-events="none"/>
"""

# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLE SVG
# ─────────────────────────────────────────────────────────────────────────────

svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {W} {H}" width="{W}" height="{H}">
{DEFS}
{BG_SCENE}
{COLOR_WASH}
{SKELETON}
{KILL_SWITCH}
{LEFT_PANEL}
{WARN_PANEL}
{INFO_PANEL}
{RIGHT_PANEL}
{BOTTOM_BAR}
{STATUS}
{legend_svg}
</svg>
"""

os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(svg)
print(f'Saved → {os.path.abspath(OUT)}')
