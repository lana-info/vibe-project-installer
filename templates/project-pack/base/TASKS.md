# Tasks

Work from top to bottom. Keep each task small and check it before moving on.

## Phase 1: Product Definition

- [ ] T001: Finish `PRD.md`
  - Result: product goal, MVP, active surfaces, feature packs, and acceptance criteria are clear.
  - Verify: `PRD.md` has no unresolved product questions.

- [ ] T002: Review `PRD.md` in a fresh AI context
  - Result: missing questions are found and answered.
  - Verify: updated `PRD.md` still has no TODOs in core requirements.

## Phase 2: First Working Slice

- [ ] T003: Pick the first user journey
  - Result: one small workflow is selected for implementation.
  - Verify: the workflow can be checked manually or with a test.

- [ ] T004: Implement the first working slice
  - Result: the selected workflow works on active surfaces: {{ACTIVE_SURFACES}}.
  - Verify: run the smallest relevant local check.

## Phase 3: Quality

- [ ] T005: Run code review
  - Result: serious issues are fixed or explicitly accepted.
  - Verify: review findings have file paths and evidence.

- [ ] T006: Add tests for risky behavior
  - Result: important auth, data, money, permissions, or user flows are protected.
  - Verify: tests pass and cover the risky behavior.

