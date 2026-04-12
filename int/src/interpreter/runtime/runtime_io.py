"""
@file runtime_io.py
@brief Runtime input and output streams are implemented.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Runtime standard input, output, and error streams are grouped here.
"""

from __future__ import annotations

from typing import TextIO


class RuntimeIO:
    """
    @brief Runtime standard streams are represented here.
    """

    stdin: TextIO
    stdout: TextIO
    stderr: TextIO

    def __init__(self, stdin: TextIO, stdout: TextIO, stderr: TextIO) -> None:
        """
        @brief Runtime standard streams are initialized.

        @param stdin Runtime standard input stream.
        @param stdout Runtime standard output stream.
        @param stderr Runtime standard error stream.
        """
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def read_line(self) -> str:
        """
        @brief A single input line is read from standard input.

        @return Line read from runtime standard input.
        """
        return self.stdin.readline()

    def write(self, text: str) -> None:
        """
        @brief Text is written to standard output.

        @param text Text to write.
        """
        self.stdout.write(text)
