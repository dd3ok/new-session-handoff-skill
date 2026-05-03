# Agent Session Continuity

Portable session-continuity assets for long coding-agent tasks.

This repository is source material for humans and other repositories. It does not install anything on the current machine by itself.

## Contents

- `skills/new-session-handoff/`: a portable `SKILL.md` for creating self-contained handoff artifacts.
- `.agents/skills/new-session-handoff`: Codex-compatible project-skill entrypoint, symlinked to `skills/new-session-handoff/`.
- `.claude/skills/new-session-handoff`: Claude-compatible project-skill entrypoint, symlinked to `skills/new-session-handoff/`.
- `orchestrators/session-rotation.md`: guidance for PTY controllers such as Hermes or OpenClaw.
- `examples/`: minimal `HANDOFF.md` and resume prompt examples.

## Intended Use

Copy or vendor `skills/new-session-handoff/` into the skill location used by your agent environment, or keep this repository's project-skill entrypoints when vendoring the repository.

Common locations include:

- Codex personal skills: `$HOME/.agents/skills/new-session-handoff/`
- Codex repo skills: `<repo>/.agents/skills/new-session-handoff/`
- Claude personal skills: `$HOME/.claude/skills/new-session-handoff/`
- Claude project skills: `<repo>/.claude/skills/new-session-handoff/`

For Claude, Gemini, or other agents, keep the same core workflow and adjust only the agent-specific installation path and session-control commands.

## Boundary

The skill prepares:

- `HANDOFF.md`
- `NEW_SESSION_PROMPT`
- readiness markers such as `SAFE_FOR_NEW_SESSION`

The skill does not execute interactive reset commands. Hermes, OpenClaw, or another PTY controller should own status checks, context thresholds, and session rotation.
