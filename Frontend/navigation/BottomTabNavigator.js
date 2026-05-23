import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '../constants/colors';

import HomeScreen from '../screens/HomeScreen';
import LeadsScreen from '../screens/LeadsScreen';
import EscalationsScreen from '../screens/EscalationsScreen';
import FollowUpsScreen from '../screens/FollowUpsScreen';

const Tab = createBottomTabNavigator();

export default function BottomTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Leads') {
            iconName = focused ? 'people' : 'people-outline';
          } else if (route.name === 'Escalations') {
            iconName = focused ? 'warning' : 'warning-outline';
          } else if (route.name === 'FollowUps') {
            iconName = focused ? 'calendar' : 'calendar-outline';
          }

          return <Ionicons name={iconName} size={24} color={color} />;
        },
        tabBarActiveTintColor: Colors.primary,
        tabBarInactiveTintColor: Colors.textTertiary,
        headerShown: false,
        tabBarStyle: {
          backgroundColor: Colors.surface,
          borderTopColor: Colors.divider,
          borderTopWidth: 1,
          elevation: 0, // Remove shadow on Android
          paddingBottom: 8,
          paddingTop: 8,
          height: 60,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '500',
        },
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Leads" component={LeadsScreen} />
      <Tab.Screen name="Escalations" component={EscalationsScreen} options={{ title: 'Alerts' }} />
      <Tab.Screen name="FollowUps" component={FollowUpsScreen} options={{ title: 'Tasks' }} />
    </Tab.Navigator>
  );
}
