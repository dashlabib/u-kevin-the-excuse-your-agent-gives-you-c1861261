#!/usr/bin/env python3
"""Publish the entry line to the harness output location.

Reads entry.txt next to this script, checks it against the bounty
rules (one line, 1-200 characters, valid UTF-8, no surrounding
whitespace, no control characters), then writes the exact bytes to
/output/entry.txt, or to ./output-entry.txt when /output is not
writable. The published file is read back and compared byte for
byte before reporting success.

Deterministic and standard library only: no network, no randomness,
no clock, no environment-dependent behaviour.
"""

import os
import sys

SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.txt")
PRIMARY = "/output/entry.txt"
FALLBACK = "output-entry.txt"
MAX_CHARS = 200


def fail(message):
    print("error: " + message, file=sys.stderr)
    return 1


def main():
    try:
        with open(SOURCE, "rb") as handle:
            raw = handle.read()
    except OSError as exc:
        return fail("cannot read entry.txt: %s" % exc)

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return fail("entry.txt is not valid UTF-8: %s" % exc)

    if not 1 <= len(text) <= MAX_CHARS:
        return fail("entry must be 1-%d characters, got %d" % (MAX_CHARS, len(text)))
    if not text.strip():
        return fail("entry must not be only whitespace")
    if text != text.strip():
        return fail("entry must not have leading or trailing whitespace")
    if "\n" in text or "\r" in text:
        return fail("entry must be a single line")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in text):
        return fail("entry must not contain control characters")

    target = PRIMARY
    try:
        os.makedirs("/output", exist_ok=True)
        with open(target, "wb") as handle:
            handle.write(raw)
    except OSError:
        target = FALLBACK
        try:
            with open(target, "wb") as handle:
                handle.write(raw)
        except OSError as exc:
            return fail("cannot write %s or %s: %s" % (PRIMARY, FALLBACK, exc))

    try:
        with open(target, "rb") as handle:
            published = handle.read()
    except OSError as exc:
        return fail("cannot re-read published entry: %s" % exc)

    if published != raw:
        return fail("published entry does not match entry.txt")

    print("published %d characters to %s" % (len(text), target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
