# Hostinger Deployment Notes

Use this when the project will run on Hostinger.

## Good Fit

- You want a simpler managed web app path for Node.js/web apps, or
- You want VPS/Docker control with Hostinger's VPS tooling.

## Typical Shapes

### Managed Web Apps Path

- Use for simpler Node.js/web apps when Hostinger's Web Apps Hosting supports the build/runtime.
- Connect GitHub or upload a build according to the selected plan.
- Keep env/secrets in Hostinger settings.
- Verify whether backend, database, worker, cron, and uploads fit this path before choosing it.

### VPS / Docker Path

- Backend/API: Docker container or Node/Bun process on VPS.
- Webapp/website: static build served by Nginx/Caddy or a managed web app if split.
- Database: Postgres on VPS, one-click PostgreSQL/Docker setup, or external managed database.
- Uploads/media: S3-compatible storage or another durable object storage provider.
- Worker/cron: separate container/process and host scheduler.

## Launch Checklist

- [ ] Choose Managed Web Apps or VPS/Docker path.
- [ ] Verify Node/Bun support and build commands.
- [ ] Decide where Postgres runs and how backups work.
- [ ] Decide where durable uploads/media live.
- [ ] Configure domain, SSL, firewall, and redirects.
- [ ] Store env/secrets outside git and chat.
- [ ] Add uptime checks and log access.
- [ ] Document rollback and restore steps.

## Official Docs

- https://www.hostinger.com/support/how-to-deploy-a-nodejs-website-in-hostinger/
- https://www.hostinger.com/web-apps-hosting
- https://www.hostinger.com/support/vps/
- https://www.hostinger.com/applications/postgresql

