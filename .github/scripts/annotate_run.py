"""Turn the key lines of a bot run's output into one GitHub notice annotation.

Annotations can be read through the public API without signing in, unlike job
logs. Only models, question counts, costs, credit usage and errors are passed
on, never forecast values, so forecasts on open questions are not exposed
before those questions close.

Usage: python annotate_run.py "<title>" <log file> [<log file> ...]
"""

import re
import sys

KEY_LINE = re.compile(
    r"Forecaster model|Testing on|Retrieved \d+ questions|Total cost estimated|"
    r"Average cost per question|Error while processing|No new questions|"
    r"Bot submitted|Partial|attempt\(s\) failed|✅|Setup problems|is missing|"
    r"usage:|could not read OpenRouter|Traceback|^[A-Za-z_.]*(Error|Exception)\b"
)
MAX_LINES = 40
MAX_LINE_LENGTH = 300


def main(title: str, log_paths: list[str]) -> None:
    lines: list[str] = []
    for path in log_paths:
        try:
            with open(path, encoding="utf-8", errors="replace") as log_file:
                lines += [line.rstrip() for line in log_file if KEY_LINE.search(line)]
        except FileNotFoundError:
            lines.append(f"{path}: not found")
    message = "\n".join(line[:MAX_LINE_LENGTH] for line in lines[:MAX_LINES])
    message = message or "no matching lines"
    message = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    print(f"::notice title={title}::{message}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
