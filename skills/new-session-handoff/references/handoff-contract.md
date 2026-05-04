# Handoff Contract

This is the canonical runtime contract for `new-session-handoff`. `HANDOFF.md` is a recoverable entry manifest, not a transcript dump and not proof that code is correct.

Recoverability comes first. Compactness comes second.

## Modes

- `compact`: one `HANDOFF.md` contains the recovery state.
- `expanded`: `HANDOFF.md` remains the entry manifest and links focused `details/*.md` artifacts.
- `prompt-only`: no files are written; the response contains a self-contained continuation prompt and marker values use `HANDOFF_READY: not-written`.

Expanded detail paths are relative to the directory containing `HANDOFF.md` unless the handoff explicitly says otherwise.

Recommended expanded artifacts:

- `details/architecture.md`: boundaries, data flow, and rationale.
- `details/changed-files.md`: file-by-file semantic ledger and anchors.
- `details/validation.md`: commands, results, key failures, and next checks.
- `details/pitfalls.md`: failed approaches and do-not-repeat notes.
- `details/open-questions.md`: unresolved questions when they need more structure.

Each detail artifact must answer one recovery question. Do not write raw transcripts, full diffs, long logs, shell history, or chat history unless the user explicitly asks and the content is essential and redacted.

## Required `HANDOFF.md` Shape

`HANDOFF.md` must include:

- `TL;DR / Operational Summary` with exactly one `Goal`, `Current state`, `Next action`, and `Blocker`.
- recovery contract with schema version, mode, safety state, blockers, trust order, and disk-verification requirement.
- session target, done criteria, out-of-scope notes, and smallest executable next step.
- repo snapshot: captured time, cwd, Git root, branch, short HEAD, status, diff stat, name-status, staged state, latest commit, loaded instruction files, and expected drift.
- required reading order and files to inspect first.
- change manifest for changed, created, deleted, moved, staged, inspected, and unknown files.
- decisions, rationale, risks, pitfalls, failed approaches, and unresolved questions.
- validation manifest with command, result, key failure lines, skipped checks, next validation, secret redaction check, and observable completion criteria.
- fresh-session prompt path or embedded prompt.
- exactly one automation marker block.

## Trust Order

On resume, trust sources in this order:

