# 🚀 Jishu Mobile App - Complete Setup Guide

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
- **Node.js**: v18.0.0 or higher
  ```bash
  node --version  # Should be 18+
  ```
- **npm** or **yarn**: Latest version
  ```bash
  npm --version
  ```
- **Expo CLI**: Latest version
  ```bash
  npm install -g expo-cli
  ```

### Platform-Specific Requirements

#### For iOS Development (Mac only)
- **Xcode**: Latest version from Mac App Store
- **CocoaPods**: Dependency manager
  ```bash
  sudo gem install cocoapods
  ```
- **iOS Simulator**: Included with Xcode

#### For Android Development
- **Android Studio**: Latest version
- **Android SDK**: API Level 33 or higher
- **Android Emulator**: Configured device
- **Java JDK**: Version 11 or higher

---

## 🛠️ Installation Steps

### Step 1: Clone and Navigate

```bash
# Navigate to the mobile directory
cd mobile
```

### Step 2: Install Dependencies

```bash
# Using npm
npm install

# OR using yarn
yarn install
```

This will install all required packages including:
- React Native core
- Expo SDK
- React Navigation
- UI libraries
- All other dependencies

### Step 3: Configure Environment

Create a `.env` file in the `/mobile` directory:

```env
API_BASE_URL=http://localhost:5000
GOOGLE_CLIENT_ID=your_google_client_id_here
```

**Note**: Update the `API_BASE_URL` when deploying to production.

---

## 🏃 Running the App

### Start Development Server

```bash
npm start
# OR
expo start
```

This will open the Expo Developer Tools in your browser at `http://localhost:19002`

### Run on Different Platforms

#### iOS Simulator (Mac only)
```bash
# Option 1: Press 'i' in the terminal after npm start
# Option 2: Run directly
npm run ios
```

**First-time setup:**
```bash
cd ios
pod install
cd ..
expo run:ios
```

#### Android Emulator
```bash
# Option 1: Press 'a' in the terminal after npm start
# Option 2: Run directly
npm run android
```

**First-time setup:**
```bash
expo run:android
```

#### Physical Device (Recommended for Testing)

1. Install **Expo Go** app on your phone:
   - iOS: App Store
   - Android: Google Play Store

2. Scan QR code shown in terminal/browser
3. App will load on your device

#### Web Browser (for quick testing)
```bash
# Press 'w' in terminal after npm start
# OR
npm run web
```

---

## 📱 Testing on Physical Devices

### iOS Device (via Expo Go)

1. Download **Expo Go** from App Store
2. Make sure your phone and computer are on the same WiFi network
3. Open Expo Go app
4. Scan the QR code from your terminal

### Android Device (via Expo Go)

1. Download **Expo Go** from Google Play Store
2. Ensure same WiFi network
3. Scan QR code using Expo Go app

### Over LAN Connection

If same WiFi network:
```bash
expo start --lan
```

If using tunnel (slower but works everywhere):
```bash
expo start --tunnel
```

---

## 🔧 Development Tools

### React Native Debugger

1. Download from: https://github.com/jhen0409/react-native-debugger/releases

2. Start the debugger before launching app

3. In app: Shake device → "Debug"

### Chrome DevTools

1. In terminal after `npm start`, press `j`
2. Opens Chrome debugger
3. View console logs, network requests

### Expo Developer Menu

**iOS**: Shake device or press `Cmd + D`
**Android**: Shake device or press `Cmd + M`

Options:
- Reload app
- Enable Fast Refresh
- Toggle Performance Monitor
- Debug Remote JS

---

## 🎨 Project Structure Overview

```
mobile/
├── App.tsx                     # Root component
├── index.js                    # Entry point
├── app.json                    # Expo configuration
├── package.json                # Dependencies
├── babel.config.js             # Babel config
├── tsconfig.json               # TypeScript config
│
├── src/
│   ├── navigation/             # All navigation logic
│   │   ├── AppNavigator.tsx        # Root navigator
│   │   ├── AuthNavigator.tsx       # Auth screens stack
│   │   ├── MainNavigator.tsx       # Drawer navigation
│   │   └── BottomTabNavigator.tsx  # Bottom tabs
│   │
│   ├── screens/                # All screen components
│   │   ├── auth/                   # Auth screens
│   │   │   ├── WelcomeScreen.tsx
│   │   │   ├── LoginScreen.tsx
│   │   │   ├── RegisterScreen.tsx
│   │   │   └── OTPScreen.tsx
│   │   ├── HomeScreen.tsx          # Dashboard
│   │   ├── CoursesScreen.tsx       # My courses
│   │   ├── TestsScreen.tsx         # Mock tests
│   │   ├── CommunityScreen.tsx     # Community posts
│   │   └── ProfileScreen.tsx       # User profile
│   │
│   ├── components/             # Reusable components
│   │   └── CustomDrawerContent.tsx # Hamburger menu
│   │
│   ├── context/                # React Context
│   │   └── AuthContext.tsx         # Auth state management
│   │
│   ├── services/               # API services
│   │   └── api.ts                  # Axios configuration
│   │
│   └── theme/                  # Design system
│       └── index.ts                # Colors, fonts
│
└── assets/                     # Images, icons, fonts
    ├── icon.png
    ├── splash.png
    └── adaptive-icon.png
```

---

## 🎯 Key Features Implemented

