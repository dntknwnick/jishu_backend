#!/usr/bin/env node

/**
 * Script to find hardcoded text colors in React components
 * Usage: node find-hardcoded-colors.js
 */

const fs = require('fs');
const path = require('path');

const HARDCODED_COLORS = [
  'text-gray-900',
  'text-gray-800',
  'text-gray-700',
  'text-gray-600',
  'text-gray-500',
  'text-gray-400',
  'text-gray-300',
  'text-black',
  'text-slate-900',
  'text-slate-800',
  'text-slate-700',
  'text-slate-600',
  'text-white',
  'text-blue-900',
  'text-blue-800',
  'text-purple-900',
  'text-purple-800',
];

const REPLACEMENTS = {
  'text-gray-900': 'text-foreground',
  'text-gray-800': 'text-foreground',
  'text-gray-700': 'text-foreground',
  'text-gray-600': 'text-muted-foreground',
  'text-gray-500': 'text-muted-foreground',
  'text-gray-400': 'text-muted-foreground',
  'text-gray-300': 'text-muted-foreground',
  'text-black': 'text-foreground',
  'text-slate-900': 'text-foreground',
  'text-slate-800': 'text-foreground',
  'text-slate-700': 'text-foreground',
  'text-slate-600': 'text-muted-foreground',
};

function findFiles(dir, ext = '.tsx') {
  let files = [];
  const items = fs.readdirSync(dir);

  items.forEach(item => {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory() && !item.startsWith('.') && item !== 'node_modules') {
      files = files.concat(findFiles(fullPath, ext));
    } else if (stat.isFile() && fullPath.endsWith(ext)) {
      files.push(fullPath);
    }
  });

  return files;
}

function analyzeFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');
  const issues = [];

  lines.forEach((line, index) => {
    HARDCODED_COLORS.forEach(color => {
      if (line.includes(color)) {
        issues.push({
          file: filePath,
          line: index + 1,
          color: color,
          replacement: REPLACEMENTS[color] || 'text-foreground',
          content: line.trim(),
        });
      }
    });
  });

  return issues;
}

function main() {
  const componentsDir = path.join(__dirname, 'src', 'components');

  if (!fs.existsSync(componentsDir)) {
    console.error(`❌ Components directory not found: ${componentsDir}`);
    process.exit(1);
  }

  console.log('🔍 Scanning for hardcoded text colors...\n');

  const files = findFiles(componentsDir);
  let totalIssues = 0;
  const issuesByFile = {};

  files.forEach(file => {
    const issues = analyzeFile(file);
    if (issues.length > 0) {
      issuesByFile[file] = issues;
      totalIssues += issues.length;
    }
  });

  if (totalIssues === 0) {
    console.log('✅ No hardcoded text colors found!');
    return;
  }

  console.log(`⚠️  Found ${totalIssues} hardcoded text color(s)\n`);

  Object.entries(issuesByFile).forEach(([file, issues]) => {
    const relativePath = path.relative(process.cwd(), file);
    console.log(`📄 ${relativePath}`);
    console.log('─'.repeat(80));

    issues.forEach(issue => {
      console.log(`  Line ${issue.line}: ${issue.color}`);
      console.log(`  Replace with: ${issue.replacement}`);
      console.log(`  Code: ${issue.content.substring(0, 70)}...`);
      console.log('');
    });
  });

  console.log('\n📋 Summary:');
  console.log(`  Total files with issues: ${Object.keys(issuesByFile).length}`);
  console.log(`  Total hardcoded colors: ${totalIssues}`);
  console.log('\n💡 Tip: Replace hardcoded colors with semantic classes:');
  console.log('  - text-foreground (for primary text)');
  console.log('  - text-muted-foreground (for secondary text)');
}

main();

