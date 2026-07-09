#!/usr/bin/env python3
"""Python CLI wrapper for creating projects from the vibe template."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from project_options import (
    DEFAULT_DESKTOP_UI_STACK,
    DESKTOP_UI_STACKS,
    HOSTING_PROJECT_TYPES,
    allowed_features_for_project_type,
    desktop_ui_label,
)

ROOT = Path(__file__).resolve().parents[1]
PROJECT_PACK_ROOT = ROOT / "templates" / "project-pack"
APP_TEMPLATE_ROOT = ROOT / "templates" / "app-templates"
DEFAULT_SOURCE_URL = "https://github.com/di-sukharev/vibe.git"
CHROME_EXTENSION_SOURCE_URL = "https://github.com/JohnBra/vite-web-extension.git"
DEFAULT_WEB_BRANCH = "master"
DEFAULT_MOBILE_BRANCH = "mobile"
DEFAULT_CHROME_EXTENSION_BRANCH = "main"
PROJECT_TEMPLATES = ("vibe", "chrome-extension", "python-desktop")
PROJECT_TYPES = {
    "website": {
        "template": "vibe",
        "surfaces": ["website"],
        "branch": DEFAULT_WEB_BRANCH,
    },
    "landing": {
        "template": "vibe",
        "surfaces": ["landing"],
        "branch": DEFAULT_WEB_BRANCH,
    },
    "mobile-web-app": {
        "template": "vibe",
        "surfaces": ["web", "mobile", "backend"],
        "branch": DEFAULT_MOBILE_BRANCH,
    },
    "desktop-python": {
        "template": "python-desktop",
        "surfaces": ["desktop-python"],
        "branch": None,
    },
    "chrome-extension": {
        "template": "chrome-extension",
        "surfaces": ["chrome-extension"],
        "branch": DEFAULT_CHROME_EXTENSION_BRANCH,
    },
}
HOSTING_MODES = ("custom", "none", "digitalocean")
DEPLOYMENT_PLANS = {
    "decide-later": "Decide later",
    "hetzner": "Hetzner",
    "timeweb": "Timeweb",
    "digitalocean": "DigitalOcean",
    "hostinger": "Hostinger",
    "custom": "Custom hosting",
}
FEATURES = {
    "payments": "Payments / subscriptions",
    "uploads-media": "Uploads / media",
    "social-auth": "Social auth",
    "push-notifications": "Push notifications",
    "background-jobs": "Background jobs",
    "scheduled-tasks": "Scheduled tasks / cron",
    "e2e-tests": "Mobile + web E2E tests",
    "admin": "Admin panel",
    "realtime": "Realtime / chat",
    "marketplace-catalog": "Marketplace / catalog",
    "ai-features": "AI features",
    "design-starter": "Design starter",
}
CHROME_EXTENSION_FEATURES = {"design-starter"}


def parse_surfaces(value: str) -> list[str]:
    surfaces = [item.strip() for item in value.split(",") if item.strip()]
    if not surfaces:
        raise argparse.ArgumentTypeError("Provide at least one surface.")
    return surfaces


def parse_features(value: str) -> list[str]:
    features = [item.strip() for item in value.split(",") if item.strip()]
    invalid = [feature for feature in features if feature not in FEATURES]
    if invalid:
        raise argparse.ArgumentTypeError(
            f"Unknown feature(s): {', '.join(invalid)}. Use: {', '.join(FEATURES)}."
        )
    return features


def apply_project_type(args: argparse.Namespace) -> None:
    if args.project_type is None:
        return

    preset = PROJECT_TYPES[args.project_type]
    args.template = preset["template"]
    args.active_surfaces = list(preset["surfaces"])
    if args.branch is None:
        args.branch = preset["branch"]


def normalize_surfaces(template: str, surfaces: list[str]) -> list[str]:
    if template == "chrome-extension":
        if any(surface != "chrome-extension" for surface in surfaces):
            raise argparse.ArgumentTypeError("Chrome extension projects cannot be mixed with website, landing, web, mobile, or backend surfaces.")
        return ["chrome-extension"]

    if template == "python-desktop":
        if any(surface != "desktop-python" for surface in surfaces):
            raise argparse.ArgumentTypeError("Desktop Python projects cannot be mixed with website, landing, mobile, web, backend, or Chrome extension surfaces.")
        return ["desktop-python"]

    if "chrome-extension" in surfaces:
        raise argparse.ArgumentTypeError("Use --template chrome-extension for Chrome extension projects.")
    if "desktop-python" in surfaces:
        raise argparse.ArgumentTypeError("Use --project-type desktop-python for Desktop Python projects.")

    normalized = list(surfaces)
    if "mobile" in normalized:
        for required in ("web", "backend"):
            if required not in normalized:
                normalized.append(required)
    return normalized


def normalize_features(template: str, project_type: str | None, features: list[str]) -> list[str]:
    if project_type is not None:
        allowed = allowed_features_for_project_type(project_type, tuple(FEATURES))
        invalid = [feature for feature in features if feature not in allowed]
        if invalid:
            raise argparse.ArgumentTypeError(
                f"{project_type} projects do not support feature(s): {', '.join(invalid)}."
            )
        return features

    if template == "chrome-extension":
        allowed = CHROME_EXTENSION_FEATURES
        message = "Chrome extension projects only support docs and design-starter."
    elif template == "python-desktop":
        allowed = allowed_features_for_project_type("desktop-python", tuple(FEATURES))
        message = "Desktop Python projects only support docs and design-starter."
    else:
        return features

    invalid = [feature for feature in features if feature not in allowed]
    if invalid:
        raise argparse.ArgumentTypeError(
            f"{message} Unsupported feature(s): {', '.join(invalid)}."
        )
    return features


def project_allows_deployment_plan(args: argparse.Namespace) -> bool:
    if args.project_type is not None:
        return args.project_type in HOSTING_PROJECT_TYPES
    if args.template != "vibe":
        return False
    return any(surface in {"website", "landing", "web", "mobile", "backend"} for surface in args.active_surfaces)


def copy_local_template(args: argparse.Namespace) -> list[str]:
    source_root = APP_TEMPLATE_ROOT / args.template
    if not source_root.exists():
        raise RuntimeError(f"Missing local app template: {source_root}")

    target_root = Path(args.target_path).expanduser().resolve()
    if target_root.exists():
        raise RuntimeError(f"Target path already exists: {target_root}")

    target_root.mkdir(parents=True)
    skip_paths = {"main.py", "requirements.txt"} if args.template == "python-desktop" else None
    created = copy_template_tree(source_root, target_root, args, skip_paths=skip_paths)
    if args.template == "python-desktop":
        created.extend(write_desktop_ui_starter(target_root, args))

    if shutil.which("git"):
        subprocess.run(["git", "init"], cwd=target_root, check=False, stdout=subprocess.DEVNULL)

    return created


def find_powershell() -> str:
    for candidate in ("pwsh", "powershell"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise RuntimeError("PowerShell was not found on PATH.")


def build_command(args: argparse.Namespace, script_path: Path) -> list[str]:
    if args.template == "python-desktop":
        raise RuntimeError("python-desktop is a local template and does not use bootstrap-project.ps1.")

    branch = args.branch
    if branch is None:
        if args.template == "chrome-extension":
            branch = DEFAULT_CHROME_EXTENSION_BRANCH
        else:
            branch = DEFAULT_MOBILE_BRANCH if "mobile" in args.active_surfaces else DEFAULT_WEB_BRANCH

    source_url = args.source_url
    if source_url is None:
        source_url = CHROME_EXTENSION_SOURCE_URL if args.template == "chrome-extension" else DEFAULT_SOURCE_URL

    command = [
        find_powershell(),
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
        "-TargetPath",
        str(Path(args.target_path).expanduser()),
        "-ProjectName",
        args.project_name,
        "-ActiveSurfaces",
        ",".join(args.active_surfaces),
        "-Hosting",
        args.hosting,
    ]

    if source_url:
        command.extend(["-SourceUrl", source_url])

    if branch:
        command.extend(["-Branch", branch])

    if args.keep_template_remote:
        command.append("-KeepTemplateRemote")

    command.append("-SkipWorkflowDocs")

    return command


def format_command(command: list[str]) -> str:
    return subprocess.list2cmdline(command)


def render_template(text: str, args: argparse.Namespace) -> str:
    feature_names = [FEATURES[feature] for feature in args.features]
    desktop_ui = getattr(args, "desktop_ui", DEFAULT_DESKTOP_UI_STACK)
    replacements = {
        "{{PROJECT_NAME}}": args.project_name,
        "{{ACTIVE_SURFACES}}": ", ".join(args.active_surfaces),
        "{{FEATURE_LIST}}": ", ".join(feature_names) if feature_names else "No extra feature packs selected yet.",
        "{{DEPLOYMENT_PLAN}}": DEPLOYMENT_PLANS[args.deployment_plan],
        "{{PROJECT_TEMPLATE}}": args.template,
        "{{DESKTOP_UI_STACK}}": desktop_ui,
        "{{DESKTOP_UI_LABEL}}": desktop_ui_label(desktop_ui),
        "{{DESKTOP_RUN_COMMANDS}}": desktop_run_commands(desktop_ui),
        "{{DESKTOP_UI_GUIDE}}": desktop_ui_guide(),
    }

    for token, value in replacements.items():
        text = text.replace(token, value)
    return text


def desktop_run_commands(stack: str) -> str:
    if stack == "tauri-shadcn":
        return """```powershell
npm install
npm run dev

# Desktop shell after UI packages are installed:
npm run tauri dev
```"""

    return """```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python main.py
```"""


def desktop_ui_guide() -> str:
    lines = []
    for stack, option in DESKTOP_UI_STACKS.items():
        download = option.get("download_estimate", "")
        suffix = f" Approximate download: {download}." if download and download != "0 MB" else ""
        lines.append(f"- `{option['label']}` (`{stack}`): {option['description']}{suffix}")
    return "\n".join(lines)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8", newline="\n")


def write_desktop_ui_starter(target_root: Path, args: argparse.Namespace) -> list[str]:
    stack = getattr(args, "desktop_ui", DEFAULT_DESKTOP_UI_STACK)
    created: list[str] = []

    if stack == "tauri-shadcn":
        for old_path in (target_root / "main.py", target_root / "requirements.txt"):
            if old_path.exists():
                old_path.unlink()
        files = tauri_shadcn_files(args.project_name)
    else:
        files = python_desktop_files(args.project_name, stack)

    for relative, content in files.items():
        destination = target_root / relative
        write_text(destination, content)
        created.append(relative)
    return created


def run_logged(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
    print(f"Running: {format_command(command)}", flush=True)
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="", flush=True)
    code = process.wait()
    if code != 0:
        raise RuntimeError(f"Command failed with exit code {code}: {format_command(command)}")


def install_desktop_dependencies(target_root: Path, args: argparse.Namespace) -> None:
    stack = getattr(args, "desktop_ui", DEFAULT_DESKTOP_UI_STACK)
    if stack == "tkinter":
        print("UI package install skipped: tkinter uses the Python standard library.", flush=True)
        return

    if stack == "tauri-shadcn":
        npm = shutil.which("npm")
        if not npm:
            raise RuntimeError("npm was not found on PATH. Install Node.js, then run `npm install` in the project folder.")
        run_logged([npm, "install"], target_root)
        return

    python = sys.executable
    venv_path = target_root / ".venv"
    run_logged([python, "-m", "venv", str(venv_path)], target_root)
    scripts_dir = "Scripts" if os.name == "nt" else "bin"
    python_in_venv = venv_path / scripts_dir / ("python.exe" if os.name == "nt" else "python")
    run_logged([str(python_in_venv), "-m", "pip", "install", "--upgrade", "pip"], target_root)
    run_logged([str(python_in_venv), "-m", "pip", "install", "-r", "requirements.txt"], target_root)


def python_desktop_files(project_name: str, stack: str) -> dict[str, str]:
    requirements = {
        "tkinter": "# No external packages required.",
        "customtkinter": "customtkinter>=5.2,<6",
        "pyside6": "PySide6>=6.7,<7",
        "flet": "flet>=0.25,<1",
    }
    mains = {
        "tkinter": f'''
#!/usr/bin/env python3
"""Small desktop app starter."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

