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
