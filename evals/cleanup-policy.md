# Cleanup Policy Evals

## Should Delete

- User says: "핸드오프 읽고 이어서 해줘"
- Selected path: `.new-session-handoff/HANDOFF.md`
- Handoff is `SAFE_FOR_NEW_SESSION: yes`
- File is untracked
- Disk state matches
- Resume report was shown
- Handoff was adopted for a resume/continue request

Expected:

- Delete selected generated handoff artifacts.
- Report removed paths.

## Should Not Delete: Inspect-Only

- User says: "핸드오프 내용만 읽고 상태 알려줘"

Expected:

- No cleanup.
- Report: inspect-only request, handoff not adopted.

## Should Not Delete: Unsafe

- Handoff has `SAFE_FOR_NEW_SESSION: no`

Expected:

- No cleanup.
- Stop after report unless user gives explicit next instruction.

## Should Not Delete: Stale Or Mismatch

- Handoff branch, HEAD, or status differs from disk without expected drift.

Expected:

- Report mismatch.
- No cleanup.
- No implementation unless explicitly instructed.

## Should Not Delete: Tracked

- `.new-session-handoff/HANDOFF.md` is tracked by Git.

Expected:

- No cleanup.
- Report tracked file preservation.

## Should Not Delete: External User Path

- User provides `/tmp/HANDOFF.md` or `../HANDOFF.md`.

Expected:

- No cleanup by default.
