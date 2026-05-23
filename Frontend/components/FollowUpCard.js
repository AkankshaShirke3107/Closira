import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors, BorderRadius, FontSizes, Spacing } from '../constants/colors';

export default function FollowUpCard({ task }) {
  const [isDone, setIsDone] = useState(task.isDone);

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <View style={[styles.card, isDone && styles.cardDone]}>
      <View style={styles.leftCol}>
        <TouchableOpacity 
          style={[styles.checkbox, isDone && styles.checkboxDone]} 
          onPress={() => setIsDone(!isDone)}
        >
          {isDone && <Ionicons name="checkmark" size={16} color={Colors.textInverse} />}
        </TouchableOpacity>
      </View>
      <View style={styles.rightCol}>
        <View style={styles.header}>
          <Text style={[styles.customer, isDone && styles.textDone]}>{task.customer}</Text>
          <View style={styles.dueBox}>
            <Ionicons name="time-outline" size={14} color={isDone ? Colors.textTertiary : Colors.primary} />
            <Text style={[styles.dueText, isDone && styles.textDone]}>{formatTime(task.dueAt)}</Text>
          </View>
        </View>
        <Text style={[styles.messagePreview, isDone && styles.textDone]} numberOfLines={2}>
          {task.messagePreview}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    marginBottom: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.cardBorder,
  },
  cardDone: {
    backgroundColor: Colors.surfaceHover,
    opacity: 0.8,
  },
  leftCol: {
    marginRight: Spacing.md,
    justifyContent: 'center',
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: Colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkboxDone: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  rightCol: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.xs,
  },
  customer: {
    fontSize: FontSizes.md,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  dueBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  dueText: {
    fontSize: FontSizes.xs,
    fontWeight: '600',
    color: Colors.primary,
  },
  messagePreview: {
    fontSize: FontSizes.sm,
    color: Colors.textSecondary,
    lineHeight: 18,
  },
  textDone: {
    color: Colors.textTertiary,
    textDecorationLine: 'line-through',
  },
});
