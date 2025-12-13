# DAR Development - Business Website

A modern, high-performance business website built with Astro, showcasing software development services and industry expertise. This project features a content-driven architecture with Astro's content collections for managing services and industries.

## 🚀 Tech Stack

- **Framework**: [Astro 5.16.4](https://astro.build)
- **Styling**: [Tailwind CSS 4.1.17](https://tailwindcss.com)
- **Content**: MDX with Astro Content Collections
- **Fonts**: IBM Plex Sans, Questrial, Space Mono
- **Code Quality**: Prettier with Astro and Tailwind plugins

## 📁 Project Structure

```text
/
├── public/                    # Static assets
├── src/
│   ├── components/
│   │   ├── global/           # Global components (Header, Footer, etc.)
│   │   ├── home/             # Homepage components
│   │   │   ├── HeroWithService.astro
│   │   │   ├── Industries.astro
│   │   │   ├── Empowering.astro
│   │   │   └── ...
│   │   ├── services/         # Service-related components
│   │   ├── ui/               # Reusable UI components (Button, etc.)
│   │   └── ...
│   ├── data/
│   │   ├── industries/       # Industry content collections
│   │   │   ├── retail/
│   │   │   ├── wholesale/
│   │   │   ├── 3pl/
│   │   │   ├── warehouse/
│   │   │   └── b2b-services/
│   │   ├── services/         # Service content collections
│   │   │   ├── web-applications/
│   │   │   ├── systems-integration/
│   │   │   ├── process-automation/
│   │   │   └── ...
│   │   └── constants.ts
│   ├── images/               # Image assets
│   │   ├── icons/
│   │   ├── shapes/
│   │   └── ...
│   ├── layouts/              # Page layouts
│   ├── pages/                # Astro pages
│   │   ├── index.astro
│   │   ├── services/
│   │   │   ├── index.astro
│   │   │   └── [id].astro
│   │   ├── industries/
│   │   │   ├── index.astro
│   │   │   └── [id].astro
│   │   └── 404.astro
│   ├── scripts/              # Client-side scripts
│   │   └── carousel.ts
│   ├── styles/               # Global styles
│   └── content.config.ts     # Content collections configuration
├── astro.config.mjs
├── tailwind.config.mjs
└── package.json
```

## ✨ Features

### Content Collections
- **Services**: Managed via MDX files in `/src/data/services/`
  - Each service has its own directory with `index.mdx`, `icon.svg`, and `image.png`
  - Schema includes: title, description, icon, image, and order

- **Industries**: Managed via MDX files in `/src/data/industries/`
  - Each industry has its own directory with `index.mdx`, `icon.svg`, and `image.png`
  - Schema includes: name, description, icon, image, position, and order

### Components
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Hero Section**: Full-screen hero with background image and service cards
- **Services Carousel**: Interactive carousel with navigation arrows and dots
- **Industries Grid**: Responsive grid layout with floating positioning on desktop
- **Reusable UI**: Button component with multiple variants (primary, secondary, outline)

### Performance
- **Static Site Generation**: Pre-rendered pages for optimal performance
- **Image Optimization**: Astro's built-in image optimization
- **Modern CSS**: Tailwind CSS 4.x with Vite plugin

## 🧞 Commands

All commands are run from the root of the project:

| Command | Action |
|:--------|:-------|
| `npm install` | Install dependencies |
| `npm run dev` | Start local dev server at `localhost:4321` |
| `npm run build` | Build production site to `./dist/` |
| `npm run preview` | Preview build locally before deploying |
| `npm run astro ...` | Run Astro CLI commands |

## 🎨 Adding New Content

### Adding a New Service

1. Create a new directory in `/src/data/services/your-service-name/`
2. Add the following files:
   - `index.mdx` - Service content and metadata
   - `icon.svg` - Service icon
   - `image.png` - Service hero image

Example `index.mdx`:
```mdx
---
title: 'Your Service Name'
description: 'Brief description of your service'
icon: './icon.svg'
image: './image.png'
order: 6
---

# Your Service Name

Detailed description of your service...
```

### Adding a New Industry

1. Create a new directory in `/src/data/industries/your-industry-name/`
2. Add the following files:
   - `index.mdx` - Industry content and metadata
   - `icon.svg` - Industry icon
   - `image.png` - Industry image

Example `index.mdx`:
```mdx
---
name: 'Your Industry'
description: 'Brief description'
icon: './icon.svg'
image: './image.png'
position: 'top-0 left-0'
order: 6
---

# Your Industry

Detailed description of your industry expertise...
```

## 🎯 Content Collection Schema

### Services Collection
- `title`: string (required) - Service title
- `description`: string (required) - Short description
- `icon`: image (required) - Service icon
- `image`: image (required) - Service hero image
- `order`: number (optional) - Display order

### Industries Collection
- `name`: string (required) - Industry name
- `description`: string (optional) - Short description
- `icon`: image (required) - Industry icon
- `image`: image (required) - Industry image
- `position`: string (optional) - CSS positioning for desktop layout
- `order`: number (optional) - Display order

## 🎨 Customization

### Fonts
The project uses three font families:
- **Headline**: IBM Plex Sans (variable)
- **Body**: Questrial
- **Supporting**: Space Mono

To change fonts, update imports in your layout files and Tailwind configuration.

### Colors
Primary colors are defined in the Tailwind configuration. Update `tailwind.config.mjs` to customize the color palette.

### Components
All reusable components are in `/src/components/ui/`. Modify these to match your brand guidelines.

## 📦 Dependencies

### Core
- `astro` - Web framework
- `tailwindcss` - CSS framework
- `@tailwindcss/vite` - Tailwind Vite integration

### Astro Integrations
- `@astrojs/mdx` - MDX support
- `@astrojs/sitemap` - Sitemap generation

### Styling
- `@tailwindcss/typography` - Typography plugin
- Font packages (IBM Plex Sans, Questrial, Space Mono)

### Development
- `prettier` - Code formatter
- `prettier-plugin-astro` - Astro formatting
- `prettier-plugin-tailwindcss` - Tailwind class sorting

## 📝 License

This project is proprietary and confidential.

## 🤝 Contributing

For internal development team only. Please follow the established code style and component patterns when contributing.

## 📞 Support

For questions or issues, contact the development team.
