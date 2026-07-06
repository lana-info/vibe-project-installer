# Project Agent Rules

Answer in the user's language.

This project is a small installer wrapper around `di-sukharev/vibe`. Keep it focused.

Before changing behavior:

1. Read `README.md` and `scripts/bootstrap-project.ps1`.
2. Keep the script provider-neutral by default.
3. Do not make DigitalOcean, Yandex Cloud, EAS, Docker, or GitHub publishing mandatory.
4. Preserve the default behavior that removes the upstream template remote after clone.
5. Verify changes with a scratch install.
6. Report the exact command used and whether the generated README contains the expected bootstrap plan.

Do not copy the full upstream template into this repo.
Do not print secrets, tokens, or `.env` content.
Do not push to upstream `di-sukharev/vibe`.
