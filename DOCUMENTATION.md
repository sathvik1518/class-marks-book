# Class Marks Book: A Menu Program With Small Functions and Safe Rules

**Day 2 Mini Capstone, Class Marks Book (Problem Solving)**  
**Project folder:** `class-marks-book`

---

## 1. Goal

A teacher wants a menu program for one class that keeps many students in memory. Each student has a name and marks.

From the task:
- Menu: add a student, list students, search by part of a name, show the top mark, show the average, remove a student, quit.
- Marks are a whole number from 0 to 100. A name cannot be empty.
- The same name cannot be added twice. `Anu` and `anu` count as the same name.
- The list is shown sorted by name, ignoring capital letters.
- Rules live in **small functions**. Print only in one or two places.
- The average of an empty class must not crash.
- A test file must be able to import the functions (so the program uses `if __name__ == "__main__"`).

I did this from the course screenshot. The Aspect 18 exercises are yours; I did not solve them.

Think of a class register. The **rules** are the clerk's checks (is the name there, is it a duplicate, is the mark 0 to 100). The **menu** is the front desk that only asks questions and reads the answer aloud. The clerk never talks to the visitor and the front desk never checks rules.

---

## 2. Tools

| Tool | Role |
|---|---|
| Python 3.10+ (tested on 3.13) | The program. Standard library only. |
| pytest 9.1.1 | Tests |
| mypy 2.4.1 | Type check (clean: no errors) |

---

## 3. Project structure

```
class-marks-book/
├── class_marks_book.py            (rules + menu)
├── tests/test_class_marks_book.py (54 tests)
├── break_it.py                    (29 deliberate mistakes)
├── NOT_COVERED.md  pytest.ini  requirements-dev.txt  .gitignore  README.md  DOCUMENTATION.md
```

---

## 4. Setup commands

```bash
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

**Commands**

```bash
python class_marks_book.py     # run the menu
python -m pytest -q            # 54 tests
python -m mypy class_marks_book.py
python break_it.py             # 29 deliberate mistakes
```

---

## 5. How it works

| Piece | Job |
|---|---|
| `clean_name`, `parse_marks` | check one value, return it clean or raise `BookError` |
| `name_key` | the "same student" test: capitals and extra spaces do not count (`casefold`) |
| `add_student`, `remove_student`, `find_students` | the book's rules; each raises `BookError` with a friendly message |
| `sorted_students` | by name ignoring capitals; does **not** change the book |
| `top_mark`, `average_mark` | return `None` for an empty class, so nothing divides by zero |
| `run(ask, say)` | the menu. `ask` types, `say` shows. It catches `BookError` once and prints it |
| `main()` | the only place that connects `input` and `print` |

**Answers to the "Check yourself" list**

| Situation | What happens |
|---|---|
| empty class: list | `The book is empty.` |
| empty class: top mark / average | a clear sentence, no crash |
| duplicate name | `Error: A student called anu is already in the book.` and nothing is stored |
| `anu` versus `Anu` | the same student |
| marks `0`, `100` | accepted |
| marks `101` | `Error: Marks must be a whole number from 0 to 100.` |
| ending the input (Ctrl+D, or Ctrl+Z then Enter) | `Input ended. Goodbye.` (the task allowed a traceback here; I fixed it anyway) |

**Decisions I made where the task is silent**
- **Top mark with a tie** shows every student who has it: `Top mark: 90 (Amy, zed)`.
- **Empty search text** is an error (`Type some letters of the name to search for.`), not "show everybody".
- **Remove** finds the student by name, ignoring capitals.
- **Name checked before marks** when both are bad.

---

## 6. The code

### `class_marks_book.py`

```python
"""Class Marks Book: a menu program that keeps many students (name and marks) in memory.

Run it:   python class_marks_book.py

Every rule lives in a small function that returns a value or raises BookError. The menu (run) only asks and shows.
All typing goes through ask() and all showing through say(), so nothing else prints.
"""
from __future__ import annotations

