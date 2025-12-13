# CSS/HTML Alternatives to JavaScript

Replace JavaScript with native browser features for better performance, accessibility, and reduced bundle size.

## Table of Contents
1. [Interactive Components](#interactive-components)
2. [Navigation & Scrolling](#navigation--scrolling)
3. [Visual Effects](#visual-effects)
4. [Layout & Responsive](#layout--responsive)
5. [Forms](#forms)
6. [Utilities](#utilities)
7. [Browser Support Notes](#browser-support-notes)

---

## Interactive Components

### Accordion / Expand-Collapse

**Option 1: Native `<details>` (Recommended)**
```html
<details>
  <summary>Click to expand</summary>
  <p>Hidden content revealed on click.</p>
</details>

<style>
details > summary { cursor: pointer; font-weight: bold; }
details[open] > summary { color: blue; }
</style>
```

**Option 2: Checkbox Hack (More Styling Control)**
```html
<div class="accordion">
  <input type="checkbox" id="acc1" hidden>
  <label for="acc1" class="accordion-header">Section Title</label>
  <div class="accordion-content">
    <p>Content goes here</p>
  </div>
</div>

<style>
.accordion-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease-out;
}
#acc1:checked ~ .accordion-content {
  max-height: 500px; /* Adjust based on content */
}
.accordion-header::after {
  content: '+';
  float: right;
}
#acc1:checked ~ .accordion-header::after {
  content: '−';
}
</style>
```

### Tabs

```html
<div class="tabs">
  <input type="radio" name="tabs" id="tab1" checked hidden>
  <input type="radio" name="tabs" id="tab2" hidden>
  <input type="radio" name="tabs" id="tab3" hidden>
  
  <nav class="tab-nav">
    <label for="tab1">Tab 1</label>
    <label for="tab2">Tab 2</label>
    <label for="tab3">Tab 3</label>
  </nav>
  
  <section class="tab-panel" id="panel1">Content 1</section>
  <section class="tab-panel" id="panel2">Content 2</section>
  <section class="tab-panel" id="panel3">Content 3</section>
</div>

<style>
.tab-panel { display: none; }
#tab1:checked ~ #panel1,
#tab2:checked ~ #panel2,
#tab3:checked ~ #panel3 { display: block; }

.tab-nav label {
  padding: 0.5em 1em;
  cursor: pointer;
  border-bottom: 2px solid transparent;
}
#tab1:checked ~ .tab-nav label[for="tab1"],
#tab2:checked ~ .tab-nav label[for="tab2"],
#tab3:checked ~ .tab-nav label[for="tab3"] {
  border-bottom-color: blue;
}
</style>
```

### Modal / Dialog

**Option 1: Native `<dialog>` (Minimal JS)**
```html
<dialog id="myModal">
  <h2>Modal Title</h2>
  <p>Modal content here.</p>
  <button onclick="this.closest('dialog').close()">Close</button>
</dialog>

<button onclick="document.getElementById('myModal').showModal()">Open Modal</button>

<style>
dialog::backdrop {
  background: rgba(0, 0, 0, 0.5);
}
dialog {
  border: none;
  border-radius: 8px;
  padding: 2em;
  max-width: 500px;
}
</style>
```

**Option 2: Pure CSS with :target**
```html
<a href="#modal">Open Modal</a>

<div id="modal" class="modal-wrapper">
  <div class="modal-content">
    <a href="#" class="close">&times;</a>
    <h2>Modal Title</h2>
    <p>Content here</p>
  </div>
</div>

<style>
.modal-wrapper {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  place-items: center;
}
.modal-wrapper:target {
  display: grid;
}
.modal-content {
  background: white;
  padding: 2em;
  border-radius: 8px;
  position: relative;
}
.close {
  position: absolute;
  top: 0.5em;
  right: 0.5em;
  text-decoration: none;
  font-size: 1.5em;
}
</style>
```

### Tooltip

```html
<button data-tooltip="Save your changes">Save</button>
<span data-tooltip="More information here" class="info-icon">ℹ️</span>

<style>
[data-tooltip] {
  position: relative;
}

[data-tooltip]::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  padding: 0.5em 0.75em;
  background: #333;
  color: white;
  font-size: 0.875rem;
  border-radius: 4px;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s, visibility 0.2s;
  pointer-events: none;
  z-index: 1000;
}

/* Arrow */
[data-tooltip]::before {
  content: '';
  position: absolute;
  bottom: calc(100% + 2px);
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: #333;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s, visibility 0.2s;
}

[data-tooltip]:hover::after,
[data-tooltip]:hover::before,
[data-tooltip]:focus::after,
[data-tooltip]:focus::before {
  opacity: 1;
  visibility: visible;
}
</style>
```

---

## Navigation & Scrolling

### Smooth Scroll

```css
/* Global smooth scroll */
html {
  scroll-behavior: smooth;
}

/* Or scoped to specific container */
.scroll-container {
  scroll-behavior: smooth;
  overflow-y: auto;
}

/* Respect user preference for reduced motion */
@media (prefers-reduced-motion: reduce) {
  html {
    scroll-behavior: auto;
  }
}
```

### Sticky Header

```css
header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: white;
}

/* Sticky within a container */
.sidebar-nav {
  position: sticky;
  top: 1rem;
  align-self: start;
}
```

### Carousel / Slider

```html
<div class="carousel">
  <div class="slide">Slide 1</div>
  <div class="slide">Slide 2</div>
  <div class="slide">Slide 3</div>
</div>

<style>
.carousel {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scroll-behavior: smooth;
  gap: 1rem;
  
  /* Hide scrollbar */
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.carousel::-webkit-scrollbar {
  display: none;
}

.slide {
  flex: 0 0 100%;
  scroll-snap-align: start;
  /* Or center for centered slides */
  /* scroll-snap-align: center; */
}

/* Partial slide peek */
.carousel-peek .slide {
  flex: 0 0 80%;
}
</style>
```

### Scroll-Driven Animations

```css
/* Animate elements as they enter viewport */
@supports (animation-timeline: view()) {
  .reveal {
    animation: slideUp linear both;
    animation-timeline: view();
    animation-range: entry 0% cover 30%;
  }
  
  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(100px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
}

/* Progress bar based on scroll */
.progress-bar {
  animation: progress linear;
  animation-timeline: scroll();
}

@keyframes progress {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}
```

---

## Visual Effects

### Dark Mode

```css
/* System preference */
:root {
  --bg: #ffffff;
  --text: #1a1a1a;
  --accent: #0066cc;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1a1a1a;
    --text: #f0f0f0;
    --accent: #66b3ff;
  }
}

body {
  background: var(--bg);
  color: var(--text);
}

/* Manual toggle with checkbox (place at top of <body>) */
#theme-toggle:checked ~ * {
  --bg: #1a1a1a;
  --text: #f0f0f0;
}
```

### Animations

```css
/* Fade in */
.fade-in {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide in from left */
.slide-in {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}

/* Transitions for state changes */
.button {
  transition: transform 0.2s, box-shadow 0.2s;
}
.button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.button:active {
  transform: translateY(0);
}
```

### Page Transitions (Astro)

```astro
---
import { ViewTransitions } from 'astro:transitions';
---
<head>
  <ViewTransitions />
</head>

<style is:global>
  /* Customize transition */
  ::view-transition-old(root) {
    animation: fadeOut 0.2s ease-out;
  }
  ::view-transition-new(root) {
    animation: fadeIn 0.2s ease-in;
  }
  
  /* Named transitions for specific elements */
  .hero-image {
    view-transition-name: hero;
  }
  ::view-transition-group(hero) {
    animation-duration: 0.4s;
  }
</style>
```

---

## Layout & Responsive

### Aspect Ratio

```css
/* Replace padding-bottom hack */
.video-wrapper {
  aspect-ratio: 16 / 9;
  width: 100%;
}

.square {
  aspect-ratio: 1;
}

.portrait {
  aspect-ratio: 3 / 4;
}

/* With object-fit for images */
img {
  aspect-ratio: 4 / 3;
  width: 100%;
  object-fit: cover;
}
```

### Container Queries

```css
/* Define container */
.card-container {
  container-type: inline-size;
  container-name: card;
}

/* Base styles */
.card {
  display: grid;
  gap: 1rem;
}

/* Responsive to container, not viewport */
@container card (min-width: 400px) {
  .card {
    grid-template-columns: 150px 1fr;
  }
}

@container card (min-width: 600px) {
  .card {
    grid-template-columns: 200px 1fr auto;
  }
}
```

### Auto-Numbering

```css
/* Numbered list with custom styling */
.steps {
  counter-reset: step;
  list-style: none;
}

.steps li {
  counter-increment: step;
}

.steps li::before {
  content: counter(step);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2em;
  height: 2em;
  border-radius: 50%;
  background: #0066cc;
  color: white;
  margin-right: 1em;
}

/* Nested counters (1.1, 1.2, etc.) */
ol {
  counter-reset: section;
  list-style: none;
}

li::before {
  counter-increment: section;
  content: counters(section, ".") " ";
}
```

---

## Forms

### Validation Styling

```css
/* Style after user interaction (modern) */
input:user-invalid {
  border-color: #dc3545;
  background-color: #fff5f5;
}

input:user-valid {
  border-color: #28a745;
  background-color: #f5fff5;
}

/* Fallback: only show after user has typed */
input:invalid:not(:placeholder-shown) {
  border-color: #dc3545;
}

input:valid:not(:placeholder-shown) {
  border-color: #28a745;
}

/* Custom validation message positioning */
input:invalid + .error-message {
  display: block;
}
.error-message {
  display: none;
  color: #dc3545;
  font-size: 0.875em;
}
```

---

## Utilities

### Content Visibility (Performance)

```css
/* Skip rendering off-screen sections */
.below-fold {
  content-visibility: auto;
  contain-intrinsic-size: 0 500px; /* Estimated height */
}

/* Caution: May affect */
/* - Sticky positioning inside */
/* - Anchor link scroll targets */
/* - Screen reader announcements */
```

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Browser Support Notes

| Feature | Chrome | Firefox | Safari | Notes |
|---------|--------|---------|--------|-------|
| `<details>` | ✅ | ✅ | ✅ | Full support |
| `<dialog>` | ✅ | ✅ | ✅ 15.4+ | Use polyfill for older Safari |
| `:target` | ✅ | ✅ | ✅ | Full support |
| `scroll-snap` | ✅ | ✅ | ✅ | Full support |
| `position: sticky` | ✅ | ✅ | ✅ | Full support |
| `aspect-ratio` | ✅ 88+ | ✅ 89+ | ✅ 15+ | Good support |
| `@container` | ✅ 105+ | ✅ 110+ | ✅ 16+ | Good support |
| `:user-invalid` | ✅ 119+ | ✅ 88+ | ✅ 16.5+ | Use fallback |
| View Transitions | ✅ 111+ | 🚧 Flag | ✅ 18+ | Progressive enhancement |
| Scroll-driven animations | ✅ 115+ | 🚧 Flag | ❌ | Progressive enhancement |

**Strategy**: Use feature queries (`@supports`) for progressive enhancement:

```css
/* Fallback */
.card { display: block; }

/* Enhanced */
@supports (container-type: inline-size) {
  .card-wrapper { container-type: inline-size; }
  @container (min-width: 400px) {
    .card { display: grid; }
  }
}
```
