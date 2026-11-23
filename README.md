# File Organizer

A small CLI that sorts a messy folder into category directories (`Images`,
`Documents`, `Videos`, `Music`, `Archives`, `Code`, `Executables`, `Others`).
Every run writes a JSON log, so any move can be reversed with a single command.

## Usage

```bash
# Preview only - nothing is moved
python organizer.py Downloads --dry-run

# Actually organize
python organizer.py Downloads

# Include files inside subfolders
python organizer.py Downloads --recursive

# Undo the last run
python organizer.py Downloads --undo
```

## Design notes

- `plan_moves()` is pure with respect to the filesystem: it only inspects and
  returns `(source, destination)` pairs. This is what powers `--dry-run`.
- Destination names are de-duplicated within a run, so two files called
  `report.pdf` become `report.pdf` and `report_1.pdf` instead of one overwriting
  the other.
- Files already living in a category folder are left alone, which makes the
  command safe to re-run.
- Undo replays the log in reverse and then deletes the log.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## License

MIT
