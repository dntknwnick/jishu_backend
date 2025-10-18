# 📝 Command Reference - React Native CLI

## 🚀 Quick Setup

### Automated Setup
```bash
# Mac/Linux
chmod +x setup-react-native-cli.sh
./setup-react-native-cli.sh

# Windows
setup-react-native-cli.bat
```

---

## 📱 Running the App

### Development

```bash
# Start Metro bundler (keep running in one terminal)
npm start

# Run on iOS (Mac only, in another terminal)
npm run ios

# Run on Android (in another terminal)
npm run android

# Run on specific iOS simulator
npm run ios -- --simulator="iPhone 15 Pro"

# Run on specific Android device
npm run android -- --deviceId=emulator-5554
```

### With Cache Reset

```bash
# Start Metro with cache cleared
npm start -- --reset-cache

# Or
npx react-native start --reset-cache
```

---

## 🧹 Cleaning

### Clear Metro Bundler Cache
```bash
npm start -- --reset-cache
rm -rf /tmp/metro-*
rm -rf /tmp/haste-*
watchman watch-del-all
```

### Clean iOS Build
```bash
# Method 1: Using npm script
npm run clean

# Method 2: Manual iOS clean
cd ios
xcodebuild clean
rm -rf ~/Library/Developer/Xcode/DerivedData
rm -rf Pods Podfile.lock
pod deintegrate
pod install
cd ..
```

### Clean Android Build
```bash
# Method 1: Using npm script  
npm run clean

# Method 2: Manual Android clean
cd android
./gradlew clean
./gradlew cleanBuildCache
cd ..
```

### Nuclear Clean (Everything)
```bash
# Remove everything and start fresh
rm -rf node_modules
rm -rf package-lock.json
rm -rf ios/Pods ios/Podfile.lock
rm -rf android/build android/app/build
rm -rf /tmp/metro-*

# Reinstall
npm install
cd ios && pod install && cd ..
```

---

## 📦 Dependencies

### Install Dependencies
```bash
# Install npm packages
npm install

# Install iOS pods (Mac only)
cd ios
pod install
cd ..

# Or use npm script
npm run pod-install
```

### Add New Package
```bash
# Install package
npm install <package-name>

# Link native dependencies (usually automatic)
# iOS
cd ios && pod install && cd ..

# Android (usually auto-linked)
```

### Update Dependencies
```bash
# Check for updates
npm outdated

# Update all packages
npm update

# Update specific package
npm install <package-name>@latest

# iOS: Update pods
cd ios
pod update
cd ..
```

---

## 🔍 Debugging

### View Logs

```bash
# iOS logs
npx react-native log-ios

# Android logs
npx react-native log-android

# Filtered Android logs
adb logcat *:S ReactNative:V ReactNativeJS:V
```

### Development Menu

**iOS Simulator:**
- Press `Cmd + D` or `Cmd + Ctrl + Z`
- Or: Device → Shake

**Android Emulator:**
- Press `Cmd + M` (Mac) or `Ctrl + M` (Windows/Linux)
- Or: `adb shell input keyevent 82`

**Physical Device:**
- Shake the device

**Menu Options:**
- Reload: Refresh the app
- Debug: Open Chrome DevTools
- Enable Fast Refresh: Auto-reload on save
- Toggle Inspector: Inspect UI elements
- Show Perf Monitor: Performance metrics

---

## 🔨 Building

### Development Builds

```bash
# iOS development build
npm run ios

# Android development build
npm run android
```

### Production Builds

#### Android APK (for testing)
```bash
cd android
./gradlew assembleRelease
cd ..

# Output: android/app/build/outputs/apk/release/app-release.apk
```

#### Android AAB (for Play Store)
```bash
cd android
./gradlew bundleRelease
cd ..

# Output: android/app/build/outputs/bundle/release/app-release.aab
```

#### iOS Archive (for App Store)
```bash
# Open in Xcode
open ios/JishuMobile.xcworkspace

# Then in Xcode:
# 1. Select "Any iOS Device"
# 2. Product → Archive
# 3. Distribute App → App Store Connect
```

---

## 📲 Device Management

### List Devices

```bash
# iOS simulators
xcrun simctl list devices

# Android devices/emulators
adb devices

# List Android emulators
emulator -list-avds
```

### Start Emulator

```bash
# Android emulator
emulator -avd Pixel_5_API_33

# Or from Android Studio:
# Tools → Device Manager → Run
```

### iOS Simulator

```bash
# Open default simulator
open -a Simulator

# Or run directly with:
npm run ios
```

### Physical Device

#### iOS (Mac only)
1. Connect iPhone via USB
2. Trust computer on iPhone
3. Open `ios/JishuMobile.xcworkspace` in Xcode
4. Select your device
5. Click Run (▶️)

#### Android
```bash
# Enable USB debugging on device
# Connect via USB
adb devices  # Should show your device

# Run app
npm run android
```

---

## 🧪 Testing

### Run Tests
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test HomeScreen.test.tsx

# Watch mode
npm test -- --watch
```

### Type Checking
```bash
# Check TypeScript types
npx tsc --noEmit

# Watch mode
npx tsc --noEmit --watch
```

### Linting
```bash
# Run ESLint
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix
```

---

## 🔧 Development Tools

### React Native Doctor
```bash
# Check development environment setup
npx react-native doctor
```

### React Native Info
```bash
# Show environment information
npx react-native info
```

### Port Management
```bash
# Check what's running on port 8081 (Metro)
lsof -i :8081

# Kill process on port 8081
kill -9 $(lsof -t -i:8081)

# Android: Reverse port for Metro
adb reverse tcp:8081 tcp:8081
adb reverse tcp:8097 tcp:8097
```

---

## 🛠️ Native Module Commands

### React Native Vector Icons

```bash
# iOS: Install
cd ios && pod install && cd ..

