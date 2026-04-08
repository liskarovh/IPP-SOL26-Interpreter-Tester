"""
@file send_expr_evaluator.py
@brief Send expression evaluation is coordinated here.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Send expression semantics are intended to be handled here separately from
ordinary expression evaluation. Shared send dependencies are stored in the
abstract base class, while instance-side and class-side send behavior is
intended to be split into dedicated subclasses.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from ..model.block_closure import BlockClosure
from ..model.runtime_class import RuntimeClass
from ..model.runtime_methods import RuntimeMethod
from ..model.values import RuntimeValue
from ..send.attribute_accessor import AttributeAccessor
from ..send.attribute_dispatch_resolver import AttributeDispatchResolver
from ..send.resolved_receiver import ResolvedReceiver
from ..support.lookup_helpers import resolve_lookup_start_class
from ..support.send_types import AttributeDispatchDecision
from ..support.typing_helpers import MethodReceiver

if TYPE_CHECKING:
    from ..execution.method_executor import MethodExecutor
    from ..model.invocation_context import InvocationContext

#regex was made by ai - https://chatgpt.com/share/69d39320-00bc-8387-bb25-1ee66b02d9ed
BLOCK_VALUE_SELECTOR_REGEX = re.compile(r"^(?:value|(?:value:)+)$")


def _if_receiver_block_check_arity(
        target: ResolvedReceiver,
        selector: str,
        args: list[RuntimeValue]
) -> BlockClosure | None :
    receiver = target.receiver
    if isinstance(receiver, BlockClosure):
        if not BLOCK_VALUE_SELECTOR_REGEX.fullmatch(selector):
            return None

        selector_arity = selector.count(":")
        if selector_arity != len(args):
            raise InterpreterError(
                ErrorCode.INT_DNU,
                "Wrong number of arguments for selector"
            )
        block_arity = receiver.block_ast.arity
        if block_arity != len(args):
            raise InterpreterError(
                ErrorCode.INT_DNU,
                "Wrong number of arguments for block"
            )
        return receiver

    return None

def _require_attribute_receiver(receiver: MethodReceiver) -> RuntimeValue:
    """
    @brief One attribute-capable receiver is required.

    @param receiver One method receiver intended for attribute access.
    @return One runtime receiver carrying instance slot storage.
    """
    if not isinstance(receiver, RuntimeValue):
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            "Attribute dispatch was requested on a non-runtime-value receiver.",
        )

    if receiver.slots is None:
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            "Attribute dispatch was requested on a receiver without slot storage.",
        )

    return receiver

def _require_class_receiver(receiver: MethodReceiver) -> RuntimeClass:
    """
    @brief One class-side receiver is required.

    @param receiver One method receiver intended for class-side dispatch.
    @return One runtime class receiver.
    """
    if not isinstance(receiver, RuntimeClass):
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            "Class-side dispatch was requested on a non-class receiver.",
        )

    return receiver

def _attribute_name_from_selector(selector: str) -> str:
    """
    @brief One attribute name is extracted from one resolved attribute selector.

    @param selector One selector already resolved as one attribute selector.
    @return One attribute name derived from the selector.
    """
    if selector.endswith(":"):
        return selector[:-1]

    return selector


class SendExprEvaluator(ABC):
    """
    @brief A shared base class for send expression evaluation is represented.
    """

    attribute_resolver: AttributeDispatchResolver
    method_executor: MethodExecutor | None
    attribute_accessor: AttributeAccessor

    def __init__(
        self,
        attribute_resolver: AttributeDispatchResolver,
        method_executor: MethodExecutor | None,
        attribute_accessor: AttributeAccessor,
    ) -> None:
        """
        @brief Shared send-evaluation dependencies are stored.

        @param attribute_resolver A resolver used for attribute-dispatch decisions.
        @param method_executor A method executor used for method activation.
        @param attribute_accessor An accessor used for low-level attribute slot access.
        """
        self.attribute_resolver = attribute_resolver
        self.method_executor = method_executor
        self.attribute_accessor = attribute_accessor


    @abstractmethod
    def dispatch_send(
        self,
        target: ResolvedReceiver,
        selector: str,
        args: list[RuntimeValue],
        ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief One resolved send is dispatched.

        @param target A resolved receiver carrying effective receiver and lookup mode.
        @param selector A selector to be dispatched.
        @param args Evaluated send arguments.
        @param ctx An invocation context carrying self/super information.
        @return A runtime value produced by the dispatched send.
        """

    def _execute_resolved_method(
            self,
            method: RuntimeMethod,
            receiver: MethodReceiver,
            args: list[RuntimeValue],
    ) -> RuntimeValue:
        """
        @brief One resolved method is executed with the given receiver and arguments.

        @param method A resolved runtime method to be executed.
        @param receiver A method receiver.
        @param args Runtime call arguments.
        @return A runtime value produced by the executed method.
        """
        return self._require_method_executor().execute(method, receiver, args)

    def wire_method_executor(self, method_executor: MethodExecutor) -> None:
        """
        @brief One method executor dependency is wired after construction.

        @param method_executor A method executor to be stored for later dispatch use.
        """
        self.method_executor = method_executor

    def _require_method_executor(self) -> MethodExecutor:
        """
        @brief One wired method executor is required.

        @return A previously wired method executor.
        """
        if self.method_executor is None:
            raise InterpreterError(
                ErrorCode.INT_STRUCTURE,
                "MethodExecutor is not wired in SendExprEvaluator.",
            )
        return self.method_executor


