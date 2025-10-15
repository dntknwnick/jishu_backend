// Environment Configuration for Frontend
// Centralized configuration for API URLs and environment settings

interface EnvironmentConfig {
  API_BASE_URL: string;
  NODE_ENV: string;
  IS_PRODUCTION: boolean;
  IS_DEVELOPMENT: boolean;
  BYPASS_PURCHASE_VALIDATION: boolean;
  LOCAL_DEV_MODE: boolean;
  DEV_MODE: boolean;
}

// Get environment variables with fallbacks
const getEnvVar = (key: string, defaultValue: string = ''): string => {
  // In Vite, environment variables are prefixed with VITE_
  return import.meta.env[`VITE_${key}`] || defaultValue;
};

const getBooleanEnvVar = (key: string, defaultValue: boolean = false): boolean => {
  const value = getEnvVar(key, defaultValue.toString());
  return value.toLowerCase() === 'true';
};

// Environment configuration
export const config: EnvironmentConfig = {
  // API Configuration
  API_BASE_URL: getEnvVar('API_BASE_URL', 'http://localhost:5000'),
  
  // Environment
  NODE_ENV: getEnvVar('NODE_ENV', 'development'),
  
  // Environment checks
  IS_PRODUCTION: getEnvVar('NODE_ENV', 'development').toLowerCase() === 'production',
  IS_DEVELOPMENT: ['development', 'local'].includes(getEnvVar('NODE_ENV', 'development').toLowerCase()),
  
  // Purchase flow configuration
  BYPASS_PURCHASE_VALIDATION: getBooleanEnvVar('BYPASS_PURCHASE_VALIDATION', true),
  LOCAL_DEV_MODE: getBooleanEnvVar('LOCAL_DEV_MODE', true),
  DEV_MODE: getBooleanEnvVar('DEV_MODE', true),
};

// Export individual values for convenience
export const {
  API_BASE_URL,
  NODE_ENV,
  IS_PRODUCTION,
  IS_DEVELOPMENT,
  BYPASS_PURCHASE_VALIDATION,
  LOCAL_DEV_MODE,
  DEV_MODE,
} = config;

// Debug logging in development
if (IS_DEVELOPMENT) {
  console.log('🔧 Environment Configuration:', {
    API_BASE_URL,
    NODE_ENV,
    IS_PRODUCTION,
    IS_DEVELOPMENT,
    BYPASS_PURCHASE_VALIDATION,
    LOCAL_DEV_MODE,
    DEV_MODE,
  });
}

export default config;
