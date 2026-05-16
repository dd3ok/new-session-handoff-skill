# New Session Handoff

A lightweight Agent Skill for creating a verified `HANDOFF.md` so coding work can continue in a fresh agent session without relying on prior chat history.

`new-session-handoff` does not run `/new`, control PTYs, rotate sessions, or edit application code while creating a handoff. It only writes a recoverable handoff artifact and a machine-readable readiness marker.

Default artifact:

```text
.new-session-handoff/HANDOFF.md
```

The default handoff embeds a `## Resume Prompt` section. `NEW_SESSION_PROMPT.txt` is not created unless the user explicitly asks for a separate prompt file or an external orchestrator requires one.

Handoff artifacts are treated as single-use bootstrap files. After a successful resume, the agent may delete only adopted, generated, untracked handoff artifacts. It must not delete artifacts for inspect-only requests, unsafe or stale handoffs, tracked files, user-authored files, or handoffs outside the default generated handoff directory unless explicitly instructed.

## 한국어 사용 예

```text
핸드오프 만들어줘
```

현재 디스크/Git 상태를 확인한 뒤 `.new-session-handoff/HANDOFF.md`를 생성하거나 갱신합니다. handoff 생성 중에는 `/new`를 실행하지 않고, PTY를 제어하지 않으며, application code를 수정하지 않습니다.

```text
핸드오프 읽고 이어서 해줘
```

`HANDOFF.md`를 읽고 현재 디스크/Git 상태와 비교한 뒤, 불일치가 있으면 먼저 보고합니다. `SAFE_FOR_NEW_SESSION: yes`이고 사용자가 구현 계속을 요청한 경우에만 가장 작은 다음 작업으로 이어갑니다.

## Canonical Contract

Runtime behavior is concentrated in the distributed skill:

- Skill router: `skills/new-session-handoff/SKILL.md`
- Artifact contract: `skills/new-session-handoff/references/handoff-contract.md`
- Handoff skeleton: `skills/new-session-handoff/references/handoff-template.md`
- Marker schema: `skills/new-session-handoff/schemas/handoff-automation-v1.schema.json`
- Portable validator: `skills/new-session-handoff/scripts/validate_handoff.py`

README is a map. The contract files above are the source of truth for marker semantics, `SAFE_FOR_NEW_SESSION`, trust order, expanded artifacts, cleanup, and resume behavior.

The OpenAI agent descriptor intentionally does not set an invocation policy field. Routing is constrained by the `SKILL.md` description and should be used only for explicit handoff requests or clear natural-language equivalents.

## Repository Layout

```text
.
├── README.md
├── SECURITY.md
├── CHANGELOG.md
├── AGENTS.md
├── skills/
│   └── new-session-handoff/
│       ├── SKILL.md
│       ├── LICENSE.txt
│       ├── agents/openai.yaml
│       ├── references/
│       │   ├── handoff-contract.md
│       │   └── handoff-template.md
│       ├── schemas/handoff-automation-v1.schema.json
│       └── scripts/
│           ├── handoff_contract.py
│           └── validate_handoff.py
├── examples/
├── evals/
├── orchestrators/
└── scripts/
```

`skills/new-session-handoff/` is the portable skill package. The root-level `examples/`, `evals`, `orchestrators/`, and `scripts/validate-repo.py` are maintainer assets. The root `scripts/validate_handoff.py` is a compatibility wrapper around the portable validator.

## Installation / Vendoring

Copy, vendor, or symlink the canonical skill into the location used by your agent environment.

Common locations:

- Codex personal skills: `$HOME/.agents/skills/new-session-handoff/`
- Codex repo skills: `<repo>/.agents/skills/new-session-handoff/`
- Claude personal skills: `$HOME/.claude/skills/new-session-handoff/`
- Claude project skills: `<repo>/.claude/skills/new-session-handoff/`

Example project symlinks:

```bash
mkdir -p .agents/skills .claude/skills
ln -s ../../skills/new-session-handoff .agents/skills/new-session-handoff
ln -s ../../skills/new-session-handoff .claude/skills/new-session-handoff
```

### Copy Install

Codex repo skill:

```bash
mkdir -p .agents/skills
cp -R skills/new-session-handoff .agents/skills/new-session-handoff
```

Claude project skill:

```bash
mkdir -p .claude/skills
cp -R skills/new-session-handoff .claude/skills/new-session-handoff
```

User-level install:

```bash
mkdir -p "$HOME/.agents/skills" "$HOME/.claude/skills"
cp -R skills/new-session-handoff "$HOME/.agents/skills/new-session-handoff"
cp -R skills/new-session-handoff "$HOME/.claude/skills/new-session-handoff"
```

## Examples

- `examples/compact-bugfix/`: compact handoff for a small bug fix.
- `examples/expanded-architecture/`: expanded handoff with focused detail artifacts.
- `examples/unsafe-handoff/`: intentionally unsafe handoff showing why `SAFE_FOR_NEW_SESSION: no` matters.
- `examples/resume-prompt.example.txt`: optional external prompt text for orchestrators that cannot read the embedded prompt.

Examples are maintainer/demo material. They are not required in the distributed skill package.

## Evals

`evals/` contains lightweight manual scenarios for maintaining the skill contract. Use them when changing `SKILL.md`, templates, marker semantics, examples, validators, or orchestrator guidance.

Core expectations:

- create mode does not modify application code.
- generated artifacts contain verified facts or explicit unknowns.
- default create mode writes `.new-session-handoff/HANDOFF.md`.
- default create mode embeds a resume prompt instead of writing `NEW_SESSION_PROMPT.txt`.
- resume mode verifies disk state before coding.
- expanded mode uses focused detail artifacts instead of context dumps.
- unsafe states do not emit `SAFE_FOR_NEW_SESSION: yes`.
- secrets are redacted or omitted.
- verified safe adopted resume may delete only untracked generated handoff artifacts.

## Validation

Before committing changes, run:

```bash
python3 scripts/check-frontmatter.py
python3 scripts/check-marker-block.py
python3 scripts/check-marker-semantics.py
python3 scripts/validate-examples.py
python3 scripts/validate-repo.py
```

To validate generated handoff artifacts directly:

```bash
python3 scripts/validate_handoff.py .new-session-handoff/HANDOFF.md
```

The root validator command delegates to the portable validator inside `skills/new-session-handoff/scripts/`.

## Orchestrators

External PTY controllers can read the final marker block and decide whether to rotate a session. See `orchestrators/session-rotation.md`.

This skill prepares and consumes handoff artifacts only. Session reset commands, context-threshold policy, PTY input, and agent CLI orchestration stay outside the skill.

## Versioning

The current handoff schema is:

```text
HANDOFF_SCHEMA_VERSION: 1
```

Breaking changes to marker names, required sections, marker meanings, or detail path resolution should increment the schema version and update examples, evals, README, validators, and orchestrator guidance together.
