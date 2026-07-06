# Admin Panel

Use this feature pack if you need an internal dashboard to manage users, content, orders, support, moderation, or settings.

## Upstream Support

Admin is not a complete ready-made upstream module. Treat it as product scope that should be designed before coding.

## Product Questions

- Who is an admin?
- What can admins view, create, edit, delete, approve, or export?
- What actions need audit logs?
- What data is sensitive?

## Setup Checklist

- [ ] Define admin roles and permissions in `PRD.md`.
- [ ] Keep admin screens behind authentication and explicit admin checks.
- [ ] Add backend permission tests for every admin action.
- [ ] Avoid exposing private user data by default.