import sys
from typing import Callable, TypedDict


class Student(TypedDict):
    name: str
    marks: int


class BookError(Exception):
    """Something the person typed cannot be used. The message is written for them to read."""


# ---------------------------------------------------------------- rules (no typing, no printing)
def clean_name(text: str) -> str:
    name = " ".join(text.split())
    if not name:
        raise BookError("The name cannot be empty.")
    return name


def name_key(name: str) -> str:
    """Two names are the same student when their keys are equal: capitals and extra spaces do not count."""
    return " ".join(name.split()).casefold()


def parse_marks(text: str) -> int:
    cleaned = text.strip()
    if not (cleaned.isascii() and cleaned.isdigit()) or int(cleaned) > 100:
        raise BookError("Marks must be a whole number from 0 to 100.")
    return int(cleaned)


def add_student(book: list[Student], name_text: str, marks_text: str) -> Student:
    name = clean_name(name_text)
    marks = parse_marks(marks_text)
    if any(name_key(s["name"]) == name_key(name) for s in book):
        raise BookError(f"A student called {name} is already in the book.")
    student: Student = {"name": name, "marks": marks}
    book.append(student)
    return student


def sorted_students(book: list[Student]) -> list[Student]:
    """By name, ignoring capitals. The book itself is not changed."""
    return sorted(book, key=lambda s: (name_key(s["name"]), s["name"]))


def find_students(book: list[Student], text: str) -> list[Student]:
    needle = name_key(text)
    if not needle:
        raise BookError("Type some letters of the name to search for.")
    return [s for s in sorted_students(book) if needle in name_key(s["name"])]


def remove_student(book: list[Student], name_text: str) -> Student:
    key = name_key(clean_name(name_text))
    for student in book:
        if name_key(student["name"]) == key:
            book.remove(student)
            return student
    raise BookError(f"No student called {clean_name(name_text)} in the book.")


def top_mark(book: list[Student]) -> tuple[int, list[str]] | None:
    """The highest mark and everybody who has it. An empty book has no top mark: None."""
    if not book:
        return None
    best = max(s["marks"] for s in book)
    return best, [s["name"] for s in sorted_students(book) if s["marks"] == best]


def average_mark(book: list[Student]) -> float | None:
    """None for an empty book, so there is never a division by zero."""
    if not book:
        return None
    return sum(s["marks"] for s in book) / len(book)


# ---------------------------------------------------------------- how things look
def describe(student: Student) -> str:
    return f"{student['name']} - {student['marks']}"


MENU = """
Class Marks Book
  1. Add a student
  2. List students
  3. Search by part of a name
  4. Show the top mark
  5. Show the average
  6. Remove a student
  7. Quit"""


# ---------------------------------------------------------------- the menu
def run(ask: Callable[[str], str], say: Callable[[str], None], book: list[Student] | None = None) -> None:
    book = [] if book is None else book
    try:
        while True:
            say(MENU)
            choice = ask("Choose 1-7: ").strip()
            try:
                if choice == "1":
                    student = add_student(book, ask("Name: "), ask("Marks (0-100): "))
                    say(f"Added {describe(student)}.")
                elif choice == "2":
                    say("\n".join(describe(s) for s in sorted_students(book)) or "The book is empty.")
                elif choice == "3":
                    found = find_students(book, ask("Search for: "))
                    say("\n".join(describe(s) for s in found) or "No student matches.")
                elif choice == "4":
                    top = top_mark(book)
                    say("The book is empty, so there is no top mark." if top is None else f"Top mark: {top[0]} ({', '.join(top[1])})")
                elif choice == "5":
                    average = average_mark(book)
                    say("The book is empty, so there is no average." if average is None else f"Average: {average:.1f}")
                elif choice == "6":
                    say(f"Removed {describe(remove_student(book, ask('Name to remove: ')))}.")
                elif choice == "7":
                    say("Goodbye.")
                    return
                else:
                    say("Please type a number from 1 to 7.")
            except BookError as problem:
                say(f"Error: {problem}")
    except EOFError:  # the input ended (Ctrl+D, or Ctrl+Z then Enter on Windows)
        say("\nInput ended. Goodbye.")


