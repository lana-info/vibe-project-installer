"""Shared project option helpers for CLI and GUI launchers."""

from __future__ import annotations

PROJECT_TYPE_SURFACES = {
    "website": ["website"],
    "landing": ["landing"],
    "mobile-web-app": ["web", "mobile", "backend"],
    "desktop-python": ["desktop-python"],
    "chrome-extension": ["chrome-extension"],
}
SIMPLE_PROJECT_FEATURES = {"design-starter"}
HOSTING_PROJECT_TYPES = {"website", "landing", "mobile-web-app"}
FEATURES_BY_PROJECT_TYPE = {
    "website": {
        "payments",
        "uploads-media",
        "social-auth",
        "background-jobs",
        "scheduled-tasks",
        "e2e-tests",
        "admin",
        "realtime",
        "marketplace-catalog",
        "ai-features",
        "design-starter",
    },
    "landing": {
        "payments",
        "social-auth",
        "scheduled-tasks",
        "e2e-tests",
        "marketplace-catalog",
        "ai-features",
        "design-starter",
    },
    "mobile-web-app": None,
    "desktop-python": SIMPLE_PROJECT_FEATURES,
    "chrome-extension": SIMPLE_PROJECT_FEATURES,
}
DESKTOP_UI_STACKS = {
    "tkinter": {
        "label": "tkinter",
        "description": "No extra dependencies. Good only for a small utility or first rough prototype.",
        "gui_help": "Самое простое. Выбирай только для маленькой утилиты или чернового прототипа: почти без красивого дизайна, зато без зависимостей.",
        "install_help": "Скачивать нечего: tkinter уже входит в Python. Примерный объем: 0 МБ.",
        "download_estimate": "0 MB",
    },
    "customtkinter": {
        "label": "customtkinter",
        "description": "Modern Python-only UI with rounded controls. Good for a simple but nicer desktop app.",
        "gui_help": "Простое, но уже симпатичное. Выбирай для небольшого Python-приложения с современными кнопками, карточками и sidebar без усложнения.",
        "install_help": "Если включить, будет создана .venv и скачан UI-пакет customtkinter для этого проекта. Примерный объем: 5-20 МБ.",
        "download_estimate": "5-20 MB",
    },
    "pyside6": {
        "label": "PySide6 / Qt",
        "description": "Professional Python desktop UI. Best Python-only option for sidebars, cards, tables, and larger apps.",
        "gui_help": "Профессиональный desktop на Python. Выбирай для серьезного приложения: много экранов, таблицы, настройки, сложная навигация, аккуратный нативный UI.",
        "install_help": "Если включить, будет создана .venv и скачан PySide6/Qt для этого проекта. Это крупный UI-пакет. Примерный объем: 150-300+ МБ.",
        "download_estimate": "150-300+ MB",
    },
    "flet": {
        "label": "Flet",
        "description": "Fast Python app with a web-like UI model. Good when speed matters more than full native control.",
        "gui_help": "Быстро и похоже на web-app. Выбирай, если нужен красивый интерфейс быстрее, чем на Qt, и удобно мыслить экранами/карточками.",
        "install_help": "Если включить, будет создана .venv и скачан UI-пакет flet для этого проекта. Примерный объем: 30-100 МБ.",
        "download_estimate": "30-100 MB",
    },
    "tauri-shadcn": {
        "label": "React + Tailwind + shadcn/ui + Tauri",
        "description": "Modern polished app: sidebar, cards, search, clean buttons, and a desktop shell.",
        "gui_help": "Самый красивый вариант для приложения как рабочий кабинет: боковое меню, карточки, поиск, аккуратные кнопки и внешний вид как у современных платных сервисов. Выбирай, если дизайн важен и нормально использовать web-технологии внутри desktop-приложения.",
        "install_help": "Если включить, будет выполнен npm install: пакеты React-интерфейса, Tailwind, Tauri-оболочка, иконки и UI-утилиты из package.json. Примерный объем: 150-400+ МБ, без учета Rust/Tauri tools, если их еще нет на компьютере.",
        "download_estimate": "150-400+ MB, not counting Rust/Tauri tools if missing",
    },
}
DEFAULT_DESKTOP_UI_STACK = "tkinter"


def surfaces_for_project_type(project_type: str) -> list[str]:
    return list(PROJECT_TYPE_SURFACES.get(project_type, PROJECT_TYPE_SURFACES["mobile-web-app"]))


def allowed_features_for_project_type(project_type: str, all_features: list[str] | tuple[str, ...]) -> set[str]:
    allowed = FEATURES_BY_PROJECT_TYPE.get(project_type)
    if allowed is None:
        return set(all_features)
    return set(allowed)


def desktop_ui_label(stack: str) -> str:
    return DESKTOP_UI_STACKS.get(stack, DESKTOP_UI_STACKS[DEFAULT_DESKTOP_UI_STACK])["label"]


def desktop_ui_option(stack: str) -> dict[str, str]:
    return DESKTOP_UI_STACKS.get(stack, DESKTOP_UI_STACKS[DEFAULT_DESKTOP_UI_STACK])
