# Automation Marker Semantics

The canonical marker contract now lives in `references/handoff-contract.md`.

Use that file for field meanings, `SAFE_FOR_NEW_SESSION` implications, and the exact marker block:

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

The machine-readable value schema is `schemas/handoff-automation-v1.schema.json`.