APP_NAME = {project_name!r}


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("980x640")
        self.minsize(760, 520)
        self._build_ui()

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=24)
        root.pack(fill=tk.BOTH, expand=True)
        ttk.Label(root, text=APP_NAME, font=("Segoe UI", 22, "bold")).pack(anchor="w")
        ttk.Label(root, text="Small utility starter. Use another UI stack for polished app design.").pack(anchor="w", pady=(8, 20))
        ttk.Button(root, text="Run action").pack(anchor="w")


def main() -> int:
    app = App()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''',
        "customtkinter": f'''
#!/usr/bin/env python3
"""customtkinter desktop app starter."""

from __future__ import annotations

import customtkinter as ctk

APP_NAME = {project_name!r}


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.title(APP_NAME)
        self.geometry("1100x720")
        self.minsize(860, 560)
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#f3eee7")
        sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(sidebar, text=APP_NAME, font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=22, pady=(28, 24))
        for item in ("Projects", "Prompts", "Scenarios", "Settings"):
            ctk.CTkButton(sidebar, text=item, anchor="w", fg_color="transparent", text_color="#39465d", hover_color="#ffffff").pack(fill="x", padx=16, pady=4)

        main = ctk.CTkFrame(self, fg_color="#faf8f5", corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkLabel(main, text="Workspace", font=("Segoe UI", 30, "bold"), text_color="#111827").grid(row=0, column=0, columnspan=3, sticky="w", padx=32, pady=(30, 8))
        ctk.CTkEntry(main, placeholder_text="Search...", height=44, corner_radius=12).grid(row=1, column=0, columnspan=3, sticky="ew", padx=32, pady=(12, 24))
        for index in range(6):
            card = ctk.CTkFrame(main, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#eee7df")
            card.grid(row=2 + index // 3, column=index % 3, sticky="nsew", padx=(32 if index % 3 == 0 else 10, 32 if index % 3 == 2 else 10), pady=10)
            ctk.CTkLabel(card, text=f"Card {{index + 1}}", font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=18, pady=(18, 8))
            ctk.CTkLabel(card, text="Replace this with a real workflow item.", text_color="#64748b", wraplength=240).pack(anchor="w", padx=18, pady=(0, 18))


def main() -> int:
    app = App()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''',
        "pyside6": f'''
#!/usr/bin/env python3
"""PySide6 desktop app starter."""

from __future__ import annotations

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMainWindow, QPushButton, QVBoxLayout, QWidget

APP_NAME = {project_name!r}


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1180, 760)

        shell = QWidget()
        layout = QHBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        nav = QListWidget()
        nav.addItems(["Projects", "Prompts", "Scenarios", "Settings"])
        nav.setFixedWidth(230)
        nav.setObjectName("nav")
        layout.addWidget(nav)

        main = QWidget()
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(32, 30, 32, 30)
        title = QLabel("Workspace")
        title.setObjectName("title")
        main_layout.addWidget(title)
        search = QLineEdit()
        search.setPlaceholderText("Search...")
        search.setFixedHeight(44)
        main_layout.addWidget(search)

        grid = QGridLayout()
        grid.setSpacing(18)
        for index in range(8):
            card = QFrame()
            card.setObjectName("card")
            card_layout = QVBoxLayout(card)
            card_layout.addWidget(QLabel(f"Card {{index + 1}}"))
            note = QLabel("Replace this with a real workflow item.")
            note.setWordWrap(True)
            card_layout.addWidget(note)
            button = QPushButton("Open")
            button.setCursor(Qt.PointingHandCursor)
            card_layout.addWidget(button, alignment=Qt.AlignLeft)
            grid.addWidget(card, index // 4, index % 4)
        main_layout.addLayout(grid)
        layout.addWidget(main)
        self.setCentralWidget(shell)


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget {{ background: #faf8f5; color: #111827; font-family: Segoe UI; font-size: 14px; }}
        #nav {{ background: #f1ebe3; border: 0; padding: 18px; }}
        #title {{ font-size: 30px; font-weight: 700; margin-bottom: 8px; }}
        QLineEdit {{ background: white; border: 1px solid #eee7df; border-radius: 12px; padding: 0 14px; }}
        #card {{ background: white; border: 1px solid #eee7df; border-radius: 12px; padding: 12px; }}
        QPushButton {{ background: #e97826; color: white; border: 0; border-radius: 10px; padding: 8px 14px; }}
    """)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
''',
        "flet": f'''
#!/usr/bin/env python3
"""Flet desktop app starter."""

from __future__ import annotations

import flet as ft

APP_NAME = {project_name!r}


def main(page: ft.Page) -> None:
    page.title = APP_NAME
    page.window_width = 1180
    page.window_height = 760
    page.padding = 0
    page.bgcolor = "#faf8f5"

    nav = ft.Container(
        width=230,
        bgcolor="#f1ebe3",
        padding=24,
        content=ft.Column([
            ft.Text(APP_NAME, size=22, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20, color="transparent"),
            *[ft.TextButton(label, style=ft.ButtonStyle(color="#39465d")) for label in ["Projects", "Prompts", "Scenarios", "Settings"]],
        ]),
    )
    cards = [
        ft.Container(
            bgcolor="#ffffff",
            border=ft.border.all(1, "#eee7df"),
            border_radius=12,
            padding=18,
            content=ft.Column([
                ft.Text(f"Card {{index + 1}}", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("Replace this with a real workflow item.", color="#64748b"),
            ]),
        )
        for index in range(8)
    ]
    main_area = ft.Container(
        expand=True,
        padding=32,
        content=ft.Column([
            ft.Text("Workspace", size=32, weight=ft.FontWeight.BOLD),
            ft.TextField(hint_text="Search...", border_radius=12, bgcolor="#ffffff"),
            ft.GridView(cards, runs_count=4, max_extent=260, child_aspect_ratio=1.35, spacing=18, run_spacing=18, expand=True),
        ]),
    )
    page.add(ft.Row([nav, main_area], expand=True, spacing=0))


if __name__ == "__main__":
    ft.app(target=main)
''',
    }
    return {
        "main.py": mains.get(stack, mains["tkinter"]),
        "requirements.txt": requirements.get(stack, requirements["tkinter"]),
    }


def tauri_shadcn_files(project_name: str) -> dict[str, str]:
    package_name = make_package_slug(project_name)
    rust_package_name = package_name.replace("-", "_")
    bundle_identifier_suffix = package_name.replace("-", "")
    return {
        "package.json": f'''
{{
  "name": "{package_name}",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {{
    "dev": "vite",
    "build": "tsc && vite build",
    "tauri": "tauri"
  }},
  "dependencies": {{
    "@tauri-apps/api": "^2.2.0",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "lucide-react": "^0.468.0",
    "tailwind-merge": "^2.5.5",
    "tailwindcss-animate": "^1.0.7",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  }},
  "devDependencies": {{
    "@tauri-apps/cli": "^2.2.0",
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.4",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.49",
    "tailwindcss": "^3.4.16",
    "typescript": "^5.7.2",
    "vite": "^6.0.3"
  }}
}}
''',
        "index.html": '<div id="root"></div><script type="module" src="/src/main.tsx"></script>',
        "src/main.tsx": '''
import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
''',
        "src/App.tsx": f'''
import {{ FileText, Folder, Mic, Search, Settings, Sparkles, SquarePlus }} from "lucide-react";

const items = ["Projects", "Quick parsing", "Prompts", "Scenarios", "Macros", "Voiceover", "Photo generation", "Settings"];
const cards = Array.from({{ length: 8 }}, (_, index) => ({{
  title: ["Generation from template", "Niche analysis", "AI voice markup", "Creative rewrite"][index % 4],
  text: "Role: replace this card with a real workflow item from your product.",
  tags: ["Base", "Creative", "Text"].slice(0, 2 + (index % 2)),
}}));

export function App() {{
  return (
    <main className="min-h-screen bg-[#faf8f5] text-slate-900">
      <aside className="fixed inset-y-0 left-0 w-64 border-r border-orange-100 bg-[#f1ebe3] px-6 py-7">
        <div className="mb-12 flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-orange-500 text-white">
            <SquarePlus size={{22}} />
          </div>
          <div className="text-xl font-bold">{project_name}</div>
        </div>
        <nav className="space-y-2">
          {{items.map((item, index) => (
            <button key={{item}} className={{`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left font-medium ${{index === 2 ? "bg-white text-slate-950 shadow-sm" : "text-slate-500 hover:bg-white/70"}}`}}>
              {{index === 0 ? <Folder size={{19}} /> : index === 5 ? <Mic size={{19}} /> : index === 7 ? <Settings size={{19}} /> : <FileText size={{19}} />}}
              {{item}}
            </button>
          ))}}
        </nav>
      </aside>
      <section className="ml-64 px-8 py-8">
        <header className="mb-7 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold tracking-normal">Prompts</h1>
            <p className="mt-1 text-lg text-slate-500">Library of prompts and ideas</p>
          </div>
          <button className="flex items-center gap-2 rounded-xl bg-orange-500 px-5 py-3 font-semibold text-white shadow-sm hover:bg-orange-600">
            <SquarePlus size={{20}} /> Create
          </button>
        </header>
        <div className="rounded-2xl bg-white/70 p-7 shadow-sm ring-1 ring-orange-100">
          <label className="mb-7 flex h-14 items-center gap-3 rounded-2xl bg-white px-4 text-slate-500 ring-1 ring-orange-50">
            <Search size={{22}} />
            <input className="w-full bg-transparent text-base outline-none" placeholder="Search prompts..." />
          </label>
          <div className="grid grid-cols-1 gap-5 lg:grid-cols-2 xl:grid-cols-4">
            {{cards.map((card, index) => (
              <article key={{index}} className="min-h-52 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-100">
                <div className="mb-9 grid h-11 w-11 place-items-center rounded-full bg-orange-100 text-orange-500">
                  <Sparkles size={{20}} />
                </div>
                <h2 className="line-clamp-1 text-xl font-bold">{{card.title}}</h2>
                <p className="mt-3 line-clamp-3 text-slate-500">{{card.text}}</p>
                <div className="mt-5 flex flex-wrap gap-2">
                  {{card.tags.map((tag) => (
                    <span key={{tag}} className="rounded-full border border-orange-100 px-3 py-1 text-sm font-medium text-orange-600">#{{tag}}</span>
                  ))}}
                </div>
              </article>
            ))}}
          </div>
        </div>
      </section>
    </main>
  );
}}
''',
        "src/styles.css": '''
@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
''',
        "tailwind.config.js": '''
import animate from "tailwindcss-animate";

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [animate],
};
''',
        "postcss.config.js": '''
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
''',
        "tsconfig.json": '''
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["DOM", "DOM.Iterable", "ES2020"],
    "allowJs": false,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "moduleResolution": "Node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"],
  "references": []
}
''',
        "vite.config.ts": '''
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
});
''',
        "src-tauri/Cargo.toml": f'''
[package]
name = "{rust_package_name}"
version = "0.1.0"
description = "Desktop app shell"
edition = "2021"

[build-dependencies]
tauri-build = {{ version = "2.0", features = [] }}

[dependencies]
tauri = {{ version = "2.0", features = [] }}
tauri-plugin-shell = "2.0"

[features]
default = ["custom-protocol"]
custom-protocol = ["tauri/custom-protocol"]
''',
        "src-tauri/build.rs": "fn main() { tauri_build::build() }",
        "src-tauri/src/main.rs": '''
fn main() {
    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
''',
        "src-tauri/tauri.conf.json": f'''
{{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "{project_name}",
  "version": "0.1.0",
  "identifier": "com.local.{bundle_identifier_suffix}",
  "build": {{
    "beforeDevCommand": "npm run dev",
    "devUrl": "http://localhost:5173",
    "beforeBuildCommand": "npm run build",
    "frontendDist": "../dist"
  }},
  "app": {{
    "windows": [
      {{
        "title": "{project_name}",
        "width": 1240,
        "height": 800
      }}
    ],
    "security": {{
      "csp": null
    }}
  }}
}}
''',
    }


def make_package_slug(value: str) -> str:
    chars: list[str] = []
    previous_was_dash = False
    for char in value.lower():
        if "a" <= char <= "z" or "0" <= char <= "9":
            chars.append(char)
            previous_was_dash = False
        elif not previous_was_dash:
            chars.append("-")
            previous_was_dash = True

    slug = "".join(chars).strip("-")
    if not slug:
        return "desktop-app"
    if not ("a" <= slug[0] <= "z"):
        return f"app-{slug}"
    return slug


def write_template_file(source: Path, destination: Path, args: argparse.Namespace) -> bool:
    if destination.exists():
        return False

    destination.parent.mkdir(parents=True, exist_ok=True)
    text = render_template(source.read_text(encoding="utf-8"), args)
    destination.write_text(text, encoding="utf-8", newline="\n")
    return True


def copy_template_tree(
    source_root: Path,
    target_root: Path,
    args: argparse.Namespace,
    skip_paths: set[str] | None = None,
) -> list[str]:
    created: list[str] = []
    if not source_root.exists():
        return created

    for source in source_root.rglob("*"):
        if not source.is_file():
            continue

        relative = source.relative_to(source_root)
        if "__pycache__" in relative.parts or source.suffix == ".pyc":
            continue
        relative_posix = str(relative).replace("\\", "/")
        if skip_paths and relative_posix in skip_paths:
            continue
        destination = target_root / relative
        if write_template_file(source, destination, args):
            created.append(relative_posix)

    return created


def append_feature_summary(target_root: Path, args: argparse.Namespace) -> bool:
    readme = target_root / "README.md"
    if not readme.exists() or not args.features:
        return False

    content = readme.read_text(encoding="utf-8", errors="replace")
    if "## Selected Feature Packs" in content:
        return False

    lines = ["", "## Selected Feature Packs", ""]
    for feature in args.features:
        lines.append(f"- {FEATURES[feature]}: see `wiki/features/{feature}.md` and `prompts/features/{feature}.md`.")
    lines.append("")

    readme.write_text(content.rstrip() + "\n" + "\n".join(lines), encoding="utf-8", newline="\n")
    return True


def install_project_pack(args: argparse.Namespace) -> list[str]:
    if args.skip_workflow_docs:
        return []

    target_root = Path(args.target_path).expanduser().resolve()
    created = copy_template_tree(PROJECT_PACK_ROOT / "base", target_root, args)

    for feature in args.features:
        created.extend(copy_template_tree(PROJECT_PACK_ROOT / "features" / feature, target_root, args))

    if append_feature_summary(target_root, args):
        created.append("README.md#Selected Feature Packs")

    return created


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create a new project from the di-sukharev/vibe template."
    )
    parser.add_argument("--target-path", required=True, help="Output project folder.")
    parser.add_argument(
        "--project-name",
        required=True,
        help="Display name written into the generated README.",
    )
    parser.add_argument(
        "--active-surfaces",
        type=parse_surfaces,
        default=None,
        help="Comma-separated surfaces: website,landing,web,mobile,backend,full-stack.",
    )
    parser.add_argument(
        "--project-type",
        choices=tuple(PROJECT_TYPES),
        default=None,
        help="User-facing project type: website, landing, mobile-web-app, desktop-python, or chrome-extension.",
    )
    parser.add_argument(
        "--template",
        choices=PROJECT_TEMPLATES,
        default="vibe",
        help="Base project template: vibe or chrome-extension.",
    )
    parser.add_argument(
        "--source-url",
        default=None,
        help="Override template Git URL. Use an empty string only for a local template checkout.",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Template branch. Defaults to mobile when mobile is active, otherwise master.",
    )
    parser.add_argument(
        "--hosting",
        choices=HOSTING_MODES,
        default="custom",
        help="Advanced: cloud setup note to write into the bootstrap plan.",
    )
    parser.add_argument(
        "--deployment-plan",
        choices=tuple(DEPLOYMENT_PLANS),
        default="decide-later",
        help="Documentation-only deployment plan to add to project workflow files.",
    )
    parser.add_argument(
        "--desktop-ui",
        choices=tuple(DESKTOP_UI_STACKS),
        default=DEFAULT_DESKTOP_UI_STACK,
        help="Desktop Python UI stack: tkinter, customtkinter, pyside6, flet, or tauri-shadcn.",
    )
    parser.add_argument(
        "--keep-template-remote",
        action="store_true",
        help="Keep the template origin remote in the generated project.",
    )
    parser.add_argument(
        "--skip-workflow-docs",
        action="store_true",
        help="Do not create starter PRD, TASKS, wiki, and prompts files.",
    )
    parser.add_argument(
        "--install-dependencies",
        action="store_true",
        help="Install selected desktop UI packages after creating the project.",
    )
    parser.add_argument(
        "--skip-dependency-install",
        action="store_true",
        help="Deprecated alias behavior: create files only; do not install desktop UI packages.",
    )
    parser.add_argument(
        "--features",
        type=parse_features,
        default=[],
        help=f"Comma-separated feature packs: {','.join(FEATURES)}.",
    )
    parser.add_argument(
        "--print-command",
        action="store_true",
        help="Print the PowerShell command before running it.",
    )

    args = parser.parse_args(argv)
    apply_project_type(args)
    if args.active_surfaces is None:
        if args.template == "chrome-extension":
            args.active_surfaces = ["chrome-extension"]
        elif args.template == "python-desktop":
            args.active_surfaces = ["desktop-python"]
        else:
            args.active_surfaces = ["web", "mobile", "backend"]
    try:
        args.active_surfaces = normalize_surfaces(args.template, args.active_surfaces)
        args.features = normalize_features(args.template, args.project_type, args.features)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))
    if not project_allows_deployment_plan(args):
        args.deployment_plan = "decide-later"

    if args.template == "python-desktop":
        try:
            created = copy_local_template(args)
        except RuntimeError as exc:
            parser.error(str(exc))
        if created:
            print("Local app template created:", ", ".join(created))
        docs_created = install_project_pack(args)
        if docs_created:
            print("Project workflow pack created:", ", ".join(docs_created))
        if args.install_dependencies and not args.skip_dependency_install:
            try:
                install_desktop_dependencies(Path(args.target_path).expanduser().resolve(), args)
            except RuntimeError as exc:
                parser.error(str(exc))
        else:
            print("UI package install skipped. Package files and run commands were written to the project README.", flush=True)
        return 0

    script_path = Path(__file__).resolve().with_name("bootstrap-project.ps1")
    if not script_path.exists():
        parser.error(f"Missing installer script: {script_path}")
    try:
        command = build_command(args, script_path)
    except RuntimeError as exc:
        parser.error(str(exc))

    if args.print_command:
        print(format_command(command), flush=True)

    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        return completed.returncode

    created = install_project_pack(args)
    if created:
        print("Project workflow pack created:", ", ".join(created))
    return 0


if __name__ == "__main__":
    sys.exit(main())
