"""
@file builtin_implementation.py
@brief Built-in method implementation strategies are defined.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Built-in method behavior is represented here through a small strategy layer.
A callback-backed adapter is provided for simple built-in implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..support.typing_helpers import BuiltinCallback, RuntimeValueList

if TYPE_CHECKING:
    from ..model.invocation_context import InvocationContext
    from ..model.values import RuntimeValue



class BuiltinImplementation(ABC):
    """
    @brief One built-in method implementation strategy is represented.
    """

    def __init__(self) -> None:
        """
        @brief One built-in method implementation strategy is initialized.
        """

    @abstractmethod
    def invoke(
        self,
        receiver: RuntimeValue,
        args: RuntimeValueList,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief One built-in method implementation is invoked.

        @param receiver A method receiver.
        @param args Runtime call arguments.
        @param ctx An invocation context.
        @return A produced runtime value.
        """


class CallbackBuiltinImplementation(BuiltinImplementation):
    """
    @brief One callback-backed built-in implementation is represented.
    """

    callback: BuiltinCallback

    def __init__(self, callback: BuiltinCallback) -> None:
        """
        @brief One callback-backed built-in implementation is initialized.

        @param callback A callback implementing built-in behavior.
        """
        super().__init__()
        self.callback = callback

    def invoke(
        self,
        receiver: RuntimeValue,
        args: RuntimeValueList,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief One callback-backed built-in implementation is invoked.

        @param receiver A method receiver.
        @param args Runtime call arguments.
        @param ctx An invocation context.
        @return A produced runtime value.
        """
        return self.callback(receiver, args, ctx)
