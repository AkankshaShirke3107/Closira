import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors, BorderRadius, FontSizes, Spacing } from '../constants/colors';

export default function ActivityFeedItem({ activity }) {
  const isMatch = activity.status === 'qualified';
  const icon = isMatch ? 'checkmark-circle' : 'alert-circle';
  const iconColor = isMatch ? Colors.success : Colors.warning;

  return (
    <View style={styles.container}>
      <View style={styles.iconContainer}>
        <Ionicons name={icon} size={20} color={iconColor} />
        <View style={styles.line} />
      </View>
      <View style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.title}>
            <Text style={styles.bold}>{activity.customer}</Text> {isMatch ? 'matched SOP' : 'was escalated'}
          </Text>
          <Text style={styles.time}>2m</Text>
        </View>
        <Text style={styles.summary} numberOfLines={1}>{activity.summary}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    marginBottom: Spacing.md,
  },
  iconContainer: {
    alignItems: 'center',
    marginRight: Spacing.md,
  },
  line: {
    flex: 1,
    width: 2,
    backgroundColor: Colors.divider,
    marginTop: 4,
    marginBottom: -Spacing.md,
  },
  content: {
    flex: 1,
    backgroundColor: Colors.surface,
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: Colors.cardBorder,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  title: {
    fontSize: FontSizes.sm,
    color: Colors.textPrimary,
  },
  bold: {
    fontWeight: '700',
  },
  time: {
    fontSize: FontSizes.xs,
    color: Colors.textTertiary,
  },
  summary: {
    fontSize: FontSizes.sm,
    color: Colors.textSecondary,
  },
});
