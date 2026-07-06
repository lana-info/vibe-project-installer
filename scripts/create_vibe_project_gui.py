#!/usr/bin/env python3
"""Small Tkinter launcher for creating vibe projects without the command line."""

from __future__ import annotations

import argparse
import queue
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPT = ROOT / "scripts" / "create-vibe-project.py"
DEFAULT_PARENT = Path("D:/WorkOS")
SURFACES = ("web", "backend", "mobile", "landing")
FEATURES = (
    (
        "payments",
        "Оплаты / подписки",
        "Если проект будет продавать доступ, подписки, премиум-контент или платные функции.",
    ),
    (
        "uploads-media",
        "Загрузка файлов / медиа",
        "Если пользователи будут загружать картинки, файлы, PDF, видео, экспорты или сгенерированные материалы.",
    ),
    (
        "social-auth",
        "Вход через Apple / Google",
        "Если пользователи должны входить через Apple или Google, а не только через email/password.",
    ),
    (
        "push-notifications",
        "Push-уведомления",
        "Если мобильное приложение должно отправлять напоминания, алерты или сообщения для возврата пользователя.",
    ),
    (
        "admin",
        "Админ-панель",
        "Если нужен внутренний кабинет для управления пользователями, контентом, заказами или поддержкой.",
    ),
    (
        "realtime",
        "Realtime / чат",
        "Если нужен чат, live-обновления, совместная работа, presence или мгновенные события.",
    ),
    (
        "marketplace-catalog",
        "Маркетплейс / каталог",
        "Если в проекте будут публичные листинги, товары, поиск, продавцы или SEO-страницы каталога.",
    ),
    (
        "ai-features",
        "AI-функции",
        "Если в продукте будет генерация, анализ, ассистент, prompt-flow или AI-автоматизация.",
    ),
)


