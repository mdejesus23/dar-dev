#!/usr/bin/env python3
"""
Analyzes JavaScript/TypeScript files and Astro components to identify
patterns that could be replaced with pure CSS/HTML solutions.
"""

import os
import re
import json
import sys
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class JsToHtmlCssFinding:
    pattern: str
    severity: str  # "high" = easy win, "medium" = moderate effort, "low" = complex migration
    file: str
    line: int | None
    evidence: str  # The code snippet that triggered detection
    html_css_solution: str
    explanation: str
    example_before: str
    example_after: str

# Detection patterns with their CSS/HTML alternatives
PATTERNS = [
    {
        "name": "accordion_toggle",
        "description": "Accordion/collapse toggle",
        "js_patterns": [
            r'\.accordion',
            r'toggle.*collapse',
            r'expand.*collapse',
            r'\.slideToggle',
            r'\.slideDown',
            r'\.slideUp',
            r'accordion.*click',
            r'classList\.(toggle|add|remove).*\b(open|active|expanded|collapsed)\b',
        ],
        "severity": "high",
        "solution": "<details>/<summary> or checkbox hack",
        "explanation": "Native <details> element provides expand/collapse without JS. For styled accordions, use hidden checkbox + :checked selector.",
        "before": """document.querySelector('.accordion-btn').addEventListener('click', () => {
  document.querySelector('.accordion-content').classList.toggle('open');
});""",
        "after": """<details>
  <summary>Click to expand</summary>
  <p>Content here</p>
</details>

/* Or checkbox hack for custom styling */
<input type="checkbox" id="acc1" hidden>
<label for="acc1">Click to expand</label>
<div class="content">Content here</div>

<style>
.content { max-height: 0; overflow: hidden; transition: max-height 0.3s; }
#acc1:checked ~ .content { max-height: 500px; }
</style>"""
    },
    {
        "name": "modal_dialog",
        "description": "Modal/dialog toggle",
        "js_patterns": [
            r'\.modal',
            r'openModal|closeModal|toggleModal',
            r'dialog.*open|open.*dialog',
            r'\.show\(\)|\.hide\(\)',
            r'display.*=.*["\']?(none|block|flex)',
            r'classList.*(modal|popup|overlay)',
        ],
        "severity": "high",
        "solution": "<dialog> element or :target selector",
        "explanation": "Native <dialog> element with showModal()/close() or pure CSS with :target pseudo-class for URL-driven modals.",
        "before": """const modal = document.querySelector('.modal');
openBtn.addEventListener('click', () => modal.style.display = 'flex');
closeBtn.addEventListener('click', () => modal.style.display = 'none');""",
        "after": """<!-- Native dialog (minimal JS but semantic) -->
<dialog id="myDialog">
  <p>Modal content</p>
  <button onclick="this.closest('dialog').close()">Close</button>
</dialog>
<button onclick="document.getElementById('myDialog').showModal()">Open</button>

<!-- Pure CSS with :target -->
<a href="#modal">Open Modal</a>
<div id="modal" class="modal">
  <a href="#" class="close">&times;</a>
  <p>Content</p>
</div>

<style>
.modal { display: none; }
.modal:target { display: flex; }
</style>"""
    },
    {
        "name": "tabs",
        "description": "Tab switching",
        "js_patterns": [
            r'\.tabs?[^a-z]',
            r'tab.*click|click.*tab',
            r'switchTab|changeTab|selectTab',
            r'tabIndex|activeTab|currentTab',
            r'\.tab-content',
        ],
        "severity": "high",
        "solution": "Radio button hack with :checked",
        "explanation": "Hidden radio buttons with labels create accessible tabs. The :checked selector shows the corresponding panel.",
        "before": """tabs.forEach(tab => tab.addEventListener('click', () => {
  tabs.forEach(t => t.classList.remove('active'));
  panels.forEach(p => p.classList.remove('active'));
  tab.classList.add('active');
  document.getElementById(tab.dataset.panel).classList.add('active');
}));""",
        "after": """<div class="tabs">
  <input type="radio" name="tabs" id="tab1" checked>
  <label for="tab1">Tab 1</label>
  <input type="radio" name="tabs" id="tab2">
  <label for="tab2">Tab 2</label>
  
  <div class="panel" id="panel1">Content 1</div>
  <div class="panel" id="panel2">Content 2</div>
</div>

<style>
.panel { display: none; }
#tab1:checked ~ #panel1,
#tab2:checked ~ #panel2 { display: block; }
</style>"""
    },
    {
        "name": "smooth_scroll",
        "description": "Smooth scrolling",
        "js_patterns": [
            r'scrollIntoView.*smooth',
            r'scroll.*behavior.*smooth',
            r'smoothScroll',
            r'animate.*scrollTop',
            r'\$.*animate.*scroll',
            r'window\.scrollTo\(',
        ],
        "severity": "high",
        "solution": "CSS scroll-behavior: smooth",
        "explanation": "Single CSS property enables smooth scrolling for the entire page or specific containers.",
        "before": """document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    e.preventDefault();
    document.querySelector(this.getAttribute('href')).scrollIntoView({
      behavior: 'smooth'
    });
  });
});""",
        "after": """<style>
html { scroll-behavior: smooth; }
/* Or scoped to a container */
.scroll-container { scroll-behavior: smooth; }
</style>

<a href="#section2">Go to Section 2</a>
<section id="section2">...</section>"""
    },
    {
        "name": "carousel_slider",
        "description": "Carousel/slider",
        "js_patterns": [
            r'carousel|slider|swiper|slick',
            r'\.slide\(',
            r'nextSlide|prevSlide|currentSlide',
            r'translateX.*%',
            r'scroll.*snap',
        ],
        "severity": "medium",
        "solution": "CSS scroll-snap",
        "explanation": "CSS scroll-snap creates native carousel behavior. Combine with scroll-behavior: smooth for polished effect.",
        "before": """let currentSlide = 0;
nextBtn.addEventListener('click', () => {
  currentSlide = (currentSlide + 1) % slides.length;
  track.style.transform = 'translateX(-' + (currentSlide * 100) + '%)';
});""",
        "after": """<div class="carousel">
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
}
.slide {
  flex: 0 0 100%;
  scroll-snap-align: start;
}
/* Hide scrollbar but keep functionality */
.carousel { scrollbar-width: none; }
.carousel::-webkit-scrollbar { display: none; }
</style>"""
    },
    {
        "name": "sticky_header",
        "description": "Sticky/fixed header on scroll",
        "js_patterns": [
            r'scroll.*fixed|fixed.*scroll',
            r'sticky.*header|header.*sticky',
            r'scrollY|pageYOffset',
            r'classList.*(sticky|fixed).*scroll',
            r'\.is-sticky',
        ],
        "severity": "high",
        "solution": "CSS position: sticky",
        "explanation": "position: sticky provides scroll-aware positioning without JS. Element sticks when reaching its threshold.",
        "before": """window.addEventListener('scroll', () => {
  if (window.scrollY > 100) {
    header.classList.add('sticky');
  } else {
    header.classList.remove('sticky');
  }
});""",
        "after": """<style>
header {
  position: sticky;
  top: 0;
  z-index: 100;
}
</style>"""
    },
    {
        "name": "dark_mode",
        "description": "Dark mode toggle",
        "js_patterns": [
            r'dark.*mode|theme.*dark|dark.*theme',
            r'prefers-color-scheme',
            r'matchMedia.*dark',
            r'classList.*(dark|light|theme)',
            r'localStorage.*(theme|dark|mode)',
        ],
        "severity": "medium",
        "solution": "CSS prefers-color-scheme + checkbox toggle",
        "explanation": "Use prefers-color-scheme for system preference, optionally with checkbox hack for manual override.",
        "before": """const toggle = document.querySelector('.theme-toggle');
toggle.addEventListener('click', () => {
  document.body.classList.toggle('dark');
  localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
});""",
        "after": """<style>
/* Automatic system preference */
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1a1a1a;
    --text: #ffffff;
  }
}

/* Manual toggle with checkbox */
:root { --bg: white; --text: black; }
#dark-toggle:checked ~ * {
  --bg: #1a1a1a;
  --text: #ffffff;
}
body { background: var(--bg); color: var(--text); }
</style>

<input type="checkbox" id="dark-toggle" hidden>
<label for="dark-toggle">🌙</label>"""
    },
    {
        "name": "form_validation",
        "description": "Form validation styling",
        "js_patterns": [
            r'\.is-valid|\.is-invalid|\.error',
            r'classList.*(valid|invalid|error)',
            r'validate.*form|form.*valid',
            r'checkValidity|reportValidity',
            r'\.setCustomValidity',
        ],
        "severity": "medium",
        "solution": "CSS :valid/:invalid/:user-invalid",
        "explanation": "Native CSS pseudo-classes style form state. :user-invalid (newer) only shows after user interaction.",
        "before": """input.addEventListener('blur', () => {
  if (input.validity.valid) {
    input.classList.remove('invalid');
    input.classList.add('valid');
  } else {
    input.classList.remove('valid');
    input.classList.add('invalid');
  }
});""",
        "after": """<style>
/* Style after user interaction */
input:user-invalid {
  border-color: red;
  background: #fff0f0;
}
input:user-valid {
  border-color: green;
  background: #f0fff0;
}

/* Fallback for older browsers */
input:invalid:not(:placeholder-shown) {
  border-color: red;
}
</style>

<input type="email" placeholder="Email" required>"""
    },
    {
        "name": "tooltip",
        "description": "Hover tooltips",
        "js_patterns": [
            r'\.tooltip',
            r'title.*hover|hover.*title',
            r'mouseenter.*tooltip|tooltip.*mouseenter',
            r'data-tooltip',
            r'tippy|popper',
        ],
        "severity": "high",
        "solution": "CSS ::before/::after with attr()",
        "explanation": "Pure CSS tooltips using pseudo-elements and data attributes. No JS library needed for simple tooltips.",
        "before": """tooltips.forEach(el => {
  el.addEventListener('mouseenter', () => {
    const tip = document.createElement('div');
    tip.className = 'tooltip';
    tip.textContent = el.dataset.tooltip;
    el.appendChild(tip);
  });
});""",
        "after": """<button data-tooltip="Click to save">Save</button>

<style>
[data-tooltip] {
  position: relative;
}
[data-tooltip]::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  padding: 0.5em 1em;
  background: #333;
  color: white;
  border-radius: 4px;
  font-size: 0.875em;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s;
}
[data-tooltip]:hover::after {
  opacity: 1;
}
</style>"""
    },
    {
        "name": "animation_js",
        "description": "JS-driven animations",
        "js_patterns": [
            r'setInterval.*style',
            r'requestAnimationFrame',
            r'\.animate\(',
            r'gsap|anime\.js|velocity',
            r'style\.(transform|opacity|left|top)',
        ],
        "severity": "medium",
        "solution": "CSS @keyframes and transitions",
        "explanation": "CSS animations are GPU-accelerated and more performant than JS. Use for most UI animations.",
        "before": """let opacity = 0;
const fade = setInterval(() => {
  opacity += 0.1;
  element.style.opacity = opacity;
  if (opacity >= 1) clearInterval(fade);
}, 50);""",
        "after": """<style>
.fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Or simpler with transition */
.element {
  opacity: 0;
  transition: opacity 0.5s;
}
.element.visible {
  opacity: 1;
}
</style>"""
    },
    {
        "name": "aspect_ratio_js",
        "description": "Aspect ratio maintenance",
        "js_patterns": [
            r'padding.*bottom.*%',
            r'aspectRatio|aspect-ratio',
            r'height.*=.*width',
            r'resize.*aspect',
        ],
        "severity": "high",
        "solution": "CSS aspect-ratio property",
        "explanation": "Native aspect-ratio property replaces the padding-bottom hack. Well-supported in modern browsers.",
        "before": """// Old padding-bottom hack
const wrapper = document.createElement('div');
wrapper.style.paddingBottom = '56.25%'; // 16:9
wrapper.style.position = 'relative';""",
        "after": """<style>
.video-container {
  aspect-ratio: 16 / 9;
  width: 100%;
}
/* Images */
img {
  aspect-ratio: 4 / 3;
  object-fit: cover;
}
</style>"""
    },
    {
        "name": "container_query_js",
        "description": "Component-based responsive logic",
        "js_patterns": [
            r'ResizeObserver',
            r'getBoundingClientRect.*width',
            r'offsetWidth|clientWidth',
            r'element.*width.*class',
        ],
        "severity": "medium",
        "solution": "CSS @container queries",
        "explanation": "Container queries allow components to respond to their container's size, not viewport. Modern alternative to ResizeObserver.",
        "before": """const observer = new ResizeObserver(entries => {
  entries.forEach(entry => {
    if (entry.contentRect.width < 400) {
      entry.target.classList.add('compact');
    } else {
      entry.target.classList.remove('compact');
    }
  });
});
observer.observe(container);""",
        "after": """<style>
.card-container {
  container-type: inline-size;
}
.card {
  display: grid;
  grid-template-columns: 1fr 2fr;
}
@container (max-width: 400px) {
  .card {
    grid-template-columns: 1fr;
  }
}
</style>"""
    },
    {
        "name": "counter_numbering",
        "description": "Auto-numbering elements",
        "js_patterns": [
            r'\.forEach.*index',
            r'counter|numbering',
            r'textContent.*=.*\d',
            r'step.*number|number.*step',
        ],
        "severity": "high",
        "solution": "CSS counter-increment",
        "explanation": "CSS counters automatically number elements. Works with nested structures too.",
        "before": """document.querySelectorAll('.step').forEach((step, i) => {
  step.querySelector('.number').textContent = i + 1;
});""",
        "after": """<style>
.steps { counter-reset: step; }
.step::before {
  counter-increment: step;
  content: counter(step) ". ";
  font-weight: bold;
}
/* Nested counters */
ol { counter-reset: section; }
li::marker {
  content: counters(section, ".") " ";
  counter-increment: section;
}
</style>"""
    },
    {
        "name": "view_transitions",
        "description": "Page transition animations",
        "js_patterns": [
            r'page.*transition|transition.*page',
            r'navigate.*animate|animate.*navigate',
            r'startViewTransition',
            r'route.*animation',
        ],
        "severity": "low",
        "solution": "View Transitions API (CSS + minimal JS)",
        "explanation": "View Transitions API provides native page transitions. Astro has built-in support via <ViewTransitions />.",
        "before": """// Complex manual implementation
async function navigate(url) {
  document.body.classList.add('fade-out');
  await new Promise(r => setTimeout(r, 300));
  const html = await fetch(url).then(r => r.text());
  document.body.innerHTML = html;
  document.body.classList.add('fade-in');
}""",
        "after": """---
// In Astro layout
import { ViewTransitions } from 'astro:transitions';
---
<head>
  <ViewTransitions />
</head>

<style>
/* Customize transitions */
::view-transition-old(root) {
  animation: fade-out 0.3s ease-out;
}
::view-transition-new(root) {
  animation: fade-in 0.3s ease-in;
}
</style>"""
    },
    {
        "name": "scroll_driven_animation",
        "description": "Scroll-triggered animations",
        "js_patterns": [
            r'IntersectionObserver',
            r'scroll.*animate|animate.*scroll',
            r'scrollY.*style',
            r'onscroll.*class',
            r'aos|scrollreveal|wow\.js',
        ],
        "severity": "medium",
        "solution": "CSS scroll-driven animations (emerging)",
        "explanation": "CSS scroll() and view() timelines enable scroll-linked animations. Fallback to IntersectionObserver for older browsers.",
        "before": """const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('animate');
    }
  });
});
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));""",
        "after": """<style>
/* Modern scroll-driven animation */
@supports (animation-timeline: view()) {
  .reveal {
    animation: reveal linear both;
    animation-timeline: view();
    animation-range: entry 0% cover 40%;
  }
  @keyframes reveal {
    from { opacity: 0; transform: translateY(50px); }
    to { opacity: 1; transform: translateY(0); }
  }
}

/* Fallback: still use IntersectionObserver */
@supports not (animation-timeline: view()) {
  .reveal { opacity: 0; transition: all 0.5s; }
  .reveal.visible { opacity: 1; }
}
</style>"""
    },
]


