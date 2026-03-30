"""
@file invocation_context.py
@brief Invocation context objects are declared.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Invocation context is intended to carry the current receiver and the current
method owner for self/super semantics during execution.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .runtime_class import RuntimeClass
    from .values import RuntimeValue


class InvocationContext:
    """
    @brief One invocation context is represented by this class.
    """

    def __init__(
        self,
        receiver: RuntimeValue,
        current_owner: RuntimeClass,
    ) -> None:
        """
        @brief One invocation context is initialized.

        @param receiver Current invocation receiver.
        @param current_owner Runtime class owning the currently executed method.
        """
        self.receiver = receiver
        self.current_owner = current_owner

    def self_value(self) -> RuntimeValue:
        """
        @brief The current self value is returned.

        @return Current invocation receiver.
        """
        return self.receiver

    def super_start(self) -> RuntimeClass | None:
        """
        @brief The starting class for super lookup is returned.

        @return Parent of the current method owner.
        """

        return self.current_owner.parent
