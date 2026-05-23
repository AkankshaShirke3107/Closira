import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import ChannelBadge from './ChannelBadge';
import StatusBadge from './StatusBadge';
import { Colors, BorderRadius, FontSizes, Spacing } from '../constants/colors';

/**
 * LeadCard — tappable card for a lead/enquiry.
 *
 * @param {object} lead - Lead data object
 * @param {function} onPress - Callback when tapped
 */
export default function LeadCard({ lead, onPress }) {
  const timeAgo = getTimeAgo(lead.receivedAt);

  return (
    <TouchableOpacity
      style={styles.card}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.topRow}>
        <View style={styles.nameRow}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              {lead.customer.charAt(0).toUpperCase()}
            </Text>
          </View>
          <View style={styles.nameCol}>
            <Text style={styles.name} numberOfLines={1}>{lead.customer}</Text>
            <Text style={styles.time}>{timeAgo}</Text>
          </View>
        </View>
        <StatusBadge status={lead.status} />
      </View>
      <Text style={styles.summary} numberOfLines={2}>{lead.summary}</Text>
      <View style={styles.bottomRow}>
        <ChannelBadge channel={lead.channel} />
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
    borderColor: Colors.cardBorder,
    shadowColor: Colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 1,
    shadowRadius: 8,
    elevation: 2,
  },
  topRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: Spacing.sm,
  },
  nameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginRight: Spacing.sm,
  },
  avatar: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: Colors.primaryLight,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: Spacing.md,
  },
  avatarText: {
    fontSize: FontSizes.md,
    fontWeight: '700',
    color: Colors.primary,
  },
  nameCol: {
    flex: 1,
  },
  name: {
    fontSize: FontSizes.md,
    fontWeight: '600',
    color: Colors.textPrimary,
  },
  time: {
    fontSize: FontSizes.xs,
    color: Colors.textTertiary,
    marginTop: 2,
  },
  summary: {
    fontSize: FontSizes.sm,
    color: Colors.textSecondary,
    lineHeight: 18,
    marginBottom: Spacing.md,
  },
  bottomRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
});
