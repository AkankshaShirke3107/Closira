import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, SafeAreaView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Badge from '../components/Badge';
import ChannelBadge from '../components/ChannelBadge';
import StatusBadge from '../components/StatusBadge';
import { Colors, BorderRadius, FontSizes, Spacing } from '../constants/colors';

import conversationsData from '../mock/conversations.json';

export default function ConversationDetailScreen({ route, navigation }) {
  const { conversationId, customerName } = route.params;
  
  // Find the conversation from mock data
  const conversation = conversationsData.find(c => c.id === conversationId) || conversationsData[0];

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      {/* Custom Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color={Colors.textPrimary} />
        </TouchableOpacity>
        <View style={styles.headerTitleContainer}>
          <Text style={styles.headerTitle}>{customerName || conversation.customer}</Text>
          <View style={styles.headerBadges}>
            <ChannelBadge channel={conversation.channel} />
            <StatusBadge status={conversation.status} />
          </View>
        </View>
      </View>

      <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer} showsVerticalScrollIndicator={false}>
        
        {/* AI Summary Card */}
        <View style={styles.summaryCard}>
          <View style={styles.summaryHeader}>
            <Ionicons name="sparkles" size={16} color={Colors.primary} />
            <Text style={styles.summaryTitle}>AI Summary</Text>
          </View>
          <Text style={styles.summaryText}>{conversation.aiSummary}</Text>
          
          <View style={styles.sopRow}>
            <Text style={styles.sopLabel}>Matched SOP:</Text>
            <Badge 
              label={conversation.sopMatch} 
              color={Colors.primaryDark} 
              bgColor={Colors.primaryLight} 
            />
          </View>
        </View>

        {/* Timeline visualization */}
        <View style={styles.timelineCard}>
          <Text style={styles.sectionTitle}>Event Timeline</Text>
          <View style={styles.timeline}>
            {conversation.timeline.map((event, index) => {
              const isLast = index === conversation.timeline.length - 1;
              return (
                <View key={index} style={styles.timelineItem}>
                  <View style={styles.timelineIndicator}>
                    <View style={styles.timelineDot} />
                    {!isLast && <View style={styles.timelineLine} />}
                  </View>
                  <View style={styles.timelineContent}>
                    <Text style={styles.timelineLabel}>{event.label}</Text>
                    <Text style={styles.timelineTime}>{formatTime(event.timestamp)}</Text>
                  </View>
                </View>
              );
            })}
          </View>
        </View>

        {/* Message Thread */}
        <Text style={styles.sectionTitle}>Conversation Thread</Text>
        <View style={styles.thread}>
          {conversation.messages.map((msg) => {
            const isAi = msg.sender === 'ai';
            return (
              <View key={msg.id} style={[styles.messageRow, isAi ? styles.messageRowAi : styles.messageRowCustomer]}>
                {!isAi && <View style={styles.avatar}><Text style={styles.avatarText}>{conversation.customer.charAt(0)}</Text></View>}
                <View style={[styles.messageBubble, isAi ? styles.messageBubbleAi : styles.messageBubbleCustomer]}>
                  <Text style={[styles.messageText, isAi && styles.messageTextAi]}>{msg.text}</Text>
                  <Text style={[styles.messageTime, isAi && styles.messageTimeAi]}>{formatTime(msg.timestamp)}</Text>
                </View>
                {isAi && <View style={styles.avatarAi}><Ionicons name="hardware-chip" size={16} color={Colors.textInverse} /></View>}
              </View>
            );
          })}
        </View>
        
        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    backgroundColor: Colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: Colors.divider,
  },
  backBtn: {
    padding: Spacing.xs,
    marginRight: Spacing.md,
  },
  headerTitleContainer: {
    flex: 1,
  },
  headerTitle: {
    fontSize: FontSizes.xl,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginBottom: 4,
  },
  headerBadges: {
    flexDirection: 'row',
    gap: Spacing.sm,
  },
  container: {
    flex: 1,
  },
  contentContainer: {
    padding: Spacing.lg,
  },
  summaryCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    marginBottom: Spacing.xl,
    borderWidth: 1,
    borderColor: Colors.primaryLight,
  },
  summaryHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.sm,
    gap: 6,
  },
  summaryTitle: {
    fontSize: FontSizes.md,
    fontWeight: '700',
    color: Colors.primary,
  },
  summaryText: {
    fontSize: FontSizes.md,
    color: Colors.textSecondary,
    lineHeight: 22,
    marginBottom: Spacing.md,
  },
  sopRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    paddingTop: Spacing.md,
    borderTopWidth: 1,
    borderTopColor: Colors.divider,
  },
  sopLabel: {
    fontSize: FontSizes.sm,
    fontWeight: '600',
    color: Colors.textTertiary,
  },
  sectionTitle: {
    fontSize: FontSizes.lg,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginBottom: Spacing.md,
  },
  timelineCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    marginBottom: Spacing.xl,
    borderWidth: 1,
    borderColor: Colors.cardBorder,
  },
  timeline: {
    marginTop: Spacing.sm,
  },
  timelineItem: {
    flexDirection: 'row',
  },
  timelineIndicator: {
    alignItems: 'center',
    marginRight: Spacing.md,
  },
  timelineDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: Colors.primary,
    zIndex: 1,
  },
  timelineLine: {
    width: 2,
    flex: 1,
    backgroundColor: Colors.divider,
    marginTop: -2,
    marginBottom: -2,
  },
  timelineContent: {
    flex: 1,
    paddingBottom: Spacing.lg,
  },
  timelineLabel: {
    fontSize: FontSizes.md,
    fontWeight: '600',
    color: Colors.textPrimary,
    marginTop: -3,
  },
  timelineTime: {
    fontSize: FontSizes.sm,
    color: Colors.textTertiary,
    marginTop: 2,
  },
  thread: {
    marginTop: Spacing.sm,
  },
  messageRow: {
    flexDirection: 'row',
    marginBottom: Spacing.md,
    alignItems: 'flex-end',
  },
  messageRowCustomer: {
    justifyContent: 'flex-start',
  },
  messageRowAi: {
    justifyContent: 'flex-end',
  },
  avatar: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: Colors.surfaceHover,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: Spacing.sm,
  },
  avatarText: {
    fontSize: FontSizes.sm,
    fontWeight: '700',
    color: Colors.textSecondary,
  },
  avatarAi: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: Colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: Spacing.sm,
  },
  messageBubble: {
    maxWidth: '75%',
    padding: Spacing.md,
    borderRadius: BorderRadius.lg,
  },
  messageBubbleCustomer: {
    backgroundColor: Colors.surface,
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: Colors.cardBorder,
  },
  messageBubbleAi: {
    backgroundColor: Colors.primary,
    borderBottomRightRadius: 4,
  },
  messageText: {
    fontSize: FontSizes.md,
    color: Colors.textPrimary,
    lineHeight: 20,
  },
  messageTextAi: {
    color: Colors.textInverse,
  },
  messageTime: {
    fontSize: FontSizes.xs,
    color: Colors.textTertiary,
    alignSelf: 'flex-end',
    marginTop: 4,
  },
  messageTimeAi: {
    color: 'rgba(255,255,255,0.7)',
  },
});
