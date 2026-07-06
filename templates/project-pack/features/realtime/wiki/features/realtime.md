# Realtime / Chat

Use this feature pack if the product needs chat, live updates, collaboration, presence, typing indicators, or instant events.

## Upstream Support

Realtime is not a complete ready-made upstream module. Upstream guidance recommends keeping the backend monolithic first and adding Redis-compatible Pub/Sub only when horizontal scaling needs cross-instance fanout.

## Product Questions

- What must update live?
- Is this chat, collaboration, presence, notifications, or status updates?
- How fresh does it need to be?
- How many users can be in one live room/session?
- What happens when users disconnect?

## Setup Checklist

- [ ] Define exact realtime use cases in `PRD.md`.
- [ ] Start with the simplest polling or single-instance approach if enough.
- [ ] Add WebSockets/SSE only when the user experience really needs it.
- [ ] Add Pub/Sub only when multiple backend instances must share events.

