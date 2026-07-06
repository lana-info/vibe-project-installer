# Marketplace / Catalog

Use this feature pack if the product has public listings, products, search pages, sellers, categories, SEO pages, or shareable item pages.

## Upstream Support

The template separates `website` for public SEO pages from `webapp` for logged-in workflows. Marketplaces usually need both.

## Product Questions

- What is listed: products, services, files, creators, courses, or something else?
- Who creates listings?
- What pages must be public and SEO-friendly?
- What filters/search/sorting are needed?
- What actions require login?

## Setup Checklist

- [ ] Put public SEO listing/catalog pages in `website`.
- [ ] Put authenticated account/admin/seller flows in `webapp`.
- [ ] Define listing schema and moderation rules.
- [ ] Add tests for public/private data separation.

