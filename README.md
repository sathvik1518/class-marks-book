# Class Marks Book

A menu program that keeps many students in memory: add, list (sorted ignoring capitals), search by part of a name, top mark, average, remove, quit. Rules are small functions; the menu only asks and shows.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python class_marks_book.py
python -m pytest -q          # 54 tests
python break_it.py           # 29 deliberate mistakes
```

Read `NOT_COVERED.md` for what the tests do not cover.

See `DOCUMENTATION.md` for the full write-up.
