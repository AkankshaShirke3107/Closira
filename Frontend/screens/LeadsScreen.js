import React from 'react';
import { SafeAreaView, FlatList, StyleSheet } from 'react-native';
import Header from '../components/Header';
import LeadCard from '../components/LeadCard';
import EmptyState from '../components/EmptyState';
import { Colors, Spacing } from '../constants/colors';

import leadsData from '../mock/leads.json';

export default function LeadsScreen({ navigation }) {
  const handlePressLead = (lead) => {
    navigation.navigate('ConversationDetail', {
      conversationId: lead.conversationId,
      customerName: lead.customer
    });
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <Header title="All Leads" subtitle="Monitor your inbound pipeline" />
      
      <FlatList
        data={leadsData}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
        renderItem={({ item }) => (
          <LeadCard 
            lead={item} 
            onPress={() => handlePressLead(item)} 
          />
        )}
        ListEmptyComponent={
          <EmptyState 
            icon="people-outline" 
            title="No leads yet" 
            message="When you receive new inquiries across WhatsApp, Email, or Phone, they will appear here." 
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
