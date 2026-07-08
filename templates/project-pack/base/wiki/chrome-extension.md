# Chrome Extension Notes

Use this when the project template is `chrome-extension`.

## Base Template

This installer uses:

```text
https://github.com/JohnBra/vite-web-extension
```

It is a browser extension starter with React, TypeScript, Tailwind CSS, Vite, Manifest V3, Chrome build, Firefox build, optional localization, and optional cross-browser polyfill support.

## Useful Commands

Check the generated `package.json`, but the upstream template currently includes:

```bash
yarn
yarn dev
yarn build
yarn build:chrome
yarn build:firefox
```

## Product Questions

- Is this extension for Chrome only or Chrome + Firefox?
- Does it need popup UI, options page, content script, background service worker, or all of them?
- What websites should it run on?
- What permissions are truly required?
- Does it need user accounts, payments, sync, local storage, or backend API?
- Will it be published to Chrome Web Store, Firefox Add-ons, or distributed privately?

## Safety Checklist

- [ ] Keep requested permissions minimal.
- [ ] Do not collect page data unless it is required and explained.
- [ ] Keep secrets out of extension frontend code.
- [ ] Add a privacy policy before store publication if data is collected.
- [ ] Test install as an unpacked extension before packaging.
- [ ] Document store assets: icon, screenshots, description, support email, privacy text.

