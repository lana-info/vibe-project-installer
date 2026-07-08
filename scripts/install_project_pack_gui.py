#!/usr/bin/env python3
"""Tkinter launcher for installing vibe-coding docs into an existing project."""

from __future__ import annotations

import argparse
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, str(Path(__file__).resolve().parent))
from create_vibe_project_gui import COLORS, DEPLOYMENT_PLANS, FEATURES, SURFACES, find_python


ROOT = Path(__file__).resolve().parents[1]
INSTALL_SCRIPT = ROOT / "scripts" / "install-project-pack.py"


class InstallProjectPackApp(tk.Tk):
    def __init__(self, target_path: Path | None = None) -> None:
        super().__init__()
        self.title("Настроить проект для вайбкодинга")
        self.geometry("920x720")
        self.minsize(820, 620)
        self.configure(bg=COLORS["bg"])

        initial_target = (target_path or Path.cwd()).resolve()
        self.target_path = tk.StringVar(value=str(initial_target))
        self.project_name = tk.StringVar(value=initial_target.name)
        self.deployment_plan_label = tk.StringVar(value=DEPLOYMENT_PLANS[0][1])
        self.surface_vars = {
            "web": tk.BooleanVar(value=True),
            "backend": tk.BooleanVar(value=True),
            "mobile": tk.BooleanVar(value=True),
            "landing": tk.BooleanVar(value=False),
        }
        self.feature_vars = {feature_id: tk.BooleanVar(value=False) for feature_id, _label, _description in FEATURES}
        self.output_queue: queue.Queue[tuple[str, str | int]] = queue.Queue()
        self.worker: threading.Thread | None = None

        self._configure_style()
        self._build_ui()
        self.after(100, self._drain_output)

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        default_font = ("Segoe UI", 10)
        heading_font = ("Segoe UI", 18, "bold")
        subheading_font = ("Segoe UI", 10)
        label_font = ("Segoe UI", 10, "bold")

        style.configure(".", font=default_font, background=COLORS["bg"], foreground=COLORS["text"])
        style.configure("App.TFrame", background=COLORS["bg"])
        style.configure("Panel.TFrame", background=COLORS["surface"])
        style.configure("Card.TFrame", background=COLORS["surface"], relief="flat")
        style.configure("Card.TLabelframe", background=COLORS["surface"], bordercolor=COLORS["border"], relief="solid")
        style.configure("Card.TLabelframe.Label", background=COLORS["surface"], foreground=COLORS["text"], font=label_font)
        style.configure("Hero.TFrame", background=COLORS["text"])
        style.configure("HeroTitle.TLabel", background=COLORS["text"], foreground="#ffffff", font=heading_font)
        style.configure("HeroText.TLabel", background=COLORS["text"], foreground="#d8deea", font=subheading_font)
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"])
        style.configure("Muted.TLabel", background=COLORS["surface"], foreground=COLORS["muted"])
        style.configure("Field.TLabel", background=COLORS["surface"], foreground=COLORS["text"], font=label_font)
        style.configure("FeatureText.TLabel", background=COLORS["surface"], foreground=COLORS["muted"])
        style.configure("TNotebook", background=COLORS["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", padding=(18, 9), background=COLORS["surface_alt"], foreground=COLORS["muted"])
        style.map("TNotebook.Tab", background=[("selected", COLORS["surface"])], foreground=[("selected", COLORS["text"])])
        style.configure("TCheckbutton", background=COLORS["surface"], foreground=COLORS["text"])
        style.map("TCheckbutton", background=[("active", COLORS["surface"])])
        style.configure("Accent.TButton", background=COLORS["accent"], foreground="#ffffff", padding=(18, 10), borderwidth=0)
        style.map("Accent.TButton", background=[("active", COLORS["accent_hover"]), ("pressed", COLORS["accent_hover"])])
        style.configure("Secondary.TButton", padding=(12, 8), borderwidth=1)

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=18, style="App.TFrame")
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        hero = ttk.Frame(root, padding=(22, 18), style="Hero.TFrame")
        hero.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        hero.columnconfigure(0, weight=1)
        ttk.Label(hero, text="Vibe Coding Setup", style="HeroTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            hero,
            text="Настройка уже существующего проекта: добавляет START_HERE, PRD, TASKS, wiki, prompts и выбранные feature packs.",
            style="HeroText.TLabel",
            wraplength=820,
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        notebook = ttk.Notebook(root)
        notebook.grid(row=1, column=0, sticky="nsew")

        project_tab = ttk.Frame(notebook, padding=16, style="Panel.TFrame")
        features_tab = ttk.Frame(notebook, padding=16, style="Panel.TFrame")
        notebook.add(project_tab, text="Проект")
        notebook.add(features_tab, text="Доп. функции")

        self._build_project_tab(project_tab)
        self._build_features_tab(features_tab)

        bottom = ttk.Frame(root, style="App.TFrame")
        bottom.grid(row=2, column=0, sticky="ew", pady=(14, 0))
        bottom.columnconfigure(1, weight=1)

        self.install_button = ttk.Button(bottom, text="Настроить проект", command=self._start_install, style="Accent.TButton")
        self.install_button.grid(row=0, column=0, sticky="w")
        self.status = ttk.Label(bottom, text="Готово")
        self.status.grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.log = tk.Text(root, height=8, wrap="word")
        self.log.configure(
            bg=COLORS["surface"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=12,
            pady=10,
            font=("Consolas", 9),
        )
        self.log.grid(row=3, column=0, sticky="nsew", pady=(10, 0))

    def _build_project_tab(self, frame: ttk.Frame) -> None:
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Папка проекта", style="Field.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.target_path).grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Button(frame, text="Выбрать", command=self._browse_target, style="Secondary.TButton").grid(
            row=0, column=2, padx=(8, 0), pady=6
        )

        ttk.Label(frame, text="Название проекта", style="Field.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.project_name).grid(row=1, column=1, columnspan=2, sticky="ew", pady=6)

        surfaces = self._section(frame, "Тип проекта")
        surfaces.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(8, 10))
        ttk.Label(
            surfaces,
            text="По умолчанию: Mobile + Web. Backend/API включён для логина, данных и логики приложения.",
            wraplength=760,
            style="Muted.TLabel",
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))
        for index, surface in enumerate(SURFACES):
            label = "backend/API поддержка" if surface == "backend" else surface
            ttk.Checkbutton(surfaces, text=label, variable=self.surface_vars[surface]).grid(
                row=1, column=index, padx=(0, 22), sticky="w"
            )

        deployment = self._section(frame, "План хостинга")
        deployment.grid(row=3, column=0, columnspan=3, sticky="ew")
        deployment.columnconfigure(1, weight=1)
        ttk.Label(deployment, text="Где потом запускать", style="Field.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 10))
        combo = ttk.Combobox(
            deployment,
            textvariable=self.deployment_plan_label,
            values=[label for _value, label, _description in DEPLOYMENT_PLANS],
            state="readonly",
            width=22,
        )
        combo.grid(row=0, column=1, sticky="w")
        self.deployment_help = ttk.Label(deployment, text="", wraplength=760, style="Muted.TLabel")
        self.deployment_help.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
        combo.bind("<<ComboboxSelected>>", self._update_deployment_help)
        self._update_deployment_help()

    def _build_features_tab(self, frame: ttk.Frame) -> None:
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        canvas = tk.Canvas(frame, bg=COLORS["surface"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        container = ttk.Frame(canvas, style="Panel.TFrame")
        window_id = canvas.create_window((0, 0), window=container, anchor="nw")
        container.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window_id, width=event.width))

        container.columnconfigure(0, weight=1)
        features = self._section(container, "Дополнительные функции")
        features.grid(row=0, column=0, sticky="nsew")
        features.columnconfigure(0, weight=1)
        features.columnconfigure(1, weight=1)

        for index, (feature_id, label, description) in enumerate(FEATURES):
            row = index // 2
            column = index % 2
            cell = ttk.Frame(features, padding=(10, 8), style="Card.TFrame")
            cell.grid(row=row, column=column, sticky="new", padx=(0 if column == 0 else 12, 12 if column == 0 else 0), pady=(0, 8))
            cell.columnconfigure(0, weight=1)
            ttk.Checkbutton(cell, text=label, variable=self.feature_vars[feature_id]).grid(row=0, column=0, sticky="w")
            ttk.Label(cell, text=description, wraplength=360, style="FeatureText.TLabel").grid(
                row=1, column=0, sticky="w", padx=(24, 0)
            )

    def _section(self, parent: ttk.Frame, title: str) -> ttk.LabelFrame:
        return ttk.LabelFrame(parent, text=title, padding=12, style="Card.TLabelframe")

    def _browse_target(self) -> None:
        selected = filedialog.askdirectory(title="Выбери папку существующего проекта", initialdir=self.target_path.get())
        if not selected:
            return
        path = Path(selected)
        self.target_path.set(str(path))
        self.project_name.set(path.name)

    def _update_deployment_help(self, _event: tk.Event | None = None) -> None:
        selected = self.deployment_plan_label.get()
        description = next((description for _value, label, description in DEPLOYMENT_PLANS if label == selected), "")
        self.deployment_help.config(text=description)

    def _selected_deployment_plan(self) -> str:
        selected = self.deployment_plan_label.get()
        return next((value for value, label, _description in DEPLOYMENT_PLANS if label == selected), "decide-later")

    def _selected_surfaces(self) -> list[str]:
        return [surface for surface, value in self.surface_vars.items() if value.get()]

    def _selected_features(self) -> list[str]:
        return [feature for feature, value in self.feature_vars.items() if value.get()]

    def _validate(self) -> bool:
        if not self.target_path.get().strip():
            messagebox.showerror("Нет папки проекта", "Выбери папку существующего проекта.")
            return False
        if not self.project_name.get().strip():
            messagebox.showerror("Нет названия проекта", "Введи название проекта.")
            return False
        if not self._selected_surfaces():
            messagebox.showerror("Не выбран тип проекта", "Выбери хотя бы одну активную часть проекта.")
            return False
        if not INSTALL_SCRIPT.exists():
            messagebox.showerror("Не найден скрипт", f"Не могу найти {INSTALL_SCRIPT}")
            return False
        return True

    def _start_install(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        if not self._validate():
            return

        self.log.delete("1.0", tk.END)
        self.status.config(text="Настраиваю проект...")
        self.install_button.config(state=tk.DISABLED)
        self.worker = threading.Thread(target=self._run_install, daemon=True)
        self.worker.start()

    def _run_install(self) -> None:
        command = [
            find_python(),
            str(INSTALL_SCRIPT),
            "--target-path",
            self.target_path.get(),
            "--project-name",
            self.project_name.get().strip(),
            "--active-surfaces",
            ",".join(self._selected_surfaces()),
            "--deployment-plan",
            self._selected_deployment_plan(),
        ]
        features = self._selected_features()
        if features:
            command.extend(["--features", ",".join(features)])

        self.output_queue.put(("line", "Настраиваю проект для вайбкодинга...\n"))
        process = subprocess.Popen(
            command,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert process.stdout is not None
        for line in process.stdout:
            self.output_queue.put(("line", line))
        self.output_queue.put(("done", process.wait()))

    def _drain_output(self) -> None:
        try:
            while True:
                kind, value = self.output_queue.get_nowait()
                if kind == "line":
                    self.log.insert(tk.END, str(value))
                    self.log.see(tk.END)
                elif kind == "done":
                    code = int(value)
                    self.install_button.config(state=tk.NORMAL)
                    if code == 0:
                        self.status.config(text=f"Готово: {self.target_path.get()}")
                        messagebox.showinfo("Проект настроен", f"Настроен проект:\n{self.target_path.get()}")
                    else:
                        self.status.config(text=f"Ошибка, код {code}")
                        messagebox.showerror("Проект не настроен", "Посмотри лог в этом окне.")
        except queue.Empty:
            pass
        self.after(100, self._drain_output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--target-path", help="Existing project folder to preselect.")
    args = parser.parse_args(argv)
    if args.self_test:
        if not INSTALL_SCRIPT.exists():
            raise SystemExit(f"Missing install script: {INSTALL_SCRIPT}")
        return 0

    app = InstallProjectPackApp(Path(args.target_path) if args.target_path else None)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
