# Architecture

## Modules

| Module | Responsibility |
| --- | --- |
| `src/file_organizer/config.py` | Category table, `ORGANIZER_LOG_NAME` and `ORGANIZER_RECURSIVE`. |
| `src/file_organizer/core/organizer.py` | Pure planning, filesystem moves, JSON journal and undo. |
| `src/file_organizer/__main__.py` | CLI parser, path resolution and user-facing messages. |
| `src/file_organizer/__init__.py` | Public API re-exports and version. |
| `organizer.py` | Thin compatibility shim for the original script name. |

## Data flow

```text
python -m file_organizer Downloads [--dry-run] [--undo]
        |
        v
__main__.main() -- resolve root + log path
        |
        +-- --undo: undo(log) --> replay journal in reverse --> unlink journal
        |
        +-- plan_moves(root, recursive)
        |       `-- scan files, skip hidden/already-organized,
        |           de-duplicate destinations --> [(source, destination), ...]
        |
        `-- apply_moves(pairs, log)
                `-- mkdir + shutil.move, append records to JSON journal
                    (or print [dry-run] lines and change nothing)
```

## Design decisions

1. **Planning is separate from applying.** `plan_moves()` only reads the
   filesystem. `--dry-run` prints exactly the pairs that a real run would use.
2. **Duplicate-safe destinations.** `_unique()` tracks reserved paths for the
   whole run, so two `report.pdf` files become `report.pdf` and `report_1.pdf`;
   existing files are never overwritten.
3. **Idempotent re-runs.** Files whose relative path already contains a
   category folder are skipped, so organizing twice is a no-op.
4. **Hidden files are ignored.** Any filename starting with `.` is left alone,
   including the journal itself and `.env` files.
5. **Reverse-order undo.** The journal records each move; undo replays it in
   reverse, restoring files to their original parent directories, then deletes
   the journal. Empty category folders are left in place.
6. **Environment defaults with CLI override.** `ORGANIZER_RECURSIVE` sets the
   default for planning; `--recursive` / `--no-recursive` override it per call.
   `ORGANIZER_LOG_NAME` changes the journal filename. Blank names and values
   other than `0`/`1` fall back to the defaults.
7. **Errors are exit codes.** Invalid folders and unreadable journals print to
   stderr and return exit code 1; success returns 0.

## Testing strategy

`tests/test_core.py` keeps the original logic tests and adds invalid-folder,
custom-category and dry-run coverage. `tests/test_main.py` exercises the CLI,
including both environment variables. Each test module bootstraps `src/` into
`sys.path`, so discovery works from the repository root without an install.
