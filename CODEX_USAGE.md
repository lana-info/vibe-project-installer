# Use From Any Codex Project

If you are already inside another project and want to configure it for vibe coding, ask Codex:

```text
Это проект для вайбкодинга. Запусти настройку проекта.
```

Codex should run the existing-project installer, not the new-project creator:

```powershell
python D:\WorkOS\vibe-project-installer\scripts\install_project_pack_gui.py `
  --target-path "<current-project-path>"
```

This opens a setup window for workflow docs, prompts, frontend design guidance, deployment planning docs, and optional feature packs. It does not clone upstream and does not change application code.

Optional feature packs can be added:

```powershell
python D:\WorkOS\vibe-project-installer\scripts\install-project-pack.py `
  --target-path "<current-project-path>" `
  --features payments,uploads-media,e2e-tests `
  --deployment-plan hetzner
```
