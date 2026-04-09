"""
@file builtin_implementation.py
@brief Built-in method implementation strategies are defined.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Built-in method behavior is represented here through a small strategy layer.
Callback-backed adapters are provided separately for instance-side and
class-side built-in implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..support.typing_helpers import (
    ClassBuiltinCallback,
    InstanceBuiltinCallback,
    MethodReceiver,
    RuntimeValueList,
)

if TYPE_CHECKING:
    from ..model.invocation_context import InvocationContext
    from ..model.values import RuntimeValue


class BuiltinImplementation(ABC):
    """
    @brief One built-in method implementation strategy is represented.
    """

    @abstractmethod
    def invoke(
        self,
        receiver: MethodReceiver,
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


class InstanceCallbackBuiltinImplementation(BuiltinImplementation):
    """
    @brief One instance-side callback-backed built-in implementation is represented.
    """

    callback: InstanceBuiltinCallback

    def __init__(self, callback: InstanceBuiltinCallback) -> None:
        """
        @brief One instance-side callback-backed built-in implementation is initialized.

        @param callback A callback implementing instance-side built-in behavior.
        """
        self.callback = callback

    def invoke(
        self,
        receiver: MethodReceiver,
        args: RuntimeValueList,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief One instance-side callback-backed built-in implementation is invoked.

        @param receiver A method receiver.
        @param args Runtime call arguments.
        @param ctx An invocation context.
        @return A produced runtime value.
        """
        from ..model.runtime_class import RuntimeClass  # Avoid circular import

        if isinstance(receiver, RuntimeClass):
            raise TypeError("Instance-side builtin received a class receiver.")

        return self.callback(receiver, args, ctx)


class ClassCallbackBuiltinImplementation(BuiltinImplementation):
    """
    @brief One class-side callback-backed built-in implementation is represented.
    """

    callback: ClassBuiltinCallback

    def __init__(self, callback: ClassBuiltinCallback) -> None:
        """
        @brief One class-side callback-backed built-in implementation is initialized.

        @param callback A callback implementing class-side built-in behavior.
        """
        self.callback = callback

    def invoke(
        self,
        receiver: MethodReceiver,
        args: RuntimeValueList,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief One class-side callback-backed built-in implementation is invoked.

        @param receiver A method receiver.
        @param args Runtime call arguments.
        @param ctx An invocation context.
        @return A produced runtime value.
        """
        from ..model.runtime_class import RuntimeClass  # Avoid circular import

        if not isinstance(receiver, RuntimeClass):
            raise TypeError("Class-side builtin received an instance receiver.")

        return self.callback(receiver, args, ctx)