### ✅ Bottom Tab Navigation
- 5 tabs: Home, Courses, Tests, Community, Profile
- Icon-based navigation
- Active/inactive states
- Platform-specific styling

### ✅ Drawer Menu (Hamburger)
- Swipe from left or tap menu icon
- User profile section with stats
- Menu items with icons
- Logout functionality

### ✅ Authentication Flow
- Welcome screen
- Login with OTP
- Registration with OTP
- OTP verification (6-digit)
- Token-based auth

### ✅ Screens
1. **Home/Dashboard**: Stats, quick actions, recent tests
2. **Courses**: My courses with progress bars
3. **Tests**: Available and completed tests
4. **Community**: Posts with likes/comments
5. **Profile**: User info, stats, settings

---

## 🔌 Backend Integration

### API Configuration

File: `src/services/api.ts`

```typescript
const API_BASE_URL = 'http://localhost:5000';
```

**For Physical Device Testing:**

Replace `localhost` with your computer's IP address:

```typescript
// Find your IP: ipconfig (Windows) or ifconfig (Mac/Linux)
const API_BASE_URL = 'http://192.168.1.100:5000';
```

### Authentication Flow

1. User enters email → Request OTP
2. OTP sent to email (backend handles this)
3. User enters OTP → Verify
4. JWT tokens stored in AsyncStorage
5. Tokens auto-refresh on expiry

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. Metro Bundler Issues
```bash
# Clear cache and restart
expo start -c
# OR
npm start -- --reset-cache
```

#### 2. Dependencies Not Installing
```bash
# Clear node_modules and reinstall
rm -rf node_modules
npm install
```

#### 3. iOS Build Errors
```bash
cd ios
pod install --repo-update
cd ..
expo run:ios
```

#### 4. Android Build Errors
```bash
cd android
./gradlew clean
cd ..
expo run:android
```

#### 5. Expo Go Not Connecting
- Ensure same WiFi network
- Disable VPN
- Check firewall settings
- Use tunnel mode: `expo start --tunnel`

#### 6. "Unable to resolve module" Error
```bash
# Install missing peer dependencies
expo install package-name
```

#### 7. TypeScript Errors
```bash
# Ensure TypeScript version matches
npm install --save-dev typescript@5.3.3
```

---

## 📦 Building for Production

### Create Development Build

```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo account
eas login

# Configure build
eas build:configure

# Build for iOS
eas build --platform ios

# Build for Android
eas build --platform android
```

### Create APK for Testing

```bash
# Android APK
eas build -p android --profile preview

# iOS Ad Hoc
eas build -p ios --profile preview
```

---

## 🔐 Security Considerations

### Current Implementation
- JWT tokens stored in AsyncStorage
- Automatic token refresh
- Secure HTTPS connections (production)

### Production Recommendations
1. Use **expo-secure-store** for sensitive data
2. Enable **SSL pinning**
3. Implement **biometric authentication**
4. Add **certificate pinning** for API calls

---

## 🎨 Customization Guide

### Change Primary Color

File: `src/theme/index.ts`

```typescript
export const colors = {
  primary: '#6366f1',  // Change this
  // ...
};
```

### Update App Icon

Replace files:
- `/assets/icon.png` (1024x1024)
- `/assets/adaptive-icon.png` (Android)
- `/assets/splash.png` (Splash screen)

### Modify Bottom Tab Icons

File: `src/navigation/BottomTabNavigator.tsx`

```typescript
tabBarIcon: ({ focused, color, size }) => {
  // Change icon names here
  let iconName = focused ? 'home' : 'home-outline';
  return <Ionicons name={iconName} size={size} color={color} />;
}
```

---

## 📊 Performance Optimization

### Tips for Better Performance

1. **Enable Hermes** (JavaScript engine):
   Already enabled in Expo 50+

2. **Use Production Build** for testing:
   ```bash
   expo start --no-dev --minify
   ```

3. **Optimize Images**:
   - Use WebP format
   - Compress images
   - Use appropriate sizes

4. **Enable Fast Refresh**:
   Already enabled by default

---

## 📚 Useful Commands

```bash
# Start development server
npm start

# Clear cache
npm start -- --clear

# Run on iOS
npm run ios

# Run on Android
npm run android

# Run on Web
npm run web

# Type check
npx tsc

# Lint code
npm run lint

# Install new package
expo install package-name

# Update all packages
expo upgrade

# Check dependencies
npm outdated
```

---

## 🆘 Getting Help

### Resources
- **Expo Documentation**: https://docs.expo.dev/
- **React Native Docs**: https://reactnative.dev/
- **React Navigation**: https://reactnavigation.org/

### Community Support
- Expo Discord: https://chat.expo.dev/
- Stack Overflow: Tag `expo` or `react-native`
- GitHub Issues: Project repository

---

## ✅ Verification Checklist

After setup, verify:

- [ ] App launches on iOS simulator/device
- [ ] App launches on Android emulator/device
- [ ] Navigation works (tabs, drawer, screens)
- [ ] Login flow works (OTP)
- [ ] API calls connect to backend
- [ ] Icons and images load correctly
- [ ] No console errors
- [ ] Fast Refresh works

---

## 🎉 You're All Set!

Your Jishu Mobile App should now be running smoothly!

**Next Steps:**
1. Test all screens and navigation
2. Connect to your backend API
3. Add real data and functionality
4. Test on physical devices
5. Build and deploy!

For any issues, refer to the troubleshooting section or check the main README.md.

Happy Coding! 🚀
