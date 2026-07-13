# Contributing

This cleanup branch is focused on publication hardening and reproducibility.

- Prefer small, traceable changes.
- Preserve reported publication artifacts unless clearly marked as regenerated.
- Keep canonical workflow code separate from archived exploratory material.
- Run `python3 -m compileall src scripts tests` and `pytest -q` before proposing changes when dependencies are available.

