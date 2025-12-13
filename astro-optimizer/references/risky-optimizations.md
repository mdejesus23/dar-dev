# Risky Optimizations

These optimizations can improve performance but may break functionality. **Always confirm with user before applying.**

## Script defer/async Addition

**Risk**: Scripts may depend on execution order or DOM readiness.

**What it does**: Adds `defer` to external `<script>` tags.

**What can break**:
- Scripts that use `document.write()`
- Scripts that expect to run before DOM is ready
- Scripts with dependencies on other scripts (order matters)
- Inline scripts that reference variables from external scripts

**Safe to apply when**:
- Script is analytics/tracking (no DOM dependencies)
- Script is explicitly designed for async loading
- User has tested the change

**Before**:
```html
<script src="https://example.com/widget.js"></script>
```

**After**:
```html
<script src="https://example.com/widget.js" defer></script>
```

---

## Self-Hosting Google Fonts

**Risk**: Font files may become outdated; licensing considerations.

**What it does**: Replaces Google Fonts CDN links with self-hosted files.

**What can break**:
- Automatic font updates from Google
- Variable font features if not properly downloaded
- Subsetting may remove needed characters

**Considerations**:
- Google Fonts are under SIL Open Font License (allows self-hosting)
- Need to manually update fonts for bug fixes
- May need multiple font files for different weights/styles

**Safe to apply when**:
- User understands maintenance responsibility
- Font usage is well-defined (known weights, character sets)
- Performance is prioritized over convenience

---

## content-visibility: auto

**Risk**: Can cause layout jumps and affect accessibility.

**What it does**: Skips rendering of off-screen content until needed.

**What can break**:
- `position: sticky` elements inside affected containers
- Anchor links jumping to wrong positions
- Screen readers may not announce content
- JavaScript measuring element dimensions
- IntersectionObserver calculations

**Safe to apply when**:
- Applied to truly independent sections
- No sticky elements inside
- User has tested scroll behavior
- Proper `contain-intrinsic-size` is set

**Example**:
```css
.article-section {
  content-visibility: auto;
  contain-intrinsic-size: 0 500px; /* Must estimate height */
}
```

---

## Aggressive Prefetching

**Risk**: Wastes bandwidth for users who don't navigate.

**What it does**: Prefetches all/most internal links.

**What can break**:
- Nothing breaks, but wastes user data
- Can overwhelm servers on high-traffic sites
- Analytics may count prefetched pages

**Configuration options** (in order of aggressiveness):
```js
// Most conservative - only on hover
prefetch: { defaultStrategy: 'hover' }

// Moderate - links in viewport
prefetch: { defaultStrategy: 'viewport' }

// Aggressive - all links on load
prefetch: { defaultStrategy: 'load', prefetchAll: true }
```

**Safe to apply when**:
- Site has few pages
- Users typically navigate to multiple pages
- Bandwidth is not a concern for target audience

---

## Delayed Third-Party Scripts

**Risk**: Features may not be available immediately.

**What it does**: Delays loading of analytics, chat widgets, etc.

**What can break**:
- Early user interactions not tracked
- Chat widgets not available on initial load
- A/B testing may flash original content

**Example approaches**:

**setTimeout delay**:
```js
setTimeout(() => {
  // Load script after 3 seconds
}, 3000);
```

**Load on interaction**:
```js
['scroll', 'click', 'keydown'].forEach(event => {
  window.addEventListener(event, loadScripts, { once: true });
});
```

**Safe to apply when**:
- User understands analytics may miss early bounces
- Chat/support can afford slight delay
- Core functionality doesn't depend on third-party

---

## Image Format Conversion to AVIF

**Risk**: Browser support, quality degradation.

**What it does**: Converts images to AVIF format.

**What can break**:
- Safari < 16.4 doesn't support AVIF
- Some image details may be lost at high compression
- Build times increase significantly

**Safe to apply when**:
- Using `<picture>` with fallbacks
- Target audience uses modern browsers
- Images are tested for quality

**Recommended approach**:
```html
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="">
</picture>
```

---

## Confirmation Checklist

Before applying risky optimizations, confirm:

1. [ ] User understands the specific risk
2. [ ] User has a way to test the changes
3. [ ] Backups are created (automatic with apply_optimizations.py)
4. [ ] User knows how to revert if needed
5. [ ] Changes are applied incrementally, not all at once
