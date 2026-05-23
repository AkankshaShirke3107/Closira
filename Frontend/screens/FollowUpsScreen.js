import React from 'react';
import { SafeAreaView, FlatList, StyleSheet } from 'react-native';
import Header from '../components/Header';
import FollowUpCard from '../components/FollowUpCard';
import EmptyState from '../components/EmptyState';
import { Colors, Spacing } from '../constants/colors';

import followupsData from '../mock/followups.json';

export default function FollowUpsScreen() {
  return (
    <SafeAreaView style={styles.safeArea}>
      <Header title="Follow-ups" subtitle="Tasks scheduled by the AI agent" />
      
      <FlatList
        data={followupsData}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
        renderItem={({ item }) => <FollowUpCard task={item} />}
        ListEmptyComponent={
          <EmptyState 
            icon="calendar-clear-outline" 
            title="No tasks scheduled" 
            message="You have no pending follow-ups today." 
          />
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  listContainer: {
    padding: Spacing.xl,
    paddingTop: Spacing.md,
    paddingBottom: 40,
  },
});
