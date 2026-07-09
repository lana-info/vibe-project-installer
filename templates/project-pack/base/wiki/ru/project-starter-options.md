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

Для `Website`, `Landing`, `Desktop Python app` и `Chrome extension` на старте оставляй только документацию и optional `Design starter`. Тяжелые app-функции добавляй позже только если PRD явно этого требует.

## Дизайн По Умолчанию

- Website и Landing: shadcn/ui-style composition, Magic UI аккуратно, потом настройка под дизайн продукта.
- Mobile app: маленькая библиотека компонентов под конкретный проект до feature work.
- Desktop Python app: начать с `tkinter`; `customtkinter`, `PySide6` или `Flet` выбирать только если UI реально этого требует.
- Extension: сфокусированный popup/options/content-script UI и минимум permissions.
