/**
 * ColorWash
 * ─────────
 * Full-screen semi-transparent overlay that provides peripheral feedback.
 * The user perceives the correct colour in their peripheral vision without
 * having to read the AlertBanner text.
 *
 * INFO      → soft green wash (correct form)
 * WARNING   → amber wash (drifting)
 * CRITICAL  → red strobing wash (danger)
 * null      → invisible (clear)
 */

import React, { useEffect, useRef } from 'react';
import { Animated, Easing, StyleSheet, ViewStyle } from 'react-native';
import type { Severity } from '../../cues/types';

// ── Palette (alpha kept low so the camera feed is always readable) ─────────────

const WASH_COLOR: Record<Severity, string> = {
  INFO:     'rgba(0, 204, 119, 0.15)',
  WARNING:  'rgba(245, 158, 11, 0.20)',
  CRITICAL: 'rgba(255, 59, 48, 0.35)',
};

// ── Props ─────────────────────────────────────────────────────────────────────

export interface ColorWashProps {
  severity: Severity | null;
  style?: ViewStyle;
}

// ── Component ─────────────────────────────────────────────────────────────────

export const ColorWash: React.FC<ColorWashProps> = ({ severity, style }) => {
  const fadeAnim   = useRef(new Animated.Value(0)).current;
  const strobeAnim = useRef(new Animated.Value(1)).current;
  const strobeRef  = useRef<Animated.CompositeAnimation | null>(null);

  // Fade in/out when severity changes
  useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue:         severity ? 1 : 0,
      duration:        severity ? 200 : 500,
      easing:          Easing.out(Easing.cubic),
      useNativeDriver: false,          // backgroundColor cannot use native driver
    }).start();
  }, [severity, fadeAnim]);

  // Strobe effect for CRITICAL
  useEffect(() => {
    if (severity === 'CRITICAL') {
      strobeRef.current = Animated.loop(
        Animated.sequence([
          Animated.timing(strobeAnim, { toValue: 0.2, duration: 150, useNativeDriver: false }),
          Animated.timing(strobeAnim, { toValue: 1,   duration: 150, useNativeDriver: false }),
        ]),
      );
      strobeRef.current.start();
    } else {
      strobeRef.current?.stop();
      strobeAnim.setValue(1);
    }
    return () => strobeRef.current?.stop();
  }, [severity, strobeAnim]);

  // Interpolate background colour based on active severity
  const backgroundColor =
    severity === null
      ? 'transparent'
      : WASH_COLOR[severity];

  const combinedOpacity = severity === 'CRITICAL'
    ? Animated.multiply(fadeAnim, strobeAnim)
    : fadeAnim;

  return (
    <Animated.View
      pointerEvents="none"
      style={[
        styles.wash,
        { backgroundColor, opacity: combinedOpacity },
        style,
      ]}
    />
  );
};

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  wash: {
    ...StyleSheet.absoluteFillObject,
    zIndex: 10,    // sits above camera, below AlertBanner (zIndex 999)
  },
});
