# 🚀 Complete Setup Guide - React Native CLI

## Step-by-Step Migration & Setup

### Phase 1: Prerequisites Installation

#### For macOS (iOS + Android)

```bash
# 1. Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install Node.js 18+
brew install node@18

# 3. Install Watchman (improves performance)
brew install watchman

# 4. Install CocoaPods (for iOS)
sudo gem install cocoapods

# 5. Install Java JDK 11 (for Android)
brew install --cask adoptopenjdk11

# 6. Install Xcode from Mac App Store
# After installation, install Command Line Tools:
xcode-select --install

# 7. Install Android Studio from https://developer.android.com/studio
```

#### For Windows (Android only)

```powershell
# 1. Install Node.js 18+ from https://nodejs.org/

# 2. Install Java JDK 11 from https://adoptium.net/

# 3. Install Android Studio from https://developer.android.com/studio

# 4. Set environment variables:
# Add to System Environment Variables:
ANDROID_HOME = C:\Users\YourUsername\AppData\Local\Android\Sdk
Path += %ANDROID_HOME%\platform-tools
Path += %ANDROID_HOME%\emulator
Path += %ANDROID_HOME%\tools
Path += %ANDROID_HOME%\tools\bin
```

#### For Linux (Android only)

```bash
# 1. Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 2. Install Java JDK 11
sudo apt install openjdk-11-jdk

# 3. Download and install Android Studio from https://developer.android.com/studio

# 4. Add to ~/.bashrc or ~/.zshrc:
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

---

### Phase 2: Android Studio Setup

1. **Open Android Studio**
2. **Configure SDK:**
   - Tools → SDK Manager
   - SDK Platforms: Install Android 13 (Tiramisu) - API Level 33
   - SDK Tools: Install:
     - Android SDK Build-Tools
     - Android Emulator
     - Android SDK Platform-Tools
     - Intel x86 Emulator Accelerator (HAXM) - for Intel CPUs

3. **Create Virtual Device:**
   - Tools → Device Manager
   - Create Device → Pixel 5
   - Download Android 13 system image
   - Finish and launch emulator

---

### Phase 3: Xcode Setup (Mac only)

1. **Open Xcode**
2. **Install Additional Components** (if prompted)
3. **Configure Simulator:**
   - Xcode → Preferences → Components
   - Download iOS 17 Simulator
4. **Accept License:**
   ```bash
   sudo xcodebuild -license accept
   ```

---

### Phase 4: Project Setup

#### Step 1: Navigate to Mobile Directory
```bash
cd mobile
```

#### Step 2: Run Migration Script
```bash
# Make the migration script executable (Mac/Linux)
chmod +x scripts/migrate-imports.sh
chmod +x scripts/migrate-imports.js

# Run the Node.js migration script (works on all platforms)
node scripts/migrate-imports.js
```

This script will:
- Replace `@expo/vector-icons` with `react-native-vector-icons`
- Replace `expo-linear-gradient` with `react-native-linear-gradient`
- Replace `expo-status-bar` with native StatusBar
- Fix TypeScript type references

#### Step 3: Install Dependencies
```bash
npm install
```

#### Step 4: iOS Setup (Mac only)
```bash
cd ios
pod install
cd ..

# Or use npm script
npm run pod-install
```

#### Step 5: Verify Installation
```bash
# Check React Native setup
npx react-native doctor

# Should show all green checkmarks for your platform
```

---

### Phase 5: Running the App

#### Option A: iOS (Mac only)

```bash
# Terminal 1: Start Metro bundler
npm start

# Terminal 2: Run iOS
npm run ios

# Or specify device
npm run ios -- --simulator="iPhone 15 Pro"

# List available simulators
xcrun simctl list devices available
```

#### Option B: Android

```bash
# Start Android Emulator first (from Android Studio or command line)
emulator -avd Pixel_5_API_33

# Terminal 1: Start Metro bundler
npm start

# Terminal 2: Run Android
npm run android

