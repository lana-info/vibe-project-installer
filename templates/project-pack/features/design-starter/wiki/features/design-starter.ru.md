# Design Starter / Основы Дизайна

Используй этот feature pack, если проект должен сразу стартовать с более сильной визуальной базой.

Это не ставит отдельный полный дизайн-шаблон по умолчанию. Это добавляет workflow и одобренные источники, чтобы UI был красивее, но оставался простым для правок.

## Рекомендованные Источники

- shadcn/ui Blocks: web apps, dashboards, forms, login screens, landing sections, app layouts. Локальный архив: `D:\WorkOS\design-shadcn-ui-archive`.
- Magic UI: аккуратно для landing-анимаций, hero sections, social proof и маркетинговой полировки. Локальный архив: `D:\WorkOS\design-magic-ui-archive`.
- Origin UI: copy-paste React/Tailwind компоненты, когда базовые shadcn/ui компоненты слишком голые. Локальный архив: `D:\WorkOS\design-origin-ui-archive`.
- React Native Reusables: смотреть осторожно для mobile-идей, но не добавлять по умолчанию без причины. Локальный архив: `D:\WorkOS\design-react-native-reusables-archive`.

Обновить архивы можно из installer-репозитория:

```powershell
.\scripts\sync-upstream-archive.ps1
```

## Когда Включать

- Первый экран должен выглядеть красиво, а не просто функционально.
- Нужны landing, dashboard, admin, settings, onboarding или paywall screens.
- Хочется маленькая компонентная библиотека проекта до feature-разработки.
- Нужно, чтобы агент делал 2-3 дизайн-прохода, а не один сырой UI-проход.

## Checklist

- [ ] Описать визуальный тон продукта в `PRD.ru.md`.
- [ ] Выбрать 2-3 reference screens/components до реализации.
- [ ] Создать или уточнить design tokens: colors, radius, spacing, typography.
- [ ] Сделать reusable components до копирования UI-паттернов.
- [ ] Для web начинать с shadcn/ui-style composition и тюнить.
- [ ] Для mobile сначала сделать маленькую локальную библиотеку компонентов.
- [ ] Проверить desktop и mobile screenshots до статуса done.

## Правила Для Агента

- Не добавлять большую UI-библиотеку просто потому, что она выглядит полезной.
- Не копировать целый design kit вслепую.
- Сначала строить настоящий workflow screen.
- Тюнить spacing, hierarchy, states и responsiveness.
- Держать компоненты простыми для будущих правок Codex.
