/**
 * AlertBanner
 * ───────────
 * Full-width HUD banner rendered at the top of the camera view.
 * Designed for 6–8 ft readability (72 pt+ text, bold, text-shadow).
 *
 * Severity mapping:
 *   INFO      → green pulse text
 *   WARNING   → amber text + directional label
 *   CRITICAL  → red strobing text + STOP icon
 */

import React, { useEffect, useRef } from 'react';
import {
  Animated,
  Easing,
  StyleSheet,
  Text,
  View,
  ViewStyle,
} from 'react-native';
import type { Severity, CueCategory } from '../cues/types';

// ── Palette ───────────────────────────────────────────────────────────────────

const COLOR: Record<Severity, string> = {
  INFO:     '#00CC77',   // green
  WARNING:  '#F59E0B',   // amber
  CRITICAL: '#FF3B30',   // red
};

const BG_COLOR: Record<Severity, string> = {
  INFO:     'rgba(0, 204, 119, 0.12)',
  WARNING:  'rgba(245, 158, 11, 0.18)',
  CRITICAL: 'rgba(255, 59, 48, 0.22)',
};

// ── Props ─────────────────────────────────────────────────────────────────────

export interface AlertBannerProps {
  severity: Severity;
  category: CueCategory;
  text: string;
  visible: boolean;
  style?: ViewStyle;
}

// ── Component ─────────────────────────────────────────────────────────────────

export const AlertBanner: React.FC<AlertBannerProps> = ({
  severity,
  category,
  text,
  visible,
  style,
}) => {
  const fadeAnim  = useRef(new Animated.Value(0)).current;
  const strobeAnim = useRef(new Animated.Value(1)).current;
  const strobeLoop = useRef<Animated.CompositeAnimation | null>(null);

  // ── Fade in / out ──────────────────────────────────────────────────────────
  useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue:         visible ? 1 : 0,
      duration:        visible ? 120 : 350,
      easing:          Easing.out(Easing.quad),
      useNativeDriver: true,
    }).start();
  }, [visible, fadeAnim]);

  // ── Strobe for CRITICAL ────────────────────────────────────────────────────
  useEffect(() => {
    if (severity === 'CRITICAL' && visible) {
      strobeLoop.current = Animated.loop(
        Animated.sequence([
          Animated.timing(strobeAnim, {
            toValue: 0.15, duration: 160, useNativeDriver: true,
          }),
          Animated.timing(strobeAnim, {
            toValue: 1, duration: 160, useNativeDriver: true,
          }),
        ]),
      );
      strobeLoop.current.start();
    } else {
      strobeLoop.current?.stop();
      strobeAnim.setValue(1);
    }
    return () => strobeLoop.current?.stop();
  }, [severity, visible, strobeAnim]);

  // ── Pulse glow for INFO ────────────────────────────────────────────────────
  const pulseAnim = useRef(new Animated.Value(1)).current;
  useEffect(() => {
    if (severity === 'INFO' && visible) {
      const pulse = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, { toValue: 1.06, duration: 600, useNativeDriver: true }),
          Animated.timing(pulseAnim, { toValue: 1,    duration: 600, useNativeDriver: true }),
        ]),
      );
      pulse.start();
      return () => pulse.stop();
    }
    pulseAnim.setValue(1);
    return undefined;
  }, [severity, visible, pulseAnim]);

  if (!visible) return null;

  const color      = COLOR[severity];
  const background = BG_COLOR[severity];
  const opacityAnim = severity === 'CRITICAL' ? strobeAnim : fadeAnim;

  return (
    <Animated.View
      style={[
        styles.container,
        { backgroundColor: background, borderColor: color, opacity: opacityAnim },
        style,
      ]}
      accessibilityLiveRegion="assertive"
      accessibilityRole="alert"
    >
      {/* CRITICAL: stop icon */}
      {severity === 'CRITICAL' && (
        <Text style={[styles.stopIcon, { color }]}>⛔</Text>
      )}

      {/* WARNING: directional marker */}
      {severity === 'WARNING' && (
        <Text style={[styles.warningIcon, { color }]}>▲</Text>
      )}

      <Animated.Text
        style={[
          styles.bannerText,
          { color, transform: [{ scale: severity === 'INFO' ? pulseAnim : 1 }] },
        ]}
        numberOfLines={2}
        adjustsFontSizeToFit={false}
      >
        {text}
      </Animated.Text>

      {/* Severity badge */}
      <View style={[styles.badge, { backgroundColor: color }]}>
        <Text style={styles.badgeText}>{severity}</Text>
      </View>
    </Animated.View>
  );
};

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: {
    position:      'absolute',
    top:           40,
    left:          16,
    right:         16,
    minHeight:     100,
    borderRadius:  16,
    borderWidth:   2,
    flexDirection: 'row',
    alignItems:    'center',
    justifyContent:'center',
    paddingHorizontal: 20,
    paddingVertical:    16,
    // Subtle frosted-glass feel
    shadowColor:   '#000',
    shadowOffset:  { width: 0, height: 4 },
    shadowOpacity: 0.55,
    shadowRadius:  12,
    elevation:     12,
    zIndex:        999,
  },

  bannerText: {
    flex:           1,
    fontSize:       72,       // readable at 6–8 ft
    fontWeight:     '900',
    textAlign:      'center',
    letterSpacing:  1.5,
    // Text shadow for readability over any camera background
    textShadowColor:  'rgba(0,0,0,0.95)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 8,
  },

  stopIcon: {
    fontSize:    72,
    marginRight: 8,
  },

  warningIcon: {
    fontSize:    48,
    marginRight: 8,
    fontWeight:  '900',
    textShadowColor:  'rgba(0,0,0,0.9)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 6,
  },

  badge: {
    position:     'absolute',
    bottom:       -10,
    right:         16,
    paddingHorizontal: 10,
    paddingVertical:    3,
    borderRadius:  8,
  },

  badgeText: {
    color:      '#fff',
    fontSize:   11,
    fontWeight: '700',
    letterSpacing: 1.2,
  },
});
