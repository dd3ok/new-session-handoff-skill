# Handoff Quality Checklist

The canonical `SAFE_FOR_NEW_SESSION` checklist now lives in `references/handoff-contract.md`.

Use that file before setting `SAFE_FOR_NEW_SESSION: yes`. The exact marker block remains:

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
