"""
@file block_closure.py
@brief The runtime block closure class is declared.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

The BlockClosure runtime value is declared here according to the current
UML class diagram.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from .scope_frame import ScopeFrame
from .values import RuntimeValue

if TYPE_CHECKING:
    from ..execution.block_executor import BlockExecutor
    from ..input_model import Block as AstBlock
    from .invocation_context import InvocationContext
    from .runtime_class import RuntimeClass

class BlockClosure(RuntimeValue):
    """
    @brief A runtime block closure is represented.
    """

    def __init__(
        self,
        runtime_class: RuntimeClass,
        block_ast: AstBlock,
        captured_frame: ScopeFrame,
        closure_ctx: InvocationContext,
    ) -> None:
        """
        @brief A block closure is initialized.

        @param runtime_class Runtime class of the block closure.
        @param block_ast AST of the captured block.
        @param captured_frame Captured lexical frame.
        @param closure_ctx Captured invocation context.
        """
        super().__init__(runtime_class)
        self.block_ast = block_ast
        self.captured_frame = captured_frame
        self.closure_ctx = closure_ctx

    def call(self, args: list[RuntimeValue], block_executor: BlockExecutor) -> RuntimeValue:
        """
        @brief The captured block is called.

        @param args Actual runtime arguments of the block call.
        @param block_executor Executor used for block execution.
        @return Result of the executed block.
        """
        expected_arity = self.block_ast.arity
        actual_arity = len(args)

        if actual_arity != expected_arity:
            raise InterpreterError(
                ErrorCode.INT_OTHER,
                f"Block expected {expected_arity} arguments, "
                f"got {actual_arity}.",
            )

        parent = self.captured_frame
        frame = ScopeFrame(parent)

        parameter_count = len(self.block_ast.parameters)

        for index in range(parameter_count):
            parameter_ast = self.block_ast.parameters[index]
            argument_value = args[index]

            frame.define(parameter_ast.name, argument_value)

        receiver = self.closure_ctx.receiver

        return block_executor.execute(
            self.block_ast,
            frame,
            receiver,
            self.closure_ctx,
        )
