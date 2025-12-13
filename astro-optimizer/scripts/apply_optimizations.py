#!/usr/bin/env python3
"""
Applies automatic optimizations to Astro project files.
Only applies 'safe' optimizations by default. Use --include-risky for risky ones.
"""

import os
import re
import json
import sys
import shutil
from pathlib import Path
from datetime import datetime

def backup_file(file_path: Path, backup_dir: Path) -> Path:
    """Create a backup of a file before modifying it."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{file_path.name}.{timestamp}.bak"
    shutil.copy2(file_path, backup_path)
    return backup_path

def add_fetchpriority_to_hero_images(content: str) -> tuple[str, list[str]]:
    """Add fetchpriority='high' to hero/banner images."""
    changes = []
    
    hero_patterns = [
        (r'(<img[^>]*(?:class|id)=["\'][^"\']*(?:hero|banner|featured|lcp|main-image)[^"\']*["\'][^>]*)(/?>)', 
         'hero/banner class'),
        (r'(<Image[^>]*(?:class|id)=["\'][^"\']*(?:hero|banner|featured|lcp|main-image)[^"\']*["\'][^>]*)(/?>)',
         'Astro Image component'),
    ]
    
    for pattern, desc in hero_patterns:
        def add_priority(match):
            tag = match.group(1)
            closing = match.group(2)
            if 'fetchpriority' not in tag.lower():
                changes.append(f"Added fetchpriority='high' to {desc}")
                return f'{tag} fetchpriority="high"{closing}'
            return match.group(0)
        
        content = re.sub(pattern, add_priority, content, flags=re.IGNORECASE)
    
    return content, changes

def add_loading_lazy_to_images(content: str) -> tuple[str, list[str]]:
    """Add loading='lazy' to images without loading attribute (excluding heroes)."""
    changes = []
    
    def add_lazy(match):
        tag = match.group(0)
        # Skip if already has loading, or if it's a hero image
        if 'loading=' in tag.lower():
            return tag
        hero_indicators = ['hero', 'banner', 'featured', 'lcp', 'above-fold', 'fetchpriority']
        if any(ind in tag.lower() for ind in hero_indicators):
            return tag
        
        # Add loading="lazy" before the closing
        if tag.endswith('/>'):
            changes.append("Added loading='lazy' to img tag")
            return tag[:-2] + ' loading="lazy" />'
        elif tag.endswith('>'):
            changes.append("Added loading='lazy' to img tag")
            return tag[:-1] + ' loading="lazy">'
        return tag
    
    content = re.sub(r'<img[^>]*/?>', add_lazy, content, flags=re.IGNORECASE)
    
    return content, changes

def add_decoding_async_to_images(content: str) -> tuple[str, list[str]]:
    """Add decoding='async' to images without decoding attribute."""
    changes = []
    
    def add_decoding(match):
        tag = match.group(0)
        if 'decoding=' in tag.lower():
            return tag
        
        if tag.endswith('/>'):
            changes.append("Added decoding='async' to img tag")
            return tag[:-2] + ' decoding="async" />'
        elif tag.endswith('>'):
            changes.append("Added decoding='async' to img tag")
            return tag[:-1] + ' decoding="async">'
        return tag
    
    content = re.sub(r'<img[^>]*/?>', add_decoding, content, flags=re.IGNORECASE)
    
    return content, changes

def add_font_display_swap(content: str) -> tuple[str, list[str]]:
    """Add font-display: swap to @font-face rules missing it."""
    changes = []
    
    def add_display(match):
        rule = match.group(0)
        if 'font-display' in rule.lower():
            return rule
        
        # Insert font-display: swap before the closing brace
        changes.append("Added font-display: swap to @font-face")
        return rule[:-1] + '\n  font-display: swap;\n}'
    
    content = re.sub(r'@font-face\s*\{[^}]*\}', add_display, content, flags=re.IGNORECASE | re.DOTALL)
    
    return content, changes

def add_defer_to_external_scripts(content: str) -> tuple[str, list[str]]:
    """Add defer to external scripts without defer/async (RISKY)."""
    changes = []
    
    def add_defer(match):
        tag = match.group(0)
        if 'defer' in tag.lower() or 'async' in tag.lower():
            return tag
        
        changes.append("Added defer to external script tag")
        return tag[:-1] + ' defer>'
    
    content = re.sub(r'<script[^>]*src=["\']https?://[^"\']+["\'][^>]*>', add_defer, content, flags=re.IGNORECASE)
    
    return content, changes

def optimize_file(file_path: Path, backup_dir: Path, include_risky: bool = False) -> dict:
    """Apply optimizations to a single file."""
    result = {
        'file': str(file_path),
        'changes': [],
        'backup': None,
        'error': None
    }
    
    try:
        content = file_path.read_text(errors='ignore')
        original_content = content
        all_changes = []
        
        # Determine file type and apply relevant optimizations
        suffix = file_path.suffix.lower()
        
        if suffix == '.astro':
            content, changes = add_fetchpriority_to_hero_images(content)
            all_changes.extend(changes)
            
            content, changes = add_loading_lazy_to_images(content)
            all_changes.extend(changes)
            
            content, changes = add_decoding_async_to_images(content)
            all_changes.extend(changes)
            
            if include_risky:
                content, changes = add_defer_to_external_scripts(content)
                all_changes.extend(changes)
        
        elif suffix in ['.css', '.scss']:
            content, changes = add_font_display_swap(content)
            all_changes.extend(changes)
        
        # Only write if changes were made
        if content != original_content:
            backup_path = backup_file(file_path, backup_dir)
            result['backup'] = str(backup_path)
            file_path.write_text(content)
            result['changes'] = all_changes
        
    except Exception as e:
        result['error'] = str(e)
    
    return result

def optimize_project(project_path: str, include_risky: bool = False) -> dict:
    """Apply optimizations to all relevant files in the project."""
    path = Path(project_path).resolve()
    src_path = path / 'src'
    backup_dir = path / '.astro-optimizer-backups'
    
    results = {
        'project_path': str(path),
        'backup_dir': str(backup_dir),
        'include_risky': include_risky,
        'files_processed': [],
        'files_modified': [],
        'total_changes': 0,
        'errors': []
    }
    
    # Process Astro files
    for astro_file in src_path.rglob("*.astro"):
        result = optimize_file(astro_file, backup_dir, include_risky)
        results['files_processed'].append(str(astro_file.relative_to(path)))
        
        if result['changes']:
            results['files_modified'].append({
                'file': str(astro_file.relative_to(path)),
                'changes': result['changes'],
                'backup': result['backup']
            })
            results['total_changes'] += len(result['changes'])
        
        if result['error']:
            results['errors'].append({
                'file': str(astro_file.relative_to(path)),
                'error': result['error']
            })
    
    # Process CSS files
    for css_file in list(src_path.rglob("*.css")) + list(src_path.rglob("*.scss")):
        result = optimize_file(css_file, backup_dir, include_risky)
        results['files_processed'].append(str(css_file.relative_to(path)))
        
        if result['changes']:
            results['files_modified'].append({
                'file': str(css_file.relative_to(path)),
                'changes': result['changes'],
                'backup': result['backup']
            })
            results['total_changes'] += len(result['changes'])
        
        if result['error']:
            results['errors'].append({
                'file': str(css_file.relative_to(path)),
                'error': result['error']
            })
    
    return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Apply automatic optimizations to Astro project')
    parser.add_argument('project_path', help='Path to Astro project')
    parser.add_argument('--include-risky', action='store_true', 
                        help='Include risky optimizations (defer on scripts, etc.)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be changed without modifying files')
    
    args = parser.parse_args()
    
    if not Path(args.project_path).exists():
        print(f"Error: Path does not exist: {args.project_path}", file=sys.stderr)
        sys.exit(1)
    
    if args.dry_run:
        print("DRY RUN - No files will be modified", file=sys.stderr)
        # TODO: Implement dry run mode
        print(json.dumps({"error": "Dry run not yet implemented"}, indent=2))
        sys.exit(0)
    
    results = optimize_project(args.project_path, args.include_risky)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
