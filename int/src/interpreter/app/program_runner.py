"""
@file program_runner.py
@brief Program execution orchestration is defined.

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME.

A loaded AST program is forwarded through the first execution pipeline step.
At this stage, only static program validation is performed.
"""

from ..input_model import Program
from .program_validator import ProgramValidator


class ProgramRunner:
    """
    @brief A minimal orchestration object is provided for the interpreter.

    The execution pipeline is intentionally kept simple at this stage.
    Only static validation is delegated from here.
    """

    def __init__(self) -> None:
        """
        @brief A phase-2 runner is initialized.

        The program validator is created here so that the first real pipeline
        step can be executed from one orchestration point.
        """
        self.program_validator = ProgramValidator()

    def run(self, program: Program, input_io: object) -> None:
        """
        @brief A loaded program is validated.

        No runtime is built yet, and no method execution is performed yet.
        The input/output adapter is accepted only because it already belongs
        to the planned runner interface.

        @param program A previously loaded AST program.
        @param input_io An input/output adapter passed from the interpreter.
        """
        _ = input_io

        self.program_validator.validate(program)
