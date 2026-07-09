# Run The App

This app can run without building an `.exe`, `.app`, or Linux package.

The GUI is Python/Tkinter, so Python must be installed on the computer that opens the app.
Project creation also calls `scripts/bootstrap-project.ps1`, so new-project creation needs Git and PowerShell.
Node.js/npm are needed later for web, Chrome extension, Vite, Tailwind, shadcn/ui, and Tauri work.

Codex CLI is not required.

For dependency install commands, see `INSTALL_DEPENDENCIES.md`.

## Windows

Install:

- Git
- Python 3

Run:

```powershell
git clone https://github.com/lana-info/vibe-project-installer.git
cd vibe-project-installer
python .\scripts\create_vibe_project_gui.py
```

You can also double-click:

```text
Create Vibe Project.vbs
```

## macOS

Install with Homebrew:

```bash
brew install python git
brew install --cask powershell
```

Run:

```bash
git clone https://github.com/lana-info/vibe-project-installer.git
cd vibe-project-installer
python3 scripts/create_vibe_project_gui.py
```

If Tkinter is missing, install Python from python.org or reinstall Python with Tk support.

## Linux

Ubuntu/Debian basics:

```bash
sudo apt update
sudo apt install python3 python3-tk git
```

Install PowerShell 7 (`pwsh`). On some systems this is available as:

```bash
sudo apt install powershell
```

If that package is not available, install PowerShell from Microsoft's Linux instructions for your distro:

```text
https://learn.microsoft.com/powershell/scripting/install/installing-powershell-on-linux
```

Run:

```bash
git clone https://github.com/lana-info/vibe-project-installer.git
cd vibe-project-installer
python3 scripts/create_vibe_project_gui.py
```

## Quick Check

From the repo folder:

```bash
python3 scripts/create_vibe_project_gui.py --self-test
python3 scripts/check-system-dependencies.py
```

On Windows, use `python` instead of `python3` if that is your installed command:

```powershell
python .\scripts\create_vibe_project_gui.py --self-test
python .\scripts\check-system-dependencies.py
```

## Package For Another User

This creates a portable zip folder. It is not an installer and does not include Python, Git, PowerShell, Node.js, or npm.

On Windows:

```powershell
.\scripts\package-app.ps1
```

Send the created `dist/vibe-project-installer-portable-*.zip` file.

The other user should unzip it, install the dependencies from `INSTALL_DEPENDENCIES.md`, then open:

```text
Create Vibe Project.vbs
```

On macOS/Linux, they can run:

```bash
python3 scripts/create_vibe_project_gui.py
```

## Configure An Existing Project

In the main GUI, switch `Режим` from `Новый проект` to `Существующий проект`.

You can also open the existing-project setup directly:

```powershell
python .\scripts\install_project_pack_gui.py --target-path "D:\WorkOS\Existing App"
```

On macOS/Linux:

```bash
python3 scripts/install_project_pack_gui.py --target-path "/path/to/existing-app"
```

This mode creates `SETUP_AUDIT.md`, writes setup notes to `VIBE_SETUP.md`, adds only missing docs/prompts, does not rewrite the existing README, and does not install dependencies automatically.

## Notes

- The app creates projects from the online upstream template by default.
- It does not deploy hosting or create paid cloud resources.
- The hosting choice only writes planning docs into the generated project.
- Keep tokens, passwords, cookies, and `.env` values out of chat and git.
