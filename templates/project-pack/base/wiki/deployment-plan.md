# Deployment Plan

Selected plan: {{DEPLOYMENT_PLAN}}

Project creation does not deploy anything and does not create paid cloud resources. Use this file when the product is ready for a launch plan.

## What This Choice Means

- `Decide later`: keep the project provider-neutral until the product shape is clearer.
- `Hetzner`: plan with `wiki/deployment-providers/hetzner.md`.
- `Timeweb`: plan with `wiki/deployment-providers/timeweb.md`.
- `DigitalOcean`: upstream has the most detailed runbooks for App Platform, Managed Postgres, Static Sites, Spaces/CDN, worker, and cron.
- `Hostinger`: plan with `wiki/deployment-providers/hostinger.md`.
- `Custom hosting`: choose the target later: Render, Railway, Vercel, Netlify, Fly.io, self-hosted VPS, or another provider.

## Before Launch

- [ ] Decide where backend/API runs.
- [ ] Decide where webapp/website static assets run.
- [ ] Decide where production Postgres lives.
- [ ] Decide where uploads/media live, if the project has files.
- [ ] Decide how background jobs and cron run, if selected.
- [ ] Define domains, SSL, backups, logs, monitoring, and rollback.
- [ ] Keep secrets in the hosting provider's secret/env settings, not in git or chat.

## Provider Notes

- Hetzner: good fit for VPS/server-style deployment where you control Docker, Postgres, firewall, backups, and monitoring.
- Timeweb: can be either App Platform-style deployment from a repository or VPS/cloud-server deployment.
- Hostinger: can be managed Node.js Web Apps for simpler web apps, or VPS/Docker for full backend/database control.
- DigitalOcean: upstream template already includes the deepest provider-specific runbook in `docs/DEPLOYMENT.md`.
