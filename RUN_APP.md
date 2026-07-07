# Run The App

This app can run without building an `.exe`, `.app`, or Linux package.

The GUI is Python/Tkinter. Project creation also calls `scripts/bootstrap-project.ps1`, so macOS and Linux need PowerShell 7 (`pwsh`) installed.

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
```

On Windows, use `python` instead of `python3` if that is your installed command:

```powershell
python .\scripts\create_vibe_project_gui.py --self-test
```

## Notes

- The app creates projects from the online upstream template by default.
- It does not deploy hosting or create paid cloud resources.
- The hosting choice only writes planning docs into the generated project.
- Keep tokens, passwords, cookies, and `.env` values out of chat and git.

