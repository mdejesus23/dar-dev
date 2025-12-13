# Optimization Reference

## Table of Contents
1. [Image Optimizations](#image-optimizations)
2. [Font Optimizations](#font-optimizations)
3. [Resource Hints](#resource-hints)
4. [Script Loading](#script-loading)
5. [CSS Optimizations](#css-optimizations)
6. [Astro Configuration](#astro-configuration)
7. [Caching](#caching)

---

## Image Optimizations

### Use Astro's Image Component
Replace native `<img>` with Astro's `<Image>` for automatic optimization:

```astro
---
import { Image } from 'astro:assets';
import heroImg from '../assets/hero.jpg';
---
<Image src={heroImg} alt="Hero" />
```

### fetchpriority Attribute
Add to LCP (Largest Contentful Paint) images:

```html
<img src="/hero.jpg" fetchpriority="high" alt="Hero">
```

### loading Attribute
- `loading="eager"` - Above-fold images (hero, header)
- `loading="lazy"` - Below-fold images (default for most)

```html
<!-- Above fold -->
<img src="/hero.jpg" loading="eager" fetchpriority="high" alt="">

<!-- Below fold -->
<img src="/gallery-1.jpg" loading="lazy" alt="">
```

### decoding Attribute
Add `decoding="async"` to allow off-main-thread decoding:

```html
<img src="/photo.jpg" decoding="async" alt="">
```

### Width/Height for CLS Prevention
Always include dimensions to prevent Cumulative Layout Shift:

```html
<img src="/photo.jpg" width="800" height="600" alt="">
```

Or use CSS aspect-ratio:
```css
img { aspect-ratio: 4/3; width: 100%; height: auto; }
```

### Modern Image Formats
Priority order: AVIF > WebP > JPEG/PNG

Use Astro's picture component for format fallbacks:
```astro
<Picture src={myImage} formats={['avif', 'webp']} alt="" />
```

---

## Font Optimizations

### Self-Host Fonts
Instead of Google Fonts, self-host for better performance:

1. Download from [google-webfonts-helper](https://gwfh.mranftl.com/) or [Fontsource](https://fontsource.org/)
2. Place in `public/fonts/`
3. Reference in CSS

### Preload Critical Fonts
In layout `<head>`:

```html
<link rel="preload" href="/fonts/Inter-Regular.woff2" as="font" type="font/woff2" crossorigin>
```

### font-display Property
Add to all @font-face rules:

```css
@font-face {
  font-family: 'Inter';
  src: url('/fonts/Inter.woff2') format('woff2');
  font-display: swap; /* or 'optional' for non-critical fonts */
}
```

Options:
- `swap` - Show fallback immediately, swap when loaded (recommended)
- `optional` - Use if loaded within ~100ms, otherwise use fallback forever
- `fallback` - Brief invisible period, then fallback, late swap allowed

### Font Subsetting
Remove unused glyphs to reduce file size. Use tools like:
- `glyphhanger` (npm)
- `fonttools` (Python)
- `subfont` (npm)

---

## Resource Hints

### Preload
For critical resources on current page:

```html
<link rel="preload" href="/critical.css" as="style">
<link rel="preload" href="/hero.jpg" as="image">
<link rel="preload" href="/app.js" as="script">
```

### Preconnect
For third-party origins:

```html
<link rel="preconnect" href="https://cdn.example.com">
<link rel="dns-prefetch" href="https://cdn.example.com">
```

### Prefetch (Pages)
Astro's built-in prefetch in `astro.config.mjs`:

```js
export default defineConfig({
  prefetch: {
    defaultStrategy: 'viewport', // 'hover', 'viewport', 'load'
    prefetchAll: false
  }
})
```

### modulepreload
For ES modules (Astro handles this automatically for its own scripts):

```html
<link rel="modulepreload" href="/app.js">
```

---

## Script Loading

### defer vs async
- `defer` - Execute after HTML parsing, maintain order
- `async` - Execute as soon as downloaded, no order guarantee

```html
<script src="/analytics.js" defer></script>
```

### Delay Non-Critical Scripts
For analytics, chat widgets, etc.:

```html
<script>
  // Load after page is interactive
  window.addEventListener('load', () => {
    setTimeout(() => {
      const script = document.createElement('script');
      script.src = 'https://analytics.example.com/script.js';
      document.body.appendChild(script);
    }, 3000);
  });
</script>
```

Or load on interaction:
```html
<script>
  let loaded = false;
  document.addEventListener('scroll', () => {
    if (!loaded) {
      loaded = true;
      // Load script here
    }
  }, { once: true });
</script>
```

---

## CSS Optimizations

### content-visibility
Skip rendering off-screen content:

```css
.below-fold-section {
  content-visibility: auto;
  contain-intrinsic-size: 0 500px; /* Estimated height */
}
```

### Critical CSS
Astro inlines small CSS automatically. For manual control:

```astro
<style is:inline>
  /* Critical above-fold styles */
</style>
```

### Remove Unused CSS
Use tools like PurgeCSS (integrated in Tailwind) or UnCSS.

---

## Astro Configuration

### Recommended astro.config.mjs

```js
import { defineConfig } from 'astro/config';

export default defineConfig({
  // Enable prefetching
  prefetch: {
    defaultStrategy: 'viewport',
    prefetchAll: false
  },
  
  // Image optimization
  image: {
    // Use sharp for image processing
    service: { entrypoint: 'astro/assets/services/sharp' }
  },
  
  // Build optimizations
  build: {
    inlineStylesheets: 'auto', // Inline small stylesheets
  },
  
  // HTML compression (enabled by default)
  compressHTML: true,
  
  // Vite optimizations
  vite: {
    build: {
      cssCodeSplit: true,
      rollupOptions: {
        output: {
          manualChunks: {
            // Split vendor chunks for better caching
          }
        }
      }
    }
  }
});
```

---

## Caching

### Static Assets
Set long cache times for hashed assets in your hosting config:

```
# Vercel vercel.json
{
  "headers": [
    {
      "source": "/_astro/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    }
  ]
}
```

### Service Worker
For repeat visitors, consider a service worker with Workbox:

```js
// Basic caching strategy
import { precacheAndRoute } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { StaleWhileRevalidate } from 'workbox-strategies';

precacheAndRoute(self.__WB_MANIFEST);

registerRoute(
  ({ request }) => request.destination === 'image',
  new StaleWhileRevalidate({ cacheName: 'images' })
);
```
