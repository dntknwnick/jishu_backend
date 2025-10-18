import { MD3LightTheme } from 'react-native-paper';

export const theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: '#6366f1',
    secondary: '#8b5cf6',
    error: '#ef4444',
    background: '#f9fafb',
    surface: '#ffffff',
    text: '#1f2937',
  },
};

export const colors = {
  primary: '#6366f1',
  secondary: '#8b5cf6',
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#06b6d4',
  
  background: '#f9fafb',
  surface: '#ffffff',
  text: '#1f2937',
  textSecondary: '#6b7280',
  textTertiary: '#9ca3af',
  
  border: '#e5e7eb',
  divider: '#f3f4f6',
  
  gradient: {
    primary: ['#6366f1', '#8b5cf6'],
    success: ['#10b981', '#059669'],
    warning: ['#f59e0b', '#f97316'],
  },
};