def find_python() -> str:
    executable = Path(sys.executable)
    if executable.name.lower() == "pythonw.exe":
        python_exe = executable.with_name("python.exe")
        if python_exe.exists():
            return str(python_exe)

    for candidate in ("python", "py"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved

    return str(sys.executable)


class CreateProjectApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Создать Vibe Project - Mobile + Web")
        self.geometry("920x720")
        self.minsize(820, 620)

        self.project_name = tk.StringVar(value="My Vibe App")
        self.target_path = tk.StringVar(value=str(DEFAULT_PARENT / "My Vibe App"))
        self.keep_remote = tk.BooleanVar(value=False)
        self.include_workflow_docs = tk.BooleanVar(value=True)
        self.surface_vars = {
            "web": tk.BooleanVar(value=True),
            "backend": tk.BooleanVar(value=True),
            "mobile": tk.BooleanVar(value=True),
            "landing": tk.BooleanVar(value=False),
        }
        self.feature_vars = {feature_id: tk.BooleanVar(value=False) for feature_id, _label, _description in FEATURES}
        self.output_queue: queue.Queue[tuple[str, str | int]] = queue.Queue()
        self.worker: threading.Thread | None = None

        self._build_ui()
        self.after(100, self._drain_output)

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=14)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        notebook = ttk.Notebook(root)
        notebook.grid(row=0, column=0, sticky="nsew")

        main_tab = ttk.Frame(notebook, padding=14)
        settings_tab = ttk.Frame(notebook, padding=14)
        notebook.add(main_tab, text="Проект")
        notebook.add(settings_tab, text="Настройки")

        self._build_main_tab(main_tab)
        self._build_settings_tab(settings_tab)

        bottom = ttk.Frame(root)
        bottom.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        bottom.columnconfigure(1, weight=1)

        self.create_button = ttk.Button(bottom, text="Создать проект", command=self._start_create)
        self.create_button.grid(row=0, column=0, sticky="w")

        self.status = ttk.Label(bottom, text="Готово")
        self.status.grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.log = tk.Text(root, height=8, wrap="word")
        self.log.grid(row=2, column=0, sticky="nsew", pady=(10, 0))

    def _build_main_tab(self, frame: ttk.Frame) -> None:
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(3, weight=1)

        ttk.Label(frame, text="Название проекта").grid(row=0, column=0, sticky="w", pady=6)
        name_entry = ttk.Entry(frame, textvariable=self.project_name)
        name_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=6)
        name_entry.bind("<KeyRelease>", self._sync_target_name)

        ttk.Label(frame, text="Папка проекта").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.target_path).grid(row=1, column=1, sticky="ew", pady=6)
        ttk.Button(frame, text="Выбрать", command=self._browse_target).grid(row=1, column=2, padx=(8, 0), pady=6)

        surfaces = ttk.LabelFrame(frame, text="Тип проекта", padding=10)
        surfaces.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(8, 10))
        ttk.Label(
            surfaces,
            text="По умолчанию: Mobile + Web. Backend/API включён для логина, данных и логики приложения.",
            wraplength=760,
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))
        for index, surface in enumerate(SURFACES):
            label = "backend/API поддержка" if surface == "backend" else surface
            ttk.Checkbutton(surfaces, text=label, variable=self.surface_vars[surface]).grid(
                row=1, column=index, padx=(0, 22), sticky="w"
            )

        features = ttk.LabelFrame(frame, text="Дополнительные функции", padding=10)
        features.grid(row=3, column=0, columnspan=3, sticky="nsew")
        features.columnconfigure(0, weight=1)
        features.columnconfigure(1, weight=1)

        for index, (feature_id, label, description) in enumerate(FEATURES):
            row = (index // 2) * 2
            column = index % 2
            cell = ttk.Frame(features)
            cell.grid(row=row, column=column, sticky="new", padx=(0 if column == 0 else 12, 12 if column == 0 else 0), pady=(0, 8))
            cell.columnconfigure(0, weight=1)
            ttk.Checkbutton(cell, text=label, variable=self.feature_vars[feature_id]).grid(row=0, column=0, sticky="w")
            ttk.Label(cell, text=description, wraplength=360, foreground="#555555").grid(
                row=1, column=0, sticky="w", padx=(24, 0)
            )

    def _build_settings_tab(self, frame: ttk.Frame) -> None:
        frame.columnconfigure(0, weight=1)

        docs = ttk.LabelFrame(frame, text="Документация для работы", padding=12)
        docs.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        docs.columnconfigure(0, weight=1)
        ttk.Checkbutton(
            docs,
            text="Добавить START_HERE, PRD, TASKS, чек-лист и готовые промпты",
            variable=self.include_workflow_docs,
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            docs,
            text=(
                "Обычно лучше оставить включённым: эти файлы помогают сразу работать с проектом через Codex/AI. "
                "Если выключить, будет скопирован только код шаблона."
            ),
            wraplength=760,
            foreground="#555555",
        ).grid(row=1, column=0, sticky="w", padx=(24, 0), pady=(4, 0))

        git = ttk.LabelFrame(frame, text="Git / remote", padding=12)
        git.grid(row=1, column=0, sticky="ew")
        git.columnconfigure(0, weight=1)
        ttk.Checkbutton(
            git,
            text="Оставить remote шаблона di-sukharev/vibe",
            variable=self.keep_remote,
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            git,
            text=(
                "Для обычного нового проекта это НЕ нужно. По умолчанию remote шаблона удаляется, "
                "чтобы случайно не отправить свои изменения в чужой репозиторий. "
                "Включать только если ты специально дорабатываешь сам шаблон."
            ),
            wraplength=760,
            foreground="#555555",
        ).grid(row=1, column=0, sticky="w", padx=(24, 0), pady=(4, 0))

    def _sync_target_name(self, _event: tk.Event) -> None:
        current = Path(self.target_path.get())
        if current.parent == DEFAULT_PARENT or not self.target_path.get().strip():
            name = self.project_name.get().strip() or "My Vibe App"
            self.target_path.set(str(DEFAULT_PARENT / name))

    def _browse_target(self) -> None:
        parent = filedialog.askdirectory(
            title="Выбери папку, внутри которой создать новый проект",
            initialdir=str(DEFAULT_PARENT if DEFAULT_PARENT.exists() else ROOT),
        )
        if not parent:
            return

        name = self.project_name.get().strip() or "My Vibe App"
        self.target_path.set(str(Path(parent) / name))

    def _selected_surfaces(self) -> list[str]:
        return [surface for surface, value in self.surface_vars.items() if value.get()]

    def _selected_features(self) -> list[str]:
        return [feature for feature, value in self.feature_vars.items() if value.get()]

    def _validate(self) -> bool:
        if not self.project_name.get().strip():
            messagebox.showerror("Нет названия проекта", "Введи название проекта.")
            return False
        if not self.target_path.get().strip():
            messagebox.showerror("Нет папки проекта", "Выбери папку проекта.")
            return False
        if not self._selected_surfaces():
            messagebox.showerror("Не выбран тип проекта", "Выбери хотя бы одну активную часть проекта.")
            return False
        if Path(self.target_path.get()).exists():
            messagebox.showerror("Папка уже существует", "Такая папка уже существует. Выбери новое имя или другую папку.")
            return False
        if not CLI_SCRIPT.exists():
            messagebox.showerror("Не найден скрипт", f"Не могу найти {CLI_SCRIPT}")
            return False
        return True

    def _start_create(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        if not self._validate():
            return

        self.log.delete("1.0", tk.END)
        self.status.config(text="Создаю проект...")
        self.create_button.config(state=tk.DISABLED)
        self.worker = threading.Thread(target=self._run_create, daemon=True)
        self.worker.start()

    def _run_create(self) -> None:
        command = [
            find_python(),
            str(CLI_SCRIPT),
            "--target-path",
            self.target_path.get(),
            "--project-name",
            self.project_name.get().strip(),
            "--active-surfaces",
            ",".join(self._selected_surfaces()),
        ]
        features = self._selected_features()
        if features:
            command.extend(["--features", ",".join(features)])
        if not self.include_workflow_docs.get():
            command.append("--skip-workflow-docs")
        if self.keep_remote.get():
            command.append("--keep-template-remote")

        self.output_queue.put(("line", "Создаю проект...\n"))
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
                    self.create_button.config(state=tk.NORMAL)
                    if code == 0:
                        self.status.config(text=f"Готово: {self.target_path.get()}")
                        messagebox.showinfo("Проект создан", f"Создан проект:\n{self.target_path.get()}")
                    else:
                        self.status.config(text=f"Ошибка, код {code}")
                        messagebox.showerror("Проект не создан", "Посмотри лог в этом окне.")
        except queue.Empty:
            pass
        self.after(100, self._drain_output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        if not CLI_SCRIPT.exists():
            raise SystemExit(f"Missing CLI script: {CLI_SCRIPT}")
        return 0

    app = CreateProjectApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
