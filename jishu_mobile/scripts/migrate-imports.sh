#!/bin/bash

# Migration script to replace Expo imports with React Native CLI equivalents

echo "🔄 Starting migration from Expo to React Native CLI..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to replace in file
replace_in_file() {
    local file=$1
    local search=$2
    local replace=$3
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|${search}|${replace}|g" "$file"
    else
        # Linux
        sed -i "s|${search}|${replace}|g" "$file"
    fi
}

# Find all TypeScript files in src directory
FILES=$(find src -name "*.tsx" -o -name "*.ts")

echo -e "${YELLOW}📝 Replacing @expo/vector-icons with react-native-vector-icons...${NC}"

for file in $FILES; do
    if grep -q "@expo/vector-icons" "$file"; then
        echo "  ✓ Updating $file"
        replace_in_file "$file" "import { Ionicons } from '@expo/vector-icons';" "import Icon from 'react-native-vector-icons/Ionicons';"
        replace_in_file "$file" "<Ionicons " "<Icon "
        replace_in_file "$file" "</Ionicons>" "</Icon>"
    fi
done

echo -e "${YELLOW}📝 Replacing expo-linear-gradient with react-native-linear-gradient...${NC}"

for file in $FILES; do
    if grep -q "expo-linear-gradient" "$file"; then
        echo "  ✓ Updating $file"
        replace_in_file "$file" "import { LinearGradient } from 'expo-linear-gradient';" "import LinearGradient from 'react-native-linear-gradient';"
    fi
done

echo -e "${YELLOW}📝 Replacing expo-status-bar with react-native StatusBar...${NC}"

for file in $FILES; do
    if grep -q "expo-status-bar" "$file"; then
        echo "  ✓ Updating $file"
        replace_in_file "$file" "import { StatusBar } from 'expo-status-bar';" "import { StatusBar } from 'react-native';"
        replace_in_file "$file" '<StatusBar style="auto" />' '<StatusBar barStyle="light-content" backgroundColor="#6366f1" />'
    fi
done

echo -e "${YELLOW}📝 Fixing TypeScript type references...${NC}"

for file in $FILES; do
    if grep -q "keyof typeof Ionicons.glyphMap" "$file"; then
        echo "  ✓ Updating TypeScript types in $file"
        replace_in_file "$file" "keyof typeof Ionicons.glyphMap" "string"
    fi
done

echo -e "${GREEN}✅ Migration complete!${NC}"
echo ""
echo "Next steps:"
echo "1. npm install"
echo "2. cd ios && pod install && cd .. (Mac only)"
echo "3. npm run ios (or npm run android)"
echo ""
echo "⚠️  Manual steps required:"
echo "- Review all changed files"
echo "- Test all features"
echo "- Update app icons and splash screen"
echo "- Configure native modules if needed"
