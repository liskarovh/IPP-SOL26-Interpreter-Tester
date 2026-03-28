"""
@file program_runner.py
@brief Program execution orchestration is defined.

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME.

A loaded AST program is validated, converted into a runtime, and resolved
to the program entry point. No execution is started yet at this stage.
"""

from ..input_model import Program
from ..runtime.runtime_io import RuntimeIO
from .entry_point_resolver import EntryPointResolver
from .program_validator import ProgramValidator
from .runtime_builder import RuntimeBuilder


class ProgramRunner:
    """
    @brief The current interpreter pipeline is orchestrated by this class.
    """

    def __init__(self) -> None:
        """
        @brief A program runner is initialized.

        The current pipeline collaborators are created here.
        """
        self.program_validator = ProgramValidator()
        self.runtime_builder = RuntimeBuilder()
        self.entry_point_resolver = EntryPointResolver()

    def run(self, program: Program, input_io: RuntimeIO) -> None:
        """
        @brief A loaded program is processed through the current pipeline.

        The program is validated first. A runtime is then built, and the
        runtime entry point is resolved. No execution is started yet.

        @param program A previously loaded AST program.
        @param input_io An input/output adapter passed from the interpreter.
        """
        self.program_validator.validate(program)

        runtime = self.runtime_builder.build(program, input_io)

        entry_receiver, entry_method = self.entry_point_resolver.resolve(runtime)
        _ = entry_receiver
        _ = entry_method
