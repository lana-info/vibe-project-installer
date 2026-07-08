# Chrome Extension

Используй этот файл, если основа проекта `chrome-extension`.

## Основа

Installer использует:

```text
https://github.com/JohnBra/vite-web-extension
```

Это starter для browser extension: React, TypeScript, Tailwind CSS, Vite, Manifest V3, Chrome build, Firefox build, optional localization и optional cross-browser polyfill.

## Вопросы По Продукту

- Расширение только для Chrome или Chrome + Firefox?
- Нужны popup UI, options page, content script, background service worker или все сразу?
- На каких сайтах оно должно работать?
- Какие permissions действительно нужны?
- Нужны аккаунты, оплаты, sync, local storage или backend API?
- Публикация будет в Chrome Web Store, Firefox Add-ons или приватно?

## Safety Checklist

- [ ] Permissions минимальны.
- [ ] Не собирать данные страницы без необходимости и объяснения.
- [ ] Не хранить secrets во frontend-коде расширения.
- [ ] Подготовить privacy policy перед публикацией, если собираются данные.
- [ ] Проверить как unpacked extension перед упаковкой.
- [ ] Подготовить store assets: icon, screenshots, description, support email, privacy text.

