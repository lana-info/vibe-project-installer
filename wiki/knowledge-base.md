# Vibe Project Installer Knowledge Base

## Purpose

This repository is a small PowerShell wrapper for creating new projects from the `di-sukharev/vibe` template.

The installer should stay focused:

- clone or copy a vibe template;
- choose active surfaces: `web`, `mobile`, `backend`, `landing`, or `full-stack`;
- keep cloud setup out of project creation by default;
- write the bootstrap plan into the generated project `README.md`;
- remove the upstream template remote by default.

## Main Files

- `README.md` - user-facing quick start, examples, smoke verification.
- `START_HERE.md` - shortest onboarding path for agents and maintainers.
- `TASKS.md` - small backlog for this wrapper project.
- `scripts/bootstrap-project.ps1` - the installer implementation.
- `examples/` - copyable example commands.
- `AGENTS.md` - local agent rules and safety constraints.

## Installer Behavior

`scripts/bootstrap-project.ps1` accepts:

- `-TargetPath` - required output folder.
- `-ProjectName` - optional display name; defaults to target folder name.
- `-ActiveSurfaces` - selected surfaces. Aliases include `full`, `fullstack`, `api`, and `backend/api`.
- `-SourceUrl` - optional Git source. If omitted, the current repo tree is copied.
- `-Branch` - optional Git branch.
- `-Hosting` - internal cloud setup note: `custom`, `none`, or `digitalocean`; default is `custom`.
- `-KeepTemplateRemote` - keeps upstream `origin`; otherwise origin is removed after clone.

Generated projects get a `Project Bootstrap Plan` in root `README.md`. Surface READMEs are marked as active or deferred when present.

## Design Rules

- Keep the wrapper provider-neutral by default.
- Do not make DigitalOcean, Yandex Cloud, EAS, Docker, or GitHub publishing mandatory.
- Preserve default removal of the upstream template remote.
- Do not copy the full upstream template into this repo.
- Do not push to `di-sukharev/vibe`.
- Do not print secrets, tokens, passwords, or `.env` contents.
- Prefer small, behavior-preserving changes.

## Common Commands

Smoke install:

```powershell
$target = Join-Path $PWD ".scratch\vibe-installer-smoke"
if (Test-Path $target) { Remove-Item -LiteralPath $target -Recurse -Force }
.\scripts\bootstrap-project.ps1 -SourceUrl "https://github.com/di-sukharev/vibe.git" -Branch master -TargetPath $target -ProjectName "Smoke App" -ActiveSurfaces web,backend
Test-Path (Join-Path $target "README.md")
Test-Path (Join-Path $target "backend\README.md")
```

Check that the generated README contains the bootstrap plan:

```powershell
Select-String -Path (Join-Path $target "README.md") -Pattern "Project Bootstrap Plan"
```

Check that the template remote was removed:

```powershell
git -C $target remote -v
```

## Change Checklist

Before changing behavior:

1. Read `README.md` and `scripts/bootstrap-project.ps1`.
2. Keep the change minimal and focused.
3. Run a scratch install.
4. Confirm the generated README contains `Project Bootstrap Plan`.
5. Confirm active/deferred surfaces are marked correctly when those READMEs exist.
6. Confirm upstream `origin` is removed unless `-KeepTemplateRemote` is passed.
7. Report the exact verification command and result.

## Current Backlog

- Add tests for common argument combinations if the script grows beyond smoke checks.
- Add an examples matrix for common project types: web app, mobile app, landing, full-stack.
