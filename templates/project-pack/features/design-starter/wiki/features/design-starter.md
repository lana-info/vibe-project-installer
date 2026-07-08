# Design Starter

Use this feature pack when the project should start with a stronger visual foundation.

This does not install another full template by default. It gives the agent a design workflow and approved reference sources so UI work starts from better components and still stays editable.

## Recommended Sources

- shadcn/ui Blocks: use for web apps, dashboards, forms, login screens, landing sections, and app layouts. Local archive: `D:\WorkOS\design-shadcn-ui-archive`.
- Magic UI: use selectively for landing page moments, tasteful animation, hero sections, social proof, and marketing polish. Local archive: `D:\WorkOS\design-magic-ui-archive`.
- Origin UI: use as copy-paste React/Tailwind component inspiration when shadcn/ui base components are too bare. Local archive: `D:\WorkOS\design-origin-ui-archive`.
- React Native Reusables: review carefully for mobile ideas, but do not add by default until it fits the app stack. Local archive: `D:\WorkOS\design-react-native-reusables-archive`.

Refresh archives from the installer repo:

```powershell
.\scripts\sync-upstream-archive.ps1
```

## When To Use

- The first screen must look polished, not merely functional.
- The product needs landing, dashboard, admin, settings, onboarding, or paywall screens.
- You want a small project-specific component set before feature work.
- You want the agent to do 2-3 design passes instead of one rough UI pass.

## Setup Checklist

- [ ] Define the product visual tone in `PRD.md`.
- [ ] Pick 2-3 reference screens or components before building.
- [ ] Create or refine design tokens: colors, radius, spacing, typography.
- [ ] Build reusable components before duplicating UI patterns.
- [ ] For web, start with shadcn/ui-style composition and tune.
- [ ] For mobile, create a small local component library before screens.
- [ ] Verify desktop and mobile layouts with screenshots before calling UI done.

## Agent Rules

- Do not add a large UI framework just because it looks useful.
- Do not copy a whole design kit blindly.
- Build the real workflow screen first.
- Tune spacing, hierarchy, states, and responsiveness.
- Keep components simple enough for future Codex edits.
