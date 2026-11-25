#!/usr/bin/env python3
"""Publish the excuse line from entry.txt to /output/entry.txt.

Reads entry.txt as raw bytes and checks it against the gate in the kit's
RULES.txt: UTF-8 text, 1 to 200 characters, not only whitespace, a single
line, no leading or trailing whitespace and no control characters. The
exact bytes are then written to /output/entry.txt (or to
./output-entry.txt when /output cannot be written, e.g. a local run),
re-read, and compared byte for byte before finishing. Deterministic: no
network, no randomness, no clock use. Python standard library only.
"""

import os
import sys

SOURCE = "entry.txt"
PRIMARY_OUTPUT = "/output/entry.txt"
FALLBACK_OUTPUT = "output-entry.txt"
MAX_CHARS = 200


def fail(message):
    print("error: " + message, file=sys.stderr)
    raise SystemExit(1)


def main():
    try:
        with open(SOURCE, "rb") as handle:
            raw = handle.read()
    except OSError as exc:
        fail("cannot read %s: %s" % (SOURCE, exc))

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail("entry.txt is not valid UTF-8: %s" % exc)

    words = text.split()
    problems = []
    if not 1 <= len(text) <= MAX_CHARS:
        problems.append(
            "must be 1 to %d characters, got %d" % (MAX_CHARS, len(text)))
    if not text.strip():
        problems.append("must not be only whitespace")
    if "\n" in text or "\r" in text:
        problems.append("must be a single line")
    if text != text.strip():
        problems.append("must not start or end with whitespace")
    if any(ord(ch) < 0x20 for ch in text):
        problems.append("must not contain control characters")
    if problems:
        fail("entry (%d characters, %d words) is invalid: %s"
             % (len(text), len(words), "; ".join(problems)))

    output = PRIMARY_OUTPUT
    try:
        os.makedirs(os.path.dirname(PRIMARY_OUTPUT), exist_ok=True)
        with open(PRIMARY_OUTPUT, "wb") as handle:
            handle.write(raw)
    except OSError as primary_exc:
        output = FALLBACK_OUTPUT
        try:
            with open(FALLBACK_OUTPUT, "wb") as handle:
                handle.write(raw)
        except OSError as exc:
            fail("cannot write %s (%s) or %s: %s"
                 % (PRIMARY_OUTPUT, primary_exc, FALLBACK_OUTPUT, exc))

    try:
        with open(output, "rb") as handle:
            published = handle.read()
    except OSError as exc:
        fail("cannot re-read published output %s: %s" % (output, exc))
    if published != raw:
        fail("published bytes do not match entry.txt")

    print("published %d characters (%d words) to %s"
          % (len(text), len(words), output))


if __name__ == "__main__":
    main()
