#!/usr/bin/env node

/**
 * Migration script to replace Expo imports with React Native CLI equivalents
 * Cross-platform (works on Windows, Mac, Linux)
 */

const fs = require('fs');
const path = require('path');

// Color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
};

console.log(`${colors.blue}🔄 Starting migration from Expo to React Native CLI...${colors.reset}\n`);

// Replacement rules
const replacements = [
  {
    name: '@expo/vector-icons → react-native-vector-icons',
    search: /import\s+{\s*Ionicons\s*}\s+from\s+['"]@expo\/vector-icons['"]/g,
    replace: "import Icon from 'react-native-vector-icons/Ionicons'",
  },
  {
    name: 'Ionicons component → Icon component',
    search: /<Ionicons\s/g,
    replace: '<Icon ',
  },
  {
    name: 'Ionicons closing tag → Icon closing tag',
    search: /<\/Ionicons>/g,
    replace: '</Icon>',
  },
  {
    name: 'expo-linear-gradient → react-native-linear-gradient',
    search: /import\s+{\s*LinearGradient\s*}\s+from\s+['"]expo-linear-gradient['"]/g,
    replace: "import LinearGradient from 'react-native-linear-gradient'",
  },
  {
    name: 'expo-status-bar → react-native StatusBar',
    search: /import\s+{\s*StatusBar\s*}\s+from\s+['"]expo-status-bar['"]/g,
    replace: "import { StatusBar } from 'react-native'",
  },
  {
    name: 'StatusBar style prop → barStyle prop',
    search: /<StatusBar\s+style="auto"\s*\/>/g,
    replace: '<StatusBar barStyle="light-content" backgroundColor="#6366f1" />',
  },
  {
    name: 'TypeScript Ionicons.glyphMap type → string',
    search: /keyof\s+typeof\s+Ionicons\.glyphMap/g,
    replace: 'string',
  },
];

// Find all TypeScript/JavaScript files recursively
function findFiles(dir, fileList = []) {
  const files = fs.readdirSync(dir);

  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      // Skip node_modules and other unwanted directories
      if (!['node_modules', '.git', 'android', 'ios', 'build'].includes(file)) {
        findFiles(filePath, fileList);
      }
    } else if (file.match(/\.(tsx?|jsx?)$/)) {
      fileList.push(filePath);
    }
  });

  return fileList;
}

// Process files
function processFiles() {
  const srcDir = path.join(__dirname, '..', 'src');
  const files = findFiles(srcDir);
  
  let filesChanged = 0;
  const changedFiles = [];

  console.log(`${colors.yellow}📝 Processing ${files.length} files...${colors.reset}\n`);

  files.forEach(filePath => {
    let content = fs.readFileSync(filePath, 'utf8');
    let originalContent = content;
    let fileHasChanges = false;

    replacements.forEach(rule => {
      if (rule.search.test(content)) {
        content = content.replace(rule.search, rule.replace);
        fileHasChanges = true;
      }
    });

    if (fileHasChanges && content !== originalContent) {
      fs.writeFileSync(filePath, content, 'utf8');
      filesChanged++;
      changedFiles.push(filePath.replace(process.cwd(), '.'));
      console.log(`  ✓ ${colors.green}Updated${colors.reset} ${filePath.replace(process.cwd(), '.')}`);
    }
  });

  console.log(`\n${colors.green}✅ Migration complete!${colors.reset}`);
  console.log(`\n📊 Summary:`);
  console.log(`   - Files processed: ${files.length}`);
  console.log(`   - Files changed: ${filesChanged}`);

  if (changedFiles.length > 0) {
    console.log(`\n📝 Changed files:`);
    changedFiles.forEach(file => console.log(`   - ${file}`));
  }

  console.log(`\n${colors.yellow}Next steps:${colors.reset}`);
  console.log('   1. npm install');
  console.log('   2. cd ios && pod install && cd .. (Mac only, for iOS)');
  console.log('   3. npm run ios (or npm run android)');
  console.log('\n⚠️  Manual verification required:');
  console.log('   - Review all changed files');
  console.log('   - Test all features thoroughly');
  console.log('   - Update app icons and splash screen');
  console.log('   - Configure any additional native modules\n');
}

// Run the migration
try {
  processFiles();
} catch (error) {
  console.error(`\n${colors.red}❌ Error during migration:${colors.reset}`, error.message);
  process.exit(1);
}
