# 🎯 START HERE - React Native CLI Setup

## 📍 You Are Here

Your Jishu Mobile App has been converted from **Expo** to **React Native CLI**.

This document will guide you through the complete setup process.

---

## ⚡ Quick Start (Recommended)

### 1. Prerequisites
Make sure you have:
- ✅ **Node.js 18+** installed
- ✅ **CocoaPods** (Mac only, for iOS): `sudo gem install cocoapods`
- ✅ **Android Studio** (for Android development)
- ✅ **Xcode** (Mac only, for iOS development)

### 2. Run Setup Script

**Mac/Linux:**
```bash
cd mobile
chmod +x setup-react-native-cli.sh
./setup-react-native-cli.sh
```

**Windows:**
```cmd
cd mobile
setup-react-native-cli.bat
```

### 3. Run the App

```bash
# iOS (Mac only)
npm run ios

# Android
npm run android
```

**That's it!** 🎉

---

## 📚 Documentation Overview

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **START_HERE.md** | Quick orientation | You're reading it! |
| **QUICKSTART.md** | Fast setup guide | Want to get running ASAP |
| **SETUP_GUIDE_CLI.md** | Detailed setup instructions | Setup script failed |
| **MIGRATION_GUIDE.md** | Expo → RN CLI migration details | Understanding the changes |
| **COMMANDS.md** | All available commands | Daily development |
| **README_CLI.md** | Complete documentation | Full reference |
| **CONVERSION_SUMMARY.md** | What was changed | Overview of conversion |

---

## 🔧 What the Setup Script Does

1. ✅ Checks if Node.js is installed
2. ✅ Checks for CocoaPods (Mac)
3. ✅ Creates iOS and Android native projects
4. ✅ Installs npm dependencies
5. ✅ Migrates Expo imports to React Native CLI
6. ✅ Installs iOS pods (Mac only)
7. ✅ Configures Android for vector icons
8. ✅ Verifies setup

---

## 🎯 Next Steps After Setup

### 1. Verify Everything Works

```bash
# Check environment
npx react-native doctor

# Start Metro bundler
npm start

# In another terminal, run the app
npm run ios    # or npm run android
```

### 2. Test Core Features

Open the app and verify:
- ✅ Navigation works (bottom tabs + drawer)
- ✅ Icons display correctly
- ✅ Gradients render properly
- ✅ Authentication screens work
- ✅ No console errors

### 3. Check What Changed

The main changes from Expo to React Native CLI:

**Icons:**
```typescript
// Before (Expo)
import { Ionicons } from '@expo/vector-icons';
<Ionicons name="home" size={24} />

// After (React Native CLI)
import Icon from 'react-native-vector-icons/Ionicons';
<Icon name="home" size={24} />
```

**Gradients:**
```typescript
// Before (Expo)
import { LinearGradient } from 'expo-linear-gradient';

// After (React Native CLI)
import LinearGradient from 'react-native-linear-gradient';
```

**Status Bar:**
```typescript
// Before (Expo)
import { StatusBar } from 'expo-status-bar';
<StatusBar style="auto" />

// After (React Native CLI)
import { StatusBar } from 'react-native';
<StatusBar barStyle="light-content" />
```

---

## 📁 Project Structure

```
mobile/
├── android/              ← Native Android project
├── ios/                  ← Native iOS project
├── src/
│   ├── components/      ← React components
│   ├── context/         ← React Context (state)
│   ├── navigation/      ← Navigation setup
│   ├── screens/         ← App screens
│   ├── services/        ← API integration
│   └── theme/           ← Design tokens
├── scripts/
│   ├── migrate-imports.js   ← Migration script
│   └── migrate-imports.sh
├── App.tsx              ← Root component
├── index.js             ← Entry point
├── package.json         ← Dependencies
├── metro.config.js      ← Metro bundler config
└── setup-react-native-cli.sh  ← Setup script
```

---

## 🐛 Troubleshooting

### Problem: Setup script fails

**Solution:** Follow manual steps in `QUICKSTART.md`

### Problem: "Unable to resolve module"

**Solution:**
```bash
npm start -- --reset-cache
```

### Problem: Icons not showing

**Solution:**
```bash
# iOS
cd ios && pod install && cd ..

# Android
# Ensure android/app/build.gradle has:
# apply from: "../../node_modules/react-native-vector-icons/fonts.gradle"
```

### Problem: Build errors

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

### Problem: Metro won't start

**Solution:**
```bash
watchman watch-del-all
rm -rf /tmp/metro-*
npm start -- --reset-cache
```

---

## 📖 Common Commands

