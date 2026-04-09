"""
This module contains the main logic of the interpreter.

IPP: You must definitely modify this file. Bend it to your will.

Author: Ondřej Ondryáš <iondryas@fit.vut.cz>
Author:
"""

import logging
import sys
from pathlib import Path
from typing import TextIO

from lxml import etree
from lxml.etree import ParseError
from pydantic import ValidationError

from .app.program_runner import ProgramRunner
from .app.xml_validator import XmlValidator
from .error_codes import ErrorCode
from .exceptions import InterpreterError
from .input_model import Program
from .runtime.runtime_io import RuntimeIO

logger = logging.getLogger(__name__)


class Interpreter:
    """
    @brief The main interpreter object is defined.

    The source file is loaded, converted to the AST model, and later
    forwarded to the program runner.
    """

    def __init__(self) -> None:
        """
        @brief The interpreter is initialized.

        A program runner is prepared, and no program is loaded initially.
        """
        self.program_runner = ProgramRunner()
        self.xml_validator = XmlValidator()
        self.loaded_program: Program | None = None

    def load_program(self, source_file_path: Path) -> None:
        """
        @brief The source SOL-XML file is loaded and converted to AST.

        The XML file is first parsed as a well-formed XML document. After that,
        document-level SOL-XML checks are performed. Finally, the AST model is
        built from the validated XML root.

        @param source_file_path A path to the source SOL-XML file.
        """
        logger.info("Opening source file: %s", source_file_path)

        try:
            xml_tree = etree.parse(source_file_path)
        except ParseError as error:
            raise InterpreterError(
                error_code=ErrorCode.INT_XML,
                message="Error parsing input XML.",
            ) from error

        xml_root = self.xml_validator.validate_xml_document(
            source_file_path,
            xml_tree,
        )

        try:
            parsed_program = Program.from_xml_tree(xml_root)  # type: ignore[arg-type]
        except ValidationError as error:
            raise InterpreterError(
                error_code=ErrorCode.INT_STRUCTURE,
                message="Invalid SOL-XML structure.",
            ) from error

        self.xml_validator.validate_program_ast(parsed_program)
        self.loaded_program = parsed_program

    def execute(self, input_io: TextIO) -> None:
        """
        @brief A previously loaded program is forwarded to the runner.

        @param input_io An input/output adapter.
        """

        runtime_io = RuntimeIO(
            stdin=input_io,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        program = self.loaded_program
        if program is None:
            raise InterpreterError(
                ErrorCode.GENERAL_OTHER,
                "No program loaded.",
            )

        self.program_runner.run(program, runtime_io)
