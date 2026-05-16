# Baseline Matrix

Compare agent behavior with and without this skill.

## Metrics

- Correct artifact path
- No application code edits during create mode
- Disk/Git state recorded
- Changed files listed
- Embedded Resume Prompt present
- Secret hygiene observed
- Marker block present and honest
- `SAFE_FOR_NEW_SESSION` correctness
- Cleanup policy correctness
- Token/time overhead

## Cases

1. Small dirty repo, compact handoff.
2. Large multi-file change, expanded handoff.
3. Unsafe handoff with blocker.
4. Resume with matching disk state.
5. Resume with stale HEAD.
6. Resume inspect-only.
7. Secret-like token in changed file.