1. Current explicit user instruction in this session.
2. Current working tree and Git state.
3. Repository instruction files such as `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `PLAN.md`, and `PLANS.md`.
4. `HANDOFF.md`.
5. Focused detail artifacts referenced by `HANDOFF.md`.
6. Prior chat history only if explicitly provided by the user.

If the handoff conflicts with disk state, disk state wins. Report the mismatch before editing.

## Create Contract

Before writing a handoff, inspect and record:

- `pwd`
- Git root if inside a repository
- branch
- short HEAD
- `git status --short`
- `git diff --stat`
- `git diff --name-status`
- `git diff --cached --stat`
- latest commit
- relevant instruction files

Read only enough files to verify recovery state. Prefer instruction files, existing handoff artifacts, changed files, and files needed for the smallest next step. Do not recursively read private agent config directories or secret-bearing files by default.

Summarize only verified facts. Use `Unknown` or `확인 필요` for unverified details.

## Resume Contract

Before implementation, confirm current disk state, read applicable instructions, read `HANDOFF.md`, resolve relative detail artifact paths against the handoff directory, inspect required files, and compare handoff claims with the working tree.

Report the loaded instructions, repo state, handoff consistency, detail artifacts read, missing or conflicting paths, and smallest next step before editing.

If `SAFE_FOR_NEW_SESSION` is not `yes`, stop after the report unless the user explicitly instructs how to proceed.

## Secret Hygiene

Never copy secrets, tokens, API keys, cookies, credentials, private keys, full environment variable values, shell history, or secret-bearing logs into `HANDOFF.md`, `NEW_SESSION_PROMPT.txt`, or detail artifacts.

Redact required mentions as `<REDACTED>` and record only the variable name, file category, or secret category when needed.

Before setting `SECRET_REDACTION_CHECKED: yes`, scan generated handoff artifacts, not the whole repository by default. If redaction cannot be verified, set `SECRET_REDACTION_CHECKED: no` and `SAFE_FOR_NEW_SESSION: no`.

## Automation Marker Block

Use exactly one final marker block:

```text
HANDOFF_AUTOMATION_V1
HANDOFF_READY: <absolute path or not-written>
HANDOFF_SCHEMA_VERSION: 1
HANDOFF_MODE: compact|expanded|prompt-only
DETAIL_ARTIFACTS_READY: yes|no|not-needed
NEW_SESSION_PROMPT_READY: yes|no
DISK_STATE_RECORDED: yes|no
VALIDATION_RECORDED: yes|no
SECRET_REDACTION_CHECKED: yes|no
SAFE_FOR_NEW_SESSION: yes|no
BLOCKERS: none|<short reason>
END_HANDOFF_AUTOMATION_V1
```

Field meanings:

- `HANDOFF_READY`: absolute path to `HANDOFF.md`, or `not-written`.
- `HANDOFF_SCHEMA_VERSION`: currently `1`.
- `HANDOFF_MODE`: `compact`, `expanded`, or `prompt-only`.
- `DETAIL_ARTIFACTS_READY`: `yes` for verified expanded artifacts, `not-needed` for compact or prompt-only, otherwise `no`.
- `NEW_SESSION_PROMPT_READY`: `yes` when a continuation prompt exists or was provided.
- `DISK_STATE_RECORDED`: `yes` only when the required repo snapshot was recorded.
- `VALIDATION_RECORDED`: `yes` when validation status is recorded, including passed, failed, or intentionally skipped validation with low-risk reason and next command.
- `SECRET_REDACTION_CHECKED`: `yes` only after checking generated artifacts for secrets.
- `SAFE_FOR_NEW_SESSION`: `yes` only when the checklist below passes.
- `BLOCKERS`: `none` or a short reason preventing safe rotation.

The marker value schema lives at `schemas/handoff-automation-v1.schema.json`.

## `SAFE_FOR_NEW_SESSION: yes`

Set `SAFE_FOR_NEW_SESSION: yes` only when all are true:

- no command, build, test, dev server, approval prompt, or session-control action is still running.
- repo snapshot is recorded.
- dirty, staged, changed, created, deleted, moved, and inspected files are listed or explicitly marked `none`.
- `HANDOFF.md` exists, or prompt-only mode intentionally records `HANDOFF_READY: not-written`.
- every referenced detail artifact exists, or details are `not-needed`.
- disk-state conflict handling is stated.
- validation command and result are recorded, or skipped validation has a low-risk reason and next command.
- secret redaction was checked.
- no unresolved user question blocks continuation.
- the next step is singular, executable, and narrow.
- `BLOCKERS: none`.

A failed validation command does not automatically force `SAFE_FOR_NEW_SESSION: no`. It may still be safe when the command has finished, key failure lines are recorded, the next step is narrow, and continuing cannot overwrite unknown state.

Force `SAFE_FOR_NEW_SESSION: no` when a command or approval prompt is still running, repo state is missing, changed files are not listed, referenced artifacts are missing, secrets are unredacted, the next step is vague, or a blocker requires user input.

`SAFE_FOR_NEW_SESSION: yes` means a fresh session can reconstruct state and continue. It does not mean tests pass, code is correct, or the task is complete.

## Staleness Rules

Report the handoff as stale before editing when branch, HEAD, dirty files, required paths, detail artifacts, or validation assumptions differ from the recorded snapshot without an explicit expected-drift note.

Stale does not always mean unsafe. If the mismatch is explained, narrow, and the next step remains executable, the fresh session may continue after reporting it. Otherwise it must stop after the verification report.
