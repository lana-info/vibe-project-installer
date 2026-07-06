# Vibe Project Installer

Small installer wrapper for creating new projects from the `di-sukharev/vibe` template.

Use the Python CLI for day-to-day project creation. It calls the PowerShell installer under `scripts/bootstrap-project.ps1`.

The goal is to keep project startup simple:

- create a fresh project folder;
- choose active surfaces: `web`, `mobile`, `backend`, `landing`, or `full-stack`;
- choose a hosting posture: `custom`, `none`, `digitalocean`, or `yandex`;
- record the bootstrap plan in the generated project README;
- remove the template Git remote by default so new projects do not push back to upstream.

## Quick Start

Create a web/backend project with the Python CLI:

```powershell
python .\scripts\create-vibe-project.py `
  --target-path "D:\WorkOS\My App" `
  --project-name "My App" `
  --active-surfaces web,backend `
  --hosting custom
```

Create a web/backend project from upstream:

```powershell
.\scripts\bootstrap-project.ps1 `
  -SourceUrl "https://github.com/di-sukharev/vibe.git" `
  -Branch master `
  -TargetPath "D:\WorkOS\My App" `
  -ProjectName "My App" `
  -ActiveSurfaces web,backend `
  -Hosting custom
```

Create from the mobile branch:

```powershell
.\scripts\bootstrap-project.ps1 `
  -SourceUrl "https://github.com/di-sukharev/vibe.git" `
  -Branch mobile `
  -TargetPath "D:\WorkOS\My Mobile App" `
  -ProjectName "My Mobile App" `
  -ActiveSurfaces mobile,backend `
  -Hosting custom
```

Create from a local checkout by running the script inside a local `vibe` repo copy:

```powershell
.\scripts\bootstrap-project.ps1 `
  -TargetPath "D:\WorkOS\My Local App" `
  -ProjectName "My Local App" `
  -ActiveSurfaces full-stack `
  -Hosting custom
```

## Hosting Modes

- `custom`: provider-neutral default. Choose hosting later from product needs.
- `none`: local-only. Do not configure deployment.
- `digitalocean`: keep the upstream DigitalOcean runbook active.
- `yandex`: keep the upstream Yandex Cloud runbook active.

## Verification

Run a local smoke install into a scratch folder:

```powershell
$target = Join-Path $PWD ".scratch\vibe-installer-smoke"
if (Test-Path $target) { Remove-Item -LiteralPath $target -Recurse -Force }
.\scripts\bootstrap-project.ps1 -SourceUrl "https://github.com/di-sukharev/vibe.git" -Branch master -TargetPath $target -ProjectName "Smoke App" -ActiveSurfaces web,backend -Hosting custom
Test-Path (Join-Path $target "README.md")
Test-Path (Join-Path $target "backend\README.md")
```

## Knowledge Base

See `wiki/knowledge-base.md` for the maintainer notes, behavior summary, and change checklist.

## Current Scope

This repo owns only the installer wrapper and workflow docs. It does not own the upstream `vibe` template source code.
