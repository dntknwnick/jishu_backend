#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Jishu Mobile - React Native CLI Setup${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check if we're in the mobile directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: Please run this script from the /mobile directory${NC}"
    exit 1
fi

# Step 1: Check prerequisites
echo -e "${YELLOW}📋 Step 1: Checking prerequisites...${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+${NC}"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}❌ Node.js version must be 18 or higher. Current: $(node -v)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js $(node -v) detected${NC}"

if command -v pod &> /dev/null; then
    echo -e "${GREEN}✅ CocoaPods detected (for iOS)${NC}"
    IOS_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  CocoaPods not found. iOS build will not be available.${NC}"
    IOS_AVAILABLE=false
fi

# Step 2: Initialize React Native project (creates native folders)
echo ""
echo -e "${YELLOW}📱 Step 2: Initializing React Native project...${NC}"
echo -e "${BLUE}This will create the ios/ and android/ native directories${NC}"

# Create a temporary project to extract native files
TEMP_DIR="JishuTemp"

if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

echo -e "${BLUE}Creating temporary React Native project...${NC}"
npx react-native init $TEMP_DIR --version 0.73.6 --skip-install

# Copy native directories if they don't exist
if [ ! -d "ios/JishuMobile.xcodeproj" ] || [ ! -d "android/app/src" ]; then
    echo -e "${BLUE}Copying native project files...${NC}"
    
    # Copy and rename Android files
    if [ ! -d "android/app/src" ]; then
        cp -R "$TEMP_DIR/android" ./ 2>/dev/null || true
        
        # Update package name in Android files
        find android -type f -name "*.java" -exec sed -i.bak 's/com.jishutemp/com.jishu.app/g' {} \;
        find android -type f -name "*.xml" -exec sed -i.bak 's/com.jishutemp/com.jishu.app/g' {} \;
        find android -type f -name "*.gradle" -exec sed -i.bak 's/com.jishutemp/com.jishu.app/g' {} \;
        find android -name "*.bak" -delete
        
        # Move package structure
        if [ -d "android/app/src/main/java/com/jishutemp" ]; then
            mkdir -p android/app/src/main/java/com/jishu/app
            mv android/app/src/main/java/com/jishutemp/* android/app/src/main/java/com/jishu/app/ 2>/dev/null || true
            rm -rf android/app/src/main/java/com/jishutemp
        fi
    fi
    
    # Copy and rename iOS files
    if [ ! -d "ios/JishuMobile.xcodeproj" ]; then
        cp -R "$TEMP_DIR/ios" ./ 2>/dev/null || true
        
        # Rename iOS project
        if [ -d "ios/$TEMP_DIR" ]; then
            mv "ios/$TEMP_DIR" "ios/JishuMobile" 2>/dev/null || true
        fi
        if [ -d "ios/${TEMP_DIR}.xcodeproj" ]; then
            mv "ios/${TEMP_DIR}.xcodeproj" "ios/JishuMobile.xcodeproj" 2>/dev/null || true
        fi
        if [ -d "ios/${TEMP_DIR}.xcworkspace" ]; then
            mv "ios/${TEMP_DIR}.xcworkspace" "ios/JishuMobile.xcworkspace" 2>/dev/null || true
        fi
        if [ -d "ios/${TEMP_DIR}Tests" ]; then
            mv "ios/${TEMP_DIR}Tests" "ios/JishuMobileTests" 2>/dev/null || true
        fi
        
        # Update references in iOS files
        find ios -type f \( -name "*.pbxproj" -o -name "*.plist" -o -name "*.m" -o -name "*.h" \) -exec sed -i.bak "s/$TEMP_DIR/JishuMobile/g" {} \;
        find ios -name "*.bak" -delete
    fi
fi

# Clean up temp directory
rm -rf "$TEMP_DIR"

echo -e "${GREEN}✅ Native project structure created${NC}"

# Step 3: Install dependencies
echo ""
echo -e "${YELLOW}📦 Step 3: Installing dependencies...${NC}"
npm install

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 4: Run migration script
echo ""
echo -e "${YELLOW}🔄 Step 4: Migrating Expo imports to React Native CLI...${NC}"

if [ -f "scripts/migrate-imports.js" ]; then
    node scripts/migrate-imports.js
    echo -e "${GREEN}✅ Import migration complete${NC}"
else
    echo -e "${YELLOW}⚠️  Migration script not found, skipping...${NC}"
fi

# Step 5: Install iOS pods (if on Mac)
if [ "$IOS_AVAILABLE" = true ]; then
    echo ""
    echo -e "${YELLOW}🍎 Step 5: Installing iOS CocoaPods...${NC}"
    cd ios
    pod install
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ iOS pods installed${NC}"
    else
        echo -e "${RED}❌ Failed to install iOS pods${NC}"
    fi
    cd ..
else
    echo ""
    echo -e "${YELLOW}⚠️  Step 5: Skipping iOS setup (CocoaPods not available)${NC}"
fi

# Step 6: Configure Android for vector icons
echo ""
echo -e "${YELLOW}🤖 Step 6: Configuring Android...${NC}"

# Ensure vector icons are linked in Android build.gradle
if ! grep -q "react-native-vector-icons" android/app/build.gradle; then
    echo "" >> android/app/build.gradle
    echo "apply from: \"../../node_modules/react-native-vector-icons/fonts.gradle\"" >> android/app/build.gradle
    echo -e "${GREEN}✅ Added vector icons to Android build.gradle${NC}"
else
    echo -e "${GREEN}✅ Vector icons already configured in Android${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  ✅ Setup Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo -e "  ${YELLOW}To run on iOS (Mac only):${NC}"
echo -e "  npm run ios"
echo ""
echo -e "  ${YELLOW}To run on Android:${NC}"
echo -e "  npm run android"
echo ""
echo -e "  ${YELLOW}To start Metro bundler:${NC}"
echo -e "  npm start"
echo ""
echo -e "${BLUE}Troubleshooting:${NC}"
echo -e "  - Clear cache: ${YELLOW}npm start -- --reset-cache${NC}"
echo -e "  - Clean build: ${YELLOW}npm run clean${NC}"
echo -e "  - Reinstall: ${YELLOW}npm run clean-install${NC}"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
echo ""
