import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import ChannelBadge from './ChannelBadge';
import { Colors, BorderRadius, FontSizes, Spacing } from '../constants/colors';
import { UrgencyConfig } from '../constants/channels';

export default function EscalationCard({ escalation, onPress }) {
  const urgency = UrgencyConfig[escalation.urgency] || UrgencyConfig.medium;
  const timeAgo = getTimeAgo(escalation.receivedAt);

  const handleResolve = () => {
    Alert.alert('Resolve Escalation', `Are you sure you want to mark this escalation for ${escalation.customer} as resolved?`);
  };

  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.7}>
      <View style={styles.headerRow}>
        <Text style={styles.customerName} numberOfLines={1}>{escalation.customer}</Text>
        <Text style={styles.time}>{timeAgo}</Text>
      </View>
      
      <View style={styles.badgeRow}>
        <ChannelBadge channel={escalation.channel} />
        <View style={[styles.urgencyBadge, { backgroundColor: urgency.bgColor }]}>
          <Text style={[styles.urgencyText, { color: urgency.color }]}>{urgency.label} Urgency</Text>
        </View>
      </View>

      <View style={styles.reasonContainer}>
        <Text style={styles.reasonLabel}>Reason for escalation:</Text>
        <Text style={styles.reasonText}>{escalation.reason}</Text>
      </View>
      
      <View style={styles.actionRow}>
        <TouchableOpacity style={styles.resolveBtn} onPress={handleResolve}>
          <Text style={styles.resolveBtnText}>Resolve Issue</Text>
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );
}

function getTimeAgo(dateString) {
  const now = new Date();
  const date = new Date(dateString);
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    marginBottom: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.urgencyHighBg,
    shadowColor: Colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 1,
    shadowRadius: 8,
    elevation: 2,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  customerName: {
    fontSize: FontSizes.lg,
    fontWeight: '700',
    color: Colors.textPrimary,
    flex: 1,
  },
  time: {
    fontSize: FontSizes.xs,
    color: Colors.textTertiary,
  },
  badgeRow: {
    flexDirection: 'row',
    gap: Spacing.sm,
    marginBottom: Spacing.md,
  },
  urgencyBadge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.full,
  },
  urgencyText: {
    fontSize: FontSizes.xs,
    fontWeight: '600',
  },
  reasonContainer: {
    backgroundColor: Colors.surfaceHover,
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    marginBottom: Spacing.md,
  },
  reasonLabel: {
    fontSize: FontSizes.xs,
    fontWeight: '600',
    color: Colors.textSecondary,
    marginBottom: 4,
  },
  reasonText: {
    fontSize: FontSizes.sm,
    color: Colors.textPrimary,
    fontWeight: '500',
  },
  actionRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
  },
  resolveBtn: {
    backgroundColor: Colors.success,
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.sm,
    borderRadius: BorderRadius.md,
  },
  resolveBtnText: {
    color: Colors.textInverse,
    fontWeight: '600',
    fontSize: FontSizes.sm,
  },
});
