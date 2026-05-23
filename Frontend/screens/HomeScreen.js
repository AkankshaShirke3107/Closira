import React from 'react';
import { SafeAreaView, ScrollView, View, Text, StyleSheet } from 'react-native';
import Header from '../components/Header';
import StatCard from '../components/StatCard';
import ActivityFeedItem from '../components/ActivityFeedItem';
import { Colors, Spacing, FontSizes } from '../constants/colors';

// Import mock data
import dashboardStats from '../mock/dashboardStats.json';
import leadsData from '../mock/leads.json';

export default function HomeScreen() {
  // Use first 3 leads as mock activity feed
  const recentActivity = leadsData.slice(0, 3);

  return (
    <SafeAreaView style={styles.safeArea}>
      <Header title="Dashboard" subtitle="Overview of today's activity" />
      
      <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
        
        {/* Quick Stats Grid */}
        <View style={styles.statsGrid}>
          <View style={styles.statsRow}>
            <StatCard 
              label="New Leads" 
              value={dashboardStats.totalLeadsToday} 
              icon="flash" 
              accentColor={Colors.primary} 
              accentBg={Colors.primaryLight} 
            />
            <View style={{ width: Spacing.md }} />
            <StatCard 
              label="Follow-ups" 
              value={dashboardStats.followUpsDue} 
              icon="calendar" 
              accentColor={Colors.info} 
              accentBg={Colors.statusNewBg} 
            />
          </View>
          <View style={styles.statsRow}>
            <StatCard 
              label="Escalations" 
              value={dashboardStats.openEscalations} 
              icon="warning" 
              accentColor={Colors.error} 
              accentBg={Colors.statusEscalatedBg} 
            />
            <View style={{ width: Spacing.md }} />
            <StatCard 
              label="Missed" 
              value={dashboardStats.missedEnquiries} 
              icon="close-circle" 
              accentColor={Colors.textTertiary} 
              accentBg={Colors.surfaceHover} 
            />
          </View>
        </View>

        {/* Recent Activity Feed */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Activity</Text>
          {recentActivity.map((activity, index) => (
            <ActivityFeedItem key={index} activity={activity} />
          ))}
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
  container: {
    flex: 1,
    paddingHorizontal: Spacing.xl,
  },
  statsGrid: {
    marginTop: Spacing.md,
    marginBottom: Spacing.xl,
  },
  statsRow: {
    flexDirection: 'row',
    marginBottom: Spacing.md,
  },
  section: {
    marginTop: Spacing.sm,
  },
  sectionTitle: {
    fontSize: FontSizes.lg,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginBottom: Spacing.md,
    letterSpacing: -0.3,
  },
});
