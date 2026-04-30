#!/usr/bin/env python3
"""Write the accurate 3-pipeline infrastructure diagram SVG."""
import os

SVG = r"""<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="960" viewBox="0 0 1600 960">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#f0f4fa"/>
      <stop offset="100%" stop-color="#eef0f8"/>
    </linearGradient>
    <linearGradient id="cardFill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="#f8f9fc"/>
    </linearGradient>
    <linearGradient id="fillA" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#e8f3fc"/>
      <stop offset="100%" stop-color="#ddeaf7"/>
    </linearGradient>
    <linearGradient id="fillB" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#e8f6ee"/>
      <stop offset="100%" stop-color="#ddf0e6"/>
    </linearGradient>
    <linearGradient id="fillC" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#f0e8f8"/>
      <stop offset="100%" stop-color="#e8ddf2"/>
    </linearGradient>
    <linearGradient id="fillKS" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#fff2f2"/>
      <stop offset="100%" stop-color="#ffe8e8"/>
    </linearGradient>
    <filter id="shadow">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#00000018"/>
    </filter>
    <marker id="arrA" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#4a7ebb"/>
    </marker>
    <marker id="arrB" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#2e8b57"/>
    </marker>
    <marker id="arrC" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#7b5eaa"/>
    </marker>
  </defs>

  <rect width="1600" height="960" fill="url(#bg)"/>

  <g opacity="0.025" stroke="#4a7ebb" stroke-width="1">
    <line x1="293" y1="0" x2="293" y2="960"/>
    <line x1="583" y1="0" x2="583" y2="960"/>
    <line x1="878" y1="0" x2="878" y2="960"/>
    <line x1="1173" y1="0" x2="1173" y2="960"/>
    <line x1="1470" y1="0" x2="1470" y2="960"/>
  </g>

  <!-- TITLE -->
  <text x="800" y="46" text-anchor="middle" font-family="'Segoe UI', system-ui, sans-serif" font-size="30" font-weight="700" fill="#1e2d4a" letter-spacing="0.5">시스템 아키텍처</text>
  <text x="800" y="72" text-anchor="middle" font-family="'Segoe UI', system-ui, sans-serif" font-size="13" fill="#6b7a99">Yogaman.club — 데이터 수집 · 포즈 매칭 · 스튜디오 랭킹 · RAG 채팅 (3개 병렬 파이프라인)</text>
  <line x1="50" y1="83" x2="1550" y2="83" stroke="#c8d4e8" stroke-width="1.5"/>

  <!-- PIPELINE A group box: y=92, h=176 -->
  <g filter="url(#shadow)">
    <rect x="12" y="92" width="1576" height="176" rx="14" fill="url(#fillA)" stroke="#4a7ebb" stroke-width="2"/>
  </g>
  <rect x="16" y="96" width="157" height="168" rx="10" fill="#c6ddf4" stroke="#4a7ebb" stroke-width="1.5"/>
  <text x="94" y="153" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="13" font-weight="700" fill="#4a7ebb">Pipeline A</text>
  <text x="94" y="170" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" fill="#2c5f9e">포즈 매칭</text>
  <text x="94" y="186" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#2c5f9e">(Spring Boot)</text>
  <text x="94" y="202" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#6b7a99">yoga-api:19090</text>

  <!-- A1: yoga repo -->
  <g filter="url(#shadow)">
    <rect x="183" y="134" width="210" height="90" rx="10" fill="url(#cardFill)" stroke="#4a7ebb" stroke-width="1.3"/>
    <rect x="183" y="134" width="5" height="90" rx="2" fill="#4a7ebb"/>
  </g>
  <text x="293" y="157" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="600" fill="#1e2d4a">yoga repo</text>
  <text x="293" y="173" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">poses_database.json</text>
  <text x="293" y="188" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">2700+ asana records</text>
  <text x="293" y="203" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#ef5350">&#x1F512; read-only external</text>
  <line x1="393" y1="179" x2="475" y2="179" stroke="#4a7ebb" stroke-width="1.8" marker-end="url(#arrA)"/>

  <!-- A2: enrich_poses.py -->
  <g filter="url(#shadow)">
    <rect x="478" y="134" width="210" height="90" rx="10" fill="url(#cardFill)" stroke="#4a7ebb" stroke-width="1.3"/>
    <rect x="478" y="134" width="5" height="90" rx="2" fill="#4a7ebb"/>
  </g>
  <text x="583" y="157" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="600" fill="#1e2d4a">enrich_poses.py</text>
  <text x="583" y="173" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">benefit tags (weight 0&#x2013;1)</text>
  <text x="583" y="188" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">kill_switch flag &#xb7; severity</text>
  <text x="583" y="203" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#7b5eaa">Schema.org ExerciseAction</text>
  <line x1="688" y1="179" x2="770" y2="179" stroke="#4a7ebb" stroke-width="1.8" marker-end="url(#arrA)"/>

  <!-- A3: poses_eat_schema + SQL -->
  <g filter="url(#shadow)">
    <rect x="773" y="134" width="210" height="90" rx="10" fill="url(#cardFill)" stroke="#4a7ebb" stroke-width="1.3"/>
    <rect x="773" y="134" width="5" height="90" rx="2" fill="#4a7ebb"/>
  </g>
  <text x="878" y="154" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="600" fill="#1e2d4a">poses_eat_schema.json</text>
  <text x="878" y="170" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">&#x2192; generate_pose_insert_sql.py</text>
  <text x="878" y="185" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">artefact filter (OCR noise)</text>
  <text x="878" y="200" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#6b7a99">emit INSERT SQL</text>
  <line x1="983" y1="179" x2="1065" y2="179" stroke="#4a7ebb" stroke-width="1.8" marker-end="url(#arrA)"/>

  <!-- A4: PostgreSQL -->
  <g filter="url(#shadow)">
    <rect x="1068" y="134" width="210" height="90" rx="10" fill="url(#cardFill)" stroke="#4a7ebb" stroke-width="1.3"/>
    <rect x="1068" y="134" width="5" height="90" rx="2" fill="#4a7ebb"/>
  </g>
  <text x="1173" y="157" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="600" fill="#1e2d4a">PostgreSQL</text>
  <text x="1173" y="173" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">poses &#xb7; pose_benefits</text>
  <text x="1173" y="188" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">pose_contraindications</text>
  <text x="1173" y="203" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#6b7a99">postgres:8879</text>
  <line x1="1278" y1="179" x2="1360" y2="179" stroke="#4a7ebb" stroke-width="1.8" marker-end="url(#arrA)"/>

  <!-- A5: Spring Boot (output, highlighted) -->
  <g filter="url(#shadow)">
    <rect x="1363" y="130" width="215" height="98" rx="10" fill="#deeeff" stroke="#2c5f9e" stroke-width="2"/>
    <rect x="1363" y="130" width="5" height="98" rx="2" fill="#2c5f9e"/>
  </g>
  <text x="1470" y="151" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="11.5" font-weight="700" fill="#1e2d4a">Spring Boot yoga-api</text>
  <text x="1470" y="167" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">&#x2460; difficulty &#x2264; user.level</text>
  <text x="1470" y="181" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">&#x2461; time_budget filter</text>
  <text x="1470" y="196" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#c62828">&#x2462; Kill-Switch &#x2192; DROP</text>
  <text x="1470" y="211" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#2c5f9e">&#x2463; &#x03A3;(benefit.w &#xd7; goal) &#x2192; Top-K</text>

  <!-- PIPELINE B group box: y=282, h=152 -->
  <g filter="url(#shadow)">
    <rect x="12" y="282" width="1576" height="152" rx="14" fill="url(#fillB)" stroke="#2e8b57" stroke-width="2"/>
  </g>
  <rect x="16" y="286" width="157" height="144" rx="10" fill="#c4e8d0" stroke="#2e8b57" stroke-width="1.5"/>
  <text x="94" y="338" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="13" font-weight="700" fill="#2e8b57">Pipeline B</text>
  <text x="94" y="355" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" fill="#1b5e20">&#xC2A4;&#xD29C;&#xB514;&#xC624; &#xB9E4;&#xCE6D;</text>
  <text x="94" y="371" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#1b5e20">(Streamlit demo)</text>
  <text x="94" y="387" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#6b7a99">LangGraph (prod)</text>

  <!-- B1: User Input -->
  <g filter="url(#shadow)">
    <rect x="183" y="313" width="210" height="90" rx="10" fill="url(#cardFill)" stroke="#2e8b57" stroke-width="1.3"/>
    <rect x="183" y="313" width="5" height="90" rx="2" fill="#2e8b57"/>
  </g>
  <text x="293" y="336" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="600" fill="#1e2d4a">User Input</text>
  <text x="293" y="352" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">physical_need</text>
  <text x="293" y="367" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">lat / lon</text>
  <text x="293" y="382" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#6b7a99">max_km radius</text>
  <line x1="393" y1="358" x2="475" y2="358" stroke="#2e8b57" stroke-width="1.8" marker-end="url(#arrB)"/>

  <!-- B2: NeedFit Score -->
  <g filter="url(#shadow)">
    <rect x="478" y="313" width="210" height="90" rx="10" fill="url(#cardFill)" stroke="#2e8b57" stroke-width="1.3"/>
    <rect x="478" y="313" width="5" height="90" rx="2" fill="#2e8b57"/>
  </g>
  <text x="583" y="333" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="600" fill="#1e2d4a">NeedFit Score</text>
  <text x="583" y="349" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">NEED_TO_SPECS overlap</text>
  <text x="583" y="364" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">min(1.0, |&#x2229;| / 2)</text>
  <text x="583" y="381" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="700" fill="#2e8b57">&#xd7; 0.40</text>
  <line x1="688" y1="358" x2="770" y2="358" stroke="#2e8b57" stroke-width="1.8" marker-end="url(#arrB)"/>

  <!-- B3: Proximity Score -->
  <g filter="url(#shadow)">
    <rect x="773" y="313" width="210" height="90" rx="10" fill="url(#cardFill)" stroke="#2e8b57" stroke-width="1.3"/>
    <rect x="773" y="313" width="5" height="90" rx="2" fill="#2e8b57"/>
  </g>
  <text x="878" y="333" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="600" fill="#1e2d4a">Proximity Score</text>
  <text x="878" y="349" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">Haversine(lat&#x2081;,lon&#x2081;,lat&#x2082;,lon&#x2082;)</text>
  <text x="878" y="364" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">1 &#x2212; dist_km / max_km</text>
  <text x="878" y="381" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="700" fill="#2e8b57">&#xd7; 0.30</text>
  <line x1="983" y1="358" x2="1065" y2="358" stroke="#2e8b57" stroke-width="1.8" marker-end="url(#arrB)"/>

  <!-- B4: Specialization Score -->
  <g filter="url(#shadow)">
    <rect x="1068" y="313" width="210" height="90" rx="10" fill="url(#cardFill)" stroke="#2e8b57" stroke-width="1.3"/>
    <rect x="1068" y="313" width="5" height="90" rx="2" fill="#2e8b57"/>
  </g>
  <text x="1173" y="333" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="600" fill="#1e2d4a">Specialization Score</text>
  <text x="1173" y="349" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">NEED_TO_CERTS overlap</text>
  <text x="1173" y="364" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">0.7&#xd7;cert + 0.3&#xd7;(rating&#x2212;4)</text>
  <text x="1173" y="381" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="700" fill="#2e8b57">&#xd7; 0.30</text>
  <line x1="1278" y1="358" x2="1360" y2="358" stroke="#2e8b57" stroke-width="1.8" marker-end="url(#arrB)"/>

  <!-- B5: Ranked Studios (output) -->
  <g filter="url(#shadow)">
    <rect x="1363" y="309" width="215" height="98" rx="10" fill="#e0f5e8" stroke="#1b5e20" stroke-width="2"/>
    <rect x="1363" y="309" width="5" height="98" rx="2" fill="#1b5e20"/>
  </g>
  <text x="1470" y="330" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="700" fill="#1e2d4a">Ranked Studios</text>
  <text x="1470" y="346" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">0.40 NeedFit</text>
  <text x="1470" y="361" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">+ 0.30 Proximity</text>
  <text x="1470" y="376" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#1b5e20">+ 0.30 Specialization</text>
  <text x="1470" y="393" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#1b5e20">sort DESC &#x2192; DataFrame</text>

  <!-- PIPELINE C group box: y=448, h=390 -->
  <g filter="url(#shadow)">
    <rect x="12" y="448" width="1576" height="390" rx="14" fill="url(#fillC)" stroke="#7b5eaa" stroke-width="2"/>
  </g>
  <rect x="16" y="452" width="157" height="382" rx="10" fill="#d4bce8" stroke="#7b5eaa" stroke-width="1.5"/>
  <text x="94" y="606" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="13" font-weight="700" fill="#7b5eaa">Pipeline C</text>
  <text x="94" y="623" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" fill="#4a235a">RAG &#xCC44;&#xD305;</text>
  <text x="94" y="639" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#4a235a">(FastAPI)</text>
  <text x="94" y="655" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#4a235a">Ollama Mistral</text>
  <text x="94" y="671" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="9.5" fill="#6b7a99">elbee.yogaman.club</text>

  <!-- C1: screenshots/ -->
  <g filter="url(#shadow)">
    <rect x="183" y="488" width="210" height="90" rx="10" fill="url(#cardFill)" stroke="#7b5eaa" stroke-width="1.3"/>
    <rect x="183" y="488" width="5" height="90" rx="2" fill="#7b5eaa"/>
  </g>
  <text x="293" y="511" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="600" fill="#1e2d4a">screenshots/</text>
  <text x="293" y="527" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">&#xAD50;&#xC7AC; &#xC774;&#xBBF8;&#xC9C0; (book pages)</text>
  <text x="293" y="542" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">jpg &#xb7; png &#xb7; webp &#xb7; tiff</text>
  <text x="293" y="557" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#6b7a99">zero-padded filenames</text>
  <line x1="393" y1="533" x2="475" y2="533" stroke="#7b5eaa" stroke-width="1.8" marker-end="url(#arrC)"/>

  <!-- C2: ocr_pipeline.py -->
  <g filter="url(#shadow)">
    <rect x="478" y="488" width="210" height="90" rx="10" fill="url(#cardFill)" stroke="#7b5eaa" stroke-width="1.3"/>
    <rect x="478" y="488" width="5" height="90" rx="2" fill="#7b5eaa"/>
  </g>
  <text x="583" y="511" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="600" fill="#1e2d4a">ocr_pipeline.py</text>
  <text x="583" y="527" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">Tesseract LSTM + cv2</text>
  <text x="583" y="542" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">deskew &#xb7; denoise &#xb7; binarize</text>
  <text x="583" y="557" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#6b7a99">upscale &lt;1500px wide</text>
  <line x1="688" y1="533" x2="770" y2="533" stroke="#7b5eaa" stroke-width="1.8" marker-end="url(#arrC)"/>

  <!-- C3: ocr_database.json -->
  <g filter="url(#shadow)">
    <rect x="773" y="488" width="210" height="90" rx="10" fill="url(#cardFill)" stroke="#7b5eaa" stroke-width="1.3"/>
    <rect x="773" y="488" width="5" height="90" rx="2" fill="#7b5eaa"/>
  </g>
  <text x="878" y="509" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="600" fill="#1e2d4a">ocr_database.json</text>
  <text x="878" y="525" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">pages[{page_number,</text>
  <text x="878" y="540" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">text, tags}]</text>
  <text x="878" y="555" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#6b7a99">data/json/&lt;slug&gt;/</text>
  <line x1="983" y1="533" x2="1065" y2="533" stroke="#7b5eaa" stroke-width="1.8" marker-end="url(#arrC)"/>

  <!-- C4: GeoDataStore.load() -->
  <g filter="url(#shadow)">
    <rect x="1068" y="488" width="210" height="90" rx="10" fill="url(#cardFill)" stroke="#7b5eaa" stroke-width="1.3"/>
    <rect x="1068" y="488" width="5" height="90" rx="2" fill="#7b5eaa"/>
  </g>
  <text x="1173" y="509" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="600" fill="#1e2d4a">GeoDataStore.load()</text>
  <text x="1173" y="525" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">keyword_index: word&#x2192;[page_idx]</text>
  <text x="1173" y="540" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10.5" fill="#6b7a99">platform_index &#xb7; region_index</text>
  <text x="1173" y="555" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#4a235a">startup singleton (FastAPI)</text>

  <!-- Fork: C4 -> /search (curve down to cy=628) -->
  <path d="M 1278,520 C 1293,520 1293,628 1298,628" fill="none" stroke="#7b5eaa" stroke-width="1.7" marker-end="url(#arrC)"/>
  <text x="1291" y="562" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#7b5eaa">/search</text>

  <!-- Fork: C4 -> /chat (curve down to cy=742) -->
  <path d="M 1278,546 C 1288,546 1288,742 1298,742" fill="none" stroke="#7b5eaa" stroke-width="1.7" stroke-dasharray="5,3" marker-end="url(#arrC)"/>
  <text x="1285" y="660" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#7b5eaa">/chat</text>

  <!-- /search node: cx=1378, cy=628 -->
  <g filter="url(#shadow)">
    <rect x="1298" y="596" width="160" height="64" rx="9" fill="url(#cardFill)" stroke="#7b5eaa" stroke-width="1.2"/>
    <rect x="1298" y="596" width="4" height="64" rx="2" fill="#7b5eaa"/>
  </g>
  <text x="1382" y="617" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="600" fill="#1e2d4a">/search endpoint</text>
  <text x="1382" y="633" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#6b7a99">platform &#x2229; region &#x2229; topic</text>
  <text x="1382" y="648" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#6b7a99">keyword_scores &#x2192; sort DESC</text>

  <!-- /chat node: cx=1378, cy=742 -->
  <g filter="url(#shadow)">
    <rect x="1298" y="710" width="160" height="64" rx="9" fill="url(#cardFill)" stroke="#7b5eaa" stroke-width="1.2"/>
    <rect x="1298" y="710" width="4" height="64" rx="2" fill="#7b5eaa"/>
  </g>
  <text x="1382" y="731" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="600" fill="#1e2d4a">/chat (RAG)</text>
  <text x="1382" y="747" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#6b7a99">top-K pages &#x2192; context</text>
  <text x="1382" y="762" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#4a235a">&#xD574;&#xC694;&#xCCB4; system prompt</text>

  <!-- /search -> Elbee -->
  <path d="M 1458,628 C 1474,628 1474,682 1480,682" fill="none" stroke="#7b5eaa" stroke-width="1.7" marker-end="url(#arrC)"/>
  <!-- /chat -> Elbee -->
  <path d="M 1458,742 C 1474,742 1474,710 1480,710" fill="none" stroke="#7b5eaa" stroke-width="1.7" marker-end="url(#arrC)"/>

  <!-- Elbee / Ollama node: x=1480, cy=696, w=108, h=152 -->
  <g filter="url(#shadow)">
    <rect x="1480" y="620" width="108" height="152" rx="10" fill="#ede0f8" stroke="#4a235a" stroke-width="2"/>
    <rect x="1480" y="620" width="5" height="152" rx="2" fill="#4a235a"/>
  </g>
  <text x="1534" y="643" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="700" fill="#4a235a">Elbee RAG</text>
  <text x="1534" y="660" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#6b7a99">Ollama</text>
  <text x="1534" y="674" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#6b7a99">(Mistral)</text>
  <line x1="1490" y1="688" x2="1582" y2="688" stroke="#7b5eaa" stroke-width="0.6" opacity="0.4"/>
  <text x="1534" y="702" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#c62828">&#x2192; OpenAI</text>
  <text x="1534" y="716" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#c62828">fallback</text>
  <line x1="1490" y1="728" x2="1582" y2="728" stroke="#7b5eaa" stroke-width="0.6" opacity="0.4"/>
  <text x="1534" y="742" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="#6b7a99">streaming SSE</text>
  <text x="1534" y="756" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="9.5" fill="#7b5eaa">elbee.yogaman.club</text>

  <!-- KILL-SWITCH BANNER -->
  <g filter="url(#shadow)">
    <rect x="12" y="852" width="1576" height="54" rx="10" fill="url(#fillKS)" stroke="#c62828" stroke-width="2"/>
  </g>
  <text x="800" y="873" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="13" font-weight="700" fill="#c62828">&#x26D4; Kill-Switch &#xBD88;&#xBCC0;&#xC2DD; (&#xD3EC;&#xC988; &#xB9E4;&#xCE6D;)</text>
  <text x="800" y="892" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="11" fill="#6b7a99">kill_switch = TRUE &#xD3EC;&#xC988;&#xB294; &#xC810;&#xC218; &#xACC4;&#xC0B0; &#xC774;&#xC804;&#xC5D0; &#xC644;&#xC804; &#xC81C;&#xC678; &#x2014; severity: CAUTION &#xb7; CRITICAL &#xb7; MEDICAL_CLEARANCE &#x2014; score &#xAC12;&#xACFC; &#xBB34;&#xAD00;&#xD558;&#xAC8C; &#xC801;&#xC6A9;</text>

  <!-- LEGEND -->
  <rect x="12" y="914" width="1576" height="42" rx="8" fill="white" opacity="0.75" stroke="#c8d4e8" stroke-width="1"/>
  <rect x="28" y="925" width="12" height="12" rx="2" fill="#4a7ebb"/>
  <text x="46" y="936" font-family="'Segoe UI', sans-serif" font-size="11" fill="#444">Pipeline A &#x2014; &#xD3EC;&#xC988; &#xB9E4;&#xCE6D; (Spring Boot &#xb7; Kill-Switch &#xB0B4;&#xC7A5;)</text>
  <rect x="318" y="925" width="12" height="12" rx="2" fill="#2e8b57"/>
  <text x="336" y="936" font-family="'Segoe UI', sans-serif" font-size="11" fill="#444">Pipeline B &#x2014; &#xC2A4;&#xD29C;&#xB514;&#xC624; &#xB9E4;&#xCE6D; (Haversine &#xb7; &#xAC00;&#xC911; &#xD569;&#xC0B0;)</text>
  <rect x="616" y="925" width="12" height="12" rx="2" fill="#7b5eaa"/>
  <text x="634" y="936" font-family="'Segoe UI', sans-serif" font-size="11" fill="#444">Pipeline C &#x2014; RAG &#xCC44;&#xD305; (OCR &#x2192; GeoDataStore &#x2192; Ollama)</text>
  <rect x="28" y="941" width="12" height="12" rx="2" fill="#c62828"/>
  <text x="46" y="952" font-family="'Segoe UI', sans-serif" font-size="11" fill="#444">Kill-Switch &#xD544;&#xD130;</text>
  <rect x="318" y="941" width="12" height="12" rx="2" fill="#336791"/>
  <text x="336" y="952" font-family="'Segoe UI', sans-serif" font-size="11" fill="#444">PostgreSQL (poses &#xb7; pose_benefits &#xb7; pose_contraindications)</text>
  <rect x="616" y="941" width="12" height="12" rx="2" fill="#4a235a"/>
  <text x="634" y="952" font-family="'Segoe UI', sans-serif" font-size="11" fill="#444">GeoDataStore: inverted keyword &#xb7; platform &#xb7; region &#xb7; topic indexes</text>
</svg>"""

out = "/home/aiegoo/repos/aiegoo/aeogeo/assets/infrastructure_diagram.svg"
with open(out, "w", encoding="utf-8") as f:
    f.write(SVG)
print(f"Written {len(SVG)} bytes to {out}")
