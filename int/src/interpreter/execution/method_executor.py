"""
@file method_executor.py
@brief Method execution is coordinated here.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

A runtime method is executed here by validating the supplied argument count,
creating one invocation context for the method call and then calling
the method with the effective receiver, the evaluated arguments and the
created invocation context.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from ..model.invocation_context import InvocationContext
from ..model.runtime_class import RuntimeClass
from ..model.runtime_methods import RuntimeMethod, UserMethod
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

    @staticmethod
    def execute(
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

        if isinstance(method, UserMethod) and isinstance(receiver, RuntimeClass):
            raise InterpreterError(
                ErrorCode.GENERAL_OTHER,
                "Class receiver is not valid for a user method execution.",
            )

        ctx = _create_invocation_context(receiver, method.owner)
        return method.call(receiver, args, ctx)
