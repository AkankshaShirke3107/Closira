import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors, BorderRadius, FontSizes, Spacing } from '../constants/colors';

/**
 * StatCard — dashboard summary card with icon, label, and count.
 *
 * @param {string} label - Card title (e.g., "Total Leads")
 * @param {number} value - Numeric count
 * @param {string} icon - Ionicons icon name
 * @param {string} accentColor - Accent color for the icon circle
 * @param {string} accentBg - Background color for the icon circle
 */
export default function StatCard({ label, value, icon, accentColor, accentBg }) {
  return (
    <View style={styles.card}>
      <View style={[styles.iconCircle, { backgroundColor: accentBg }]}>
        <Ionicons name={icon} size={20} color={accentColor} />
      </View>
      <Text style={styles.value}>{value}</Text>
      <Text style={styles.label}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1,
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: Colors.cardBorder,
    shadowColor: Colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 1,
    shadowRadius: 8,
    elevation: 2,
  },
  iconCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  value: {
    fontSize: FontSizes.xxl,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginBottom: 2,
  },
  label: {
    fontSize: FontSizes.xs,
    fontWeight: '500',
    color: Colors.textSecondary,
    textAlign: 'center',
  },
});
