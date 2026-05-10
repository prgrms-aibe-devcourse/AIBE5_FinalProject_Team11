/**
 * useCueManager
 * ─────────────
 * React hook that wires a CueManager singleton to component state.
 *
 * Usage:
 *   const { activeCue, evaluate } = useCueManager({ ttsLang: 'ko' });
 *
 *   // On each PoseFrame received from the Pi WebSocket:
 *   const state = deriveState(frame);
 *   state.kneeWobble    = sensorFusion.wobbleRadsPerSec;
 *   state.stabilityScore = sensorFusion.score;
 *   state.holdConfirmed  = holdTimer.confirmed;
 *   evaluate(state);
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { CueManager, deriveState } from '../cues/CueManager';
import type { BiometricState, Cue, PoseFrame } from '../cues/types';

// ── Options ───────────────────────────────────────────────────────────────────

interface UseCueManagerOptions {
  /** ms between repeated identical cue ids. Default 2000. */
  defaultDebounceMs?: number;
  /** Language for TTS output. Default 'en'. */
  ttsLang?: 'en' | 'ko';
}

// ── Return value ──────────────────────────────────────────────────────────────

interface UseCueManagerResult {
  /** Currently active cue, or null if form is acceptable / no cue fired. */
  activeCue: Cue | null;
  /**
   * Evaluate a fully-merged BiometricState directly.
   * Use this when sensor-fusion values (wobble, stability, hold) are already merged.
   */
  evaluate: (state: BiometricState) => void;
  /**
   * Convenience: derive a BiometricState from a raw PoseFrame then evaluate.
   * Merges the optional overrides (wobble, stabilityScore, holdConfirmed) into the derived state.
   */
  evaluateFrame: (
    frame: PoseFrame,
    overrides?: Partial<Pick<BiometricState, 'kneeWobble' | 'stabilityScore' | 'holdConfirmed'>>,
  ) => void;
}

// ── Hook ──────────────────────────────────────────────────────────────────────

export function useCueManager(options: UseCueManagerOptions = {}): UseCueManagerResult {
  const managerRef = useRef<CueManager | null>(null);
  const [activeCue, setActiveCue] = useState<Cue | null>(null);

  // Instantiate once
  useEffect(() => {
    const mgr = new CueManager(options);
    managerRef.current = mgr;
    const unsub = mgr.subscribe((cue) => setActiveCue(cue));
    return () => {
      unsub();
      mgr.destroy();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const evaluate = useCallback((state: BiometricState) => {
    managerRef.current?.evaluate(state);
  }, []);

  const evaluateFrame = useCallback(
    (
      frame: PoseFrame,
      overrides?: Partial<Pick<BiometricState, 'kneeWobble' | 'stabilityScore' | 'holdConfirmed'>>,
    ) => {
      const state = deriveState(frame);
      if (overrides) Object.assign(state, overrides);
      managerRef.current?.evaluate(state);
    },
    [],
  );

  return { activeCue, evaluate, evaluateFrame };
}
