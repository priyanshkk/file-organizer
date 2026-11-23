# File Organizer documentation

A standard-library CLI that sorts files into category folders and can undo its
own runs from a JSON journal.

- [Architecture](architecture.md) — modules, data flow and design decisions.
- [Usage](usage.md) — every command, environment variable and public API with
  real output.

Quick start:

```bash
pip install -r requirements-dev.txt
python -m file_organizer Downloads --dry-run
```
