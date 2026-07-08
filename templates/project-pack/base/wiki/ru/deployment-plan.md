# План Хостинга

Выбранный план: {{DEPLOYMENT_PLAN}}

Создание проекта ничего не деплоит и не создает платные облачные ресурсы. Этот файл нужен, когда продукт будет готов к запуску.

## Что Значит Выбор

- `Decide later`: не привязываем проект к провайдеру на старте.
- `Hetzner`: смотри `wiki/deployment-providers/hetzner.md`.
- `Timeweb`: смотри `wiki/deployment-providers/timeweb.md`.
- `DigitalOcean`: upstream имеет самый подробный runbook в `docs/DEPLOYMENT.md`.
- `Hostinger`: смотри `wiki/deployment-providers/hostinger.md`.
- `Custom hosting`: Render, Railway, Vercel, Netlify, Fly.io, VPS или другой вариант.

## Перед Запуском

- [ ] Решить, где работает backend/API.
- [ ] Решить, где лежит webapp/website.
- [ ] Решить, где production Postgres.
- [ ] Решить, где durable uploads/media, если есть файлы.
- [ ] Решить, как запускаются background jobs и cron, если выбраны.
- [ ] Описать domains, SSL, backups, logs, monitoring и rollback.
- [ ] Хранить secrets в настройках хостинга, не в git и не в чате.

