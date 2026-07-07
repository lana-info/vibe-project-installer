# Timeweb Deployment Notes

Use this when the project will run on Timeweb Cloud.

## Good Fit

- You want Russian-language hosting/docs and Timeweb account infrastructure.
- You may choose either App Platform-style deployment from a repository or a VPS/cloud-server deployment.
- The project may need cloud servers, managed databases, S3 object storage, domains, and SSL.

## Typical Shapes

### App Platform Path

- Backend/API: deploy from Git repository if the runtime and build commands fit.
- Webapp/website: deploy static build or app build from repository.
- Env/secrets: store in Timeweb settings, not in repo.
- Good for simpler deployment when the platform supports the build/runtime cleanly.

### VPS / Cloud Server Path

- Backend/API: Docker container or process managed on the server.
- Webapp/website: static build served by Nginx/Caddy.
- Database: managed database or Postgres on a separate protected server.
- Uploads/media: Timeweb S3/object storage when files are in scope.
- Worker/cron: separate container/process plus provider/server scheduler.

## Launch Checklist

- [ ] Choose App Platform or VPS path.
- [ ] Verify Bun/Node version and build commands.
- [ ] Decide database location and backup policy.
- [ ] Decide object storage for uploads/media.
- [ ] Configure domain, SSL, redirects, and CORS.
- [ ] Store env/secrets in provider settings.
- [ ] Add logs and monitoring.
- [ ] Document rollback and database restore process.

## Official Docs

- https://timeweb.cloud/docs/apps
- https://timeweb.cloud/tutorials/cloud
- https://github.com/timeweb-cloud/twc