# Or specify device
adb devices  # Get device ID
npm run android -- --deviceId=emulator-5554
```

#### Option C: Physical Device

**iOS:**
1. Connect iPhone via USB
2. Open `ios/JishuMobile.xcworkspace` in Xcode
3. Select your device from dropdown
4. Click Run (▶️)
5. Trust developer certificate on iPhone:
   - Settings → General → VPN & Device Management

**Android:**
1. Enable Developer Options on phone:
   - Settings → About Phone → Tap "Build Number" 7 times
2. Enable USB Debugging:
   - Settings → Developer Options → USB Debugging
3. Connect via USB
4. Run: `npm run android`

---

### Phase 6: Verification Checklist

Test all features to ensure migration was successful:

#### Navigation
- [ ] Bottom tabs work (Home, Courses, Tests, Community, Profile)
- [ ] Drawer menu opens from hamburger icon
- [ ] All screens navigate correctly
- [ ] Back button works properly

#### UI Components
- [ ] All icons display correctly
- [ ] Gradients render properly
- [ ] Colors and styling are correct
- [ ] Images load properly

#### Authentication
- [ ] Welcome screen displays
- [ ] Login screen works
- [ ] Register screen works
- [ ] OTP input works
- [ ] Authentication state persists

#### Functionality
- [ ] API calls work
- [ ] Data fetches correctly
- [ ] Forms submit properly
- [ ] No console errors
- [ ] App doesn't crash

---

### Phase 7: Troubleshooting

#### Issue 1: Metro Bundler Won't Start
```bash
# Clear cache
npm start -- --reset-cache

# Or
rm -rf node_modules
rm -rf /tmp/metro-*
npm install
npm start
```

#### Issue 2: iOS Build Failed
```bash
# Clean iOS build
cd ios
rm -rf Pods Podfile.lock
pod cache clean --all
pod deintegrate
pod install
cd ..

# Clean Xcode derived data
rm -rf ~/Library/Developer/Xcode/DerivedData

# Rebuild
npm run ios
```

#### Issue 3: Android Build Failed
```bash
# Clean Android build
cd android
./gradlew clean
./gradlew cleanBuildCache
cd ..

# Clear Gradle cache
rm -rf ~/.gradle/caches/

# Rebuild
npm run android
```

#### Issue 4: Icons Not Showing

**iOS:**
```bash
cd ios
pod install
cd ..
npm run ios
```

**Android:**
Verify `android/app/build.gradle` has:
```gradle
apply from: "../../node_modules/react-native-vector-icons/fonts.gradle"
```

#### Issue 5: Linear Gradient Not Working

**iOS:**
```bash
cd ios
pod install
cd ..
```

**Android:**
Should auto-link. If not, check `android/settings.gradle`.

#### Issue 6: "Unable to boot simulator"
```bash
# Reset iOS Simulators
xcrun simctl erase all

# Or manually in Simulator app:
# Device → Erase All Content and Settings
```

#### Issue 7: Android SDK Not Found
```bash
# Check environment variables
echo $ANDROID_HOME  # Should show path to Android SDK

# If empty, add to ~/.zshrc or ~/.bash_profile:
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools

# Reload shell
source ~/.zshrc  # or source ~/.bash_profile
```

---

### Phase 8: Native Module Configuration

#### React Native Vector Icons

**iOS:**
Already configured in Podfile. Just run:
```bash
cd ios && pod install && cd ..
```

**Android:**
Already configured in `app/build.gradle`:
```gradle
apply from: "../../node_modules/react-native-vector-icons/fonts.gradle"
```

#### React Native Linear Gradient

**iOS:**
Already configured in Podfile. Just run:
```bash
cd ios && pod install && cd ..
```

**Android:**
Auto-linked, no configuration needed.

#### React Native Gesture Handler

**iOS:**
```bash
cd ios && pod install && cd ..
```

**Android:**
Already configured in `MainActivity.java`.

#### React Native Reanimated

**iOS:**
```bash
cd ios && pod install && cd ..
```

**Android:**
Already configured in `babel.config.js`.

---

### Phase 9: App Icons & Splash Screen

#### iOS App Icon
1. Create app icons: Use https://appicon.co/
2. Replace `ios/JishuMobile/Images.xcassets/AppIcon.appiconset/`
3. Rebuild: `npm run ios`

#### Android App Icon
1. Create icons for multiple densities
2. Replace files in `android/app/src/main/res/mipmap-*/`
3. Rebuild: `npm run android`

#### Splash Screen
Install `react-native-splash-screen`:
```bash
npm install react-native-splash-screen
cd ios && pod install && cd ..
```

---

### Phase 10: Build for Production

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

#### iOS (for TestFlight/App Store)
1. Open `ios/JishuMobile.xcworkspace` in Xcode
2. Select "Any iOS Device" or your connected device
3. Product → Archive
4. Distribute App → App Store Connect
5. Upload

---

### Phase 11: Useful Commands

```bash
# Development
npm start                           # Start Metro
npm run ios                         # Run iOS app
npm run android                     # Run Android app
npm start -- --reset-cache          # Clear Metro cache