def analyze_file(file_path: Path, project_path: Path) -> list[JsToHtmlCssFinding]:
    """Analyze a single file for JS patterns replaceable with CSS/HTML."""
    findings = []
    
    try:
        content = file_path.read_text(errors='ignore')
    except Exception:
        return findings
    
    for pattern_def in PATTERNS:
        for js_pattern in pattern_def["js_patterns"]:
            matches = list(re.finditer(js_pattern, content, re.IGNORECASE))
            
            if matches:
                # Get the first match for evidence
                match = matches[0]
                line_num = content[:match.start()].count('\n') + 1
                
                # Extract surrounding context (the line containing the match)
                lines = content.split('\n')
                evidence_line = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                findings.append(JsToHtmlCssFinding(
                    pattern=pattern_def["name"],
                    severity=pattern_def["severity"],
                    file=str(file_path.relative_to(project_path)),
                    line=line_num,
                    evidence=evidence_line[:100] + ("..." if len(evidence_line) > 100 else ""),
                    html_css_solution=pattern_def["solution"],
                    explanation=pattern_def["explanation"],
                    example_before=pattern_def["before"],
                    example_after=pattern_def["after"]
                ))
                break  # Only report once per pattern per file
    
    return findings


def analyze_project(project_path: str) -> dict:
    """Analyze entire project for JS-to-CSS/HTML opportunities."""
    path = Path(project_path).resolve()
    src_path = path / "src"
    
    all_findings = []
    
    # File patterns to analyze
    extensions = [".js", ".ts", ".jsx", ".tsx", ".astro", ".vue", ".svelte"]
    
    for ext in extensions:
        for file in src_path.rglob(f"*{ext}"):
            # Skip node_modules and build directories
            if "node_modules" in str(file) or "dist" in str(file):
                continue
            
            findings = analyze_file(file, path)
            all_findings.extend(findings)
    
    # Also check inline scripts in HTML
    for html_file in src_path.rglob("*.html"):
        findings = analyze_file(html_file, path)
        all_findings.extend(findings)
    
    # Deduplicate by pattern+file
    seen = set()
    unique_findings = []
    for f in all_findings:
        key = (f.pattern, f.file)
        if key not in seen:
            seen.add(key)
            unique_findings.append(f)
    
    # Summary
    summary = {
        "total": len(unique_findings),
        "by_severity": {
            "high": len([f for f in unique_findings if f.severity == "high"]),
            "medium": len([f for f in unique_findings if f.severity == "medium"]),
            "low": len([f for f in unique_findings if f.severity == "low"]),
        },
        "by_pattern": {}
    }
    
    for f in unique_findings:
        summary["by_pattern"][f.pattern] = summary["by_pattern"].get(f.pattern, 0) + 1
    
    return {
        "findings": [asdict(f) for f in unique_findings],
        "summary": summary,
        "patterns_detected": list(summary["by_pattern"].keys())
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: detect_js_patterns.py <project-path>", file=sys.stderr)
        sys.exit(1)
    
    project_path = sys.argv[1]
    
    if not Path(project_path).exists():
        print(f"Error: Path does not exist: {project_path}", file=sys.stderr)
        sys.exit(1)
    
    result = analyze_project(project_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
