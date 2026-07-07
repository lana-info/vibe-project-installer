# Deployment Plan

Selected plan: {{DEPLOYMENT_PLAN}}

Project creation does not deploy anything and does not create paid cloud resources. Use this file when the product is ready for a launch plan.

## What This Choice Means

- `Decide later`: keep the project provider-neutral until the product shape is clearer.
- `Hetzner`: plan for VPS/server deployment, usually Docker, Postgres, backups, firewall, domains, and monitoring.
- `Timeweb`: plan for Timeweb Cloud/VPS with the same production concerns: backend, database, static frontend, files, backups, logs.
- `DigitalOcean`: upstream has the most detailed runbooks for App Platform, Managed Postgres, Static Sites, Spaces/CDN, worker, and cron.
- `Hostinger`: plan for Hostinger VPS/hosting; verify Node/Bun, database, process manager, SSL, backups, and deployment workflow.
- `Custom hosting`: choose the target later: Render, Railway, Vercel, Netlify, Fly.io, self-hosted VPS, or another provider.

## Before Launch

- [ ] Decide where backend/API runs.
- [ ] Decide where webapp/website static assets run.
- [ ] Decide where production Postgres lives.
- [ ] Decide where uploads/media live, if the project has files.
- [ ] Decide how background jobs and cron run, if selected.
- [ ] Define domains, SSL, backups, logs, monitoring, and rollback.
- [ ] Keep secrets in the hosting provider's secret/env settings, not in git or chat.

