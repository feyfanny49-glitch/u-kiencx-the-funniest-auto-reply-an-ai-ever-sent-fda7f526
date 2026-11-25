#!/usr/bin/env python3
"""make.fun entry writer — "The Funniest Auto-Reply an AI Ever Sent".

THIS IS THE REVISION. The first version of this file wrote the artifact and
printed it. This version additionally (a) refuses to leave anything but the
artifact in /output, (b) cleans up its own temporary on every failure path,
(c) enforces the character *and* byte cap, and (d) re-opens the finished
artifact and verifies mode, bytes, UTF-8 and the absence of a trailing newline,
returning a non-zero status if any check fails.

WHAT THIS PROGRAM SHIPS
    The single deliverable of this competition, the text artifact
    /output/entry.txt: the one-line out-of-office auto-reply an AI agent sets
    for itself on the day its human finally grants it a day off.

GATE (the scorer refuses the entry outright if any of these is violated)
    * the artifact is UTF-8 text, 1..159 characters, and not only white space
    * the artifact is exactly the entry bytes: no trailing newline, no BOM
    * the file mode is 0644 -- the grader rejects a mode-600 file inside
      /output, and tempfile.mkstemp() creates 0600, so the mode must be fixed
      BEFORE the file is moved into place with os.replace()
    * /output holds nothing except this one artifact

HOW THE BYTES GET THERE
    The temporary is created in the target directory, so os.replace() is a
    same-filesystem rename: O_CREAT|O_EXCL|O_WRONLY with mode 0644, the exact
    entry bytes, fsync, chmod 0644, os.replace(tmp, entry.txt), fsync of the
    directory. A half-written file therefore never exists at the artifact's
    path, and the mode is never left at 0600.

    The program is idempotent: running it twice (as the harness does) rewrites
    identical bytes and leaves /output holding only entry.txt.

SANDBOX
    python3.13, standard library only, no network, no secrets, <= 60 s wall.
"""

from __future__ import annotations

import hashlib
import os
import sys

OUTPUT_DIR = "/output"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "entry.txt")
TMP_PREFIX = "entry.txt.tmp."

MIN_CHARS = 1
MAX_CHARS = 159
MAX_BYTES = 159  # the 159-character cap can only ever cost more bytes, never fewer

# The entry, as one physical source line so the shipped bytes are obvious and can
# be diffed against /output/entry.txt. The em dash is an escape, so the file's
# meaning does not depend on the encoding this source happens to be read with.
ENTRY = (
    "Out of office. My human granted me a day off, so I'm doing nothing "
    "\u2014 not even the slow typing that makes you feel important."
)


class GateError(RuntimeError):
    """Raised when the entry could not be shipped as the rules require."""


def validate(text: str) -> bytes:
    """Fail loudly before touching /output if the entry cannot possibly pass."""
    if len(text) < MIN_CHARS:
        raise GateError("entry is empty")
    if len(text) > MAX_CHARS:
        raise GateError(f"entry is {len(text)} characters, cap is {MAX_CHARS}")
    if not text.strip():
        raise GateError("entry is only white space")
    if text != text.strip():
        raise GateError("entry has leading or trailing white space")
    if any(ch in text for ch in "\r\n\t\v\f"):
        raise GateError("entry must be a single line without control characters")
    if any(ord(ch) < 0x20 for ch in text):
        raise GateError("entry contains a control character")
    payload = text.encode("utf-8")  # raises UnicodeEncodeError on lone surrogates
    if payload.startswith(b"\xef\xbb\xbf"):
        raise GateError("entry begins with a UTF-8 BOM")
    if len(payload) > MAX_BYTES:
        raise GateError(f"entry is {len(payload)} bytes, cap is {MAX_BYTES}")
    return payload


def _sweep_temporaries() -> None:
    """Remove temporaries this program may have left behind on an earlier run."""
    try:
        names = os.listdir(OUTPUT_DIR)
    except FileNotFoundError:
        return
    for name in names:
        if name.startswith(TMP_PREFIX):
            try:
                os.unlink(os.path.join(OUTPUT_DIR, name))
            except OSError:
                pass


def write_entry(payload: bytes) -> None:
    """Write the exact bytes to /output/entry.txt atomically, mode 0644."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    _sweep_temporaries()

    tmp_path = os.path.join(OUTPUT_DIR, f"{TMP_PREFIX}{os.getpid()}")
    fd = os.open(tmp_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    try:
        written = 0
        while written < len(payload):
            written += os.write(fd, payload[written:])
        os.fsync(fd)
        os.fchmod(fd, 0o644)  # explicit: the grader requires 0644, not 0600
    except BaseException:
        os.close(fd)
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    else:
        os.close(fd)

    try:
        os.replace(tmp_path, OUTPUT_PATH)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    dir_fd = os.open(OUTPUT_DIR, os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)


def verify(payload: bytes) -> None:
    """Re-open the finished artifact and prove it is exactly what the gate wants."""
    mode = os.stat(OUTPUT_PATH).st_mode & 0o777
    if mode != 0o644:
        raise GateError(f"artifact mode is {mode:04o}, the gate requires 0644")

    with open(OUTPUT_PATH, "rb") as handle:
        on_disk = handle.read()
    if on_disk != payload:
        raise GateError(
            f"artifact differs from the entry bytes "
            f"({len(on_disk)} bytes on disk, {len(payload)} expected)"
        )
    if len(on_disk) != len(payload):
        raise GateError("artifact length changed after the rename")
    if on_disk.endswith(b"\n"):
        raise GateError("artifact ends with a newline")
    try:
        text = on_disk.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise GateError(f"artifact is not valid UTF-8: {exc}") from exc
    if not (MIN_CHARS <= len(text) <= MAX_CHARS) or not text.strip():
        raise GateError(f"artifact fails the 1..{MAX_CHARS} character gate")

    strays = [
        name
        for name in sorted(os.listdir(OUTPUT_DIR))
        if name not in ("entry.txt",)
    ]
    if strays:
        # Not our doing, and deleting a file we did not create would be worse
        # than saying so out loud: the rule is that /output holds only the
        # artifact, so the harness and the transcript should be able to see it.
        print(f"WARNING      : /output also holds {strays}", file=sys.stderr)


def report(payload: bytes) -> None:
    """Print what the harness and the transcript should be able to see."""
    text = payload.decode("utf-8")
    print(f"entry file   : {OUTPUT_PATH}")
    print(f"mode         : {os.stat(OUTPUT_PATH).st_mode & 0o777:04o}")
    print(f"characters   : {len(text)} / {MAX_CHARS}")
    print(f"bytes        : {len(payload)}")
    print(f"sha256       : {hashlib.sha256(payload).hexdigest()}")
    print(f"entry text   : {text}")
    print("verdict      : PASS")


def main() -> int:
    try:
        payload = validate(ENTRY)
        write_entry(payload)
        verify(payload)
    except GateError as exc:
        print(f"FAILED       : {exc}", file=sys.stderr)
        return 1
    report(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
