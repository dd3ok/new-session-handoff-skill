---
name: new-session-handoff
description: Create a self-contained handoff for a fresh coding-agent session when context is nearly full, compacted, or being rotated by an orchestrator.
---

# New Session Handoff

## Purpose

Prepare a fresh coding-agent session to continue work without relying on prior chat history, hidden reasoning, tool output, or compacted context.

This skill does not run interactive session commands such as Codex `/new`, and it does not control an agent CLI. It creates the handoff artifact and machine-readable markers that a user or external PTY orchestrator can use before starting a new session.

## Workflow

1. Inspect the current state before summarizing:
   - `pwd`
   - `git rev-parse --show-toplevel` if inside a Git repository
   - `git branch --show-current`
   - `git status --short`
   - `git diff --stat`
   - relevant instruction files: `AGENTS.md`, `AGENTS.override.md`, `PLANS.md`, `PLAN.md`, `HANDOFF.md`, `CLAUDE.md`, `GEMINI.md`

2. Do not modify application code while preparing the handoff.
   - Read files as needed.
   - If the user asked to save the handoff, write or update only `HANDOFF.md` unless they explicitly requested another path.
   - If the user only asked for a prompt, return the prompt and Markdown draft without writing files.

3. Summarize only verified facts.
   - Do not invent file paths, commands, test results, branch names, or decisions.
   - Mark unknowns as `확인 필요` or `Unknown`.
   - Prefer exact paths and exact commands.
   - Keep log snippets short and include only lines needed to identify the result or failure.

4. Produce two artifacts:
   - `NEW_SESSION_PROMPT`: a copy-paste prompt for a fresh agent session.
   - `HANDOFF.md`: a self-contained Markdown handoff.

5. Make the handoff self-contained.
   - The next session must be able to continue from the repository state and the handoff alone.
   - If the handoff conflicts with the actual working tree, instruct the next session to trust the working tree.
   - Include the smallest safe first step, not only a broad to-do list.

6. End with markers for automation:

   ```text
   HANDOFF_READY: <absolute path or not-written>
   NEW_SESSION_PROMPT_READY: yes
   VALIDATION_RECORDED: yes|no
   SAFE_FOR_NEW_SESSION: yes|no
   ```

   Use `SAFE_FOR_NEW_SESSION: yes` only when no command is still running, the handoff is complete, and the current work can be resumed from the artifacts.

## HANDOFF.md Template

Use this structure:

```md
# Handoff

## Goal

- Original goal:
- Expected final result:
- User-emphasized requirements:

## Updated Requirements

- Changed requirements:
- Requirements no longer applicable:
- Ambiguous or unverified conditions:

## Current Repository State

- Working directory:
- Git root:
- Branch:
- Git status:
- Instruction files found:
- Files to inspect first:

## Work Completed So Far

- Completed work:
- Files changed:
- Files inspected without changes:
- Files created/deleted/moved:

## Decisions and Rationale

- Decision:
  Rationale:
  Alternatives considered:

## Known Pitfalls

- Failed or abandoned approaches:
- Do not repeat:
- Confusing files/functions/tests/edge cases:
- Commands requiring explicit user approval:

## Remaining Work

1. Smallest next step:
2. Next implementation step:
3. Validation/cleanup:
4. Optional later work:

## Validation

- Last commands run:
- Results:
- Failures or skipped checks:
- Commands to run next:
- Observable completion criteria:

## Constraints

- Architecture/style/security/compatibility:
- No new dependency, public API change, DB/schema change, destructive command, force push, or large deletion without user approval.

## Done When

- Required tests/checks:
- Required behavior:
- Final summary expected:
```

## NEW_SESSION_PROMPT Template

Return a fenced `text` block with this shape:

```text
This task continues from a previous coding-agent session.

Assume this session has no access to prior chat history, hidden reasoning, compacted context, or tool output. Use only this prompt, the repository, and any handoff files present.

First, do not implement. Establish context in this order:

1. Confirm the working directory and Git root.
2. Read applicable instruction files such as AGENTS.md, AGENTS.override.md, PLANS.md, PLAN.md, HANDOFF.md, CLAUDE.md, and GEMINI.md.
3. Run git status --short.
4. Inspect the files listed under "Files to inspect first".
5. Compare the handoff with the actual working tree.
6. If the handoff conflicts with files on disk, prefer the files on disk and report the mismatch.
7. If the state is consistent, continue from the smallest remaining task.

Rules:
- Keep changes minimal and aligned with nearby code.
- Do not start a broad refactor.
- Do not add dependencies, change public APIs, change DB/schema, run destructive commands, force push, or delete large areas without user approval.
- Run the narrowest relevant validation after changes.
- If validation fails, summarize the command, the key failure lines, and the likely cause.

# Handoff

[Paste the self-contained handoff here or instruct the session to read HANDOFF.md at an exact path.]

# First response expected

Report:
1. Loaded instructions:
2. Repo state:
3. Handoff consistency:
4. First implementation step:

Then proceed with the first remaining task.
```

## Automation Boundary

External agents such as Hermes or OpenClaw may use the final markers to decide when to send a session-reset command to an agent CLI PTY. This skill itself must not claim to execute `/new` or any other interactive reset command; it only prepares safe continuation artifacts.

## Quality Bar

- Focused: only solve session handoff, not general planning or CI repair.
- Progressive disclosure: keep the skill short; put platform-specific PTY automation outside the skill.
- Deterministic where possible: use exact commands and exact markers.
- Self-contained: the next worker should not need the previous conversation.
