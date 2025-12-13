import { z, defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';

const serviceCollection = defineCollection({
  loader: glob({ pattern: '**/index.mdx', base: './src/data/services' }),
  schema: ({ image }) =>
    z.object({
      title: z.string().min(1),
      description: z.string().min(1),
      icon: image(),
      image: image(),
      order: z.number().optional(),
    }),
});

const industryCollection = defineCollection({
  loader: glob({ pattern: '**/index.mdx', base: './src/data/industries' }),
  schema: ({ image }) =>
    z.object({
      name: z.string().min(1),
      description: z.string().optional(),
      icon: image(),
      image: image(),
      position: z.string().optional(),
      order: z.number().optional(),
    }),
});

export const collections = {
  services: serviceCollection,
  industries: industryCollection,
};
