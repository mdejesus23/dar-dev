import ogImageSrc from '@/images/default-og.png';

export const SITE = {
  title: 'dar.dev - Custom Software & Web Solutions',
  tagline: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
  description:
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed vitae nisl vel mauris consequat placerat non ut lectus. Suspendisse potenti.',
  description_short: 'Lorem ipsum dolor sit amet.',
  url: 'https://loremipsumstore.com',
  author: 'Dar Arish',
};

export const ISPARTOF = {
  '@type': 'WebSite',
  url: SITE.url,
  name: SITE.title,
  description: SITE.description,
};

export const SEO = {
  title: SITE.title,
  description: SITE.description,
  structuredData: {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    inLanguage: 'en-US',
    '@id': SITE.url,
    url: SITE.url,
    name: SITE.title,
    description: SITE.description,
    isPartOf: ISPARTOF,
  },
};

export const OG = {
  locale: 'en_US',
  type: 'website',
  url: SITE.url,
  title: SITE.title,
  description:
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla facilisi. Cras non ligula eget erat convallis porttitor.',
  image: ogImageSrc,
};
