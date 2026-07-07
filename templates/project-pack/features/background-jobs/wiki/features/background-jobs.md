# Background Jobs

Use this feature pack if the product needs work that should run outside the user's immediate request.

## Examples

- Process uploaded images, PDFs, videos, or exports.
- Generate AI content or large files.
- Send batches of email or notifications.
- Process payment webhooks.
- Sync data with another service.
- Recalculate reports, recommendations, or search indexes.

## Upstream Support

The upstream template includes a backend worker entry point. Treat it as a place for real background handlers, not as a separate app.

## Product Questions

- What event creates a job?
- Does the user need progress, retry, or cancellation?
- How long can the job run?
- What happens if it fails?
- Does it need a queue, or is a simple worker enough for MVP?

## Setup Checklist

- [ ] Define each background job in `PRD.md`.
- [ ] Keep job state in the database when users need status or retries.
- [ ] Make handlers safe to retry.
- [ ] Keep secrets out of git and chat.
- [ ] Add tests for job creation, failure, and retry behavior.

