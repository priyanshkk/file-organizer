# File Organizer

[![CI](https://github.com/priyanshkk/file-organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/priyanshkk/file-organizer/actions/workflows/tests.yml)
[![Linter](https://github.com/priyanshkk/file-organizer/actions/workflows/linter.yml/badge.svg)](https://github.com/priyanshkk/file-organizer/actions/workflows/linter.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Typing: mypy](https://img.shields.io/badge/typing-mypy-2f6fab.svg)](https://mypy.readthedocs.io/)
[![Tests: unittest](https://img.shields.io/badge/tests-unittest-green.svg)](https://docs.python.org/3/library/unittest.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sort a messy folder into category directories and undo the whole run with one command.

## Overview / why

Manual sorting is repetitive and risky: it is easy to overwrite a file with the
same name or forget where something came from. This CLI plans every move first,
de-duplicates colliding names, writes a JSON journal, and can replay that
journal in reverse. Planning and applying are separate functions, so
`--dry-run` shows the exact plan without touching a single file.

## Tech stack

| Area | Choice | Why |
| --- | --- | --- |
| Language | Python 3.10–3.13 | Modern type syntax, stdlib only. |
| Filesystem | `pathlib`, `shutil` | Cross-platform paths and moves. |
| Journal | `json` | Human-readable, reversible record of every run. |
| Packaging | Hatchling, `src/` layout | Standard PEP 621 metadata and console script. |
| Tests / checks | unittest, Ruff, mypy (strict) | Offline suite plus static guarantees. |

## Real demo output

A scratch folder with `photo.png`, `notes.txt`, `track.mp3` and `mystery.xyz`:

```console
$ python -m file_organizer .demo-scratch --dry-run
[dry-run] mystery.xyz -> Others/mystery.xyz
[dry-run] notes.txt -> Documents/notes.txt
[dry-run] photo.png -> Images/photo.png
[dry-run] track.mp3 -> Music/track.mp3
```

```console
$ python -m file_organizer .demo-scratch
Moved 4 file(s). Undo with: python organizer.py "C:\Users\Priyanshu kk\Documents\PythonPortfolio\file-organizer\.demo-scratch" --undo

$ python -m file_organizer .demo-scratch --undo
Restored 4 file(s).
```

After applying, the folder contains `Documents/`, `Images/`, `Music/`, `Others/`
and `.organizer-log.json`; after undo, the files are back at the root and the
journal is gone. The empty category folders remain.

## Install & setup

```bash
git clone https://github.com/priyanshkk/file-organizer.git
cd file-organizer
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

Windows users can also run `powershell -File scripts\setup.ps1`; POSIX users can
run `bash scripts/setup.sh`. Runtime dependencies are stdlib only, so
`pip install -r requirements.txt` simply installs the package itself.

## Usage

```bash
python -m file_organizer Downloads --dry-run    # preview
python -m file_organizer Downloads              # organize
python -m file_organizer Downloads --recursive  # include subfolders
python -m file_organizer Downloads --undo       # restore the last run
python -m file_organizer Downloads --log ./my-log.json
python organizer.py Downloads                  # backward-compatible launcher
file-organizer Downloads --dry-run             # installed console script
```

Categories: `Images`, `Documents`, `Videos`, `Music`, `Archives`, `Code`,
`Executables`, `Others`. Hidden files and files already inside a category folder
are skipped. Full API examples are in [docs/usage.md](docs/usage.md).

## Project structure

```text
file-organizer/
├── .github/
│   ├── ISSUE_TEMPLATE/{bug_report,feature_request}.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/{tests,linter}.yml
├── docs/{index,architecture,usage}.md
├── scripts/{setup.ps1,setup.sh}
├── src/file_organizer/
│   ├── __init__.py
│   ├── __main__.py          # CLI parser and messages
│   ├── config.py            # categories + env-backed defaults
│   └── core/
│       ├── __init__.py
│       └── organizer.py     # plan, apply, undo
├── tests/{__init__,test_core,test_main}.py
├── .env.example
├── .pre-commit-config.yaml
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── organizer.py             # compatibility shim
├── LICENSE
└── README.md
```

## Environment configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `ORGANIZER_LOG_NAME` | `.organizer-log.json` | Journal filename created in the target folder. |
| `ORGANIZER_RECURSIVE` | `0` | `1` includes subfolders by default; `0` does not. |

`--recursive` / `--no-recursive` override the second variable per invocation.
Invalid values fall back to the defaults. See
[docs/architecture.md](docs/architecture.md) for details.

## Testing & quality

```bash
python -m unittest discover -s tests -v
python -m ruff check .
python -m mypy src/file_organizer
python -m build
```

The suite runs on Python 3.10, 3.11, 3.12 and 3.13 in GitHub Actions.

## Roadmap

- [ ] Custom category maps via a JSON config file.
- [ ] Size-based categories (for example `Large Files`).
- [ ] Date-based subfolders inside each category.
- [ ] `--undo-all` to replay multiple journals.

## License

MIT — see [LICENSE](LICENSE).
