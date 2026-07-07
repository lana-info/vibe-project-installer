# Mobile + Web E2E Tests

Use this feature pack if the project should automatically test real user flows across mobile and web.

## What E2E Means

End-to-end tests open the app like a user and check that the full flow works: login, onboarding, payment, profile, upload, catalog, or another important journey.

## Upstream Support

The upstream mobile app includes Maestro test setup for mobile flows. The webapp includes browser/e2e test structure. Use both when the same product journey must work on mobile and web.

## Product Questions

- What are the 1-3 flows that must never break?
- Should the flow be tested on mobile, web, or both?
- What test account/data is safe to use?
- Should payments/uploads be mocked or tested in sandbox?
- What must run locally before each commit?

## Setup Checklist

- [ ] Pick one critical mobile flow.
- [ ] Pick one critical web flow.
- [ ] Keep test credentials out of git and chat.
- [ ] Prefer sandbox services for payments and uploads.
- [ ] Add E2E only after the UI flow is stable enough to test.

