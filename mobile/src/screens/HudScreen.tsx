/**
 * HudScreen (example wiring)
 * ──────────────────────────
 * Shows how AlertBanner + ColorWash + useCueManager connect
 * to a VisionCamera frame processor that streams to the Pi.
 *
 * Replace <PiWebSocket /> and <FrameProcessor /> with your actual
 * implementations from mobile/src/api/ and mobile/src/sync/.
 */

import React, { useCallback, useRef } from 'react';
import { StyleSheet, View } from 'react-native';
import { Camera, useCameraDevice, useFrameProcessor } from 'react-native-vision-camera';
import { AlertBanner } from '../components/hud/AlertBanner';
import { ColorWash } from '../components/hud/ColorWash';
import { useCueManager } from '../hooks/useCueManager';
import type { PoseFrame } from '../cues/types';

// ── Screen ────────────────────────────────────────────────────────────────────

export const HudScreen: React.FC = () => {
  const device = useCameraDevice('front');

  // ── Cue hook ────────────────────────────────────────────────────────────────
  const { activeCue, evaluateFrame } = useCueManager({ ttsLang: 'en' });

  // Track wobble / stability from IMU sensor-fusion (update from your SensorFusion layer)
  const wobbleRef       = useRef(0);
  const stabilityRef    = useRef(1);
  const holdConfirmedRef = useRef(false);

  // ── Handle Pi WebSocket pose frame ──────────────────────────────────────────
  const onPoseFrame = useCallback(
    (frame: PoseFrame) => {
      evaluateFrame(frame, {
        kneeWobble:    wobbleRef.current,
        stabilityScore: stabilityRef.current,
        holdConfirmed:  holdConfirmedRef.current,
      });
    },
    [evaluateFrame],
  );

  // ── Frame processor (sends to Pi via WebSocket — implement in src/sync/) ────
  const frameProcessor = useFrameProcessor((frame) => {
    'worklet';
    // Forward compressed frame to Pi WebSocket — implementation in PiSyncBridge
    // piSyncBridge.sendFrame(frame);
  }, []);

  if (!device) return null;

  return (
    <View style={styles.root}>
      {/* Camera background */}
      <Camera
        style={StyleSheet.absoluteFill}
        device={device}
        isActive
        frameProcessor={frameProcessor}
        pixelFormat="yuv"
      />

      {/* Peripheral colour wash */}
      <ColorWash severity={activeCue?.severity ?? null} />

      {/* Alert banner — visible only when a cue is active */}
      {activeCue && (
        <AlertBanner
          severity={activeCue.severity}
          category={activeCue.category}
          text={activeCue.text}
          visible
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#000',
  },
});