```bash
# Development
npm start                    # Start Metro bundler
npm run ios                  # Run on iOS
npm run android              # Run on Android
npm start -- --reset-cache   # Clear cache

# Cleaning
npm run clean                # Clean native builds
npm run clean-install        # Full clean + reinstall

# iOS (Mac only)
cd ios && pod install && cd ..   # Install pods

# Android
cd android && ./gradlew clean && cd ..  # Clean build

# Debugging
npx react-native log-ios     # View iOS logs
npx react-native log-android # View Android logs
```

---

## 🎨 Key Features

### ✅ Bottom Tab Navigation
- Home (Dashboard)
- Courses
- Tests
- Community
- Chatbot (AI Study Assistant)

### ✅ Drawer Navigation (Hamburger Menu)
- My Profile (Full profile view)
- Edit Profile
- Account Settings
- Notifications
- Bookmarks
- Help & Support
- About
- Logout

### ✅ Authentication
- Welcome Screen
- Login (OTP)
- Register
- OTP Verification

### ✅ Screens
- **Home:** Stats, quick actions, recent tests
- **Courses:** Enrolled courses with progress
- **Tests:** Available & completed tests
- **Community:** Posts and discussions
- **Profile:** User info and achievements

---

## 🚀 Development Workflow

### Daily Development
```bash
# Terminal 1: Start Metro
npm start

# Terminal 2: Run app
npm run ios    # or npm run android

# Make changes → Fast Refresh auto-updates
```

### Before Committing
```bash
npm run lint       # Check code style
npm test           # Run tests
npx tsc --noEmit   # Check types
```

---

## 🎯 Production Build

### Android APK
```bash
cd android
./gradlew assembleRelease
# Output: android/app/build/outputs/apk/release/app-release.apk
```

### iOS Archive
```bash
open ios/JishuMobile.xcworkspace
# In Xcode: Product → Archive → Distribute
```

---

## 📱 Platform Differences

### iOS (Mac Required)
- ✅ Native build via Xcode
- ✅ CocoaPods for dependencies
- ✅ Runs on Simulator or device
- ✅ Better performance
- ✅ Smoother animations

### Android (All Platforms)
- ✅ Native build via Gradle
- ✅ Auto-linked dependencies
- ✅ Runs on Emulator or device
- ✅ Easier to build/test
- ✅ More device options

---

## 💡 Tips

1. **Use the setup script** - Automates most work
2. **Clear cache often** - Fixes many issues
3. **Check logs** - `npx react-native log-ios/android`
4. **Clean builds** - When in doubt, clean and rebuild
5. **Ask for help** - React Native community is helpful

---

## ✅ Success Checklist

After setup, you should have:

- [ ] `node_modules/` installed
- [ ] `ios/` folder with Xcode project (Mac)
- [ ] `android/` folder with Gradle project
- [ ] `ios/Pods/` installed (Mac)
- [ ] App runs on iOS Simulator (Mac)
- [ ] App runs on Android Emulator
- [ ] Icons display correctly
- [ ] Gradients work
- [ ] Navigation works
- [ ] No console errors

---

## 🆘 Getting Help

### Resources
- **QUICKSTART.md** - Fast setup guide
- **SETUP_GUIDE_CLI.md** - Detailed instructions
- **COMMANDS.md** - Command reference
- **MIGRATION_GUIDE.md** - Migration details

### External Help
- [React Native Docs](https://reactnative.dev/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/react-native)
- [React Native Community](https://github.com/react-native-community)
- [Discord](https://discord.gg/react-native)

---

## 🎯 Current Status

### ✅ Completed
- [x] Package.json updated with RN CLI dependencies
- [x] Babel config updated
- [x] Metro config created
- [x] iOS Podfile created
- [x] Android Gradle configs created
- [x] Migration scripts created
- [x] Setup scripts created
- [x] All documentation created

### ⚠️ Needs Action
- [ ] Run setup script to initialize native projects
- [ ] Install dependencies
- [ ] Run migration script
- [ ] Test on iOS (if Mac)
- [ ] Test on Android
- [ ] Verify all features work

---

## 🚀 Ready to Start?

**Choose your path:**

### Path 1: Automated (Recommended)
```bash
cd mobile
./setup-react-native-cli.sh   # Mac/Linux
# OR
setup-react-native-cli.bat    # Windows
```

### Path 2: Manual
Follow steps in **QUICKSTART.md**

### Path 3: Learn First
Read **SETUP_GUIDE_CLI.md** for detailed understanding

---

## 🎉 Let's Go!

You're all set to start developing with React Native CLI!

**Run this to begin:**
```bash
cd mobile
./setup-react-native-cli.sh
npm run ios  # or npm run android
```

Happy coding! 🚀

---

_Need help? Check the docs listed above or ask in the React Native community!_
