declare module 'astro:content' {
	interface Render {
		'.md': Promise<{
			Content: import('astro').MarkdownInstance<{}>['Content'];
			headings: import('astro').MarkdownHeading[];
			remarkPluginFrontmatter: Record<string, any>;
		}>;
	}
}

declare module 'astro:content' {
	export { z } from 'astro/zod';
	export type CollectionEntry<C extends keyof typeof entryMap> =
		(typeof entryMap)[C][keyof (typeof entryMap)[C]];

	// TODO: Remove this when having this fallback is no longer relevant. 2.3? 3.0? - erika, 2023-04-04
	/**
	 * @deprecated
	 * `astro:content` no longer provide `image()`.
	 *
	 * Please use it through `schema`, like such:
	 * ```ts
	 * import { defineCollection, z } from "astro:content";
	 *
	 * defineCollection({
	 *   schema: ({ image }) =>
	 *     z.object({
	 *       image: image(),
	 *     }),
	 * });
	 * ```
	 */
	export const image: never;

	// This needs to be in sync with ImageMetadata
	export type ImageFunction = () => import('astro/zod').ZodObject<{
		src: import('astro/zod').ZodString;
		width: import('astro/zod').ZodNumber;
		height: import('astro/zod').ZodNumber;
		format: import('astro/zod').ZodUnion<
			[
				import('astro/zod').ZodLiteral<'png'>,
				import('astro/zod').ZodLiteral<'jpg'>,
				import('astro/zod').ZodLiteral<'jpeg'>,
				import('astro/zod').ZodLiteral<'tiff'>,
				import('astro/zod').ZodLiteral<'webp'>,
				import('astro/zod').ZodLiteral<'gif'>,
				import('astro/zod').ZodLiteral<'svg'>
			]
		>;
	}>;

	type BaseSchemaWithoutEffects =
		| import('astro/zod').AnyZodObject
		| import('astro/zod').ZodUnion<import('astro/zod').AnyZodObject[]>
		| import('astro/zod').ZodDiscriminatedUnion<string, import('astro/zod').AnyZodObject[]>
		| import('astro/zod').ZodIntersection<
				import('astro/zod').AnyZodObject,
				import('astro/zod').AnyZodObject
		  >;

	type BaseSchema =
		| BaseSchemaWithoutEffects
		| import('astro/zod').ZodEffects<BaseSchemaWithoutEffects>;

	export type SchemaContext = { image: ImageFunction };

	type BaseCollectionConfig<S extends BaseSchema> = {
		schema?: S | ((context: SchemaContext) => S);
	};
	export function defineCollection<S extends BaseSchema>(
		input: BaseCollectionConfig<S>
	): BaseCollectionConfig<S>;

	type EntryMapKeys = keyof typeof entryMap;
	type AllValuesOf<T> = T extends any ? T[keyof T] : never;
	type ValidEntrySlug<C extends EntryMapKeys> = AllValuesOf<(typeof entryMap)[C]>['slug'];

	export function getEntryBySlug<
		C extends keyof typeof entryMap,
		E extends ValidEntrySlug<C> | (string & {})
	>(
		collection: C,
		// Note that this has to accept a regular string too, for SSR
		entrySlug: E
	): E extends ValidEntrySlug<C>
		? Promise<CollectionEntry<C>>
		: Promise<CollectionEntry<C> | undefined>;
	export function getCollection<C extends keyof typeof entryMap, E extends CollectionEntry<C>>(
		collection: C,
		filter?: (entry: CollectionEntry<C>) => entry is E
	): Promise<E[]>;
	export function getCollection<C extends keyof typeof entryMap>(
		collection: C,
		filter?: (entry: CollectionEntry<C>) => unknown
	): Promise<CollectionEntry<C>[]>;

	type ReturnTypeOrOriginal<T> = T extends (...args: any[]) => infer R ? R : T;
	type InferEntrySchema<C extends keyof typeof entryMap> = import('astro/zod').infer<
		ReturnTypeOrOriginal<Required<ContentConfig['collections'][C]>['schema']>
	>;

