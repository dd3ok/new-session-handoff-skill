# Repository Instructions

This repository contains session-continuity assets for coding agents such as Codex, Claude, Gemini, and external PTY orchestrators.

## Structure

- `skills/new-session-handoff/`: portable skill that creates handoff artifacts.
- `orchestrators/`: External PTY-controller guidance for Hermes/OpenClaw style agents.
- `examples/`: Minimal examples and prompt templates.

## Rules

- Keep the skill focused on handoff artifact generation.
- Keep `/status`, `/new`, PTY control, and context-threshold policy outside the skill.
- Do not claim a skill can execute interactive slash commands.
- Use exact command names, exact markers, and conservative safety checks.
- Prefer concise files over broad documentation.
