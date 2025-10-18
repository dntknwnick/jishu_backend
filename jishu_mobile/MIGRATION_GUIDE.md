# 🔄 Migration from Expo to React Native CLI

## Overview
This guide documents the migration from Expo to React Native CLI for the Jishu Mobile App.

## Key Changes

### 1. Package Changes

#### Removed (Expo Dependencies)
- `expo`
- `expo-status-bar`
- `@expo/vector-icons`
- `expo-linear-gradient`
- `expo-haptics`
- `expo-notifications`
- `expo-image-picker`

#### Added (React Native CLI Equivalents)
- `react-native` (bare bones)
- `react-native-vector-icons`
- `react-native-linear-gradient`
- `react-native-haptic-feedback`
- `@react-native-community/netinfo`

### 2. Import Changes

#### Icons
```typescript
// OLD (Expo)
import { Ionicons } from '@expo/vector-icons';
<Ionicons name="home" size={24} color="black" />

// NEW (React Native CLI)
import Icon from 'react-native-vector-icons/Ionicons';
<Icon name="home" size={24} color="black" />
```

#### Linear Gradient
```typescript
// OLD (Expo)
import { LinearGradient } from 'expo-linear-gradient';

// NEW (React Native CLI)
import LinearGradient from 'react-native-linear-gradient';
```

#### Status Bar
```typescript
// OLD (Expo)
import { StatusBar } from 'expo-status-bar';
<StatusBar style="auto" />

// NEW (React Native CLI)
import { StatusBar } from 'react-native';
<StatusBar barStyle="light-content" backgroundColor="#6366f1" />
```

### 3. File Structure Changes

#### Root Files
- `app.json` - Simplified (removed Expo config)
- `babel.config.js` - Updated to use `@react-native/babel-preset`
- `metro.config.js` - Added (required for React Native CLI)
- `index.js` - Simplified entry point

#### Native Folders (New)
- `ios/` - iOS native project
- `android/` - Android native project

### 4. Navigation Changes

No major changes to navigation logic, but removed Expo Router plugin from app.json.

### 5. Asset Handling

#### Images
```typescript
// Both work the same
<Image source={require('./assets/image.png')} />
<Image source={{ uri: 'https://...' }} />
```

#### Fonts
Need to be linked using `react-native.config.js` instead of Expo's font loading.

## Setup Instructions

### Prerequisites
```bash
# Install Watchman (Mac)
brew install watchman

# Install CocoaPods (Mac for iOS)
sudo gem install cocoapods

# Install JDK 11+ (for Android)
brew install --cask adoptopenjdk11
```

### Installation Steps

1. **Install Dependencies**
```bash
cd mobile
npm install
```

2. **iOS Setup (Mac only)**
```bash
cd ios
pod install
cd ..
```

3. **Link Vector Icons (iOS)**
Add to `ios/JishuMobile/Info.plist`:
```xml
<key>UIAppFonts</key>
<array>
  <string>Ionicons.ttf</string>
</array>
```

4. **Link Vector Icons (Android)**
Already configured in `android/app/build.gradle`:
```gradle
apply from: "../../node_modules/react-native-vector-icons/fonts.gradle"
```

### Running the App

#### iOS
```bash
npm run ios
# Or specify device
npm run ios -- --simulator="iPhone 15 Pro"
```

#### Android
```bash
npm run android
# Or specify device
npm run android -- --deviceId=emulator-5554
```

### Development Server
```bash
npm start
# Or with cache clearing
npm start -- --reset-cache
```

## Common Issues & Solutions

### Issue 1: Metro Bundler Cache
```bash
npm start -- --reset-cache
```

### Issue 2: iOS Build Failed
```bash
cd ios
pod deintegrate
pod install
cd ..
npm run ios
```

### Issue 3: Android Gradle Issues
```bash
cd android
./gradlew clean
cd ..
npm run android
```

### Issue 4: Vector Icons Not Showing
```bash
# iOS
cd ios && pod install && cd ..

# Android - Add to android/app/build.gradle
apply from: "../../node_modules/react-native-vector-icons/fonts.gradle"
```

### Issue 5: Linear Gradient Not Working
```bash
# iOS
cd ios && pod install && cd ..

# Android - Should work automatically
```

## File-by-File Changes Required

### All Screen Files
Replace:
```typescript
import { Ionicons } from '@expo/vector-icons';
```
With:
```typescript
import Icon from 'react-native-vector-icons/Ionicons';
```

Then replace all instances of:
```typescript
<Ionicons name="..." />
```
With:
```typescript
<Icon name="..." />
```

### Files with Linear Gradient
Replace:
```typescript
import { LinearGradient } from 'expo-linear-gradient';
```
With:
```typescript
import LinearGradient from 'react-native-linear-gradient';
```

Usage remains the same.

## Scripts Reference

```json
{
  "android": "react-native run-android",
  "ios": "react-native run-ios",
  "start": "react-native start",
  "pod-install": "cd ios && pod install && cd ..",
  "clean": "cd android && ./gradlew clean && cd ..",
  "clean-install": "rm -rf node_modules && npm install && npm run pod-install"
}
```

## Testing Checklist

- [ ] iOS app builds successfully
- [ ] Android app builds successfully
- [ ] All icons display correctly
- [ ] Gradients render properly
- [ ] Navigation works (tabs, drawer, stack)
- [ ] Authentication flow works
- [ ] API calls function correctly
- [ ] Images load properly
- [ ] No console errors

## Performance Improvements

React Native CLI generally provides:
- Faster app launch times
- Better native module integration
- More control over build configuration
- Smaller bundle sizes
- Better debugging tools

## Next Steps

1. Test all features thoroughly
2. Update native configurations as needed
3. Add splash screen
4. Configure app icons
5. Setup push notifications (if needed)
6. Configure deep linking (if needed)
7. Setup code signing for distribution

## Resources

- [React Native CLI Docs](https://reactnative.dev/docs/environment-setup)
- [React Native Vector Icons](https://github.com/oblador/react-native-vector-icons)
- [React Native Linear Gradient](https://github.com/react-native-linear-gradient/react-native-linear-gradient)
- [React Navigation](https://reactnavigation.org/)

## Support

For issues specific to this migration, check:
1. Metro bundler logs
2. Native build logs (Xcode/Android Studio)
3. React Native documentation
4. Stack Overflow with `react-native-cli` tag
