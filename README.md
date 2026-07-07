# Vibe Project Installer

Small installer wrapper for creating new projects from the `di-sukharev/vibe` template.

Use the Python CLI for day-to-day project creation. It calls the PowerShell installer under `scripts/bootstrap-project.ps1`.

The goal is to keep project startup simple:

- create a fresh project folder;
- choose active surfaces: `web`, `mobile`, `backend`, `landing`, or `full-stack`;
- record the bootstrap plan in the generated project README;
- create starter workflow files from `templates/project-pack`;
- add frontend design guidance for shadcn-style web components and a small custom mobile component library;
- add optional feature checklists and prompts for payments, uploads/media, social auth, push notifications, background jobs, cron, E2E tests, admin, realtime, marketplace/catalog, and AI features;
- record a documentation-only deployment plan: decide later, Hetzner, Timeweb, DigitalOcean, Hostinger, or custom hosting;
- remove the template Git remote by default so new projects do not push back to upstream.

## Quick Start

Create a mobile + web project with the Python CLI:

```powershell
python .\scripts\create-vibe-project.py `
  --target-path "D:\WorkOS\My App" `
  --project-name "My App" `
  --active-surfaces web,mobile,backend
```

Create a web/backend project from upstream:

```powershell
.\scripts\bootstrap-project.ps1 `
  -SourceUrl "https://github.com/di-sukharev/vibe.git" `
  -Branch master `
  -TargetPath "D:\WorkOS\My App" `
  -ProjectName "My App" `
  -ActiveSurfaces web,backend
```

Create from the mobile branch:

```powershell
.\scripts\bootstrap-project.ps1 `
  -SourceUrl "https://github.com/di-sukharev/vibe.git" `
  -Branch mobile `
  -TargetPath "D:\WorkOS\My Mobile App" `
  -ProjectName "My Mobile App" `
  -ActiveSurfaces mobile,backend
```

Create from a local checkout by running the script inside a local `vibe` repo copy:

```powershell
.\scripts\bootstrap-project.ps1 `
  -TargetPath "D:\WorkOS\My Local App" `
  -ProjectName "My Local App" `
  -ActiveSurfaces full-stack
```

## Cloud Deployment

Project creation does not configure hosting or create cloud resources. Decide deployment later when the product is ready to launch.

The GUI can record a deployment plan for project docs: `Decide later`, `Hetzner`, `Timeweb`, `DigitalOcean`, `Hostinger`, or `Custom hosting`. This only writes checklists and prompts. It does not deploy, connect accounts, or create paid resources.

Generated projects include provider notes for Hetzner, Timeweb, and Hostinger under `wiki/deployment-providers/`.

## Project Pack

The app code comes from `di-sukharev/vibe`. The working instructions, checklists, and prompts come from this installer repo:

- `templates/project-pack/base` - copied into every new project.
- `templates/project-pack/features` - copied only for selected feature checkboxes.

In the GUI, the documentation checkbox is on the `Проект` tab. Optional feature packs are on the `Доп. функции` tab.

## Template Remote

By default, the generated project removes the original `di-sukharev/vibe` Git remote. Leave it that way for normal new projects.

The GUI does not expose this setting because normal projects should not keep the template remote. The advanced CLI flag `--keep-template-remote` is only for intentionally working on the upstream template itself.

## Upstream Archive

The app creates new projects from the online upstream repo by default. Keep a local archive next to this installer for reference and updates:

```powershell
.\scripts\sync-upstream-archive.ps1
```

Default archive path: `D:\WorkOS\vibe-upstream-archive`.

## Verification

Run a local smoke install into a scratch folder:

```powershell
$target = Join-Path $PWD ".scratch\vibe-installer-smoke"
if (Test-Path $target) { Remove-Item -LiteralPath $target -Recurse -Force }
.\scripts\bootstrap-project.ps1 -SourceUrl "https://github.com/di-sukharev/vibe.git" -Branch master -TargetPath $target -ProjectName "Smoke App" -ActiveSurfaces web,backend
Test-Path (Join-Path $target "README.md")
Test-Path (Join-Path $target "backend\README.md")
Test-Path (Join-Path $target "PRD.md")
Test-Path (Join-Path $target "prompts\code-review.md")
```

## Knowledge Base

See `wiki/knowledge-base.md` for the maintainer notes, behavior summary, and change checklist.

## Current Scope

This repo owns only the installer wrapper and workflow docs. It does not own the upstream `vibe` template source code.
