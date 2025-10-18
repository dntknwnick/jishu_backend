import React, { useEffect, useState } from 'react';
import { StatusBar } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import AppNavigator from './src/navigation/AppNavigator';
import { AuthProvider } from './src/context/AuthContext';
import AsyncStorage from '@react-native-async-storage/async-storage';

const App = () => {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Check for existing auth token
    const checkAuth = async () => {
      try {
        const token = await AsyncStorage.getItem('access_token');
        console.log('Token exists:', !!token);
      } catch (error) {
        console.error('Error checking auth:', error);
      } finally {
        setIsReady(true);
      }
    };

    checkAuth();
  }, []);

  if (!isReady) {
    return null; // Can add a splash screen component here
  }

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <AuthProvider>
        <NavigationContainer>
          <AppNavigator />
          <StatusBar barStyle="light-content" backgroundColor="#6366f1" />
        </NavigationContainer>
      </AuthProvider>
    </GestureHandlerRootView>
  );
};

export default App;
