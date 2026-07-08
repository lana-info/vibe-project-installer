# Vibe Project Installer

Small installer wrapper for creating new projects from the `di-sukharev/vibe` template.

Use the Python CLI for day-to-day project creation. It calls the PowerShell installer under `scripts/bootstrap-project.ps1`.

The goal is to keep project startup simple:

- create a fresh project folder;
- choose a base template: `Mobile app + Web` or `Chrome extension`;
- for Vibe projects, `Mobile app + Web` records `web,mobile,backend` because the upstream mobile branch includes the mobile app, browser web app/site, and backend/API;
- record the bootstrap plan in the generated project README;
- create starter workflow files from `templates/project-pack`;
- include English and Russian starter docs;
- add optional feature checklists and prompts for payments, uploads/media, social auth, push notifications, background jobs, cron, E2E tests, admin, realtime, marketplace/catalog, AI features, and design starter;
- record a documentation-only deployment plan: decide later, Hetzner, Timeweb, DigitalOcean, Hostinger, or custom hosting;
- remove the template Git remote by default so new projects do not push back to upstream.

## Quick Start

To open the GUI app on Windows, macOS, or Linux, see `RUN_APP.md`.

Install vibe-coding workflow docs into an existing project:

```powershell
python .\scripts\install_project_pack_gui.py --target-path "D:\WorkOS\Existing App"
```

Or run it without the GUI:

```powershell
python .\scripts\install-project-pack.py `
  --target-path "D:\WorkOS\Existing App" `
  --project-name "Existing App" `
  --active-surfaces web,mobile,backend `
  --deployment-plan decide-later
```

Create a mobile app + web project with the Python CLI:

```powershell
python .\scripts\create-vibe-project.py `
  --target-path "D:\WorkOS\My App" `
  --project-name "My App" `
  --active-surfaces mobile
```

The CLI expands `mobile` to `mobile,web,backend` for Vibe projects because the upstream mobile branch is the mobile app + web + backend template line.

Create a Chrome extension project:

```powershell
python .\scripts\create-vibe-project.py `
  --target-path "D:\WorkOS\My Extension" `
  --project-name "My Extension" `
  --template chrome-extension `
  --active-surfaces chrome-extension
```

Chrome extension is a separate project base. Do not combine it with `web`, `mobile`, `backend`, or `landing`.
For Chrome extension projects, the GUI only allows workflow docs and the optional `Design starter` feature pack.

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

Chrome extension projects use `JohnBra/vite-web-extension` as the app template.

- `templates/project-pack/base` - copied into every new project.
- `templates/project-pack/features` - copied only for selected feature checkboxes.

In the GUI, the documentation checkbox is on the `Проект` tab. Optional feature packs are on the `Доп. функции` tab.

## Template Remote

By default, the generated project removes the original `di-sukharev/vibe` Git remote. Leave it that way for normal new projects.

The GUI does not expose this setting because normal projects should not keep the template remote. The advanced CLI flag `--keep-template-remote` is only for intentionally working on the upstream template itself.

## Template Archives

The app creates new projects from online template repos by default. Keep local archives next to this installer for backup, reference, and updates:

```powershell
.\scripts\sync-upstream-archive.ps1
```

Default archive paths:

- `D:\WorkOS\vibe-upstream-archive` for `di-sukharev/vibe`.
- `D:\WorkOS\vite-web-extension-upstream-archive` for `JohnBra/vite-web-extension`.
- `D:\WorkOS\design-shadcn-ui-archive` for `shadcn-ui/ui`.
- `D:\WorkOS\design-magic-ui-archive` for `magicuidesign/magicui`.
- `D:\WorkOS\design-origin-ui-archive` for `shadcn/originui`.
- `D:\WorkOS\design-react-native-reusables-archive` for `founded-labs/react-native-reusables`.

The archive sync script also creates local fallback branches such as `mobile` for `vibe`, so local archives can be used if an online source is unavailable.

Update one archive only:

```powershell
.\scripts\sync-upstream-archive.ps1 -Template chrome-extension
```

Update one design reference archive:

```powershell
.\scripts\sync-upstream-archive.ps1 -Template design-shadcn-ui
```

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
