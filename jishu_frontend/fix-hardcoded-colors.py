#!/usr/bin/env python3

"""
Script to automatically fix hardcoded text colors in React components
Replaces hardcoded colors with semantic CSS variable classes
"""

import os
import re
from pathlib import Path

# Mapping of hardcoded colors to semantic classes
COLOR_REPLACEMENTS = {
    # Primary text colors (dark in light mode, white in dark mode)
    'text-gray-900': 'text-foreground',
    'text-gray-800': 'text-foreground',
    'text-gray-700': 'text-foreground',
    'text-black': 'text-foreground',
    'text-slate-900': 'text-foreground',
    'text-slate-800': 'text-foreground',
    'text-slate-700': 'text-foreground',
    'text-blue-900': 'text-foreground',
    'text-purple-900': 'text-foreground',
    
    # Secondary text colors (medium gray in light mode, light gray in dark mode)
    'text-gray-600': 'text-muted-foreground',
    'text-gray-500': 'text-muted-foreground',
    'text-gray-400': 'text-muted-foreground',
    'text-gray-300': 'text-muted-foreground',
    'text-slate-600': 'text-muted-foreground',
    'text-slate-500': 'text-muted-foreground',
    
    # White text (for dark backgrounds)
    'text-white': 'text-primary-foreground',
}

def fix_file(filepath):
    """Fix hardcoded colors in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace each hardcoded color
        for hardcoded, semantic in COLOR_REPLACEMENTS.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(hardcoded) + r'\b'
            content = re.sub(pattern, semantic, content)
        
        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Main function to process all component files"""
    components_dir = Path(__file__).parent / 'src' / 'components'
    
    if not components_dir.exists():
        print(f"❌ Components directory not found: {components_dir}")
        return
    
    print("🔧 Fixing hardcoded text colors...\n")
    
    fixed_files = []
    total_files = 0
    
    # Process all .tsx files
    for filepath in components_dir.rglob('*.tsx'):
        total_files += 1
        if fix_file(filepath):
            relative_path = filepath.relative_to(components_dir.parent)
            fixed_files.append(str(relative_path))
            print(f"✅ Fixed: {relative_path}")
    
    print(f"\n📊 Summary:")
    print(f"  Total files processed: {total_files}")
    print(f"  Files fixed: {len(fixed_files)}")
    
    if fixed_files:
        print(f"\n📝 Fixed files:")
        for f in fixed_files:
            print(f"  - {f}")
    else:
        print("\n✨ No files needed fixing!")

if __name__ == '__main__':
    main()