def main() -> int:
    run(input, print)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `pytest.ini`

```ini
[pytest]
pythonpath = .
testpaths = tests
```

### `requirements-dev.txt`

```text
pytest==9.1.1
mypy==2.4.1
```

### `break_it.py`

```python
"""Break the code on purpose, one rule at a time, and check that the tests notice.

Run from the project folder:   python break_it.py            (all cases)
                          or   python break_it.py word ...   (only cases whose name contains a word)

Each case edits one file, runs the tests, expects them to FAIL, then puts the file back.
A test run that hangs or runs out of time also counts as caught.
"""
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).parent
LIMIT = 90  # seconds for one test run
CMD = [sys.executable, "-B", "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider"]

# (name, file, old text that appears exactly once, new text)
CASES = [
    ('marks: 101 allowed', 'class_marks_book.py', 'or int(cleaned) > 100:', 'or int(cleaned) > 101:'),
    ('marks: 100 refused', 'class_marks_book.py', 'or int(cleaned) > 100:', 'or int(cleaned) >= 100:'),
    ('marks: plain int accepts underscores and signs', 'class_marks_book.py', 'if not (cleaned.isascii() and cleaned.isdigit()) or int(cleaned) > 100:', "if not cleaned.lstrip('+-').replace('_', '').isdigit() or int(cleaned) > 100:"),
    ('marks: other-script digits allowed', 'class_marks_book.py', 'cleaned.isascii() and cleaned.isdigit()', 'cleaned.isdigit()'),
    ('name: empty name allowed', 'class_marks_book.py', '    if not name:\n        raise BookError("The name cannot be empty.")', '    if False:\n        raise BookError("The name cannot be empty.")'),
    ('name: capitals make a different student', 'class_marks_book.py', 'return " ".join(name.split()).casefold()', 'return " ".join(name.split())'),
    ('name: extra spaces make a different student', 'class_marks_book.py', 'return " ".join(name.split()).casefold()', 'return name.casefold()'),
    ('add: duplicates allowed', 'class_marks_book.py', 'if any(name_key(s["name"]) == name_key(name) for s in book):', 'if False:'),
    ('add: marks checked before the name', 'class_marks_book.py', '    name = clean_name(name_text)\n    marks = parse_marks(marks_text)', '    marks = parse_marks(marks_text)\n    name = clean_name(name_text)'),
    ('add: a duplicate is refused but stored anyway', 'class_marks_book.py', '    if any(name_key(s["name"]) == name_key(name) for s in book):\n        raise BookError(f"A student called {name} is already in the book.")\n    student: Student = {"name": name, "marks": marks}\n    book.append(student)', '    student: Student = {"name": name, "marks": marks}\n    book.append(student)\n    if any(name_key(s["name"]) == name_key(name) for s in book[:-1]):\n        raise BookError(f"A student called {name} is already in the book.")'),
    ('sort: capitals sort before lower case', 'class_marks_book.py', 'key=lambda s: (name_key(s["name"]), s["name"])', 'key=lambda s: s["name"]'),
    ('sort: the book itself is sorted', 'class_marks_book.py', 'return sorted(book, key=', 'book.sort(key=lambda s: s["name"]); return sorted(book, key='),
    ('search: capitals matter', 'class_marks_book.py', '    needle = name_key(text)\n    if not needle:', '    needle = text.strip()\n    if not needle:'),
    ('search: only the start of a name', 'class_marks_book.py', 'if needle in name_key(s["name"])]', 'if name_key(s["name"]).startswith(needle)]'),
    ('search: empty text finds everyone', 'class_marks_book.py', '    if not needle:\n        raise BookError("Type some letters of the name to search for.")', '    if False:\n        raise BookError("Type some letters of the name to search for.")'),
    ('search: results not sorted', 'class_marks_book.py', 'return [s for s in sorted_students(book) if needle', 'return [s for s in book if needle'),
    ('remove: capitals matter', 'class_marks_book.py', '    key = name_key(clean_name(name_text))\n    for student in book:\n        if name_key(student["name"]) == key:', '    key = clean_name(name_text)\n    for student in book:\n        if student["name"] == key:'),
    ('remove: unknown name is silent', 'class_marks_book.py', '    raise BookError(f"No student called {clean_name(name_text)} in the book.")', '    return {"name": "", "marks": 0}'),
    ('top: empty class crashes', 'class_marks_book.py', '    if not book:\n        return None\n    best', '    best'),
    ('top: ties show only one name', 'class_marks_book.py', '[s["name"] for s in sorted_students(book) if s["marks"] == best]', '[s["name"] for s in sorted_students(book) if s["marks"] == best][:1]'),
    ('top: lowest instead of highest', 'class_marks_book.py', 'best = max(s["marks"] for s in book)', 'best = min(s["marks"] for s in book)'),
    ('average: empty class crashes', 'class_marks_book.py', '    if not book:\n        return None\n    return sum', '    return sum'),
    ('average: wrong divisor', 'class_marks_book.py', '/ len(book)', '/ (len(book) + 1)'),
    ('menu: errors are not caught', 'class_marks_book.py', '            except BookError as problem:\n                say(f"Error: {problem}")', '            except KeyError as problem:\n                say(f"Error: {problem}")'),
    ('menu: input ending shows a traceback', 'class_marks_book.py', '    except EOFError:  # the input ended', '    except KeyError:  # the input ended'),
    ('menu: quit does not quit', 'class_marks_book.py', '                    say("Goodbye.")\n                    return', '                    say("Goodbye.")'),
    ('menu: a bad choice is silent', 'class_marks_book.py', '                    say("Please type a number from 1 to 7.")', '                    pass'),
    ('menu: average has no decimal place', 'class_marks_book.py', 'f"Average: {average:.1f}"', 'f"Average: {average:.0f}"'),
    ('menu: the empty-list message is lost', 'class_marks_book.py', 'or "The book is empty.")', 'or "")'),
]


def tests_fail() -> bool:
    for cache in ROOT.rglob("__pycache__"):  # an old compiled copy of a file we just changed would hide the change
        shutil.rmtree(cache, ignore_errors=True)
    try:
        return subprocess.run(CMD, cwd=ROOT, capture_output=True, text=True, timeout=LIMIT).returncode != 0
    except subprocess.TimeoutExpired:
        return True


def main(words: list[str]) -> None:
    chosen = [c for c in CASES if not words or any(w.lower() in c[0].lower() for w in words)]
    assert not tests_fail(), "the tests must pass before anything is broken"
    survivors = []
    for name, file, old, new in chosen:
        path = ROOT / file
        original = path.read_text(encoding="utf-8")
        if original.count(old) != 1:
            print(f"BAD CASE (text found {original.count(old)} times): {name}")
            survivors.append(name)
            continue
        try:
            path.write_text(original.replace(old, new), encoding="utf-8")
            caught = tests_fail()
        finally:
            path.write_text(original, encoding="utf-8")
        print(("caught   " if caught else "MISSED   ") + name, flush=True)
        if not caught:
            survivors.append(name)
    assert not tests_fail(), "files were not restored"
    print(f"\n{len(chosen) - len(survivors)} of {len(chosen)} mistakes caught")
    if survivors:
        print("NOT caught:", *survivors, sep="\n  - ")
        sys.exit(1)


main(sys.argv[1:])
```

