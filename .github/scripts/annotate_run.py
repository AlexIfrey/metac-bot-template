"""Turn the key lines of a bot run's output into one GitHub notice annotation.

Annotations can be read through the public API without signing in, unlike job
logs. Only models, question counts, costs, credit usage and errors are passed
on, never forecast values, so forecasts on open questions are not exposed
before those questions close.

GitHub cuts long annotation messages, so summary lines come first and error
lines last, shortened.

Usage: python annotate_run.py "<title>" <log file> [<log file> ...]
"""

import re
import sys

SUMMARY_LINE = re.compile(
    r"Forecaster model|Testing on|Retrieved \d+ questions|Total cost estimated|"
    r"Average cost per question|No new questions|Bot submitted|Partial|"
    r"attempt\(s\) failed|✅|Setup problems|is missing|usage:|"
    r"could not read OpenRouter"
)
ERROR_LINE = re.compile(
    r"Error while processing|Traceback|^[A-Za-z_.]*(Error|Exception)\b"
)
MAX_SUMMARY_LINES = 25
MAX_ERROR_LINES = 8
MAX_SUMMARY_LINE_LENGTH = 250
MAX_ERROR_LINE_LENGTH = 160
MAX_MESSAGE_LENGTH = 3500


def main(title: str, log_paths: list[str]) -> None:
    summary_lines: list[str] = []
    error_lines: list[str] = []
    for path in log_paths:
        try:
            with open(path, encoding="utf-8", errors="replace") as log_file:
                for line in log_file:
                    line = line.rstrip()
                    if SUMMARY_LINE.search(line):
                        summary_lines.append(line[:MAX_SUMMARY_LINE_LENGTH])
                    elif ERROR_LINE.search(line):
                        error_lines.append(line[:MAX_ERROR_LINE_LENGTH])
        except FileNotFoundError:
            summary_lines.append(f"{path}: not found")
    lines = summary_lines[:MAX_SUMMARY_LINES]
    if error_lines:
        lines.append(f"--- errors: {len(error_lines)} line(s), first {MAX_ERROR_LINES} ---")
        lines += error_lines[:MAX_ERROR_LINES]
    message = "\n".join(lines)[:MAX_MESSAGE_LENGTH] or "no matching lines"
    message = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    print(f"::notice title={title}::{message}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
