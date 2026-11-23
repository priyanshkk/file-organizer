# Usage

Install the dev extras first (`pip install -r requirements-dev.txt`), or set
`PYTHONPATH=src` when running from a checkout.

## CLI reference

```text
usage: file-organizer [-h] [--dry-run] [--recursive] [--no-recursive] [--undo]
                      [--log LOG]
                      folder

Organize files into category folders.

positional arguments:
  folder          folder to organize

options:
  -h, --help      show this help message and exit
  --dry-run       show the plan, move nothing
  --recursive     include subfolders (default: 0)
  --no-recursive  only organize the top level, overriding ORGANIZER_RECURSIVE
  --undo          restore the last run
  --log LOG       custom log path (default: <folder>/.organizer-log.json)
```

## Preview a plan

```bash
python -m file_organizer Downloads --dry-run
```

Real output for a folder containing `photo.png`, `notes.txt`, `track.mp3` and
`mystery.xyz`:

```text
[dry-run] mystery.xyz -> Others/mystery.xyz
[dry-run] notes.txt -> Documents/notes.txt
[dry-run] photo.png -> Images/photo.png
[dry-run] track.mp3 -> Music/track.mp3
```

Nothing is moved and no journal is written.

## Organize and undo

```bash
python -m file_organizer Downloads
python -m file_organizer Downloads --undo
```

Real output from the same folder:

```text
Moved 4 file(s). Undo with: python organizer.py "C:\Users\Priyanshu kk\Documents\PythonPortfolio\file-organizer\.demo-scratch" --undo
```

After the move, the folder contains `Documents/`, `Images/`, `Music/`, `Others/`
and `.organizer-log.json`. Undo prints:

```text
Restored 4 file(s).
```

The four files return to the folder root; the empty category folders remain and
the journal is removed. Running `--undo` again prints
`Nothing to undo: no log file found.` on stderr and returns 0.

## Other commands

```bash
python -m file_organizer Downloads --recursive     # include subfolders
python -m file_organizer Downloads --no-recursive  # force top level only
python -m file_organizer Downloads --log ./my-log.json
python organizer.py Downloads                     # backward-compatible launcher
file-organizer Downloads --dry-run                # installed console script
python -m file_organizer --help
```

An invalid folder prints `error: Not a directory: <path>` to stderr and exits 1.

## Environment configuration

| Variable | Default | Effect |
| --- | --- | --- |
| `ORGANIZER_LOG_NAME` | `.organizer-log.json` | Journal filename inside the target folder. |
| `ORGANIZER_RECURSIVE` | `0` | `1` includes subfolders by default; `0` does not. |

PowerShell:

```powershell
$env:ORGANIZER_LOG_NAME = "my-log.json"
$env:ORGANIZER_RECURSIVE = "1"
python -m file_organizer Downloads --dry-run
Remove-Item Env:ORGANIZER_LOG_NAME, Env:ORGANIZER_RECURSIVE
```

POSIX shells:

```bash
ORGANIZER_LOG_NAME=my-log.json ORGANIZER_RECURSIVE=1 \
  python -m file_organizer Downloads --dry-run
```

`--no-recursive` overrides `ORGANIZER_RECURSIVE=1`; blank log names and values
other than `0`/`1` are ignored.

## Public API

```python
from pathlib import Path

from file_organizer.core.organizer import apply_moves, plan_moves

root = Path("Downloads")
moves = plan_moves(root, recursive=False)
print(f"{len(moves)} file(s) planned")
# Preview: apply_moves(moves, root / ".organizer-log.json", dry_run=True)
# Apply:   apply_moves(moves, root / ".organizer-log.json")
```

`category_for(path)` returns the category name for a single path, and
`undo(log_path)` restores a previous run.

## Testing and linting

```bash
python -m unittest discover -s tests -v
python -m ruff check .
python -m mypy src/file_organizer
```