# Android: Already configured via build.gradle
```

### React Native Linear Gradient

```bash
# iOS: Install
cd ios && pod install && cd ..

# Android: Auto-linked
```

### React Native Gesture Handler

```bash
# Install
npm install react-native-gesture-handler

# iOS
cd ios && pod install && cd ..

# Add to MainActivity.java (already done)
```

---

## 📱 iOS Specific

### Pods Management
```bash
# Install pods
cd ios && pod install && cd ..

# Update pods
cd ios && pod update && cd ..

# Clean pods
cd ios
pod deintegrate
pod cache clean --all
pod install
cd ..
```

### Simulator Commands
```bash
# List simulators
xcrun simctl list devices

# Boot simulator
xcrun simctl boot "iPhone 15 Pro"

# Erase simulator
xcrun simctl erase all

# Reset specific simulator
xcrun simctl erase "iPhone 15 Pro"
```

### Xcode
```bash
# Open workspace
open ios/JishuMobile.xcworkspace

# Clean derived data
rm -rf ~/Library/Developer/Xcode/DerivedData
```

---

## 🤖 Android Specific

### Gradle Commands
```bash
cd android

# Clean
./gradlew clean

# Build debug
./gradlew assembleDebug

# Build release
./gradlew assembleRelease

# Bundle release (AAB)
./gradlew bundleRelease

# List tasks
./gradlew tasks

# Check dependencies
./gradlew app:dependencies

cd ..
```

### ADB Commands
```bash
# List devices
adb devices

# Install APK
adb install android/app/build/outputs/apk/release/app-release.apk

# Uninstall app
adb uninstall com.jishu.app

# Clear app data
adb shell pm clear com.jishu.app

# Open dev menu
adb shell input keyevent 82

# Reverse port
adb reverse tcp:8081 tcp:8081

# View logs
adb logcat

# Restart ADB server
adb kill-server
adb start-server
```

### Emulator Commands
```bash
# List emulators
emulator -list-avds

# Start emulator
emulator -avd Pixel_5_API_33

# Start with wipe data
emulator -avd Pixel_5_API_33 -wipe-data
```

---

## 🔄 Migration Commands

### Run Migration Script
```bash
# Migrate Expo imports to React Native CLI
node scripts/migrate-imports.js

# Or using bash (Mac/Linux)
chmod +x scripts/migrate-imports.sh
./scripts/migrate-imports.sh
```

---

## 📊 Performance

### Enable Hermes
```bash
# Already enabled in android/gradle.properties
# hermesEnabled=true

# Verify Hermes is running (in app):
# Dev menu → Settings → "Hermes Enabled"
```

### Bundle Analysis
```bash
# Generate bundle stats
npx react-native bundle \
  --platform android \
  --dev false \
  --entry-file index.js \
  --bundle-output /tmp/bundle.js \
  --assets-dest /tmp
```

---

## 🎨 Assets

### Link Fonts
```bash
# Add fonts to assets/fonts/
# Update react-native.config.js
# Run:
npx react-native-asset

# iOS: Pods update
cd ios && pod install && cd ..
```

### App Icon

**iOS:**
```bash
# Use Xcode to add icons
# Or replace files in ios/JishuMobile/Images.xcassets/AppIcon.appiconset/
```

**Android:**
```bash
# Replace files in:
# android/app/src/main/res/mipmap-*/ic_launcher.png
```

---

## 🚨 Emergency Commands

### App Won't Build
```bash
# Full clean and reinstall
rm -rf node_modules package-lock.json
rm -rf ios/Pods ios/Podfile.lock
rm -rf android/build android/app/build
npm install
cd ios && pod install && cd ..
npm start -- --reset-cache
```

### Metro Won't Start
```bash
watchman watch-del-all
rm -rf /tmp/metro-*
rm -rf /tmp/haste-*
npm start -- --reset-cache
```

### App Crashes on Launch
```bash
# Check logs
npx react-native log-ios    # or log-android

# Common fixes:
# 1. Clear cache
npm start -- --reset-cache

# 2. Reinstall
rm -rf node_modules && npm install

# 3. Reset simulator/emulator
xcrun simctl erase all      # iOS
adb shell pm clear com.jishu.app  # Android
```

---

## 📚 Useful Aliases

Add to your `.bashrc` or `.zshrc`:

```bash
# React Native shortcuts
alias rn='npx react-native'
alias rni='npm run ios'
alias rna='npm run android'
alias rnl='npx react-native log-ios'
alias rnla='npx react-native log-android'
alias rnc='npm start -- --reset-cache'

# Clean shortcuts
alias rnclean='rm -rf node_modules && npm install'
alias rniosclean='cd ios && pod deintegrate && pod install && cd ..'
alias rnandroidclean='cd android && ./gradlew clean && cd ..'
```

---

## 🎯 Common Workflows

### Daily Development
```bash
# Terminal 1
npm start

# Terminal 2
npm run ios    # or npm run android

# Make changes → Fast Refresh auto-updates
```

### After Pulling New Code
```bash
npm install
cd ios && pod install && cd ..
npm start -- --reset-cache
npm run ios
```

### Before Committing
```bash
npm run lint
npm test
npx tsc --noEmit
```

### Building for Distribution
```bash
# Android
cd android
./gradlew bundleRelease
cd ..

# iOS
open ios/JishuMobile.xcworkspace
# Archive in Xcode
```

---

For more help, see:
- `QUICKSTART.md` - Quick start guide
- `SETUP_GUIDE_CLI.md` - Detailed setup
- `MIGRATION_GUIDE.md` - Migration details
- `README_CLI.md` - Full documentation
