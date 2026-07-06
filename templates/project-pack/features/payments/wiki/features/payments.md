# Payments / Subscriptions

Use this feature pack if the project sells access, subscriptions, premium content, paid tools, or paid mobile features.

## Upstream Support

The `mobile` branch includes App Store and Google Play subscription foundation, mobile paywall flows, backend entitlement checks, and `docs/IAP.md`.

## Product Questions

- What is paid: access, content, credits, files, services, or subscription?
- Is payment required for mobile only, web only, or both?
- Monthly, yearly, lifetime, one-time, or credit-based?
- What does a free user see?
- What happens when subscription expires, is refunded, or is cancelled?

## Setup Checklist

- [ ] Define products and prices in `PRD.md`.
- [ ] Decide free vs premium access rules.
- [ ] Read `docs/IAP.md` before changing payment code.
- [ ] Keep store credentials out of git and chat.
- [ ] Add tests for entitlement and access-control behavior.

