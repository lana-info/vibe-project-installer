# Scheduled Tasks / Cron

Use this feature pack if the product needs tasks that run on a schedule.

## Examples

- Send a daily or weekly report.
- Check subscription/payment status every hour.
- Clean temporary files.
- Process notification queues every few minutes.
- Refresh data from another API.
- Run maintenance or reminder jobs.

## Upstream Support

The upstream template includes a backend cron entry point. Hosting providers run cron differently, so keep the schedule documented and provider-neutral until launch.

## Product Questions

- What task runs on a schedule?
- How often should it run?
- What timezone matters?
- Can two runs overlap?
- What happens if a scheduled run fails?

## Setup Checklist

- [ ] Define each scheduled task in `PRD.md`.
- [ ] Record schedule, timezone, and failure behavior.
- [ ] Make each task safe to run twice.
- [ ] Log success and failure clearly.
- [ ] Add tests for the task logic separately from the hosting scheduler.

