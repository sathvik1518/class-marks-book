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
