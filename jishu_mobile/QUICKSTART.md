# 🚀 Quick Start Guide - React Native CLI

## One-Command Setup

### Mac/Linux
```bash
cd mobile
chmod +x setup-react-native-cli.sh
./setup-react-native-cli.sh
```

### Windows
```cmd
cd mobile
setup-react-native-cli.bat
```

---

## Manual Step-by-Step (if script fails)

### Step 1: Initialize Native Projects

The easiest way is to use React Native CLI to generate the native folders:

```bash
cd mobile

# Create a temporary project to extract native files
npx react-native init JishuMobileTemp --version 0.73.6

# Copy Android files
cp -r JishuMobileTemp/android ./

# Copy iOS files (Mac only)
cp -r JishuMobileTemp/ios ./

# Clean up
rm -rf JishuMobileTemp
```

### Step 2: Update Package Names

#### Android
Navigate to `android/app/src/main/java/com/` and rename folder structure from `jishumobiletemp` to `jishu/app`.

Update these files with correct package name `com.jishu.app`:
- `android/app/src/main/AndroidManifest.xml`
- `android/app/src/main/java/com/jishu/app/MainActivity.java`
- `android/app/src/main/java/com/jishu/app/MainApplication.java`
- `android/app/build.gradle` (applicationId)

#### iOS (Mac only)
Rename folders:
- `ios/JishuMobileTemp` → `ios/JishuMobile`
- `ios/JishuMobileTemp.xcodeproj` → `ios/JishuMobile.xcodeproj`
- `ios/JishuMobileTempTests` → `ios/JishuMobileTests`

Update references in:
- `ios/JishuMobile.xcodeproj/project.pbxproj`
- `ios/JishuMobile/Info.plist`

### Step 3: Install Dependencies

```bash
npm install
```

### Step 4: Run Migration Script

```bash
# This updates all Expo imports to React Native CLI equivalents
node scripts/migrate-imports.js
```

### Step 5: iOS Setup (Mac only)

```bash
cd ios
pod install
cd ..
```

### Step 6: Configure Android

Add to `android/app/build.gradle` at the bottom:

```gradle
apply from: "../../node_modules/react-native-vector-icons/fonts.gradle"
```

### Step 7: Run the App

#### iOS (Mac only)
```bash
npm run ios
```

#### Android
```bash
npm run android
```

---

## Alternative: Use Official React Native CLI

If you prefer to start completely fresh:

```bash
# From parent directory (not mobile/)
cd ..

# Initialize new React Native project
npx react-native init JishuMobile --version 0.73.6 --template react-native-template-typescript

# Copy your source code
cp -r mobile/src JishuMobile/
cp -r mobile/package.json JishuMobile/package.json

# Merge dependencies manually in package.json
cd JishuMobile

# Install dependencies
npm install

# Run migration script
node ../mobile/scripts/migrate-imports.js

# iOS setup
cd ios && pod install && cd ..

# Run app
npm run ios  # or npm run android
```

---

## Verification

After setup, verify everything works:

### 1. Check Environment
```bash
npx react-native doctor
```

Should show:
- ✅ Node.js
- ✅ Android SDK (for Android)
- ✅ Xcode (for iOS on Mac)
- ✅ CocoaPods (for iOS on Mac)

### 2. Start Metro Bundler
```bash
npm start
```

Should start without errors.

### 3. Run iOS (Mac)
```bash
npm run ios
```

Should:
- Build successfully
- Launch iOS Simulator
- Show the app without errors

### 4. Run Android
```bash
npm run android
```

Should:
- Build successfully
- Launch Android Emulator (or connect to device)
- Show the app without errors

---

## Common Issues

### Issue: "Unable to resolve module"
**Solution:**
```bash
npm start -- --reset-cache
```

### Issue: Icons not showing
**Solution:**
```bash
# iOS
cd ios && pod install && cd ..

# Android - Add to android/app/build.gradle:
apply from: "../../node_modules/react-native-vector-icons/fonts.gradle"
```

### Issue: Build failed
**Solution:**
```bash
# Clean everything
rm -rf node_modules
rm -rf ios/Pods ios/Podfile.lock
rm -rf android/build android/app/build

# Reinstall
npm install
cd ios && pod install && cd ..

# Try again
npm run ios  # or npm run android
```

### Issue: Metro bundler issues
**Solution:**
```bash
# Clear all caches
watchman watch-del-all
rm -rf /tmp/metro-*
rm -rf /tmp/haste-*
npm start -- --reset-cache
```

### Issue: Xcode build failed (Mac)
**Solution:**
```bash
# Clean Xcode
cd ios
xcodebuild clean
rm -rf ~/Library/Developer/Xcode/DerivedData
cd ..

# Reinstall pods
cd ios && pod install && cd ..

# Try again
npm run ios
```

### Issue: Android Gradle failed
**Solution:**
```bash
cd android
./gradlew clean
./gradlew cleanBuildCache
cd ..
npm run android
```

---

## What the Setup Does

1. **Checks Prerequisites**: Node.js, CocoaPods (Mac)
2. **Creates Native Projects**: Generates ios/ and android/ folders
3. **Installs Dependencies**: npm install
4. **Migrates Imports**: Replaces Expo packages with React Native equivalents
5. **Links Native Modules**: Vector icons, linear gradient, etc.
6. **Configures Build**: Updates Gradle and Podfile

---

## Next Steps After Setup

1. **Test Navigation**: Ensure all tabs and drawer work
2. **Test Features**: Login, courses, tests, community, profile
3. **Check API**: Ensure backend connectivity works
4. **Update Icons**: Replace default app icons
5. **Add Splash Screen**: Configure launch screen
6. **Production Build**: Test release builds

---

## Need Help?

1. Check `SETUP_GUIDE_CLI.md` for detailed instructions
2. Check `MIGRATION_GUIDE.md` for migration details
3. Check `TROUBLESHOOTING.md` (if it exists)
4. Search [React Native Docs](https://reactnative.dev/docs/troubleshooting)
5. Ask on [Stack Overflow](https://stackoverflow.com/questions/tagged/react-native)

---

## Success Checklist

After running setup, you should have:

- [x] `node_modules/` installed
- [x] `ios/` folder with Xcode project
- [x] `android/` folder with Gradle project
- [x] `ios/Pods/` installed (Mac only)
- [x] All imports updated (no `@expo/` imports)
- [x] App runs on iOS Simulator (Mac)
- [x] App runs on Android Emulator
- [x] No build errors
- [x] Icons display correctly
- [x] Gradients work
- [x] Navigation works

---

**You're ready to develop! 🎉**

Run `npm run ios` or `npm run android` to start!
