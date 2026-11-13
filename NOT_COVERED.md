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
