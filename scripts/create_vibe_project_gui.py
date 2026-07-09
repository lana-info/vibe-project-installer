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

from project_options import (
    DEFAULT_DESKTOP_UI_STACK,
    DESKTOP_UI_STACKS,
    HOSTING_PROJECT_TYPES,
    allowed_features_for_project_type,
    desktop_ui_label,
    desktop_ui_option,
    surfaces_for_project_type,
)
from system_dependencies import check_system_dependencies, format_dependency_report


ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPT = ROOT / "scripts" / "create-vibe-project.py"
INSTALL_SCRIPT = ROOT / "scripts" / "install-project-pack.py"
DEFAULT_PARENT = Path("D:/WorkOS")
PROJECT_TYPES = (
    ("website", "Website", "Обычный сайт, который работает в браузере на телефоне и компьютере."),
    ("landing", "Landing", "Одна продающая или презентационная страница для проверки идеи, рекламы или запуска."),
    ("mobile-web-app", "Mobile app + Web app", "Отдельное мобильное приложение плюс веб-приложение/сайт и backend/API."),
    ("desktop-python", "Desktop Python app", "Простое приложение для запуска на компьютере. Локальный Python starter без лишних зависимостей."),
    ("chrome-extension", "Chrome extension", "Расширение Chrome/Firefox на React, TypeScript, Tailwind и Vite из JohnBra/vite-web-extension."),
)
COLORS = {
    "bg": "#f6f7fb",
    "surface": "#ffffff",
    "surface_alt": "#f1f4f9",
    "border": "#d9e0ec",
    "text": "#172033",
    "muted": "#5d6880",
    "accent": "#2563eb",
    "accent_hover": "#1d4ed8",
    "success": "#0f766e",
}
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
        "background-jobs",
        "Background jobs",
        "Если нужны фоновые задачи: обработка файлов, генерация, рассылки, webhooks, синхронизации или тяжелые операции.",
    ),
    (
        "scheduled-tasks",
        "Scheduled tasks / cron",
        "Если нужны регулярные задачи по расписанию: отчеты, проверки оплат, очистка, обновления или обработка очередей.",
    ),
    (
        "e2e-tests",
        "Mobile + Web E2E tests",
        "Если нужно автоматически проверять основные сценарии в мобильной и веб-версии: логин, оплата, профиль, главные экраны.",
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
    (
        "design-starter",
        "Design starter / основы дизайна",
        "Если нужно сразу добавить дизайн workflow: shadcn/ui Blocks, Magic UI, Origin UI и осторожный mobile component starter.",
    ),
)
DEPLOYMENT_PLANS = (
    ("decide-later", "Решить позже", "По умолчанию: не привязываем проект к хостингу на старте."),
    ("hetzner", "Hetzner", "Если планируешь VPS/сервер, Docker, Postgres и самостоятельную настройку деплоя."),
    ("timeweb", "Timeweb", "Если хочешь запускать проект на Timeweb Cloud/VPS и хранить инструкции под этот путь."),
    ("digitalocean", "DigitalOcean", "Если хочешь использовать готовые upstream runbooks: App Platform, Postgres, Static Sites, Spaces/CDN."),
    ("hostinger", "Hostinger", "Если проект будет запускаться на Hostinger VPS/hosting и нужен отдельный checklist."),
    ("custom", "Другой / custom", "Если хостинг будет выбран вручную: Render, Railway, Vercel, Netlify, Fly.io или другой."),
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
        self.title("Создать Vibe Project")
        self.geometry("920x720")
        self.minsize(820, 620)
        self.configure(bg=COLORS["bg"])

        self.project_mode = tk.StringVar(value="new")
        self.project_name = tk.StringVar(value="My Vibe App")
        self.target_path = tk.StringVar(value=str(DEFAULT_PARENT / "My Vibe App"))
        self.project_type_label = tk.StringVar(value=PROJECT_TYPES[0][1])
        self.desktop_ui_label = tk.StringVar(value=desktop_ui_label(DEFAULT_DESKTOP_UI_STACK))
        self.include_workflow_docs = tk.BooleanVar(value=True)
        self.install_dependencies = tk.BooleanVar(value=False)
        self.deployment_plan_label = tk.StringVar(value=DEPLOYMENT_PLANS[0][1])
        self.feature_vars = {feature_id: tk.BooleanVar(value=False) for feature_id, _label, _description in FEATURES}
        self.feature_checkbuttons: dict[str, ttk.Checkbutton] = {}
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
        style.configure(
            "Card.TLabelframe.Label",
            background=COLORS["surface"],
            foreground=COLORS["text"],
            font=label_font,
        )
        style.configure("Hero.TFrame", background=COLORS["text"])
        style.configure("HeroTitle.TLabel", background=COLORS["text"], foreground="#ffffff", font=heading_font)
        style.configure("HeroText.TLabel", background=COLORS["text"], foreground="#d8deea", font=subheading_font)
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"])
        style.configure("Panel.TLabel", background=COLORS["surface"], foreground=COLORS["text"])
        style.configure("Muted.TLabel", background=COLORS["surface"], foreground=COLORS["muted"])
        style.configure("Field.TLabel", background=COLORS["surface"], foreground=COLORS["text"], font=label_font)
        style.configure("FeatureTitle.TLabel", background=COLORS["surface"], foreground=COLORS["text"], font=label_font)
        style.configure("FeatureText.TLabel", background=COLORS["surface"], foreground=COLORS["muted"])
        style.configure("TEntry", fieldbackground="#ffffff", bordercolor=COLORS["border"], lightcolor=COLORS["border"])
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
        ttk.Label(hero, text="Vibe Project Creator", style="HeroTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            hero,
            text="Красивый старт нового проекта: код из upstream, рабочие промпты и чек-листы из этого installer.",
            style="HeroText.TLabel",
            wraplength=820,
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        notebook = ttk.Notebook(root)
        notebook.grid(row=1, column=0, sticky="nsew")

        main_tab_outer = ttk.Frame(notebook, style="Panel.TFrame")
        features_tab = ttk.Frame(notebook, padding=16, style="Panel.TFrame")
        notebook.add(main_tab_outer, text="Проект")
        notebook.add(features_tab, text="Доп. функции")

        main_tab = self._build_scrollable_tab(main_tab_outer)
        self._build_main_tab(main_tab)
        self._build_features_tab(features_tab)

        bottom = ttk.Frame(root, style="App.TFrame")
        bottom.grid(row=2, column=0, sticky="ew", pady=(14, 0))
        bottom.columnconfigure(1, weight=1)

        self.create_button = ttk.Button(bottom, text="Создать проект", command=self._start_create, style="Accent.TButton")
        self.dependency_check_button = ttk.Button(
            bottom,
            text="Проверить зависимости",
            command=self._show_dependency_check,
            style="Secondary.TButton",
        )
        self.dependency_check_button.grid(row=0, column=0, sticky="w")
        self.create_button.grid(row=0, column=1, sticky="w", padx=(10, 0))

        self.status = ttk.Label(bottom, text="Готово")
        self.status.grid(row=0, column=2, sticky="w", padx=(12, 0))

        self._sync_template_controls()

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

    def _build_scrollable_tab(self, parent: ttk.Frame) -> ttk.Frame:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        canvas = tk.Canvas(parent, bg=COLORS["surface"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        container = ttk.Frame(canvas, padding=16, style="Panel.TFrame")
        window_id = canvas.create_window((0, 0), window=container, anchor="nw")

        def sync_scroll_region(_event: tk.Event) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def sync_width(event: tk.Event) -> None:
            canvas.itemconfigure(window_id, width=event.width)

        container.bind("<Configure>", sync_scroll_region)
        canvas.bind("<Configure>", sync_width)
        return container

    def _build_main_tab(self, frame: ttk.Frame) -> None:
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(3, weight=1)

        mode = self._section(frame, "Режим")
        mode.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        ttk.Radiobutton(
            mode,
            text="Новый проект",
            value="new",
            variable=self.project_mode,
            command=self._on_mode_changed,
        ).grid(row=0, column=0, sticky="w", padx=(0, 20))
        ttk.Radiobutton(
            mode,
            text="Существующий проект",
            value="existing",
            variable=self.project_mode,
            command=self._on_mode_changed,
        ).grid(row=0, column=1, sticky="w")
        self.mode_help = ttk.Label(mode, text="", wraplength=760, style="Muted.TLabel")
        self.mode_help.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        ttk.Label(frame, text="Название проекта", style="Field.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        name_entry = ttk.Entry(frame, textvariable=self.project_name)
        name_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=6)
        name_entry.bind("<KeyRelease>", self._sync_target_name)

        ttk.Label(frame, text="Папка проекта", style="Field.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.target_path).grid(row=2, column=1, sticky="ew", pady=6)
        self.browse_button = ttk.Button(frame, text="Выбрать", command=self._browse_target, style="Secondary.TButton")
        self.browse_button.grid(
            row=2, column=2, padx=(8, 0), pady=6
        )

        template = self._section(frame, "Тип проекта")
        template.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(8, 10))
        template.columnconfigure(1, weight=1)
        ttk.Label(template, text="Что создаем", style="Field.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 10))
        template_combo = ttk.Combobox(
            template,
            textvariable=self.project_type_label,
            values=[label for _value, label, _description in PROJECT_TYPES],
            state="readonly",
            width=30,
        )
        template_combo.grid(row=0, column=1, sticky="w")
        self.template_help = ttk.Label(template, text="", wraplength=760, style="Muted.TLabel")
        self.template_help.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
        template_combo.bind("<<ComboboxSelected>>", self._on_template_changed)
        self._update_template_help()

        self.desktop_ui_section = self._section(frame, "Дизайн desktop-приложения")
        self.desktop_ui_section.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        self.desktop_ui_section.columnconfigure(1, weight=1)
        ttk.Label(self.desktop_ui_section, text="Какой интерфейс нужен", style="Field.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.desktop_ui_combo = ttk.Combobox(
            self.desktop_ui_section,
            textvariable=self.desktop_ui_label,
            values=[option["label"] for option in DESKTOP_UI_STACKS.values()],
            state="readonly",
            width=38,
        )
        self.desktop_ui_combo.grid(row=0, column=1, sticky="w")
        self.desktop_ui_help = ttk.Label(self.desktop_ui_section, text="", wraplength=760, style="Muted.TLabel")
        self.desktop_ui_help.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
        self.desktop_ui_combo.bind("<<ComboboxSelected>>", self._update_desktop_ui_help)
        self._update_desktop_ui_help()

        self.dependency_section = self._section(frame, "Пакеты интерфейса")
        self.dependency_section.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        self.dependency_section.columnconfigure(0, weight=1)
        ttk.Checkbutton(
            self.dependency_section,
            text="Скачать пакеты для выбранного интерфейса после создания проекта",
            variable=self.install_dependencies,
        ).grid(row=0, column=0, sticky="w")
        self.dependency_help = ttk.Label(
            self.dependency_section,
            text="По умолчанию выключено: проект получит только список пакетов и команды в README. Если включить, в логе будет видно скачивание.",
            wraplength=760,
            style="Muted.TLabel",
        )
        self.dependency_help.grid(row=1, column=0, sticky="w", padx=(24, 0), pady=(4, 0))

        docs = self._section(frame, "Документация для работы")
        docs.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(0, 10))
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
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", padx=(24, 0), pady=(4, 0))

        self.deployment_section = self._section(frame, "План хостинга")
        self.deployment_section.grid(row=7, column=0, columnspan=3, sticky="ew")
        self.deployment_section.columnconfigure(1, weight=1)
        ttk.Label(self.deployment_section, text="Где потом запускать", style="Field.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.deployment_combo = ttk.Combobox(
            self.deployment_section,
            textvariable=self.deployment_plan_label,
            values=[label for _value, label, _description in DEPLOYMENT_PLANS],
            state="readonly",
            width=22,
        )
        self.deployment_combo.grid(row=0, column=1, sticky="w")
        self.deployment_help = ttk.Label(self.deployment_section, text="", wraplength=760, style="Muted.TLabel")
        self.deployment_help.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
        self.deployment_combo.bind("<<ComboboxSelected>>", self._update_deployment_help)
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

        def sync_scroll_region(_event: tk.Event) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def sync_width(event: tk.Event) -> None:
            canvas.itemconfigure(window_id, width=event.width)

        container.bind("<Configure>", sync_scroll_region)
        canvas.bind("<Configure>", sync_width)

        container.columnconfigure(0, weight=1)
        features = self._section(container, "Дополнительные функции")
        features.grid(row=0, column=0, sticky="nsew")
        features.columnconfigure(0, weight=1)
        features.columnconfigure(1, weight=1)

        for index, (feature_id, label, description) in enumerate(FEATURES):
            row = (index // 2) * 2
            column = index % 2
            cell = ttk.Frame(features, padding=(10, 8), style="Card.TFrame")
            cell.grid(row=row, column=column, sticky="new", padx=(0 if column == 0 else 12, 12 if column == 0 else 0), pady=(0, 8))
            cell.columnconfigure(0, weight=1)
            checkbutton = ttk.Checkbutton(cell, text=label, variable=self.feature_vars[feature_id])
            checkbutton.grid(row=0, column=0, sticky="w")
            self.feature_checkbuttons[feature_id] = checkbutton
            ttk.Label(cell, text=description, wraplength=360, style="FeatureText.TLabel").grid(
                row=1, column=0, sticky="w", padx=(24, 0)
            )

    def _section(self, parent: ttk.Frame, title: str) -> ttk.LabelFrame:
        return ttk.LabelFrame(parent, text=title, padding=12, style="Card.TLabelframe")

    def _selected_project_template(self) -> str:
        project_type = self._selected_project_type()
        if project_type == "chrome-extension":
            return "chrome-extension"
        if project_type == "desktop-python":
            return "python-desktop"
        return "vibe"

    def _selected_project_type(self) -> str:
        selected = self.project_type_label.get()
        return next((value for value, label, _description in PROJECT_TYPES if label == selected), "website")

    def _update_template_help(self) -> None:
        selected = self.project_type_label.get()
        description = next((description for _value, label, description in PROJECT_TYPES if label == selected), "")
        self.template_help.config(text=description)

    def _on_template_changed(self, _event: tk.Event | None = None) -> None:
        self._update_template_help()
        self._sync_template_controls(reset_values=True)

    def _is_existing_mode(self) -> bool:
        return self.project_mode.get() == "existing"

    def _on_mode_changed(self) -> None:
        self._sync_template_controls()

    def _sync_template_controls(self, reset_values: bool = False) -> None:
        self._sync_mode_controls()
        self._sync_feature_controls()
        self._sync_desktop_ui_controls()
        self._sync_deployment_controls()
        self._sync_dependency_controls()

    def _sync_mode_controls(self) -> None:
        if self._is_existing_mode():
            self.create_button.config(text="Настроить существующий проект")
            self.mode_help.config(
                text="Безопасно добавляет SETUP_AUDIT, VIBE_SETUP, docs/prompts и выбранные feature packs в уже существующую папку. Код проекта не перезаписывается."
            )
        else:
            self.create_button.config(text="Создать проект")
            self.mode_help.config(
                text="Создаёт новую папку проекта из выбранной основы. Папка не должна существовать заранее."
            )

    def _sync_feature_controls(self) -> None:
        allowed = allowed_features_for_project_type(self._selected_project_type(), tuple(self.feature_vars))
        for feature_id, checkbutton in self.feature_checkbuttons.items():
            if feature_id in allowed:
                checkbutton.state(["!disabled"])
            else:
                self.feature_vars[feature_id].set(False)
                checkbutton.state(["disabled"])

    def _selected_surfaces(self) -> list[str]:
        return surfaces_for_project_type(self._selected_project_type())

    def _selected_desktop_ui(self) -> str:
        selected = self.desktop_ui_label.get()
        return next((value for value, option in DESKTOP_UI_STACKS.items() if option["label"] == selected), DEFAULT_DESKTOP_UI_STACK)

    def _update_desktop_ui_help(self, _event: tk.Event | None = None) -> None:
        stack = self._selected_desktop_ui()
        self.desktop_ui_help.config(text=desktop_ui_option(stack)["gui_help"])
        if hasattr(self, "dependency_help"):
            self._sync_dependency_controls()

    def _sync_desktop_ui_controls(self) -> None:
        if not self._is_existing_mode() and self._selected_project_type() == "desktop-python":
            self.desktop_ui_section.grid()
        else:
            self.desktop_ui_section.grid_remove()

    def _sync_deployment_controls(self) -> None:
        if self._selected_project_type() in HOSTING_PROJECT_TYPES:
            self.deployment_section.grid()
        else:
            self.deployment_plan_label.set(DEPLOYMENT_PLANS[0][1])
            self.deployment_section.grid_remove()

    def _sync_dependency_controls(self) -> None:
        if not self._is_existing_mode() and self._selected_project_type() == "desktop-python":
            self.dependency_section.grid()
            self.dependency_help.config(text=desktop_ui_option(self._selected_desktop_ui())["install_help"])
        else:
            self.dependency_section.grid_remove()

    def _update_deployment_help(self, _event: tk.Event | None = None) -> None:
        selected = self.deployment_plan_label.get()
        description = next((description for _value, label, description in DEPLOYMENT_PLANS if label == selected), "")
        self.deployment_help.config(text=description)

    def _selected_deployment_plan(self) -> str:
        if self._selected_project_type() not in HOSTING_PROJECT_TYPES:
            return "decide-later"
        selected = self.deployment_plan_label.get()
        return next((value for value, label, _description in DEPLOYMENT_PLANS if label == selected), "decide-later")

    def _sync_target_name(self, _event: tk.Event) -> None:
        if self._is_existing_mode():
            return
        current = Path(self.target_path.get())
        if current.parent == DEFAULT_PARENT or not self.target_path.get().strip():
            name = self.project_name.get().strip() or "My Vibe App"
            self.target_path.set(str(DEFAULT_PARENT / name))

    def _browse_target(self) -> None:
        if self._is_existing_mode():
            selected = filedialog.askdirectory(
                title="Выбери папку существующего проекта",
                initialdir=str(Path(self.target_path.get()).parent if self.target_path.get().strip() else DEFAULT_PARENT),
            )
            if not selected:
                return
            path = Path(selected)
            self.target_path.set(str(path))
            self.project_name.set(path.name)
            return

        parent = filedialog.askdirectory(
            title="Выбери папку, внутри которой создать новый проект",
            initialdir=str(DEFAULT_PARENT if DEFAULT_PARENT.exists() else ROOT),
        )
        if not parent:
            return

        name = self.project_name.get().strip() or "My Vibe App"
        self.target_path.set(str(Path(parent) / name))

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
        target = Path(self.target_path.get())
        if self._is_existing_mode():
            if not target.exists() or not target.is_dir():
                messagebox.showerror("Папка не найдена", "Для режима существующего проекта выбери уже существующую папку.")
                return False
            if not INSTALL_SCRIPT.exists():
                messagebox.showerror("Не найден скрипт", f"Не могу найти {INSTALL_SCRIPT}")
                return False
        else:
            if target.exists():
                messagebox.showerror("Папка уже существует", "Такая папка уже существует. Выбери новое имя или другую папку.")
                return False
            if not CLI_SCRIPT.exists():
                messagebox.showerror("Не найден скрипт", f"Не могу найти {CLI_SCRIPT}")
                return False
        return True

    def _show_dependency_check(self) -> None:
        checks = check_system_dependencies()
        report = format_dependency_report(checks)
        self.log.delete("1.0", tk.END)
        self.log.insert(tk.END, report)
        self.log.see(tk.END)

        missing_required = [check.name for check in checks if check.required and not check.found]
        if missing_required:
            messagebox.showwarning(
                "Не хватает зависимостей",
                "Для создания новых проектов нужно установить: " + ", ".join(missing_required),
            )
        else:
            messagebox.showinfo("Зависимости проверены", "Минимум для создания проектов установлен.")

    def _start_create(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        if not self._validate():
            return

        self.log.delete("1.0", tk.END)
        self.status.config(text="Настраиваю проект..." if self._is_existing_mode() else "Создаю проект...")
        self.create_button.config(state=tk.DISABLED)
        self.worker = threading.Thread(target=self._run_create, daemon=True)
        self.worker.start()

    def _run_create(self) -> None:
        if self._is_existing_mode():
            self._run_existing_setup()
            return

        command = [
            find_python(),
            str(CLI_SCRIPT),
            "--target-path",
            self.target_path.get(),
            "--project-name",
            self.project_name.get().strip(),
            "--template",
            self._selected_project_template(),
            "--project-type",
            self._selected_project_type(),
            "--active-surfaces",
            ",".join(self._selected_surfaces()),
        ]
        features = self._selected_features()
        if features:
            command.extend(["--features", ",".join(features)])
        command.extend(["--deployment-plan", self._selected_deployment_plan()])
        if self._selected_project_type() == "desktop-python":
            command.extend(["--desktop-ui", self._selected_desktop_ui()])
            if self.install_dependencies.get():
                command.append("--install-dependencies")
        if not self.include_workflow_docs.get():
            command.append("--skip-workflow-docs")

        self._run_command_with_log(
            command,
            "Создаю проект. Если будут скачиваться репозитории или UI-пакеты, прогресс будет виден ниже.",
        )

    def _run_existing_setup(self) -> None:
        command = [
            find_python(),
            str(INSTALL_SCRIPT),
            "--target-path",
            self.target_path.get(),
            "--project-name",
            self.project_name.get().strip(),
            "--project-type",
            self._selected_project_type(),
            "--active-surfaces",
            ",".join(self._selected_surfaces()),
            "--deployment-plan",
            self._selected_deployment_plan(),
        ]
        features = self._selected_features()
        if features:
            command.extend(["--features", ",".join(features)])
        if not self.include_workflow_docs.get():
            command.append("--skip-workflow-docs")

        self._run_command_with_log(command, "Настраиваю существующий проект. Код проекта не перезаписывается.")

    def _run_command_with_log(self, command: list[str], intro: str) -> None:
        self.output_queue.put(("line", f"{intro}\n"))
        self.output_queue.put(("line", f"Команда: {subprocess.list2cmdline(command)}\n"))
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
                        title = "Проект настроен" if self._is_existing_mode() else "Проект создан"
                        action = "Настроен проект" if self._is_existing_mode() else "Создан проект"
                        messagebox.showinfo(title, f"{action}:\n{self.target_path.get()}")
                    else:
                        self.status.config(text=f"Ошибка, код {code}")
                        messagebox.showerror("Операция не выполнена", "Посмотри лог в этом окне.")
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
