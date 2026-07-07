# Hetzner Deployment Notes

Use this when the project will run on Hetzner Cloud or a Hetzner server.

## Good Fit

- You want VPS/server control and predictable infrastructure.
- You are comfortable with Docker, SSH, firewall rules, backups, and monitoring.
- The project needs backend/API, Postgres, uploads, worker, or cron under your control.

## Typical Shape

- Backend/API: Docker container on a cloud server.
- Webapp/website: static build served by Nginx/Caddy or a separate static hosting path.
- Database: Postgres on the server for small projects, or a separate managed/self-managed database host for production.
- Uploads/media: S3-compatible object storage if available for the chosen account/region, otherwise an external S3-compatible provider.
- Background jobs: separate worker process/container.
- Cron: host scheduler or a dedicated cron container.

## Launch Checklist

- [ ] Choose server region and size.
- [ ] Create SSH keys and disable password login.
- [ ] Configure firewall: only SSH, HTTP, HTTPS, and required private ports.
- [ ] Decide whether Postgres is on-server or external.
- [ ] Configure backups/snapshots before production traffic.
- [ ] Configure domain DNS and SSL.
- [ ] Store production env/secrets outside git and chat.
- [ ] Add monitoring for uptime, disk, memory, CPU, logs, and failed jobs.
- [ ] Document rollback: previous image, previous git commit, database restore point.

## Official Docs

- https://docs.hetzner.com/cloud/
- https://docs.hetzner.cloud/

