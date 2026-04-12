"""
@file expression_dispatcher.py
@brief Expression evaluation is dispatched here.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Expression evaluation is coordinated in this module.
Variables, literals, blocks, and sends are distinguished here,
while actual send dispatch is delegated to specialized send evaluators.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from ..input_model import Block as AstBlock
from ..input_model import Expr as AstExpr
from ..input_model import Literal as AstLiteral
from ..input_model import Send as AstSend
from ..model.invocation_context import InvocationContext
from ..model.runtime_class import RuntimeClass
from ..model.scope_frame import ScopeFrame
from ..model.values import RuntimeValue
from ..runtime.object_factory import ObjectFactory
from ..send.resolved_receiver import ResolvedReceiver
from ..support.send_types import LookupMode, ReceiverOrigin
from ..support.typing_helpers import MethodReceiver

if TYPE_CHECKING:
    from ..send.send_expr_evaluator import (
        ClassSendExprEvaluator,
        InstanceSendExprEvaluator,
    )


def _decode_string_literal(raw_value: str) -> str:
    """
    @brief One SOL26 string literal payload is decoded.

    @param raw_value One raw string payload from the AST.
    @return One decoded runtime string payload.
    """
    decoded_chars: list[str] = []
    is_escape = False

    # handling of escape sequences
    for char in raw_value:
        if is_escape:
            if char == "n":
                decoded_chars.append("\n")
            elif char == "'":
                decoded_chars.append("'")
            elif char == "\\":
                decoded_chars.append("\\")
            else:
                raise InterpreterError(
                    ErrorCode.INT_STRUCTURE,
                    "Invalid string literal escape sequence.",
                )

            is_escape = False
            continue

        if char == "\\":
            is_escape = True
            continue

        decoded_chars.append(char)

    if is_escape:
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            "Invalid string literal escape sequence.",
        )

    return "".join(decoded_chars)


def _if_var_get_name(expr: AstExpr) -> str | None:
    """
    @brief Variable name is returned when the expression is a variable branch.

    @param expr One AST expression to be inspected.
    @return Variable name, or None when the expression is not a variable branch.
    """
    if expr.var is not None:
        return expr.var.name
    return None


def _if_literal_get_class_id(expr: AstExpr) -> str | None:
    """
    @brief Literal class identifier is returned when the expression is a literal branch.

    @param expr One AST expression to be inspected.
    @return Literal class identifier, or None when the expression is not a literal branch.
    """
    if expr.literal is not None:
        return expr.literal.class_id
    return None


def _if_block_return(expr: AstExpr) -> AstBlock | None:
    """
    @brief Block AST is returned when the expression is a block branch.

    @param expr One AST expression to be inspected.
    @return Block AST, or None when the expression is not a block branch.
    """
    if expr.block is not None:
        return expr.block
    return None


def _set_lookup_mode(expr: AstExpr) -> LookupMode:
    """
    @brief Lookup mode for one send receiver expression is resolved.

    @param expr One AST expression used as the send receiver.
    @return Lookup mode derived from the receiver syntax.
    """
    receiver_name = _if_var_get_name(expr)
    if receiver_name == "super":
        return LookupMode.SUPER
    return LookupMode.NORMAL


def _resolve_receiver_origin(expr: AstExpr) -> ReceiverOrigin:
    """
    @brief One syntactic receiver origin is resolved.

    @param expr One AST expression used as the send receiver.
    @return One receiver-origin classification for the send.
    """
    receiver_name = _if_var_get_name(expr)

    if receiver_name == "self":
        return ReceiverOrigin.EXPLICIT_SELF

    if receiver_name == "super":
        return ReceiverOrigin.EXPLICIT_SUPER

    return ReceiverOrigin.ORDINARY


def _require_runtime_self_value(receiver: MethodReceiver) -> RuntimeValue:
    """
    @brief Runtime self-value is required for ordinary expression evaluation.

    @param receiver One method receiver value.
    @return Runtime receiver value usable as a normal expression result.
    @throws InterpreterError When a class receiver leaks into ordinary self/super evaluation.
    """
    if isinstance(receiver, RuntimeClass):
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            "Class receiver leaked into ordinary self/super expression evaluation.",
        )
    return receiver


class ExpressionDispatcher:
    """
    @brief Non-send expression evaluation is coordinated by this class.
    """

    object_factory: ObjectFactory
    instance_send_evaluator: InstanceSendExprEvaluator
    class_send_evaluator: ClassSendExprEvaluator

    def __init__(
        self,
        object_factory: ObjectFactory,
        instance_send_evaluator: InstanceSendExprEvaluator,
        class_send_evaluator: ClassSendExprEvaluator,
    ) -> None:
        """
        @brief Required execution dependencies are stored.

        @param object_factory A factory used for runtime value creation.
        @param instance_send_evaluator One instance-side send evaluator.
        @param class_send_evaluator One class-side send evaluator.
        """
        self.object_factory = object_factory
        self.instance_send_evaluator = instance_send_evaluator
        self.class_send_evaluator = class_send_evaluator

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

        # expression kind resolved by checking AST branch
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

        if expr_ast.send is not None:
            return self._evaluate_send(expr_ast.send, frame, ctx)

        raise NotImplementedError("Unsupported expression kind")

    @staticmethod
    def _evaluate_var(
        var_name: str,
        frame: ScopeFrame,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief One variable expression is evaluated.

        @param var_name One variable name to be evaluated.
        @param frame One lexical scope frame used for variable lookup.
        @param ctx One invocation context carrying self/super information.
        @return One runtime value stored under the variable name.
        """
        # self and super read from invocation context
        if var_name == "self" or var_name == "super":
            return _require_runtime_self_value(ctx.self_value())

        value = frame.get(var_name)
        if value is None:
            raise InterpreterError(
                ErrorCode.SEM_UNDEF,
                f"Variable {var_name} is not defined.",
            )

        return value

    def _evaluate_literal(
        self,
        class_id: str,
        literal: AstLiteral,
    ) -> RuntimeValue:
        """
        @brief One non-class literal expression is evaluated.

        @param class_id One literal class identifier.
        @param literal One literal AST node.
        @return One runtime value produced from the literal.
        """
        # runtime literal creation delegated to object factory
        if class_id == "Integer":
            value = literal.value
            return self.object_factory.new_integer(int(value))

        if class_id == "String":
            return self.object_factory.new_string(literal.value)

        if class_id == "True":
            return self.object_factory.new_boolean(True)

        if class_id == "False":
            return self.object_factory.new_boolean(False)

        if class_id == "Nil":
            return self.object_factory.new_nil()

        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            "Unsupported literal class: " + class_id,
        )

    def _evaluate_block(
        self,
        block: AstBlock,
        frame: ScopeFrame,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief One block literal is evaluated.

        @param block One block AST node.
        @param frame One lexical scope frame captured by the block.
        @param ctx One invocation context captured by the block.
        @return One runtime block closure.
        """
        return self.object_factory.new_block_closure(block, frame, ctx)

    def _resolve_send_receiver(
        self,
        receiver_expr: AstExpr,
        frame: ScopeFrame,
        ctx: InvocationContext,
    ) -> ResolvedReceiver:
        """
        @brief One send receiver is resolved into an effective receiver and lookup mode.

        @param receiver_expr One AST expression used as the send receiver.
        @param frame One lexical scope frame used for nested expression evaluation.
        @param ctx One invocation context carrying self/super information.
        @return One resolved send receiver.
        """

        # receiver syntax determines origin and  lookup
        lookup_mode = _set_lookup_mode(receiver_expr)
        receiver_origin = _resolve_receiver_origin(receiver_expr)

        receiver_name = _if_var_get_name(receiver_expr)

        # self and super keep current runtime receiver and change lookup mode
        if receiver_name == "self" or receiver_name == "super":
            return ResolvedReceiver(
                ctx.self_value(),
                lookup_mode,
                receiver_origin,
            )

        # direct convert to runtime class
        literal = receiver_expr.literal
        if literal is not None and literal.class_id == "class":
            runtime_class = self.object_factory.class_registry.require(literal.value)
            return ResolvedReceiver(
                runtime_class,
                lookup_mode,
                receiver_origin,
            )

        # evaluate receiver expression
        receiver_value = self.evaluate(receiver_expr, frame, ctx)
        return ResolvedReceiver(
            receiver_value,
            lookup_mode,
            receiver_origin,
        )

    def _evaluate_send(
        self,
        send: AstSend,
        frame: ScopeFrame,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief One send expression is evaluated.

        @param send One send AST node.
        @param frame One lexical scope frame used for receiver and argument evaluation.
        @param ctx One invocation context carrying self/super information.
        @return One runtime value returned by the dispatched send.
        """
        resolved_receiver = self._resolve_send_receiver(send.receiver, frame, ctx)

        resolved_args: list[RuntimeValue] = []
        for arg in send.args:
            arg_value = self.evaluate(arg.expr, frame, ctx)
            resolved_args.append(arg_value)

        selector = send.selector

        # runtime classes represent class side sends and use class send evaluator
        if isinstance(resolved_receiver.receiver, RuntimeClass):
            return self.class_send_evaluator.dispatch_send(
                resolved_receiver,
                selector,
                resolved_args,
                ctx,
            )

        # all non class receivers handled as instance sends
        return self.instance_send_evaluator.dispatch_send(
            resolved_receiver,
            selector,
            resolved_args,
            ctx,
        )