class InstanceSendExprEvaluator(SendExprEvaluator):
    """
    @brief Instance-side send expression evaluation is represented.
    """

    def dispatch_send(
        self,
        target: ResolvedReceiver,
        selector: str,
        args: list[RuntimeValue],
        ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief One resolved instance-side send is dispatched.

        @param target A resolved receiver carrying effective receiver and lookup mode.
        @param selector A selector to be dispatched.
        @param args Evaluated send arguments.
        @param ctx An invocation context carrying self/super information.
        @return A runtime value produced by the dispatched send.
        """

        receiver = target.receiver
        lookup_start = resolve_lookup_start_class(
            target.receiver,
            target.lookup_mode,
            ctx,
        )

        block = _if_receiver_block_check_arity(target, selector, args)
        #has to be with _require helper because of circular imports
        block_executor = self._require_method_executor().block_executor
        if block is not None:
            return block.call(args, block_executor)

        decision = self.attribute_resolver.resolve(
            receiver,
            selector,
            target.lookup_mode,
            target.origin,
            ctx,
        )

        if decision == AttributeDispatchDecision.ATTRIBUTE_READ:
            attribute_name = _attribute_name_from_selector(selector)
            attribute_receiver = _require_attribute_receiver(receiver)
            return self.attribute_accessor.read(attribute_receiver, attribute_name)

        if decision == AttributeDispatchDecision.ATTRIBUTE_WRITE:
            attribute_name = _attribute_name_from_selector(selector)
            attribute_receiver = _require_attribute_receiver(receiver)
            written_value = args[0]
            return self.attribute_accessor.write(
                attribute_receiver,
                attribute_name,
                written_value,
            )

        if decision == AttributeDispatchDecision.CONFLICT:
            attribute_name = _attribute_name_from_selector(selector)
            raise InterpreterError(
                ErrorCode.INT_INST_ATTR,
                f"Instance attribute '{attribute_name}' collides with a method.",
            )

        method = lookup_start.lookup_instance(selector)
        if method is None:
            raise InterpreterError(
                ErrorCode.INT_DNU,
                f"No method found for selector {selector}"
            )

        return self._execute_resolved_method(method, receiver, args)


class ClassSendExprEvaluator(SendExprEvaluator):
    """
    @brief Class-side send expression evaluation is represented.
    """

    def dispatch_send(
            self,
            target: ResolvedReceiver,
            selector: str,
            args: list[RuntimeValue],
            ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief One resolved class-side send is dispatched.

        @param target A resolved receiver carrying effective receiver and lookup mode.
        @param selector A selector to be dispatched.
        @param args Evaluated send arguments.
        @param ctx An invocation context carrying self/super information.
        @return A runtime value produced by the dispatched send.
        """
        receiver = _require_class_receiver(target.receiver)

        lookup_start = resolve_lookup_start_class(
            receiver,
            target.lookup_mode,
            ctx,
        )

        method = lookup_start.lookup_class(selector)
        if method is None:
            raise InterpreterError(
                ErrorCode.INT_DNU,
                f"Class {receiver.name} does not understand class selector {selector}.",
            )

        return self._execute_resolved_method(method, receiver, args)
