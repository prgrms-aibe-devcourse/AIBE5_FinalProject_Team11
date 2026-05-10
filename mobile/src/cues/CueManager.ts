/**
 * CueManager
 * ──────────
 * Maps Hailo-8 / Pi pose inference → prioritised voice + visual cues.
 *
 * Priority ladder (highest wins):
 *   3  KILL_SWITCH  (CRITICAL)
 *   2  CORRECTION   (WARNING)
 *   1  ENCOURAGEMENT (INFO)
 *
 * Debounce: each cue id is silenced for `debounceMs` after firing.
 * The default is 2 000 ms; individual cues may override via `debounceMsOverride`.
 */

import Tts from 'react-native-tts';
import {
  Cue,
  CueCategory,
  Severity,
  BiometricState,
  PoseFrame,
  LM,
  THRESHOLDS,
} from './types';

// ── Cue catalogue ─────────────────────────────────────────────────────────────

const CUE_CATALOGUE: Cue[] = [
  // ── ENCOURAGEMENT ──────────────────────────────────────────────────────────
  {
    id: 'enc_perfect_depth',
    severity: 'INFO',
    category: 'ENCOURAGEMENT',
    text: 'Perfect depth',
    textKo: '완벽한 깊이예요',
    speak: true,
  },
  {
    id: 'enc_solid_hold',
    severity: 'INFO',
    category: 'ENCOURAGEMENT',
    text: 'Solid hold',
    textKo: '마시며, 척추 길게, 내시며, 여유 공간을 찾아 더 깊게',
    speak: true,
  },
  {
    id: 'enc_keep_up',
    severity: 'INFO',
    category: 'ENCOURAGEMENT',
    text: 'Keep it up',
    speak: true,
  },

  // ── CORRECTION ─────────────────────────────────────────────────────────────
  {
    id: 'cor_back_knee',
    severity: 'WARNING',
    category: 'CORRECTION',
    text: 'Back knee lower',
    targetLandmark: LM.LEFT_KNEE,
    speak: true,
    debounceMsOverride: 3_000,
  },
  {
    id: 'cor_chest_up',
    severity: 'WARNING',
    category: 'CORRECTION',
    text: 'Chest up',
    targetLandmark: LM.LEFT_SHOULDER,
    speak: true,
    debounceMsOverride: 3_000,
  },
  {
    id: 'cor_wobble',
    severity: 'WARNING',
    category: 'CORRECTION',
    text: 'Watch your balance',
    targetLandmark: LM.LEFT_KNEE,
    speak: true,
  },

  // ── KILL_SWITCH ────────────────────────────────────────────────────────────
  {
    id: 'ks_knee_shear',
    severity: 'CRITICAL',
    category: 'KILL_SWITCH',
    text: 'CAUTION: KNEE STRESS',
    speak: true,
    debounceMsOverride: 1_000,
  },
  {
    id: 'ks_abort',
    severity: 'CRITICAL',
    category: 'KILL_SWITCH',
    text: 'STOP IMMEDIATELY',
    speak: true,
    debounceMsOverride: 1_500,
  },
];

// ── Angle helpers ─────────────────────────────────────────────────────────────

/**
 * Derive a BiometricState snapshot from a raw PoseFrame.
 * All angles are approximated in 2-D (x, y) — replace with 3-D if z is reliable.
 */
export function deriveState(frame: PoseFrame): BiometricState {
  const lm = frame.landmarks;

  const angleDeg = (a: number, b: number, c: number): number => {
    const ax = lm[a].x - lm[b].x, ay = lm[a].y - lm[b].y;
    const cx = lm[c].x - lm[b].x, cy = lm[c].y - lm[b].y;
    const dot = ax * cx + ay * cy;
    const mag = Math.sqrt(ax * ax + ay * ay) * Math.sqrt(cx * cx + cy * cy);
    if (mag === 0) return 180;
    return (Math.acos(Math.min(1, Math.max(-1, dot / mag))) * 180) / Math.PI;
  };

  const frontKneeAngle = angleDeg(LM.RIGHT_HIP, LM.RIGHT_KNEE, LM.RIGHT_ANKLE);

  // Torso lean: angle between vertical and hip→shoulder vector
  const midHipX = (lm[LM.LEFT_HIP].x + lm[LM.RIGHT_HIP].x) / 2;
  const midHipY = (lm[LM.LEFT_HIP].y + lm[LM.RIGHT_HIP].y) / 2;
  const midShX  = (lm[LM.LEFT_SHOULDER].x + lm[LM.RIGHT_SHOULDER].x) / 2;
  const midShY  = (lm[LM.LEFT_SHOULDER].y + lm[LM.RIGHT_SHOULDER].y) / 2;
  const torsoLean = Math.abs(
    (Math.atan2(midShX - midHipX, midHipY - midShY) * 180) / Math.PI,
  );

  // Knee shear: how far the knee x extends past the ankle x (normalised)
  const kneeShearNorm = lm[LM.RIGHT_KNEE].x - lm[LM.RIGHT_ANKLE].x;
  const kneeShearDeg  = kneeShearNorm * 90; // rough linear mapping

  // Wobble & stability are injected externally (sensor fusion) — default safe vals
  return {
    frontKneeAngle,
    kneeWobble: 0,           // populated by SensorFusion layer before calling evaluate()
    torsoLean,
    kneeShearDeg,
    holdConfirmed: false,    // set by CalibrationStore after 500 ms timer
    stabilityScore: 1,       // set by SensorFusion layer
  };
}

