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
    from .values import RuntimeValue


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
        self._validate_arity(args)

        call_frame = self._create_call_frame()
        self._bind_arguments(call_frame, args)

        return block_executor.execute(
            self.block_ast,
            call_frame,
            self.closure_ctx,
        )

    def _validate_arity(self, args: list[RuntimeValue]) -> None:
        """
        @brief Block-call arity is validated.

        @param args Actual runtime arguments of the block call.
        """
        actual_arity = len(args)
        expected_arity = self.block_ast.arity

        if actual_arity != expected_arity:
            raise InterpreterError(
                ErrorCode.INT_DNU,
                f"Block expected {expected_arity} argument(s), but received {actual_arity}.",
            )

    def _create_call_frame(self) -> ScopeFrame:
        """
        @brief One new block-call frame is created.

        @return Fresh block-call frame.
        """
        call_frame = ScopeFrame()
        call_frame.parent = self.captured_frame
        return call_frame

    def _bind_arguments(
        self,
        call_frame: ScopeFrame,
        args: list[RuntimeValue],
    ) -> None:
        """
        @brief Block arguments are bound into the call frame.

        @param call_frame Fresh call frame of the block invocation.
        @param args Actual runtime arguments of the block call.
        """
        call_frame.bind_block_parameters(self.block_ast.parameters, args)
