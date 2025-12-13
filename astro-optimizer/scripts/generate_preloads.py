#!/usr/bin/env python3
"""
Generates preload directives for fonts and critical resources found in CSS.
Determines whether preloads should be at layout level (global) or page level.
"""

import os
import re
import json
import sys
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class PreloadDirective:
    href: str
    as_type: str  # "font", "style", "script", "image"
    type_attr: str | None  # e.g., "font/woff2"
    crossorigin: bool
    scope: str  # "layout" or "page"
    source_file: str
    reason: str

def extract_fonts_from_css(css_content: str, css_file_path: Path, project_path: Path) -> list[PreloadDirective]:
    """Extract font URLs from @font-face declarations."""
    preloads = []
    
    # Match @font-face with src containing url()
    font_face_pattern = r'@font-face\s*\{([^}]*)\}'
    
    for match in re.finditer(font_face_pattern, css_content, re.IGNORECASE | re.DOTALL):
        face_content = match.group(1)
        
        # Extract URL from src
        url_pattern = r'url\(["\']?([^"\')\s]+\.(?:woff2?|ttf|otf|eot))["\']?\)'
        url_matches = re.findall(url_pattern, face_content, re.IGNORECASE)
        
        for url in url_matches:
            # Normalize the URL
            if url.startswith('/'):
                href = url
            elif url.startswith('http'):
                href = url
            else:
                # Relative path - resolve from CSS file location
                css_dir = css_file_path.parent
                resolved = (css_dir / url).resolve()
                try:
                    href = '/' + str(resolved.relative_to(project_path / 'public'))
                except ValueError:
                    try:
                        href = '/' + str(resolved.relative_to(project_path / 'src'))
                    except ValueError:
                        href = url
            
            # Determine font type
            if '.woff2' in url.lower():
                type_attr = 'font/woff2'
            elif '.woff' in url.lower():
                type_attr = 'font/woff'
            elif '.ttf' in url.lower():
                type_attr = 'font/ttf'
            else:
                type_attr = None
            
            preloads.append(PreloadDirective(
                href=href,
                as_type='font',
                type_attr=type_attr,
                crossorigin=True,  # Fonts always need crossorigin
                scope='layout',  # Fonts are typically global
                source_file=str(css_file_path.relative_to(project_path)),
                reason='Font declared in CSS - preloading prevents FOIT/FOUT'
            ))
    
    return preloads

def extract_critical_images_from_css(css_content: str, css_file_path: Path, project_path: Path) -> list[PreloadDirective]:
    """Extract background images that might be critical (hero images, etc.)."""
    preloads = []
    
    # Look for background images in selectors that suggest above-fold content
    critical_selectors = ['hero', 'banner', 'header', 'masthead', 'jumbotron', 'above-fold', 'splash']
    
    # Pattern to match selectors with background-image
    rule_pattern = r'([^{]+)\{([^}]*background(?:-image)?:\s*url\(["\']?([^"\')\s]+)["\']?\)[^}]*)\}'
    
    for match in re.finditer(rule_pattern, css_content, re.IGNORECASE | re.DOTALL):
        selector = match.group(1).lower()
        url = match.group(3)
        
        is_critical = any(pattern in selector for pattern in critical_selectors)
        
        if is_critical and not url.startswith('data:'):
            # Normalize URL
            if url.startswith('/'):
                href = url
            elif url.startswith('http'):
                href = url
            else:
                href = '/' + url
            
            preloads.append(PreloadDirective(
                href=href,
                as_type='image',
                type_attr=None,
                crossorigin=False,
                scope='layout' if 'header' in selector else 'page',
                source_file=str(css_file_path.relative_to(project_path)),
                reason=f'Critical background image in CSS selector: {selector.strip()[:50]}'
            ))
    
    return preloads

