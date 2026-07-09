#!/usr/bin/env python3
"""Check system tools needed by the project installer."""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class DependencyCheck:
    name: str
    command: str
    found: bool
    required: bool
    path: str | None
    version: str
    why: str
    install_hint: str

    @property
    def status(self) -> str:
        if self.found:
            return "OK"
        return "MISSING" if self.required else "OPTIONAL"


def _run_version(command: list[str]) -> str:
    if platform.system() == "Windows" and command[0].lower().endswith(".cmd"):
        command = ["cmd", "/c", *command]
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""

    return " ".join(result.stdout.strip().splitlines()[:2])


def _which(candidates: tuple[str, ...]) -> tuple[str, str | None]:
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return candidate, resolved
    return candidates[0], None


def check_system_dependencies() -> list[DependencyCheck]:
    powershell_candidates = ("pwsh", "powershell") if platform.system() == "Windows" else ("pwsh",)
    powershell_command, powershell_path = _which(powershell_candidates)
    node_command, node_path = _which(("node",))
    npm_command, npm_path = _which(("npm",))
    git_command, git_path = _which(("git",))

    checks = [
        DependencyCheck(
            name="Python",
            command="python",
            found=True,
            required=True,
            path=sys.executable,
            version=_run_version([sys.executable, "--version"]),
            why="Запускает это приложение и Python desktop starters.",
            install_hint="Установи Python 3.11+ с python.org. На Linux также нужен python3-tk.",
        ),
        DependencyCheck(
            name="Git",
            command=git_command,
            found=git_path is not None,
            required=True,
            path=git_path,
            version=_run_version([git_path, "--version"]) if git_path else "",
            why="Скачивает шаблоны с GitHub и нужен для commits/push в созданных проектах.",
            install_hint="Windows: winget install Git.Git. macOS: brew install git. Linux: sudo apt install git.",
        ),
        DependencyCheck(
            name="PowerShell",
            command=powershell_command,
            found=powershell_path is not None,
            required=True,
            path=powershell_path,
            version=_powershell_version(powershell_command) if powershell_path else "",
            why="Запускает scripts/bootstrap-project.ps1 при создании web, landing, mobile+web и Chrome extension проектов.",
            install_hint="Windows: PowerShell обычно уже есть, лучше поставить PowerShell 7. macOS: brew install --cask powershell. Linux: установи powershell по инструкции Microsoft.",
        ),
        DependencyCheck(
            name="Node.js",
            command=node_command,
            found=node_path is not None,
            required=False,
            path=node_path,
            version=_run_version([node_path, "--version"]) if node_path else "",
            why="Нужен для web/frontend, Chrome extension, npm install, Vite, Tailwind, shadcn/ui и Tauri frontend.",
            install_hint="Windows: winget install OpenJS.NodeJS.LTS. macOS: brew install node. Linux: sudo apt install nodejs npm или NodeSource.",
        ),
        DependencyCheck(
            name="npm",
            command=npm_command,
            found=npm_path is not None,
            required=False,
            path=npm_path,
            version=_run_version([npm_path, "--version"]) if npm_path else "",
            why="Ставит JavaScript-пакеты проекта. Обычно устанавливается вместе с Node.js.",
            install_hint="Установи Node.js LTS: npm обычно появится автоматически.",
        ),
    ]
    return checks

def _powershell_version(command: str) -> str:
    if command == "pwsh":
        return _run_version(["pwsh", "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"])
    return _run_version(["powershell", "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"])


def format_dependency_report(checks: list[DependencyCheck]) -> str:
    lines = ["System dependency check", ""]
    for check in checks:
        version = f" - {check.version}" if check.version else ""
        location = f" ({check.path})" if check.path else ""
        lines.append(f"[{check.status}] {check.name}: {check.command}{version}{location}")
        lines.append(f"    Зачем: {check.why}")
        if not check.found:
            lines.append(f"    Как установить: {check.install_hint}")
    lines.append("")
    missing_required = [check.name for check in checks if check.required and not check.found]
    if missing_required:
        lines.append(f"Нельзя создавать новые проекты, пока не установлено: {', '.join(missing_required)}.")
    else:
        lines.append("Минимум для создания проектов установлен.")
    missing_optional = [check.name for check in checks if not check.required and not check.found]
    if missing_optional:
        lines.append(f"Для web/extension/UI-пакетов позже понадобится: {', '.join(missing_optional)}.")
    return "\n".join(lines)