### `NOT_COVERED.md`

```markdown
# What these tests do NOT cover

| Not covered | Why it matters |
|---|---|
| **Windows.** Everything ran on Linux (Python 3.13). | The program uses only `input()` and `print()`; I did not run it on Windows. |
| **A real terminal.** Tests type through a pipe or a fake `ask`. | Arrow keys, paste and slow typing were not tried. |
| **Saving.** The book lives in memory only. | Close the program and every student is gone. That is the next topic (Day 3). |
| **Many students.** | Searching is a loop through the list. Ten thousand students were not tried. |
| **Names with unusual letters.** | `casefold()` handles most, but a name with an accent written in two different ways (one letter vs letter plus accent mark) counts as two different names. |
| **Two students with the same mark and the same name in different capitals** | Refused as a duplicate by design. |
| **Message wording.** | Tests check the key words, not every character. |

**About the break-it script.** `python break_it.py` makes 29 mistakes I thought of. A test run that hangs counts as "caught".
```

### `.gitignore`

```text
.venv/
__pycache__/
.pytest_cache/
.env
*.pyc
```

### Design decisions

| Decision | Reason |
|---|---|
| `run(ask, say)` takes the typing and showing functions | Tests give fake ones, so the whole menu is tested without a keyboard. Printing happens in one place (`main`). |
| Rules raise `BookError`; the menu catches it once | No error text is repeated in many places. |
| `name_key` is the single "same student" rule | Add, remove and search all agree about capitals and spaces. |
| Return `None` for an empty class | The caller must decide what to say, so a division by zero cannot happen. |
| `sorted_students` returns a new list | Listing never reorders the book. |
| Tests use `StopIteration` for "typed too little" | A test that forgets to type `7` fails loudly instead of hanging. |

