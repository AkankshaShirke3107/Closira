import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ChannelConfig } from '../constants/channels';
import { BorderRadius, FontSizes, Spacing } from '../constants/colors';

/**
 * Channel badge — renders a WhatsApp / Email / Call pill with icon.
 *
 * @param {string} channel - One of 'whatsapp', 'email', 'call'
 */
export default function ChannelBadge({ channel }) {
  const config = ChannelConfig[channel];
  if (!config) return null;

  return (
    <View style={[styles.badge, { backgroundColor: config.bgColor }]}>
      <Ionicons name={config.icon} size={12} color={config.color} />
      <Text style={[styles.label, { color: config.color }]}>{config.label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.sm,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.full,
    gap: 4,
  },
  label: {
    fontSize: FontSizes.xs,
    fontWeight: '600',
    letterSpacing: 0.3,
  },
});