# Cleaning
npm run clean                       # Clean native builds
npm run clean-install               # Clean and reinstall everything
rm -rf node_modules package-lock.json npm install

# iOS
cd ios && pod install && cd ..      # Install/update pods
npm run pod-install                 # Same as above (npm script)
xcrun simctl list devices           # List iOS simulators
xcrun simctl erase all              # Reset all simulators

# Android
adb devices                         # List connected devices
adb reverse tcp:8081 tcp:8081       # Reverse port for Metro
adb shell input keyevent 82         # Open dev menu on device
./gradlew clean                     # Clean Android build (in android/)

# Debugging
npx react-native log-ios            # View iOS logs
npx react-native log-android        # View Android logs
adb logcat *:S ReactNative:V        # Android logs (filtered)

# Utilities
npx react-native doctor             # Check environment setup
npx react-native info               # Show environment info
npm outdated                        # Check for updates
```

---

### Phase 12: Environment Variables

Create `.env` file in `/mobile`:

```env
API_BASE_URL=http://localhost:5000
API_TIMEOUT=30000
```

For different environments:
```env
# .env.development
API_BASE_URL=http://localhost:5000

# .env.production
API_BASE_URL=https://api.jishu.com
```

Install `react-native-config`:
```bash
npm install react-native-config
cd ios && pod install && cd ..
```

---

### Phase 13: Performance Monitoring

#### Enable Hermes
Already enabled in `android/gradle.properties`:
```properties
hermesEnabled=true
```

#### Flipper (debugging tool)
Already configured. Open Flipper app to debug:
- Network requests
- Redux state
- Logs
- React DevTools

---

### Phase 14: Code Signing (Production)

#### Android

**Generate keystore:**
```bash
cd android/app
keytool -genkeypair -v -storetype PKCS12 \
  -keystore jishu-release.keystore \
  -alias jishu-key \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000
```

**Update `android/gradle.properties`:**
```properties
MYAPP_RELEASE_STORE_FILE=jishu-release.keystore
MYAPP_RELEASE_KEY_ALIAS=jishu-key
MYAPP_RELEASE_STORE_PASSWORD=YOUR_PASSWORD
MYAPP_RELEASE_KEY_PASSWORD=YOUR_PASSWORD
```

#### iOS

Configure in Xcode:
1. Select project in navigator
2. Signing & Capabilities
3. Select your team
4. Enable "Automatically manage signing"

---

## 🎉 Setup Complete!

Your React Native CLI app is now ready for development and production!

### Final Verification
```bash
# Check everything is working
npx react-native doctor

# Run on iOS
npm run ios

# Run on Android
npm run android
```

### Next Steps
1. Test all app features
2. Add splash screen
3. Configure push notifications (if needed)
4. Setup crash reporting (Sentry, Firebase Crashlytics)
5. Configure analytics
6. Submit to App Store/Play Store

For any issues, refer to:
- [React Native Docs](https://reactnative.dev/)
- [Troubleshooting Guide](https://reactnative.dev/docs/troubleshooting)
- MIGRATION_GUIDE.md in this directory

Happy coding! 🚀