	const entryMap: {
		"blog": {
"2020-11-29-hello-world/index.md": {
  id: "2020-11-29-hello-world/index.md",
  slug: "2020-11-29-hello-world",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2020-12-13-python-testing-unittest/index.md": {
  id: "2020-12-13-python-testing-unittest/index.md",
  slug: "2020-12-13-python-testing-unittest",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2021-08-16-exponentialGrowth/index.md": {
  id: "2021-08-16-exponentialGrowth/index.md",
  slug: "2021-08-16-exponentialgrowth",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2021-09-05-sorting/index.md": {
  id: "2021-09-05-sorting/index.md",
  slug: "2021-09-05-sorting",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2021-10-04-chart-js/index.md": {
  id: "2021-10-04-chart-js/index.md",
  slug: "2021-10-04-chart-js",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2021-11-01-unbiased-estimation/index.md": {
  id: "2021-11-01-unbiased-estimation/index.md",
  slug: "2021-11-01-unbiased-estimation",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2021-12-06-versioning/index.md": {
  id: "2021-12-06-versioning/index.md",
  slug: "2021-12-06-versioning",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2022-04-04-python-finally/index.md": {
  id: "2022-04-04-python-finally/index.md",
  slug: "2022-04-04-python-finally",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2022-05-02-bayesian-update-problem/index.md": {
  id: "2022-05-02-bayesian-update-problem/index.md",
  slug: "2022-05-02-bayesian-update-problem",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2022-07-04-solving-odes-with-python/index.md": {
  id: "2022-07-04-solving-odes-with-python/index.md",
  slug: "2022-07-04-solving-odes-with-python",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2022-08-01-curve-fitting/index.md": {
  id: "2022-08-01-curve-fitting/index.md",
  slug: "2022-08-01-curve-fitting",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2022-09-05-binomialUpdate/index.md": {
  id: "2022-09-05-binomialUpdate/index.md",
  slug: "2022-09-05-binomialupdate",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2022-10-03-ranking/index.md": {
  id: "2022-10-03-ranking/index.md",
  slug: "2022-10-03-ranking",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2022-11-07-decorators/index.md": {
  id: "2022-11-07-decorators/index.md",
  slug: "2022-11-07-decorators",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2022-12-05-inferring-extinction/index.md": {
  id: "2022-12-05-inferring-extinction/index.md",
  slug: "2022-12-05-inferring-extinction",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2023-01-02-graphql-cypress/index.md": {
  id: "2023-01-02-graphql-cypress/index.md",
  slug: "2023-01-02-graphql-cypress",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2023-02-06-labelling-ggplot/index.md": {
  id: "2023-02-06-labelling-ggplot/index.md",
  slug: "2023-02-06-labelling-ggplot",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2023-03-06-solving-ivps-with-desolve/index.md": {
  id: "2023-03-06-solving-ivps-with-desolve/index.md",
  slug: "2023-03-06-solving-ivps-with-desolve",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2023-04-03-logistic-growth/index.md": {
  id: "2023-04-03-logistic-growth/index.md",
  slug: "2023-04-03-logistic-growth",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2023-05-01-harvesting-methods/index.md": {
  id: "2023-05-01-harvesting-methods/index.md",
  slug: "2023-05-01-harvesting-methods",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2023-06-20-simple-bayesian-workflow/index.md": {
  id: "2023-06-20-simple-bayesian-workflow/index.md",
  slug: "2023-06-20-simple-bayesian-workflow",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2023-10-14-creating-dataframes-the-bad-way/index.md": {
  id: "2023-10-14-creating-dataframes-the-bad-way/index.md",
  slug: "2023-10-14-creating-dataframes-the-bad-way",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2023-10-21-melting-dataframes/index.md": {
  id: "2023-10-21-melting-dataframes/index.md",
  slug: "2023-10-21-melting-dataframes",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2023-11-11-typescript-type-predicates/index.md": {
  id: "2023-11-11-typescript-type-predicates/index.md",
  slug: "2023-11-11-typescript-type-predicates",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
"2023-11-18-sorting-in-python/index.md": {
  id: "2023-11-18-sorting-in-python/index.md",
  slug: "2023-11-18-sorting-in-python",
  body: string,
  collection: "blog",
  data: InferEntrySchema<"blog">
} & { render(): Render[".md"] },
},

	};

	type ContentConfig = typeof import("../src/content/config");
}
