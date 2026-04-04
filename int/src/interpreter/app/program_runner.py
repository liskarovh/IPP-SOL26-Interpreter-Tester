"""
@file program_runner.py
@brief Program execution orchestration is defined.

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME.

A loaded AST program is validated, converted into a runtime, resolved
to the program entry point, and then executed.
"""

from __future__ import annotations

from ..execution.block_executor import BlockExecutor
from ..execution.expression_dispatcher import ExpressionDispatcher
from ..execution.method_executor import MethodExecutor
from ..input_model import Program
from ..runtime.runtime import Runtime
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
        @brief Stateless pipeline collaborators are initialized.

        The execution chain is not created here, because it must be bound
        to the concrete runtime instance built for one program run.
        """
        self.program_validator = ProgramValidator()
        self.runtime_builder = RuntimeBuilder()
        self.entry_point_resolver = EntryPointResolver()

    def run(self, program: Program, input_io: RuntimeIO) -> None:
        """
        @brief One loaded program is validated, built, resolved, and executed.

        The program is validated first. A runtime is then built, the
        runtime entry point is resolved, and the entry method is executed.

        @param program A previously loaded AST program.
        @param input_io An input/output adapter passed from the interpreter.
        """
        self.program_validator.validate(program)

        runtime = self.runtime_builder.build(program, input_io)
        method_executor = self._create_method_executor(runtime)

        entry_receiver, entry_method = self.entry_point_resolver.resolve(runtime)
        _ = method_executor.execute(entry_method, entry_receiver, [])

    @staticmethod
    def _create_method_executor(runtime: Runtime) -> MethodExecutor:
        """
        @brief One execution chain is created for the supplied runtime.

        The created chain is bound to the runtime object factory so that
        execution uses the same runtime world that was built from the AST.

        @param runtime A runtime prepared for one program run.
        @return A method executor wired for this runtime.
        """
        expression_dispatcher = ExpressionDispatcher(runtime.object_factory)
        block_executor = BlockExecutor(expression_dispatcher)
        return MethodExecutor(block_executor)