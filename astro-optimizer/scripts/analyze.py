#!/usr/bin/env python3
"""
Analyzes an Astro project and identifies optimization opportunities.
Outputs a JSON report of findings categorized by type and risk level.
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import TypedDict
from dataclasses import dataclass, field, asdict

@dataclass
class Finding:
    type: str
    severity: str  # "high", "medium", "low"
    risk: str      # "safe", "risky"
    file: str
    line: int | None
    message: str
    suggestion: str
    auto_fixable: bool = False

@dataclass
class AnalysisReport:
    project_path: str
    findings: list[Finding] = field(default_factory=list)
    summary: dict = field(default_factory=dict)

def find_astro_root(start_path: str) -> Path | None:
    """Find the Astro project root by looking for astro.config.*"""
    path = Path(start_path).resolve()
    for parent in [path] + list(path.parents):
        for config in parent.glob("astro.config.*"):
            return parent
    return None

def analyze_images(project_path: Path) -> list[Finding]:
    """Analyze image usage for optimization opportunities."""
    findings = []
    src_path = project_path / "src"
    public_path = project_path / "public"
    
    # Check for images without width/height or aspect-ratio
    for astro_file in src_path.rglob("*.astro"):
        content = astro_file.read_text(errors='ignore')
        
        # Find img tags without width/height
        img_pattern = r'<img[^>]*>'
        for match in re.finditer(img_pattern, content, re.IGNORECASE):
            img_tag = match.group()
            has_dimensions = ('width=' in img_tag and 'height=' in img_tag) or 'aspect-ratio' in img_tag
            
            if not has_dimensions and 'Image' not in img_tag:
                line_num = content[:match.start()].count('\n') + 1
                findings.append(Finding(
                    type="image_cls",
                    severity="high",
                    risk="safe",
                    file=str(astro_file.relative_to(project_path)),
                    line=line_num,
                    message="Image missing width/height attributes (causes CLS)",
                    suggestion="Add width and height attributes or use Astro's <Image> component",
                    auto_fixable=False
                ))
        
        # Check for missing loading attribute on below-fold images
        if '<img' in content and 'loading=' not in content:
            findings.append(Finding(
                type="image_loading",
                severity="medium",
                risk="safe",
                file=str(astro_file.relative_to(project_path)),
                line=None,
                message="Images without explicit loading strategy",
                suggestion="Add loading='lazy' for below-fold images, loading='eager' for above-fold",
                auto_fixable=True
            ))
        
        # Check for missing fetchpriority on hero images
        hero_patterns = ['hero', 'banner', 'header-image', 'main-image', 'lcp']
        for pattern in hero_patterns:
            if pattern in content.lower() and 'fetchpriority' not in content:
                findings.append(Finding(
                    type="image_priority",
                    severity="high",
                    risk="safe",
                    file=str(astro_file.relative_to(project_path)),
                    line=None,
                    message=f"Potential hero/LCP image without fetchpriority attribute",
                    suggestion="Add fetchpriority='high' to your main above-fold image",
                    auto_fixable=True
                ))
                break
    
    # Check for non-optimized image formats in public/
    if public_path.exists():
        for img_file in public_path.rglob("*"):
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                findings.append(Finding(
                    type="image_format",
                    severity="medium",
                    risk="safe",
                    file=str(img_file.relative_to(project_path)),
                    line=None,
                    message=f"Image could be converted to modern format (AVIF/WebP)",
                    suggestion="Convert to AVIF for best compression, WebP for broader support",
                    auto_fixable=False
                ))
    
    return findings

def analyze_fonts(project_path: Path) -> list[Finding]:
    """Analyze font loading for optimization opportunities."""
    findings = []
    src_path = project_path / "src"
    
    # Check CSS files for @font-face without preload
    css_files = list(src_path.rglob("*.css")) + list(src_path.rglob("*.scss"))
    font_files = []
    
    for css_file in css_files:
        content = css_file.read_text(errors='ignore')
        
        # Find @font-face declarations
        font_face_pattern = r'@font-face\s*\{[^}]*src:\s*url\(["\']?([^"\')\s]+)["\']?\)[^}]*\}'
        for match in re.finditer(font_face_pattern, content, re.IGNORECASE | re.DOTALL):
            font_url = match.group(1)
            font_files.append(font_url)
    
    # Check for Google Fonts
    for file in src_path.rglob("*.astro"):
        content = file.read_text(errors='ignore')
        if 'fonts.googleapis.com' in content or 'fonts.gstatic.com' in content:
            findings.append(Finding(
                type="font_external",
                severity="high",
                risk="risky",
                file=str(file.relative_to(project_path)),
                line=None,
                message="Using Google Fonts (external dependency, extra DNS lookup)",
                suggestion="Self-host fonts for better performance. Download from google-webfonts-helper or fontsource",
                auto_fixable=False
            ))
    
    # Check if fonts are preloaded in layouts
    layout_files = list(src_path.rglob("**/layouts/*.astro")) + list(src_path.rglob("Layout*.astro"))
    fonts_preloaded = False
    
    for layout in layout_files:
        content = layout.read_text(errors='ignore')
        if 'rel="preload"' in content and ('as="font"' in content or "as='font'" in content):
            fonts_preloaded = True
            break
    
    if font_files and not fonts_preloaded:
        findings.append(Finding(
            type="font_preload",
            severity="high",
            risk="safe",
            file="src/layouts/",
            line=None,
            message="Fonts declared in CSS but not preloaded",
            suggestion="Add <link rel='preload' href='/fonts/your-font.woff2' as='font' type='font/woff2' crossorigin> in layout <head>",
            auto_fixable=True
        ))
    
    # Check for font-display
    for css_file in css_files:
        content = css_file.read_text(errors='ignore')
        if '@font-face' in content and 'font-display' not in content:
            findings.append(Finding(
                type="font_display",
                severity="medium",
                risk="safe",
                file=str(css_file.relative_to(project_path)),
                line=None,
                message="@font-face without font-display property",
                suggestion="Add font-display: swap (or optional) to prevent FOIT",
                auto_fixable=True
            ))
    
    return findings

def analyze_prefetch(project_path: Path) -> list[Finding]:
    """Analyze page prefetching configuration."""
    findings = []
    
    # Check astro.config for prefetch settings
    config_files = list(project_path.glob("astro.config.*"))
    if config_files:
        config_content = config_files[0].read_text(errors='ignore')
        
        if 'prefetch' not in config_content:
            findings.append(Finding(
                type="prefetch_config",
                severity="medium",
                risk="safe",
                file=str(config_files[0].relative_to(project_path)),
                line=None,
                message="No prefetch configuration found",
                suggestion="Enable Astro's built-in prefetch: prefetch: { defaultStrategy: 'viewport' }",
                auto_fixable=True
            ))
    
    return findings

def analyze_preconnect(project_path: Path) -> list[Finding]:
    """Analyze third-party origins that could benefit from preconnect."""
    findings = []
    src_path = project_path / "src"
    
    third_party_origins = set()
    origin_pattern = r'https?://[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}'
    
    for file in src_path.rglob("*.astro"):
        content = file.read_text(errors='ignore')
        for match in re.finditer(origin_pattern, content):
            origin = match.group()
            # Exclude common localhost patterns
            if 'localhost' not in origin and '127.0.0.1' not in origin:
                third_party_origins.add(origin.split('/')[0] + '//' + origin.split('/')[2])
    
    # Check if preconnect exists for these origins
    layout_files = list(src_path.rglob("**/layouts/*.astro")) + list(src_path.rglob("Layout*.astro"))
    preconnected = set()
    
    for layout in layout_files:
        content = layout.read_text(errors='ignore')
        if 'rel="preconnect"' in content or "rel='preconnect'" in content:
            for origin in third_party_origins:
                if origin in content:
                    preconnected.add(origin)
    
    missing_preconnect = third_party_origins - preconnected
    if missing_preconnect:
        findings.append(Finding(
            type="preconnect",
            severity="medium",
            risk="safe",
            file="src/layouts/",
            line=None,
            message=f"Third-party origins without preconnect: {', '.join(list(missing_preconnect)[:3])}",
            suggestion="Add <link rel='preconnect' href='ORIGIN'> for external resources",
            auto_fixable=True
        ))
    
    return findings

def analyze_scripts(project_path: Path) -> list[Finding]:
    """Analyze script loading patterns."""
    findings = []
    src_path = project_path / "src"
    
    for file in src_path.rglob("*.astro"):
        content = file.read_text(errors='ignore')
        
        # Check for third-party scripts without defer/async
        script_pattern = r'<script[^>]*src=["\']https?://[^"\']+["\'][^>]*>'
        for match in re.finditer(script_pattern, content, re.IGNORECASE):
            script_tag = match.group()
            if 'defer' not in script_tag and 'async' not in script_tag:
                line_num = content[:match.start()].count('\n') + 1
                findings.append(Finding(
                    type="script_blocking",
                    severity="high",
                    risk="risky",
                    file=str(file.relative_to(project_path)),
                    line=line_num,
                    message="Third-party script without defer/async (render-blocking)",
                    suggestion="Add defer or async attribute, or load on interaction",
                    auto_fixable=True
                ))
        
        # Check for analytics/tracking loaded immediately
        tracking_patterns = ['analytics', 'gtag', 'gtm', 'facebook', 'pixel', 'hotjar', 'intercom', 'crisp', 'drift']
        for pattern in tracking_patterns:
            if pattern in content.lower() and 'setTimeout' not in content and 'requestIdleCallback' not in content:
                if f'<script' in content and pattern in content.lower():
                    findings.append(Finding(
                        type="script_tracking",
                        severity="medium",
                        risk="risky",
                        file=str(file.relative_to(project_path)),
                        line=None,
                        message=f"Tracking/analytics script loaded immediately",
                        suggestion="Delay non-critical scripts with setTimeout or load on user interaction",
                        auto_fixable=False
                    ))
                    break
    
    return findings

def analyze_css(project_path: Path) -> list[Finding]:
    """Analyze CSS for optimization opportunities."""
    findings = []
    src_path = project_path / "src"
    
    # Check for content-visibility usage
    css_files = list(src_path.rglob("*.css")) + list(src_path.rglob("*.scss"))
    has_content_visibility = False
    
    for css_file in css_files:
        content = css_file.read_text(errors='ignore')
        if 'content-visibility' in content:
            has_content_visibility = True
            break
    
    if not has_content_visibility:
        findings.append(Finding(
            type="css_content_visibility",
            severity="low",
            risk="risky",
            file="Global CSS",
            line=None,
            message="Not using content-visibility: auto for off-screen content",
            suggestion="Add content-visibility: auto to below-fold sections for paint performance",
            auto_fixable=False
        ))
    
    return findings

def analyze_astro_config(project_path: Path) -> list[Finding]:
    """Analyze Astro configuration for optimization opportunities."""
    findings = []
    
    config_files = list(project_path.glob("astro.config.*"))
    if not config_files:
        return findings
    
    config_content = config_files[0].read_text(errors='ignore')
    
    # Check for image optimization settings
    if 'image:' not in config_content and 'astro:assets' not in config_content:
        findings.append(Finding(
            type="config_image",
            severity="medium",
            risk="safe",
            file=str(config_files[0].relative_to(project_path)),
            line=None,
            message="No explicit image optimization configuration",
            suggestion="Configure image service for automatic optimization: image: { service: sharpImageService() }",
            auto_fixable=True
        ))
    
    # Check for compression
    if 'compress' not in config_content and 'compressHTML' not in config_content:
        findings.append(Finding(
            type="config_compress",
            severity="low",
            risk="safe",
            file=str(config_files[0].relative_to(project_path)),
            line=None,
            message="HTML compression not explicitly enabled",
            suggestion="Astro compresses HTML by default, but verify compressHTML: true in config",
            auto_fixable=True
        ))
    
    return findings

def analyze_project(project_path: str) -> AnalysisReport:
    """Run all analyzers on the project."""
    path = Path(project_path).resolve()
    report = AnalysisReport(project_path=str(path))
    
    analyzers = [
        analyze_images,
        analyze_fonts,
        analyze_prefetch,
        analyze_preconnect,
        analyze_scripts,
        analyze_css,
        analyze_astro_config,
    ]
    
    for analyzer in analyzers:
        try:
            findings = analyzer(path)
            report.findings.extend(findings)
        except Exception as e:
            print(f"Warning: {analyzer.__name__} failed: {e}", file=sys.stderr)
    
    # Generate summary
    report.summary = {
        "total": len(report.findings),
        "by_severity": {
            "high": len([f for f in report.findings if f.severity == "high"]),
            "medium": len([f for f in report.findings if f.severity == "medium"]),
            "low": len([f for f in report.findings if f.severity == "low"]),
        },
        "by_risk": {
            "safe": len([f for f in report.findings if f.risk == "safe"]),
            "risky": len([f for f in report.findings if f.risk == "risky"]),
        },
        "auto_fixable": len([f for f in report.findings if f.auto_fixable]),
    }
    
    return report

def main():
    if len(sys.argv) < 2:
        print("Usage: analyze.py <project-path>", file=sys.stderr)
        sys.exit(1)
    
    project_path = sys.argv[1]
    astro_root = find_astro_root(project_path)
    
    if not astro_root:
        print(f"Error: Could not find Astro project at {project_path}", file=sys.stderr)
        sys.exit(1)
    
    report = analyze_project(str(astro_root))
    
    # Convert to JSON-serializable format
    output = {
        "project_path": report.project_path,
        "findings": [asdict(f) for f in report.findings],
        "summary": report.summary
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
