"""
@file expression_dispatcher.py
@brief Expression evaluation is dispatched here.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Non-send expression kinds are intended to be evaluated here first.
Send evaluation is intended to be delegated later.
"""

from __future__ import annotations

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from ..input_model import Block as AstBlock
from ..input_model import Expr as AstExpr
from ..input_model import Literal as AstLiteral
from ..model.invocation_context import InvocationContext
from ..model.scope_frame import ScopeFrame
from ..model.values import RuntimeValue
from ..runtime.object_factory import ObjectFactory


def _if_var_get_name(expr: AstExpr) -> str | None:
    if expr.var is not None:
        return expr.var.name
    return None

def _if_literal_get_class_id(expr: AstExpr) -> str | None:
    if expr.literal is not None:
        return expr.literal.class_id
    return None
def _if_block_return(expr: AstExpr) -> AstBlock | None:
    if expr.block is not None:
        return expr.block
    return None

class ExpressionDispatcher:
    """
    @brief Non-send expression evaluation is coordinated by this class.
    """

    object_factory: ObjectFactory
    # send_evaluator: SendExprEvaluator

    def __init__(self, object_factory: ObjectFactory) -> None:
        """
        @brief Required execution dependencies are stored.

        @param object_factory A factory used for runtime value creation.
        """
        self.object_factory = object_factory

    def evaluate(
        self,
        expr_ast: AstExpr,
        frame: ScopeFrame,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief One expression node is evaluated.

        @param expr_ast An AST expression node to be evaluated.
        @param frame A lexical scope frame used for variable lookup.
        @param ctx An invocation context carrying self/super information.
        @return A runtime value produced by the expression.
        """
        var_name = _if_var_get_name(expr_ast)
        if var_name is not None:
            return self._evaluate_var(var_name, frame, ctx)

        literal_class_id = _if_literal_get_class_id(expr_ast)
        if literal_class_id is not None:
            literal = expr_ast.literal
            if literal is not None:
                return self._evaluate_literal(literal_class_id, literal)
        block_ast = _if_block_return(expr_ast)
        if block_ast is not None:
            return self._evaluate_block(block_ast, frame, ctx)

        raise NotImplementedError("Unsupported expression kind")
    @staticmethod
    def _evaluate_var(var_name: str, frame: ScopeFrame, ctx: InvocationContext) -> RuntimeValue:
        if var_name == "self" or var_name == "super":
            return ctx.self_value()
        value = frame.get(var_name)
        if value is None:
            raise InterpreterError(
                ErrorCode.SEM_UNDEF,
                f"Variable {var_name} is not defined."
            )
        return value

    def _evaluate_literal(self, class_id: str, literal: AstLiteral) -> RuntimeValue:
        if class_id == "Integer":
            value = literal.value
            return self.object_factory.new_integer(int(value))
        if class_id == "String":
            value = literal.value
            return self.object_factory.new_string(value)
        if class_id == "True":
            return self.object_factory.new_boolean(True)
        if class_id == "False":
            return self.object_factory.new_boolean(False)
        if class_id == "Nil":
            return self.object_factory.new_nil()
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            "Unsupported literal class: " + class_id
        )

    def _evaluate_block(
            self,
            block: AstBlock,
            frame: ScopeFrame,
            ctx: InvocationContext
    ) -> RuntimeValue:
        return self.object_factory.new_block_closure(block, frame, ctx)
