import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Colors, BorderRadius, FontSizes, Spacing } from '../constants/colors';

/**
 * Generic badge component — renders a colored pill with a label.
 *
 * @param {string} label - Text to display
 * @param {string} color - Text/foreground color
 * @param {string} bgColor - Background color
 * @param {object} style - Optional additional styles
 */
export default function Badge({ label, color, bgColor, style }) {
  return (
    <View style={[styles.badge, { backgroundColor: bgColor }, style]}>
      <Text style={[styles.label, { color }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.full,
    alignSelf: 'flex-start',
  },
  label: {
    fontSize: FontSizes.xs,
    fontWeight: '600',
    letterSpacing: 0.3,
  },
});
