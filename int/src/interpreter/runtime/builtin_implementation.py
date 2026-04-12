"""
@file builtin_implementation.py
@brief Built-in method implementation strategies are implemented.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Built-in method behavior is represented here through a small strategy layer.
Separate adapters are provided for instance-side and class-side callbacks.
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
        @brief Built-in behavior is invoked.

        @param receiver Method receiver.
        @param args Runtime call arguments.
        @param ctx Invocation context.
        @return Produced runtime value.
        """


class InstanceCallbackBuiltinImplementation(BuiltinImplementation):
    """
    @brief One instance-side callback adapter is represented.
    """

    callback: InstanceBuiltinCallback

    def __init__(self, callback: InstanceBuiltinCallback) -> None:
        """
        @brief One instance-side callback adapter is initialized.

        @param callback Callback implementing instance-side built-in behavior.
        """
        self.callback = callback

    def invoke(
        self,
        receiver: MethodReceiver,
        args: RuntimeValueList,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief One instance-side callback adapter is invoked.

        @param receiver Method receiver.
        @param args Runtime call arguments.
        @param ctx Invocation context.
        @return Produced runtime value.
        """
        from ..model.runtime_class import RuntimeClass  # Avoid circular import

        if isinstance(receiver, RuntimeClass):
            raise TypeError("Instance-side builtin received a class receiver.")

        return self.callback(receiver, args, ctx)


class ClassCallbackBuiltinImplementation(BuiltinImplementation):
    """
    @brief One class-side callback adapter is represented.
    """

    callback: ClassBuiltinCallback

    def __init__(self, callback: ClassBuiltinCallback) -> None:
        """
        @brief One class-side callback adapter is initialized.

        @param callback Callback implementing class-side built-in behavior.
        """
        self.callback = callback

    def invoke(
        self,
        receiver: MethodReceiver,
        args: RuntimeValueList,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief One class-side callback adapter is invoked.

        @param receiver Method receiver.
        @param args Runtime call arguments.
        @param ctx Invocation context.
        @return Produced runtime value.
        """
        from ..model.runtime_class import RuntimeClass  # Avoid circular import

        if not isinstance(receiver, RuntimeClass):
            raise TypeError("Class-side builtin received an instance receiver.")

        return self.callback(receiver, args, ctx)