def analyze_page_specific_resources(astro_file: Path, project_path: Path) -> list[PreloadDirective]:
    """Analyze an Astro page/component for page-specific preload candidates."""
    preloads = []
    content = astro_file.read_text(errors='ignore')
    
    # Check for page-specific hero images
    hero_img_pattern = r'<img[^>]*(?:class=["\'][^"\']*(?:hero|banner|featured)[^"\']*["\']|id=["\'][^"\']*(?:hero|banner|featured)[^"\']*["\'])[^>]*src=["\']([^"\']+)["\'][^>]*>'
    
    for match in re.finditer(hero_img_pattern, content, re.IGNORECASE):
        src = match.group(1)
        if not src.startswith('data:'):
            preloads.append(PreloadDirective(
                href=src if src.startswith('/') else '/' + src,
                as_type='image',
                type_attr=None,
                crossorigin=False,
                scope='page',
                source_file=str(astro_file.relative_to(project_path)),
                reason='Hero/banner image on this page'
            ))
    
    return preloads

def generate_preload_html(preloads: list[PreloadDirective]) -> dict[str, str]:
    """Generate HTML preload tags grouped by scope."""
    layout_preloads = []
    page_preloads = []
    
    seen = set()
    
    for p in preloads:
        if p.href in seen:
            continue
        seen.add(p.href)
        
        attrs = [
            f'rel="preload"',
            f'href="{p.href}"',
            f'as="{p.as_type}"',
        ]
        
        if p.type_attr:
            attrs.append(f'type="{p.type_attr}"')
        
        if p.crossorigin:
            attrs.append('crossorigin')
        
        tag = f'<link {" ".join(attrs)}>'
        
        if p.scope == 'layout':
            layout_preloads.append(tag)
        else:
            page_preloads.append(tag)
    
    return {
        'layout': '\n'.join(layout_preloads),
        'page': '\n'.join(page_preloads),
    }

def analyze_project(project_path: str) -> dict:
    """Analyze project and generate preload recommendations."""
    path = Path(project_path).resolve()
    src_path = path / 'src'
    
    all_preloads = []
    
    # Analyze CSS files for fonts and critical images
    css_files = list(src_path.rglob("*.css")) + list(src_path.rglob("*.scss"))
    
    for css_file in css_files:
        try:
            content = css_file.read_text(errors='ignore')
            all_preloads.extend(extract_fonts_from_css(content, css_file, path))
            all_preloads.extend(extract_critical_images_from_css(content, css_file, path))
        except Exception as e:
            print(f"Warning: Could not process {css_file}: {e}", file=sys.stderr)
    
    # Analyze pages for page-specific resources
    page_files = list((src_path / 'pages').rglob("*.astro")) if (src_path / 'pages').exists() else []
    
    page_specific = {}
    for page_file in page_files:
        try:
            page_preloads = analyze_page_specific_resources(page_file, path)
            if page_preloads:
                page_specific[str(page_file.relative_to(path))] = [asdict(p) for p in page_preloads]
        except Exception as e:
            print(f"Warning: Could not process {page_file}: {e}", file=sys.stderr)
    
    # Generate HTML
    html = generate_preload_html(all_preloads)
    
    return {
        'preloads': [asdict(p) for p in all_preloads],
        'page_specific': page_specific,
        'generated_html': html,
        'summary': {
            'total_preloads': len(all_preloads),
            'layout_scope': len([p for p in all_preloads if p.scope == 'layout']),
            'page_scope': len([p for p in all_preloads if p.scope == 'page']),
            'fonts': len([p for p in all_preloads if p.as_type == 'font']),
            'images': len([p for p in all_preloads if p.as_type == 'image']),
        }
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: generate_preloads.py <project-path>", file=sys.stderr)
        sys.exit(1)
    
    project_path = sys.argv[1]
    
    if not Path(project_path).exists():
        print(f"Error: Path does not exist: {project_path}", file=sys.stderr)
        sys.exit(1)
    
    result = analyze_project(project_path)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
