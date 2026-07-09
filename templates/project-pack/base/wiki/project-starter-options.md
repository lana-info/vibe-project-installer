# Project Starter Options

Use this file when deciding what kind of product to vibe-code and which base should be loaded first.

## Built-In Project Types

- `Website`: a normal website that works in a browser on mobile and desktop.
- `Landing`: one marketing or presentation page for testing an idea, ads, or launch.
- `Mobile app + Web app`: a real mobile app plus web app/site and backend/API.
- `Desktop Python app`: a local computer app built from a small Python starter.
- `Chrome extension`: a browser extension based on `JohnBra/vite-web-extension`.

## Feature Pack Rule

Use app feature packs such as payments, uploads, push, admin, background jobs, and E2E tests for `Mobile app + Web app`.

For `Website` and `Landing`, use only the feature packs that match the public web flow. `Desktop Python app` and `Chrome extension` stay limited to docs and optional `Design starter`.

## Design Defaults

- Website and Landing: start from shadcn/ui-style composition, Magic UI sparingly, and tune the product's own design.
- Mobile app: build a small project-specific component library before feature work.
- Desktop Python app: choose the UI stack during project creation. `tkinter` is the simplest no-download option; `customtkinter` is a simple modern Python UI; `PySide6 / Qt` is a professional heavier desktop UI; `Flet` is a fast web-like Python UI; `React + Tailwind + shadcn/ui + Tauri` is for a polished work-dashboard app with sidebar, cards, and search.
- Extension: keep popup/options/content-script UI focused and permission-light.

## UI Packages

For desktop projects, the installer creates files and package manifests by default. It does not download `.venv`, `node_modules`, or UI packages unless the user explicitly turns on `Пакеты интерфейса` / UI package install.

Approximate download size when UI package install is enabled:

- `tkinter`: 0 MB, included with Python.
- `customtkinter`: about 5-20 MB.
- `PySide6 / Qt`: about 150-300+ MB.
- `Flet`: about 30-100 MB.
- `React + Tailwind + shadcn/ui + Tauri`: about 150-400+ MB, plus Rust/Tauri tools if missing.

## Hosting

Hosting plan selection applies only to `Website`, `Landing`, and `Mobile app + Web app`. For `Desktop Python app` and `Chrome extension`, keep hosting as `Decide later` at the start.
