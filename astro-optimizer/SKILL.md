---
name: astro-optimizer
description: Performance optimization toolkit for Astro SSG sites. Analyzes and applies optimizations including resource preloading (fonts, images, CSS), page prefetching, image loading strategies (lazy/eager, fetchpriority), and configuration improvements. Use when the user asks to optimize an Astro site, improve Astro performance, add preloading, configure prefetching, or speed up their Astro build. Handles both automatic safe optimizations and user-confirmed risky optimizations.
---

# Astro Optimizer

Performance optimization toolkit for Astro static sites. Analyzes projects, generates preload directives, configures prefetching, applies image/font/script optimizations, and identifies JavaScript patterns replaceable with CSS/HTML.

## Workflow

1. **Analyze** - Run `scripts/analyze.py` to scan project for optimization opportunities
2. **Detect JS Patterns** - Run `scripts/detect_js_patterns.py` to find JS replaceable with CSS/HTML
3. **Review** - Present findings grouped by severity and risk level
4. **Apply Safe** - Apply safe, auto-fixable optimizations with `scripts/apply_optimizations.py`
5. **Confirm Risky** - Get user confirmation before applying risky optimizations
6. **Generate Preloads** - Run `scripts/generate_preloads.py` for resource hints
7. **Suggest Manual** - Recommend configuration and manual improvements

## Quick Start

```bash
# 1. Analyze project for performance issues
python3 scripts/analyze.py /path/to/astro-project

# 2. Find JS that could be CSS/HTML
python3 scripts/detect_js_patterns.py /path/to/astro-project

# 3. Generate preload directives
python3 scripts/generate_preloads.py /path/to/astro-project

# 4. Apply safe optimizations
python3 scripts/apply_optimizations.py /path/to/astro-project

# 5. Apply including risky (after user confirmation)
python3 scripts/apply_optimizations.py /path/to/astro-project --include-risky
```

## Analysis Output

The analyzer returns JSON with findings categorized by:

- **severity**: `high` | `medium` | `low`
- **risk**: `safe` | `risky`
- **auto_fixable**: Whether the script can fix it automatically

Present findings to user grouped by severity, highlighting high-severity items first.

## JS Pattern Detection

`detect_js_patterns.py` identifies JavaScript that can be replaced with pure CSS/HTML:

| Pattern | CSS/HTML Alternative | Severity |
|---------|---------------------|----------|
| Accordion/collapse | `<details>` or checkbox hack | high |
| Modal/dialog | `<dialog>` or `:target` | high |
| Tabs | Radio button + `:checked` | high |
| Smooth scroll | `scroll-behavior: smooth` | high |
| Sticky header | `position: sticky` | high |
| Tooltips | `::after` + `attr()` | high |
| Carousel/slider | `scroll-snap-type` | medium |
| Dark mode toggle | `prefers-color-scheme` | medium |
| Form validation | `:valid`/`:invalid`/`:user-invalid` | medium |
| Animations | `@keyframes`/`transition` | medium |
| Container responsive | `@container` queries | medium |
| Scroll animations | Scroll-driven animations | medium |
| Aspect ratio | `aspect-ratio` property | high |
| Auto-numbering | `counter-increment` | high |
| Page transitions | View Transitions API | low |

**Output includes:**
- File and line where pattern was detected
- Code evidence snippet
- Explanation of the CSS/HTML solution
- Before/after code examples

Present these as suggestions. The user must manually refactor since these changes require understanding context. See `references/css-html-alternatives.md` for detailed implementation patterns.

## Optimization Categories

### Safe (Auto-Apply)

These can be applied without user confirmation:

| Optimization | What it does |
|--------------|--------------|
| `fetchpriority="high"` | Adds to hero/banner images |
| `loading="lazy"` | Adds to non-hero images |
| `decoding="async"` | Adds to all images |
| `font-display: swap` | Adds to @font-face rules |
| Preload generation | Creates `<link rel="preload">` for fonts |
| Prefetch config | Enables Astro's built-in prefetch |

### Risky (Require Confirmation)

**Always ask user before applying.** See `references/risky-optimizations.md` for details.

| Optimization | Risk |
|--------------|------|
| Script `defer` | May break script dependencies |
| Self-host fonts | Maintenance responsibility |
| `content-visibility` | Layout/accessibility issues |
| Aggressive prefetch | Bandwidth waste |
| Script delay | Missing early interactions |

## Preload Scope Decision

The preload generator determines scope automatically:

- **Layout level** (global): Fonts, header images, site-wide resources
- **Page level**: Hero images specific to one page, page-specific resources

For layout preloads, add to `src/layouts/Layout.astro` (or equivalent):
```astro
<head>
  <!-- Generated preloads go here -->
</head>
```

For page preloads, add to specific page frontmatter:
```astro
---
// In src/pages/about.astro
---
<head>
  <!-- Page-specific preloads -->
</head>
```

## Suggesting Additional Optimizations

After automated analysis, suggest these manual improvements based on findings:

**Image Format Conversion**:
- If `.jpg`/`.png` found in `public/`: Suggest converting to AVIF/WebP
- Recommend using Astro's `<Image>` component with `formats` prop

**Astro Config**:
- If no prefetch config: Suggest enabling with `viewport` strategy
- If no image service: Suggest configuring Sharp

**Font Optimization**:
- If Google Fonts detected: Suggest self-hosting (with caveats)
- If fonts not subsetted: Suggest using `glyphhanger` or `fonttools`

**Third-Party Scripts**:
- If analytics loads immediately: Suggest delayed loading pattern
- If multiple third-party origins: Suggest preconnect

**Caching**:
- Suggest cache headers for static assets
- Mention service worker for repeat visitors

## Backups

`apply_optimizations.py` creates backups in `.astro-optimizer-backups/` before modifying files. Mention this to user and explain how to restore if needed.

## References

- `references/optimizations.md` - Detailed documentation on each optimization type with code examples
- `references/risky-optimizations.md` - In-depth explanation of risky optimizations and when they're safe to apply
- `references/css-html-alternatives.md` - Complete guide to CSS/HTML alternatives for common JS patterns with browser support info