---

## 7. Tests (54 tests)

| Group | Tests | What it proves |
|---|---|---|
| Marks and names | 25 | edges 0/100/101, bad text, empty name, duplicates in other capitals, refused students not stored |
| Sorting and search | 6 | by name ignoring capitals; book unchanged; part of a name; sorted results; empty search refused |
| Remove | 2 | ignoring capitals; unknown and empty |
| Top mark and average | 4 | empty class, a tie, one student, plain average |
| The menu | 11 | a full walk, empty-class messages, bad choices, errors keep the menu going, search and remove messages |
| The real program | 6 | a real session; the input ending at five different places gives a message, never a traceback |

| # | Test | What it proves |
|---|---|---|
| 1 | `test_ending_the_input_is_not_a_traceback` | input ending at any question prints `Input ended` |
| 2 | `test_search_results_come_back_sorted_whatever_the_order_added` | added in the order Tom, Amy, Kim; found as Amy, Kim, Tom |

### `tests/test_class_marks_book.py`

```python
import os
import subprocess
import sys
from pathlib import Path

import pytest

from class_marks_book import (BookError, add_student, average_mark, clean_name, find_students, name_key, parse_marks, remove_student, run,
                              sorted_students, top_mark)

SCRIPT = Path(__file__).resolve().parent.parent / "class_marks_book.py"


def make(*pairs):
    book = []
    for name, marks in pairs:
        add_student(book, name, str(marks))
    return book


def session(*typed):
    """Run the menu with these typed answers. Returns everything the program showed."""
    answers = iter(typed)
    shown = []

    def ask(prompt):
        return next(answers)  # StopIteration is not EOFError, so a test that types too little fails loudly

    run(ask, shown.append)
    return "\n".join(shown)


# ---------------------------------------------------------------- marks
@pytest.mark.parametrize("text,value", [("0", 0), ("100", 100), (" 55 ", 55)])
def test_good_marks(text, value):
    assert parse_marks(text) == value


@pytest.mark.parametrize("text", ["101", "-1", "abc", "", " ", "4.5", "1_000", "+5", "٣", "1e2"])
def test_bad_marks(text):
    with pytest.raises(BookError, match="whole number from 0 to 100"):
        parse_marks(text)


# ---------------------------------------------------------------- names
def test_name_cleaning_and_key():
    assert clean_name("  Anu   Reddy ") == "Anu Reddy"
    assert name_key("ANU  reddy") == name_key("anu Reddy") == "anu reddy"


@pytest.mark.parametrize("text", ["", "   ", "\t "])
def test_empty_name(text):
    with pytest.raises(BookError, match="cannot be empty"):
        clean_name(text)


def test_add_returns_and_stores_the_student():
    book = []
    student = add_student(book, " Anu ", "80")
    assert student == {"name": "Anu", "marks": 80} and book == [student]


@pytest.mark.parametrize("second", ["anu", "ANU", " Anu ", "aNu"])
def test_same_name_in_other_capitals_is_a_duplicate(second):
    book = make(("Anu", 80))
    with pytest.raises(BookError, match="already in the book"):
        add_student(book, second, "50")
    assert len(book) == 1


def test_refused_students_are_not_stored():
    book = make(("Anu", 80))
    for name, marks in [("", "50"), ("Ravi", "101"), ("Ravi", "x")]:
        with pytest.raises(BookError):
            add_student(book, name, marks)
    assert len(book) == 1


def test_a_bad_name_is_reported_before_a_bad_mark():
    with pytest.raises(BookError, match="name"):
        add_student([], "", "999")


def test_edge_marks_are_stored():
    book = make(("Zero", 0), ("Full", 100))
    assert {s["marks"] for s in book} == {0, 100}


# ---------------------------------------------------------------- sorting, search
def test_sorted_by_name_ignoring_capitals():
    book = make(("charlie", 1), ("Bob", 2), ("alice", 3), ("Dave", 4))
    assert [s["name"] for s in sorted_students(book)] == ["alice", "Bob", "charlie", "Dave"]


def test_sorting_does_not_change_the_book():
    book = make(("b", 1), ("a", 2))
    sorted_students(book)
    assert [s["name"] for s in book] == ["b", "a"]


def test_search_is_part_of_a_name_and_ignores_capitals():
    book = make(("Anu Reddy", 70), ("Ravi", 60), ("Manu", 50))
    assert [s["name"] for s in find_students(book, "NU")] == ["Anu Reddy", "Manu"]
    assert [s["name"] for s in find_students(book, " reddy ")] == ["Anu Reddy"]
    assert find_students(book, "zzz") == []


def test_search_results_come_back_sorted_whatever_the_order_added():
    book = make(("Tom", 1), ("Amy", 2), ("Kim", 3))
    assert [s["name"] for s in find_students(book, "m")] == ["Amy", "Kim", "Tom"]


@pytest.mark.parametrize("text", ["", "   "])
def test_empty_search_is_refused(text):
    with pytest.raises(BookError, match="Type some letters"):
        find_students(make(("Anu", 1)), text)


# ---------------------------------------------------------------- remove
def test_remove_ignores_capitals():
    book = make(("Anu", 80), ("Ravi", 60))
    assert remove_student(book, "ANU")["name"] == "Anu"
    assert [s["name"] for s in book] == ["Ravi"]


def test_remove_unknown_and_empty():
    book = make(("Anu", 80))
    with pytest.raises(BookError, match="No student called Zed"):
        remove_student(book, "Zed")
    with pytest.raises(BookError, match="cannot be empty"):
        remove_student(book, " ")
    assert len(book) == 1


# ---------------------------------------------------------------- top mark and average
def test_empty_class_has_no_top_and_no_average_and_does_not_crash():
    assert top_mark([]) is None and average_mark([]) is None


def test_top_mark_with_a_tie_lists_everybody_sorted():
    book = make(("zed", 90), ("Amy", 90), ("Bob", 40))
    assert top_mark(book) == (90, ["Amy", "zed"])


def test_top_mark_of_one_student():
    assert top_mark(make(("Solo", 0))) == (0, ["Solo"])


def test_average():
    assert average_mark(make(("a", 100), ("b", 50))) == 75
    assert average_mark(make(("a", 0))) == 0


# ---------------------------------------------------------------- the menu
def test_menu_full_walk():
    out = session("1", "Anu", "80", "1", "ravi", "60", "2", "3", "NU", "4", "5", "6", "ANU", "2", "7")
    assert "Added Anu - 80." in out and "Added ravi - 60." in out
    assert "Anu - 80\nravi - 60" in out
    assert "Top mark: 80 (Anu)" in out and "Average: 70.0" in out
    assert "Removed Anu - 80." in out and out.rstrip().endswith("Goodbye.")


def test_menu_empty_class_messages():
    out = session("2", "4", "5", "7")
    assert "The book is empty." in out and "no top mark" in out and "no average" in out


@pytest.mark.parametrize("choice", ["0", "8", "x", "", "1.5", "  "])
def test_menu_bad_choice(choice):
    assert "Please type a number from 1 to 7." in session(choice, "7")


def test_menu_shows_the_error_and_keeps_going():
    out = session("1", "Anu", "101", "1", "", "50", "1", "Anu", "5", "1", "anu", "6", "2", "7")
    assert out.count("Error: Marks must be a whole number from 0 to 100.") == 1
    assert "Error: The name cannot be empty." in out
    assert "Error: A student called anu is already in the book." in out
    listing = out.split("Error: A student called anu is already in the book.")[1]
    assert "Anu - 5" in listing and "anu - 6" not in listing  # only the first Anu is in the book; refused ones were not stored


def test_menu_search_with_no_match_and_with_empty_text():
    out = session("1", "Anu", "5", "3", "zzz", "3", "", "7")
    assert "No student matches." in out and "Type some letters" in out


def test_menu_remove_unknown():
    assert "No student called Bob in the book." in session("6", "Bob", "7")


# ---------------------------------------------------------------- the real program
def run_program(text):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run([sys.executable, str(SCRIPT)], input=text, capture_output=True, text=True, encoding="utf-8", env=env, timeout=20)


def test_real_program_session():
    result = run_program("1\nAnu\n80\n2\n7\n")
    assert result.returncode == 0 and "Anu - 80" in result.stdout and "Traceback" not in result.stderr


@pytest.mark.parametrize("typed", ["", "1\n", "1\nAnu\n", "2", "1\nAnu\n80\n"])
def test_ending_the_input_is_not_a_traceback(typed):
    result = run_program(typed)
    assert result.returncode == 0 and "Input ended" in result.stdout and "Traceback" not in result.stderr
```

