# Social Auth

Use this feature pack if users should sign in with Apple or Google instead of only email/password.

## Upstream Support

The `mobile` branch includes Apple and Google social auth foundation and `docs/SOCIAL_AUTH.md`.

## Product Questions

- Which providers are needed: Apple, Google, or both?
- Mobile only, web only, or both?
- Should social accounts link to existing email/password accounts?
- What happens if provider email is missing or already used?

## Setup Checklist

- [ ] Define provider behavior in `PRD.md`.
- [ ] Read `docs/SOCIAL_AUTH.md`.
- [ ] Keep OAuth client secrets out of git and chat.
- [ ] Add tests for provider token validation and account collision behavior.

