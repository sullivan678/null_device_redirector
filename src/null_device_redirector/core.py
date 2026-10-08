"""Context manager that redirects stdout and stderr to os.devnull."""

import os
import sys
from contextlib import AbstractContextManager
from typing import IO, Optional


class suppress_output(AbstractContextManager):
    """Redirect sys.stdout and sys.stderr to os.devnull within a block.

    Restores the original stream objects on exit, including the case where an
    exception propagates through the block.

    Only sys.stdout and sys.stderr are redirected. Stream objects that were
    captured by user code before entering the block are not affected; they keep
    referencing the original streams they were bound to. This is a deliberate
    consequence of how Python's stream redirection works and is the reason this
    library is small and predictable.
    """

    def __init__(self) -> None:
        self._null: Optional[IO[str]] = None
        self._old_stdout: Optional[IO[str]] = None
        self._old_stderr: Optional[IO[str]] = None

    def __enter__(self) -> "suppress_output":
        # Stash the live stream objects, then point the module attributes at a
        # /dev/null handle. We hold the null handle on the instance so __exit__
        # can close it after restoring the originals.
        self._old_stdout = sys.stdout
        self._old_stderr = sys.stderr
        self._null = open(os.devnull, "w", encoding="utf-8")
        sys.stdout = self._null
        sys.stderr = self._null
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        # Restore first, then close the null handle. If close() were to raise,
        # the original streams would already be back in place.
        if self._old_stdout is not None:
            sys.stdout = self._old_stdout
        if self._old_stderr is not None:
            sys.stderr = self._old_stderr
        if self._null is not None:
            self._null.close()
