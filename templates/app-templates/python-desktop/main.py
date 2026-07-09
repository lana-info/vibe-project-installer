#!/usr/bin/env python3
"""Small desktop app starter."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


APP_NAME = "{{PROJECT_NAME}}"


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("720x480")
        self.minsize(560, 360)

        self._configure_style()
        self._build_ui()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=24)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)

        ttk.Label(root, text=APP_NAME, style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            root,
            text="Desktop app starter. Replace this screen with the first real workflow.",
        ).grid(row=1, column=0, sticky="w", pady=(8, 18))

        content = ttk.Frame(root, padding=18, relief="solid")
        content.grid(row=2, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)

        ttk.Label(content, text="Main workspace").grid(row=0, column=0, sticky="w")
        ttk.Button(content, text="Run action", command=self._run_action).grid(row=1, column=0, sticky="w", pady=(12, 0))

        self.status = tk.StringVar(value="Ready")
        ttk.Label(root, textvariable=self.status).grid(row=3, column=0, sticky="w", pady=(18, 0))

    def _run_action(self) -> None:
        self.status.set("Action clicked. Add your app logic here.")


def main() -> int:
    app = App()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
