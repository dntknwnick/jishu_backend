# 📱 Jishu Mobile App - React Native CLI

A comprehensive mobile application for exam preparation (NEET, JEE, CET) built with **React Native CLI** (bare bones, no Expo).

## 🚀 Quick Start

### Prerequisites

#### Mac (for iOS development)
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js 18+
brew install node@18

# Install Watchman
brew install watchman

# Install CocoaPods
sudo gem install cocoapods

# Install Xcode from Mac App Store
# Then install Xcode Command Line Tools
xcode-select --install
```

#### Windows/Mac/Linux (for Android development)
```bash
# Install Node.js 18+ from nodejs.org

# Install Java JDK 11+
# Mac:
brew install --cask adoptopenjdk11

# Windows: Download from Oracle or AdoptOpenJDK

# Install Android Studio from developer.android.com
# During installation, make sure to install:
# - Android SDK
# - Android SDK Platform
# - Android Virtual Device
```

### Environment Setup

#### Android SDK Setup
Add to your `~/.bash_profile` or `~/.zshrc`:

```bash
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

### Installation

```bash
# Navigate to mobile directory
cd mobile

# Install dependencies
npm install

# iOS: Install pods (Mac only)
cd ios
pod install
cd ..

# Or use the npm script
npm run pod-install
```

## 🏃 Running the App

### iOS (Mac only)

```bash
# Start Metro bundler
npm start

# In a new terminal, run iOS
npm run ios

# Or specify a device
npm run ios -- --simulator="iPhone 15 Pro"

# List available simulators
xcrun simctl list devices
```

### Android

```bash
# Start Metro bundler
npm start

# In a new terminal, run Android
npm run android

# Or specify a device
npm run android -- --deviceId=emulator-5554

# List connected devices
adb devices
```

### Running on Physical Device

#### iOS
1. Open `ios/JishuMobile.xcworkspace` in Xcode
2. Select your device from the device dropdown
3. Trust your developer account on your iPhone (Settings > General > VPN & Device Management)
4. Click Run (▶️) in Xcode

#### Android
1. Enable Developer Mode on your phone
2. Enable USB Debugging
3. Connect via USB
4. Run: `npm run android`

## 📁 Project Structure

```
mobile/
├── android/                    # Android native code
│   ├── app/
│   │   ├── build.gradle       # App-level Gradle config
│   │   └── src/main/
│   │       ├── AndroidManifest.xml
│   │       └── java/com/jishu/
│   ├── build.gradle           # Project-level Gradle
│   └── gradle.properties      # Gradle properties
│
├── ios/                       # iOS native code
│   ├── JishuMobile/
│   │   ├── Info.plist         # iOS app configuration
│   │   └── AppDelegate.mm     # App entry point
│   ├── JishuMobile.xcodeproj
│   ├── JishuMobile.xcworkspace
│   └── Podfile               # CocoaPods dependencies
│
├── src/
│   ├── components/           # Reusable components
│   │   └── CustomDrawerContent.tsx
│   ├── context/              # React Context
│   │   └── AuthContext.tsx
│   ├── navigation/           # Navigation setup
│   │   ├── AppNavigator.tsx
│   │   ├── AuthNavigator.tsx
│   │   ├── BottomTabNavigator.tsx
│   │   └── MainNavigator.tsx
│   ├── screens/              # Screen components
│   │   ├── auth/
│   │   ├── HomeScreen.tsx
│   │   ├── CoursesScreen.tsx
│   │   ├── TestsScreen.tsx
│   │   ├── CommunityScreen.tsx
│   │   └── ProfileScreen.tsx
│   ├── services/
│   │   └── api.ts            # API integration
│   └── theme/
│       └── index.ts          # Design tokens
│
├── App.tsx                   # Root component
├── index.js                  # Entry point
├── app.json                  # App metadata
├── babel.config.js           # Babel configuration
├── metro.config.js           # Metro bundler config
├── package.json              # Dependencies
└── tsconfig.json             # TypeScript config
```

## 🔧 Key Differences from Expo

### Package Changes

| Feature | Expo | React Native CLI |
|---------|------|------------------|
| **Icons** | `@expo/vector-icons` | `react-native-vector-icons` |
| **Gradient** | `expo-linear-gradient` | `react-native-linear-gradient` |
| **Status Bar** | `expo-status-bar` | Built-in `react-native` |
| **Storage** | `expo-secure-store` | `@react-native-async-storage/async-storage` |

### Import Changes

```typescript
// Icons
// OLD: import { Ionicons } from '@expo/vector-icons';
// NEW: 
import Icon from 'react-native-vector-icons/Ionicons';

// Linear Gradient
// OLD: import { LinearGradient } from 'expo-linear-gradient';
// NEW:
import LinearGradient from 'react-native-linear-gradient';

// Status Bar
// OLD: import { StatusBar } from 'expo-status-bar';
// NEW:
import { StatusBar } from 'react-native';
```

### Usage Changes

```typescript
// Icons
// OLD: <Ionicons name="home" size={24} color="black" />
// NEW:
<Icon name="home" size={24} color="black" />

// Status Bar
// OLD: <StatusBar style="auto" />
// NEW:
<StatusBar barStyle="light-content" backgroundColor="#6366f1" />
```

## 🎨 Features

### ✅ Implemented
- Bottom tab navigation (5 tabs)
- Drawer navigation (hamburger menu)
- Authentication flow (OTP-based)
- Home dashboard with stats
- Course management
- Mock tests interface
- Community posts
- User profile
- API integration with JWT auth

