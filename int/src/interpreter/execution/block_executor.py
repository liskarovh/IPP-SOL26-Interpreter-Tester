"""
@file block_executor.py
@brief Block execution is coordinated here.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

A block is intended to be executed here as a sequence of assignments.
The right-hand side of each assignment is intended to be evaluated by the
expression dispatcher.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..execution.expression_dispatcher import ExpressionDispatcher
from ..model.values import RuntimeValue

if TYPE_CHECKING:
    from ..input_model import Assign as AstAssign
    from ..input_model import Block as AstBlock
    from ..model.invocation_context import InvocationContext
    from ..model.scope_frame import ScopeFrame


class BlockExecutor:
    """
    @brief Block execution is coordinated by this class.
    """

    expression_dispatcher: ExpressionDispatcher

    def __init__(self, expression_dispatcher: ExpressionDispatcher) -> None:
        """
        @brief Required execution dependencies are stored.

        @param expression_dispatcher An expression dispatcher used for RHS evaluation.
        """
        self.expression_dispatcher = expression_dispatcher

    def execute(
        self,
        block_ast: AstBlock,
        frame: ScopeFrame,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief One block AST is executed.

        @param block_ast A block AST whose assignments are to be executed.
        @param frame A lexical scope frame used for variable storage and lookup.
        @param ctx An invocation context carrying self/super information.
        @return The value of the last evaluated assignment expression, or nil for an empty block.

        """
        last_value: RuntimeValue | None = None

        for assign_ast in block_ast.assigns:
            last_value = self.execute_assignment(assign_ast, frame, ctx)

        if last_value is not None:
            return last_value

        return self.expression_dispatcher.object_factory.new_nil()

    def execute_assignment(
        self,
        assign_ast: AstAssign,
        frame: ScopeFrame,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief One assignment AST is executed.

        @param assign_ast An assignment AST to be executed.
        @param frame A lexical scope frame used for variable storage and lookup.
        @param ctx An invocation context carrying self/super information.
        @return The evaluated right-hand-side result of the assignment.
        """
        target_name = assign_ast.target.name
        expr_ast = assign_ast.expr
        value = self.expression_dispatcher.evaluate(expr_ast, frame, ctx)
        if frame.contains(target_name):
            frame.set(target_name, value)
        else:
            frame.define(target_name, value)
        return value
