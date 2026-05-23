import React from 'react';
import { SafeAreaView, FlatList, StyleSheet } from 'react-native';
import Header from '../components/Header';
import EscalationCard from '../components/EscalationCard';
import EmptyState from '../components/EmptyState';
import { Colors, Spacing } from '../constants/colors';

import escalationsData from '../mock/escalations.json';

export default function EscalationsScreen({ navigation }) {
  const handlePressEscalation = (escalation) => {
    navigation.navigate('ConversationDetail', {
      conversationId: escalation.conversationId,
      customerName: escalation.customer
    });
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <Header title="Action Required" subtitle="Urgent escalations from your AI agent" />
      
      <FlatList
        data={escalationsData}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
        renderItem={({ item }) => (
          <EscalationCard 
            escalation={item} 
            onPress={() => handlePressEscalation(item)} 
          />
        )}
        ListEmptyComponent={
          <EmptyState 
            icon="checkmark-done-circle-outline" 
            title="All clear" 
            message="There are no active escalations right now. Great job keeping customers happy!" 
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
