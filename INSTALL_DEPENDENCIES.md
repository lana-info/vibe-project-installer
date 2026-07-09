# Install Dependencies

This project does not have a separate app installer. It is a Python/Tkinter app.

That means:

- to open the app window, the computer needs Python 3;
- to create new projects from GitHub templates, it also needs Git and PowerShell;
- to work with web, Chrome extension, Vite, Tailwind, shadcn/ui, or Tauri projects, it needs Node.js and npm.

Codex CLI is not required.

## Check From The App

Open the app and click `Проверить зависимости`.

The app will show:

- what is installed;
- what is missing;
- why each tool is needed;
- how to install it.

You can also check from the repo folder:

```bash
python scripts/check-system-dependencies.py
```

On Windows, use:

```powershell
python .\scripts\check-system-dependencies.py
```

## Windows

Install Python 3:

```powershell
winget install Python.Python.3.12
```

Install Git:

```powershell
winget install Git.Git
```

Install PowerShell 7:

```powershell
winget install Microsoft.PowerShell
```

Install Node.js LTS:

```powershell
winget install OpenJS.NodeJS.LTS
```

Restart the terminal/app after installing tools so PATH updates are visible.

## macOS

Install Homebrew first if it is missing:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Install the tools:

```bash
brew install python git node
brew install --cask powershell
```

If Tkinter is missing, install Python from python.org or reinstall Python with Tk support.

## Linux

Ubuntu/Debian basics:

```bash
sudo apt update
sudo apt install python3 python3-tk git nodejs npm
```

Install PowerShell 7:

```bash
sudo apt install powershell
```

If `powershell` is not available in the default package source, use Microsoft's official instructions for your Linux distribution:

```text
https://learn.microsoft.com/powershell/scripting/install/installing-powershell-on-linux
```

## What To Ask Codex On A New Computer

Use this prompt:

```text
Проверь, установлены ли Python 3, Git, PowerShell 7, Node.js и npm.
Codex CLI не нужен.
Ничего не устанавливай молча.
Сначала покажи, чего не хватает, зачем это нужно, и какие команды установки подходят для этой системы.
После моего подтверждения установи недостающее и проверь версии.
```

## Prompt: Ask Codex To Install Python

Use this when the app does not start because Python is missing:

```text
Мне нужно запускать Python/Tkinter приложение vibe-project-installer.
Проверь, установлен ли Python 3 и работает ли tkinter.
Codex CLI не нужен.
Ничего не устанавливай молча.
Сначала покажи:
1. какая у меня операционная система;
2. найден ли python/python3;
3. найден ли tkinter;
4. какую команду установки Python ты предлагаешь и почему.
После моего подтверждения установи Python 3, проверь `python --version` или `python3 --version`, проверь tkinter, и скажи, какой командой запускать приложение.
```

## Minimum Needed

To only open this app:

- Python 3 with Tkinter.

To create new website, landing, mobile+web, or Chrome extension projects:

- Python 3;
- Git;
- PowerShell 7 (`pwsh`) or Windows PowerShell on Windows.

To install and run web/frontend packages:

- Node.js;
- npm.
