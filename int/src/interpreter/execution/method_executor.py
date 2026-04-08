"""
@file method_executor.py
@brief Method execution is coordinated here.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

A runtime method is executed here. The minimum version supports only
user-defined methods needed for the first simple programs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from ..model.invocation_context import InvocationContext
from ..model.runtime_class import RuntimeClass
from ..model.runtime_methods import BuiltinMethod, RuntimeMethod, UserMethod
from ..model.scope_frame import ScopeFrame
from ..model.values import RuntimeValue
from ..support.typing_helpers import MethodReceiver

if TYPE_CHECKING:
    from ..execution.block_executor import BlockExecutor


def _validate_argument_count(
        method: RuntimeMethod,
    args: list[RuntimeValue],
) -> None:
    """
    @brief The supplied argument count is validated.

    @param method A runtime method whose arity is to be respected.
    @param args Evaluated method arguments.
    """
    expected_arity = method.arity()
    actual_arity = len(args)

    if actual_arity != expected_arity:
        raise InterpreterError(
            ErrorCode.GENERAL_OTHER,
            "Internal method invocation arity mismatch.",
        )


def _create_invocation_context(
    receiver: MethodReceiver,
    owner: RuntimeClass,
) -> InvocationContext:
    """
    @brief One invocation context is created for a method call.

    @param receiver A receiver of the method call.
    @param owner An owning runtime class of the executed method.
    @return A freshly created invocation context.
    """
    return InvocationContext(receiver, owner)


def _create_method_frame() -> ScopeFrame:
    """
    @brief One fresh method scope frame is created.

    @return A fresh method scope frame.
    """
    return ScopeFrame()


def _parameter_names(method: UserMethod) -> list[str]:
    """
    @brief Declared parameter names of one user-defined method are extracted.

    @param method A user-defined runtime method.
    @return Declared parameter names in source order.
    """
    return [parameter_ast.name for parameter_ast in method.method_ast.block.parameters]


def _bind_method_parameters(
        method: UserMethod,
    args: list[RuntimeValue],
    frame: ScopeFrame,
) -> None:
    """
    @brief Method parameters are bound into the method frame.

    @param method A user-defined runtime method whose parameters are to be bound.
    @param args Evaluated method arguments.
    @param frame A method scope frame receiving parameter bindings.
    """
    parameter_names = _parameter_names(method)
    expected_count = len(parameter_names)
    actual_count = len(args)

    if actual_count != expected_count:
        raise InterpreterError(
            ErrorCode.GENERAL_OTHER,
            "Internal parameter binding mismatch.",
        )

    index = 0
    while index < expected_count:
        parameter_name = parameter_names[index]
        argument_value = args[index]
        frame.define(parameter_name, argument_value)

        index += 1


class MethodExecutor:
    """
    @brief Method execution is coordinated by this class.
    """

    block_executor: BlockExecutor

    def __init__(self, block_executor: BlockExecutor) -> None:
        """
        @brief Required execution dependencies are stored.

        @param block_executor A block executor used for method-body execution.
        """
        self.block_executor = block_executor

    def execute(
        self,
        method: RuntimeMethod,
        receiver: MethodReceiver,
        args: list[RuntimeValue],
    ) -> RuntimeValue:
        """
        @brief One runtime method is executed.

        @param method A runtime method to be executed.
        @param receiver A receiver of the method call.
        @param args Evaluated method arguments.
        @return A runtime value returned by the executed method.
        """
        _validate_argument_count(method, args)

        if isinstance(method, UserMethod):
            if isinstance(receiver, RuntimeClass):
                raise InterpreterError(
                    ErrorCode.GENERAL_OTHER,
                    "Class receiver is not valid for a user method execution.",
                )
            return self._execute_user_method(method, receiver, args)

        if isinstance(method, BuiltinMethod):
            return self._execute_builtin(method, receiver, args)

        raise InterpreterError(
            ErrorCode.GENERAL_OTHER,
            "Unsupported runtime method type in MethodExecutor.",
        )

    def _execute_user_method(
        self,
        method: UserMethod,
        receiver: RuntimeValue,
        args: list[RuntimeValue],
    ) -> RuntimeValue:
        """
        @brief One user-defined method is executed.

        @param method A user-defined runtime method.
        @param receiver A receiver of the method call.
        @param args Evaluated method arguments.
        @return A runtime value returned by the method body.
        """
        ctx = _create_invocation_context(receiver, method.owner)
        frame = _create_method_frame()
        _bind_method_parameters(method, args, frame)
        return self.block_executor.execute(method.method_ast.block, frame, ctx)

    @staticmethod
    def _execute_builtin(
            method: BuiltinMethod,
            receiver: MethodReceiver,
            args: list[RuntimeValue]
    ) -> RuntimeValue:
        """
        @brief One built-in method is executed.

        @param method A built-in runtime method.
        @param receiver A receiver of the method call.
        @param args Evaluated method arguments.
        @return A runtime value returned by the built-in implementation.
        """
        ctx = _create_invocation_context(receiver, method.owner)
        return method.call(receiver, args, ctx)

