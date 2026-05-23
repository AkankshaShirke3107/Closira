import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import BottomTabNavigator from './BottomTabNavigator';
import ConversationDetailScreen from '../screens/ConversationDetailScreen';

const Stack = createNativeStackNavigator();

export default function AppNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {/* Main Tabs */}
        <Stack.Screen name="MainTabs" component={BottomTabNavigator} />
        
        {/* Stack Screens */}
        <Stack.Screen 
          name="ConversationDetail" 
          component={ConversationDetailScreen} 
          options={{
            presentation: 'card',
            animation: 'slide_from_right'
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
