# How To Work With AI Coding Agents

Use this file as the simple operating checklist for Codex, Claude Code, or another coding agent.

## Short Rule

Do not ask the agent to build the whole product at once. Work in small checked steps:

1. Write or update `PRD.md`.
2. Review `PRD.md` in a fresh context.
3. Create or update `TASKS.md`.
4. Implement one small task.
5. Verify it.
6. Run code review.
7. Commit.

## Copy This First

```text
Read README.md, START_HERE.md, PRD.md, TASKS.md, and relevant files.
Do not change files yet.
Tell me what the next smallest safe task is, what files are involved, and how you will verify it.
```

## After The Plan Looks Right

```text
Implement only this task.
Keep the change minimal.
Do not add unrelated features or dependencies.
Run the shortest relevant verification.
Report changed files, checks run, and anything not verified.
```

## Code Review Prompt

```text
Do a read-only code review of the current changes.
Prioritize real bugs, regressions, security/privacy risks, data loss, and missing important tests.
Return findings with severity, file/line, evidence, risk, fix, and verification.
```

## When To Add Tests

Add tests when work touches:

- login, accounts, permissions, or sessions;
- payments or subscriptions;
- database writes or migrations;
- uploads, private files, or user data;
- important user flows;
- bugs that could come back.

## Safety Rules

- Do not paste secrets, tokens, passwords, cookies, or `.env` values into chat.
- Do not publish, deploy, or connect cloud services until you explicitly choose to launch.
- Do not let the agent delete or rewrite unrelated work.
- Keep each commit focused.

