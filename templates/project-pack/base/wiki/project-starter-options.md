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

For `Website`, `Landing`, `Desktop Python app`, and `Chrome extension`, start with docs and optional `Design starter` only. Add heavier app features later only when the PRD clearly needs them.

## Design Defaults

- Website and Landing: start from shadcn/ui-style composition, Magic UI sparingly, and tune the product's own design.
- Mobile app: build a small project-specific component library before feature work.
- Desktop Python app: start with `tkinter`; consider `customtkinter`, `PySide6`, or `Flet` only when the UI needs it.
- Extension: keep popup/options/content-script UI focused and permission-light.