---

## 8. Results

| Check | Command | Result |
|---|---|---|
| Tests | `python -m pytest -q` | **54 passed** |
| Type check | `python -m mypy class_marks_book.py` | **no issues found** |
| Break it on purpose | `python break_it.py` | **29 of 29 caught** (first run 27 of 29: one mistake was equivalent to the real code and one needed a test with students added out of order; both fixed) |
| Clean unzip | fresh folder, new venv, tests | see the final message |

---

## 9. Problems avoided

| Problem | Cause | Fix |
|---|---|---|
| Division by zero on an empty class | `sum / len` with no students | `average_mark` returns `None` for an empty book |
| `Anu` and `anu` both stored | Plain comparison of names | `name_key` with `casefold` and squeezed spaces |
| A test that hung forever waiting for typing | Fake typing ran out | The fake raises `StopIteration` instead |
| Search results in the wrong order | Results followed the order of adding | Search goes through `sorted_students` |

---

## 10. What was practiced

- Lists of dictionaries
- Small functions with one job
- Exceptions with friendly messages
- `casefold`, `strip`, `split`
- `if __name__ == "__main__"`
- Passing functions as arguments (`ask`, `say`)
- Testing the menu without a keyboard

---

## 11. Known limit

- **Windows was not tested.** Everything ran on Linux with Python 3.13.
- **Nothing is saved.** Close the program and the book is gone (that is Day 3).
- Two spellings of the same accented letter count as different names.
- The break-it script covers 29 mistakes I thought of. See `NOT_COVERED.md`.

---

## 12. How to run it

```bash
# Windows PowerShell, from the folder that holds class-marks-book.zip
Expand-Archive class-marks-book.zip -DestinationPath .
cd class-marks-book
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m pytest -q
python class_marks_book.py
```

Try it: choose 1 and add `Anu` with 80, then add `anu` again and read the message.
