// ── Hailo-8 / Pi inference payload ────────────────────────────────────────────

export interface Landmark {
  x: number;          // normalised [0,1] relative to frame width
  y: number;          // normalised [0,1] relative to frame height
  z: number;          // depth relative to hip mid-point (metres)
  visibility: number; // [0,1]
}

/** 33-landmark MoveNet Thunder / MediaPipe output forwarded by the Pi server */
export interface PoseFrame {
  frameId: number;
  processedAt: number;        // Unix ms (Pi clock)
  receivedAt?: number;        // Unix ms (phone clock, set on receipt)
  landmarks: Landmark[];      // indices follow MediaPipe BlazePose convention
}

// ── Landmark indices (BlazePose / MoveNet) ────────────────────────────────────

export const LM = {
  LEFT_HIP:    23,
  RIGHT_HIP:   24,
  LEFT_KNEE:   25,
  RIGHT_KNEE:  26,
  LEFT_ANKLE:  27,
  RIGHT_ANKLE: 28,
  LEFT_SHOULDER:  11,
  RIGHT_SHOULDER: 12,
  NOSE:         0,
} as const;

// ── Cue severity ──────────────────────────────────────────────────────────────

export type Severity = 'INFO' | 'WARNING' | 'CRITICAL';

// ── Cue categories (maps to your three trigger groups) ───────────────────────

export type CueCategory = 'ENCOURAGEMENT' | 'CORRECTION' | 'KILL_SWITCH';

// ── A single displayable cue ──────────────────────────────────────────────────

export interface Cue {
  id: string;
  severity: Severity;
  category: CueCategory;
  /** Text shown in the AlertBanner */
  text: string;
  /** Bilingual: Korean cue text (optional, spoken / shown) */
  textKo?: string;
  /** Joint index the directional arrow should point to (CORRECTION only) */
  targetLandmark?: number;
  /** Whether TTS should speak this cue */
  speak: boolean;
  /** Minimum ms to wait before this id fires again */
  debounceMsOverride?: number;
}

// ── Biometric thresholds (tuneable) ──────────────────────────────────────────

export interface BiometricState {
  /** Front knee angle in degrees (90° is ideal for Runner's Lunge) */
  frontKneeAngle: number;
  /** Lateral wobble of the front knee in rad/s */
  kneeWobble: number;
  /** Torso lean away from vertical in degrees */
  torsoLean: number;
  /** Front knee projected shear over toes in degrees */
  kneeShearDeg: number;
  /** Whether the pose has been held for ≥ 500 ms at correct depth */
  holdConfirmed: boolean;
  /** Normalised stability score [0,1] from sensor fusion */
  stabilityScore: number;
}

export const THRESHOLDS = {
  KNEE_IDEAL_DEG:     90,
  KNEE_DEPTH_TOL:     10,     // ±10° around 90° is "good"
  WOBBLE_MAX:          0.15,  // rad/s
  TORSO_LEAN_MAX:     20,     // degrees from vertical
  KNEE_SHEAR_KILL:    20,     // degrees — triggers kill-switch
  STABILITY_HIGH:      0.80,
  HOLD_MS:            500,
} as const;
