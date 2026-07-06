# Upstream Vibe Feature Options

Snapshot date: 2026-07-06.

Source checked:

- `di-sukharev/vibe` `master`
- `di-sukharev/vibe` `mobile`

## Current Installer Choices

- Surfaces: `web`, `mobile`, `backend`, `landing`, `full-stack`.
- Hosting is not shown in the GUI. The app creates projects in provider-neutral mode by default.
- Default project type should be shown as `mobile + web`. Under the hood it includes `backend` as API support for auth, data, and app logic.
- When `mobile` is active, use the upstream `mobile` branch. The `master` branch has only a mobile pointer README.

## What Hosting Currently Means Internally

Hosting does not install a cloud provider locally. The GUI hides this choice and uses `custom` by default.

- `custom`: provider-neutral. Choose deployment later.
- `none`: local-only. Do not configure deployment.
- `digitalocean`: keep the DigitalOcean deployment runbook active.

DigitalOcean support in upstream includes:

- App Platform specs under `.do`.
- `scripts/prepare-do-specs.mjs` to generate concrete specs into `.scratch/deploy`.
- Backend API service sizing via `DO_API_INSTANCE_SIZE_SLUG` and `DO_API_INSTANCE_COUNT`.
- Managed PostgreSQL.
- Static Site deployment for `webapp` and static `website`.
- Optional backend worker through `DO_BACKEND_WORKER_ENABLED`.
- Optional backend cron through `DO_BACKEND_CRON_*`.
- Spaces/CDN guidance for uploads and media.

## Good Next Feature Toggles

These should be product/intake toggles first. They should write a bootstrap plan and setup checklist before they remove or rewrite template code.

- Accounts/auth: baseline exists in backend, webapp, and mobile.
- Database/persistence: baseline PostgreSQL and Prisma exist.
- Uploads/media: storage service and DigitalOcean Spaces docs exist.
- Payments/subscriptions: mobile branch has App Store and Google Play IAP foundation plus backend verification.
- Social auth: mobile branch has Apple and Google social auth docs and code.
- Push notifications: mobile branch has Expo Push foundation and backend notification outbox.
- Admin tools: not a dedicated upstream module; should be a generated product scope/checklist.
- Realtime/chat/presence: not implemented as a ready module; upstream docs recommend Redis-compatible Pub/Sub only when horizontal scaling needs fanout.
- Deployment extras: backend worker, backend cron, API instance size/count, static website/webapp release, storage/CDN.

## Suggested UI Grouping

- Project type: `mobile + web` default, `web only`, `mobile only`, `landing/public site`, `full-stack`.
- Core capabilities: auth, database, uploads/media, payments/subscriptions, social auth, push notifications, admin, realtime.
- Cloud/deployment settings should stay out of the first GUI unless the user asks to plan launch.