// ── CueManager ────────────────────────────────────────────────────────────────

export type CueListener = (cue: Cue | null) => void;

export class CueManager {
  private readonly defaultDebounceMs: number;
  private lastFiredAt: Map<string, number> = new Map();
  private listeners: Set<CueListener> = new Set();
  private ttsLang: 'en' | 'ko' = 'en';

  constructor(options: { defaultDebounceMs?: number; ttsLang?: 'en' | 'ko' } = {}) {
    this.defaultDebounceMs = options.defaultDebounceMs ?? 2_000;
    this.ttsLang = options.ttsLang ?? 'en';

    Tts.setDefaultLanguage(this.ttsLang === 'ko' ? 'ko-KR' : 'en-US');
    Tts.setDefaultPitch(1.0);
    Tts.setDefaultRate(0.5);
  }

  // ── Subscribe / unsubscribe ─────────────────────────────────────────────────

  subscribe(listener: CueListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private emit(cue: Cue | null) {
    this.listeners.forEach((l) => l(cue));
  }

  // ── Core evaluation ─────────────────────────────────────────────────────────

  /**
   * Call on every PoseFrame + merged sensor state.
   * Returns the highest-priority Cue that is not debounced, or null.
   */
  evaluate(state: BiometricState): Cue | null {
    const candidates = this.selectCandidates(state);
    if (candidates.length === 0) {
      this.emit(null);
      return null;
    }

    // Highest priority first (KILL_SWITCH > CORRECTION > ENCOURAGEMENT)
    const priority: Record<CueCategory, number> = {
      KILL_SWITCH:    3,
      CORRECTION:     2,
      ENCOURAGEMENT:  1,
    };
    candidates.sort((a, b) => priority[b.category] - priority[a.category]);

    for (const cue of candidates) {
      if (this.isDebounced(cue)) continue;
      this.fire(cue);
      return cue;
    }

    return null;
  }

  // ── Internal ────────────────────────────────────────────────────────────────

  private selectCandidates(s: BiometricState): Cue[] {
    const cues: Cue[] = [];

    // KILL_SWITCH: knee shear
    if (s.kneeShearDeg > THRESHOLDS.KNEE_SHEAR_KILL) {
      cues.push(this.byId('ks_knee_shear')!);
    }
    // KILL_SWITCH: severe wobble + torso lean combo
    if (s.kneeWobble > THRESHOLDS.WOBBLE_MAX * 2.5 && s.torsoLean > THRESHOLDS.TORSO_LEAN_MAX) {
      cues.push(this.byId('ks_abort')!);
    }

    // CORRECTION: wobble
    if (s.kneeWobble > THRESHOLDS.WOBBLE_MAX) {
      cues.push(this.byId('cor_wobble')!);
    }
    // CORRECTION: torso lean
    if (s.torsoLean > THRESHOLDS.TORSO_LEAN_MAX) {
      cues.push(this.byId('cor_chest_up')!);
    }
    // CORRECTION: front knee too high (not deep enough)
    if (s.frontKneeAngle > THRESHOLDS.KNEE_IDEAL_DEG + THRESHOLDS.KNEE_DEPTH_TOL) {
      cues.push(this.byId('cor_back_knee')!);
    }

    // ENCOURAGEMENT: good depth + stability + hold
    const nearIdeal =
      Math.abs(s.frontKneeAngle - THRESHOLDS.KNEE_IDEAL_DEG) <= THRESHOLDS.KNEE_DEPTH_TOL;
    if (nearIdeal && s.stabilityScore >= THRESHOLDS.STABILITY_HIGH) {
      cues.push(this.byId('enc_perfect_depth')!);
    }
    if (s.holdConfirmed && s.stabilityScore >= THRESHOLDS.STABILITY_HIGH) {
      cues.push(this.byId('enc_solid_hold')!);
    }

    return cues.filter(Boolean);
  }

  private byId(id: string): Cue | undefined {
    return CUE_CATALOGUE.find((c) => c.id === id);
  }

  private isDebounced(cue: Cue): boolean {
    const last = this.lastFiredAt.get(cue.id) ?? 0;
    const wait = cue.debounceMsOverride ?? this.defaultDebounceMs;
    return Date.now() - last < wait;
  }

  private fire(cue: Cue) {
    this.lastFiredAt.set(cue.id, Date.now());
    this.emit(cue);

    if (cue.speak) {
      const text =
        this.ttsLang === 'ko' && cue.textKo ? cue.textKo : cue.text;
      // Stop current utterance only for CRITICAL to avoid cutting off encouragement
      if (cue.severity === 'CRITICAL') Tts.stop();
      Tts.speak(text);
    }
  }

  // ── Lifecycle ───────────────────────────────────────────────────────────────

  destroy() {
    this.listeners.clear();
    Tts.stop();
  }
}