### 🚧 To Be Added
- Push notifications
- Deep linking
- Biometric authentication
- Offline mode
- Image upload/camera
- Analytics tracking

## 🐛 Troubleshooting

### Common Issues

#### 1. Metro Bundler Not Starting
```bash
npm start -- --reset-cache
```

#### 2. iOS Build Failed
```bash
cd ios
pod deintegrate
pod install
cd ..
npm run ios
```

#### 3. Android Gradle Build Failed
```bash
cd android
./gradlew clean
cd ..
npm run android
```

#### 4. Icons Not Showing (iOS)
```bash
cd ios
pod install
cd ..
```

#### 5. Icons Not Showing (Android)
Make sure `android/app/build.gradle` has:
```gradle
apply from: "../../node_modules/react-native-vector-icons/fonts.gradle"
```

#### 6. Linear Gradient Not Working (iOS)
```bash
cd ios
pod install
cd ..
```

#### 7. Multiple Instances of React
```bash
rm -rf node_modules
npm install
```

#### 8. Watchman Warning
```bash
watchman watch-del-all
rm -rf /tmp/metro-*
npm start -- --reset-cache
```

## 📦 Building for Production

### Android APK

```bash
cd android
./gradlew assembleRelease

# Output: android/app/build/outputs/apk/release/app-release.apk
```

### Android AAB (for Play Store)

```bash
cd android
./gradlew bundleRelease

# Output: android/app/build/outputs/bundle/release/app-release.aab
```

### iOS (requires paid Apple Developer account)

1. Open `ios/JishuMobile.xcworkspace` in Xcode
2. Select "Any iOS Device" as destination
3. Product > Archive
4. Distribute App > App Store Connect

## 🔐 Code Signing

### Android

Create `android/app/my-release-key.keystore`:
```bash
cd android/app
keytool -genkeypair -v -storetype PKCS12 -keystore my-release-key.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000
```

Update `android/gradle.properties`:
```properties
MYAPP_RELEASE_STORE_FILE=my-release-key.keystore
MYAPP_RELEASE_KEY_ALIAS=my-key-alias
MYAPP_RELEASE_STORE_PASSWORD=*****
MYAPP_RELEASE_KEY_PASSWORD=*****
```

### iOS

Configure in Xcode:
1. Signing & Capabilities tab
2. Select your team
3. Enable automatic signing

## 📊 Performance Optimization

### Enable Hermes (already enabled)
Check `android/gradle.properties`:
```properties
hermesEnabled=true
```

### Production Build Optimizations
- Enabled Proguard for Android
- Code splitting for larger apps
- Image optimization
- Remove console logs in production

## 🧪 Testing

```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test HomeScreen.test.tsx
```

## 📚 Useful Commands

```bash
# Clean everything and reinstall
npm run clean-install

# Clear Metro cache
npm start -- --reset-cache

# Check React Native setup
npx react-native doctor

# Generate Android debug APK
cd android && ./gradlew assembleDebug && cd ..

# List iOS simulators
xcrun simctl list

# List Android emulators
emulator -list-avds

# Start Android emulator
emulator -avd Pixel_5_API_33

# View Android logs
adb logcat *:S ReactNative:V ReactNativeJS:V

# View iOS logs
npx react-native log-ios
```

## 🔗 Native Modules Integration

### Adding a Native Module

```bash
# Install package
npm install <package-name>

# iOS: Install pods
cd ios && pod install && cd ..

# Android: Usually auto-linked

# Rebuild app
npm run ios  # or npm run android
```

### Manual Linking (if auto-linking fails)

#### iOS
Add to `ios/Podfile`:
```ruby
pod 'PackageName', :path => '../node_modules/package-name'
```

#### Android
Add to `android/settings.gradle`:
```gradle
include ':package-name'
project(':package-name').projectDir = new File(rootProject.projectDir, '../node_modules/package-name/android')
```

## 📖 Documentation References

- [React Native Docs](https://reactnative.dev/)
- [React Navigation](https://reactnavigation.org/)
- [React Native Vector Icons](https://github.com/oblador/react-native-vector-icons)
- [React Native Linear Gradient](https://github.com/react-native-linear-gradient/react-native-linear-gradient)

## 🆘 Support

For issues:
1. Check [React Native Troubleshooting](https://reactnative.dev/docs/troubleshooting)
2. Search [Stack Overflow](https://stackoverflow.com/questions/tagged/react-native)
3. Check GitHub issues for specific packages
4. React Native Discord community

## ✅ Migration Checklist

- [x] Updated package.json dependencies
- [x] Removed Expo packages
- [x] Added React Native CLI packages
- [x] Created metro.config.js
- [x] Updated babel.config.js
- [x] Created Android native project structure
- [x] Created iOS Podfile
- [ ] Replace all `@expo/vector-icons` imports
- [ ] Replace all `expo-linear-gradient` imports
- [ ] Test on iOS device/simulator
- [ ] Test on Android device/emulator
- [ ] Verify all features work
- [ ] Update app icons
- [ ] Configure splash screen
- [ ] Setup push notifications (if needed)
- [ ] Configure deep linking (if needed)

## 🎉 You're Ready!

Your React Native CLI app is configured and ready to run. Start with:

```bash
npm install
npm run pod-install  # Mac only, for iOS
npm start            # Start Metro
npm run ios          # or npm run android
```

Happy coding! 🚀
