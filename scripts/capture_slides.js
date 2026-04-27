#!/usr/bin/env node
/**
 * capture_slides.js
 *
 * Headless slide capture using Playwright.
 * Renders slides_marp.md → HTML via marp-cli, then screenshots + records
 * each slide as a short motion clip.
 *
 * Prerequisites:
 *   npm install -g @marp-team/marp-cli
 *   npm install playwright
 *   npx playwright install chromium
 *
 * Usage:
 *   node scripts/capture_slides.js [--slides-html path/to/slides.html] [--out-dir docs/assets/slides]
 *
 * Outputs:
 *   docs/assets/slides/slide-01-intro.png          ← 1280×720 screenshot
 *   docs/assets/slides/slide-01-intro.webm         ← 3s motion clip (fade-in)
 *   ...
 *   docs/assets/slides/manifest.json               ← slide index with paths + metadata
 */

const { chromium } = require('playwright');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// ── Config ────────────────────────────────────────────────────────────────────
const ROOT       = path.resolve(__dirname, '..');
const MARP_SRC   = path.join(ROOT, 'video', 'slides_marp.md');
const HTML_OUT   = path.join(ROOT, 'video', 'slides_marp.html');
const ASSETS_DIR = path.join(ROOT, 'docs', 'assets', 'slides', 'v2');
const VIEWPORT   = { width: 1280, height: 720 };
const CLIP_MS    = 3000;   // motion clip duration per slide (ms)
const FPS        = 25;

// Slide IDs must match <!-- slide: <id> --> comments in slides_marp.md
// Used for output filenames and manifest.
const SLIDE_META = [
  { id: '01-intro',            title: '요가큐 — 인트로' },
  { id: '02-agenda',           title: '발표 순서' },
  { id: '03-background',       title: '프로젝트 배경' },
  { id: '04-platforms-social', title: '기존 플랫폼 — 검색·소셜' },
  { id: '05-platforms-booking',title: '기존 플랫폼 — 예약' },
  { id: '06-differentiation',  title: '차별점' },
  { id: '07-data',             title: '활용 데이터' },
  { id: '08-stack',            title: '기술 스택' },
  { id: '09-features',         title: '주요 기능' },
  { id: '10-demo',             title: '시연' },
  { id: '11-troubleshooting',  title: '트러블슈팅' },
  { id: '12-roadmap',          title: '향후 개선 방향' },
];

// ── Helpers ───────────────────────────────────────────────────────────────────
function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function buildMarpHtml() {
  console.log('▶ Building HTML from Marp slides…');
  execSync(
    `"${path.join(ROOT, 'node_modules', '.bin', 'marp')}" --html --allow-local-files "${MARP_SRC}" -o "${HTML_OUT}"`,
    { stdio: 'inherit' }
  );
  console.log(`✔ HTML written → ${HTML_OUT}`);
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  ensureDir(ASSETS_DIR);

  buildMarpHtml();

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: VIEWPORT,
    // Record video for every page so we can save per-slide clips
    recordVideo: {
      dir:  ASSETS_DIR,
      size: VIEWPORT,
    },
  });

  const manifest = [];

  for (let i = 0; i < SLIDE_META.length; i++) {
    const meta   = SLIDE_META[i];
    const slideN = i + 1;  // Marp pages are 1-indexed in URL hash

    console.log(`\n[${slideN}/${SLIDE_META.length}] Capturing: ${meta.id}`);

    const page = await context.newPage();

    // Navigate to the specific Marp slide (hash-based)
    await page.goto(`file://${HTML_OUT}#${slideN}`, { waitUntil: 'networkidle' });

    // Allow fonts / transitions to settle
    await page.waitForTimeout(600);

    // ── Screenshot ───────────────────────────────────────────────────────────
    const pngPath = path.join(ASSETS_DIR, `slide-${meta.id}.png`);
    await page.screenshot({ path: pngPath, type: 'png' });
    console.log(`  📸 ${path.relative(ROOT, pngPath)}`);

    // ── Motion clip (Playwright video) ───────────────────────────────────────
    // Simulate a subtle entrance: wait CLIP_MS then close to flush video.
    // The recorded .webm will contain the live render for that duration.
    await page.waitForTimeout(CLIP_MS);

    const video    = page.video();
    await page.close();  // flush video file
    const rawPath  = await video.path();
    const webmPath = path.join(ASSETS_DIR, `slide-${meta.id}.webm`);
    fs.renameSync(rawPath, webmPath);
    console.log(`  🎬 ${path.relative(ROOT, webmPath)}`);

    manifest.push({
      slide:      slideN,
      id:         meta.id,
      title:      meta.title,
      screenshot: `assets/slides/v2/slide-${meta.id}.png`,
      clip:       `assets/slides/v2/slide-${meta.id}.webm`,
    });
  }

  await browser.close();

  // ── Write manifest ────────────────────────────────────────────────────────
  const manifestPath = path.join(ASSETS_DIR, 'manifest.json');
  fs.writeFileSync(manifestPath, JSON.stringify({ slides: manifest }, null, 2));
  console.log(`\n✅ manifest.json → ${path.relative(ROOT, manifestPath)}`);
  console.log(`✅ Done. ${SLIDE_META.length} slides captured.`);
}

main().catch(err => {
  console.error('❌ Capture failed:', err.message);
  process.exit(1);
});
