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
