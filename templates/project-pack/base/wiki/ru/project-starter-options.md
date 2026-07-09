# Варианты Основы Проекта

Этот файл нужен, когда выбираем, что именно вайбкодить и какую основу загрузить.

## Встроенные Типы Проекта

- `Website`: обычный сайт, который работает в браузере на телефоне и компьютере.
- `Landing`: одна продающая или презентационная страница для проверки идеи, рекламы или запуска.
- `Mobile app + Web app`: отдельное мобильное приложение плюс веб-приложение/сайт и backend/API.
- `Desktop Python app`: локальное приложение для компьютера на маленьком Python starter.
- `Chrome extension`: расширение браузера на `JohnBra/vite-web-extension`.

## Правило Feature Packs

Оплаты, uploads, push, admin, background jobs, E2E tests и другие app-функции включай для `Mobile app + Web app`.

Для `Website` и `Landing` включай только те feature packs, которые реально подходят публичному веб-сценарию. `Desktop Python app` и `Chrome extension` оставляй ограниченными документацией и optional `Design starter`.

## Дизайн По Умолчанию

- Website и Landing: shadcn/ui-style composition, Magic UI аккуратно, потом настройка под дизайн продукта.
- Mobile app: маленькая библиотека компонентов под конкретный проект до feature work.
- Desktop Python app: выбрать UI-стек при создании проекта. `tkinter` - самое простое без скачивания; `customtkinter` - простой современный Python UI; `PySide6 / Qt` - профессиональный тяжелый desktop UI; `Flet` - быстрый web-like Python UI; `React + Tailwind + shadcn/ui + Tauri` - красивый рабочий кабинет с sidebar, карточками и поиском.
- Extension: сфокусированный popup/options/content-script UI и минимум permissions.

## Пакеты Интерфейса

Для desktop-проекта installer по умолчанию только создает файлы и список пакетов (`requirements.txt` или `package.json`). Он не скачивает `.venv`, `node_modules` и UI-пакеты, пока пользователь явно не включит `Пакеты интерфейса`.

Примерный объем скачивания, если включить установку:

- `tkinter`: 0 МБ, уже входит в Python.
- `customtkinter`: примерно 5-20 МБ.
- `PySide6 / Qt`: примерно 150-300+ МБ.
- `Flet`: примерно 30-100 МБ.
- `React + Tailwind + shadcn/ui + Tauri`: примерно 150-400+ МБ, плюс Rust/Tauri tools, если их еще нет.

## Хостинг

План хостинга выбирается только для `Website`, `Landing` и `Mobile app + Web app`. Для `Desktop Python app` и `Chrome extension` на старте оставляй `Decide later`: это не серверный проект.
