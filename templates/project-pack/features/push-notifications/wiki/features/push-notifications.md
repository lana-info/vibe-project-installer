# Push Notifications

Use this feature pack if the mobile app should send reminders, alerts, re-engagement messages, or important status updates.

## Upstream Support

The `mobile` branch includes Expo Push notification foundation, backend notification routes, and an outbox/worker pattern.

## Product Questions

- What events should trigger notifications?
- Transactional, reminders, marketing, or all?
- Should users control notification preferences?
- What should happen when a notification is tapped?

## Setup Checklist

- [ ] Define notification types and consent rules in `PRD.md`.
- [ ] Keep APNs/FCM/EAS credentials out of git and chat.
- [ ] Test on a physical device or real development build.
- [ ] Add safe internal navigation paths for notification taps.

