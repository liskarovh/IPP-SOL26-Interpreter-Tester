"""
@file attribute_accessor.py
@brief Attribute slot access is implemented.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Low-level attribute slot reads and writes are handled here.
Selector meaning is resolved elsewhere.
"""

from __future__ import annotations

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from ..model.values import RuntimeValue


class AttributeAccessor:
    """
    @brief Low-level attribute slot access is handled by this class.
    """

    @staticmethod
    def read(receiver: RuntimeValue, name: str) -> RuntimeValue:
        """
        @brief An attribute slot value is read.

        @param receiver Runtime receiver whose attribute is read.
        @param name Slot name to read.
        @return Runtime value stored in the requested attribute slot.
        """
        slots = receiver.slots
        if slots is None:
            raise InterpreterError(
                ErrorCode.INT_STRUCTURE,
                "Attribute read was requested on a non-user object.",
            )

        return slots.get(name)

    @staticmethod
    def write(
        receiver: RuntimeValue,
        name: str,
        value: RuntimeValue,
    ) -> RuntimeValue:
        """
        @brief An attribute slot value is written.

        @param receiver Runtime receiver whose attribute is written.
        @param name Slot name to write.
        @param value Runtime value to store in the requested attribute slot.
        @return Receiver after the attribute slot is written.
        """
        slots = receiver.slots
        if slots is None:
            raise InterpreterError(
                ErrorCode.INT_STRUCTURE,
                "Attribute write was requested on a non-user object.",
            )

        if slots.has(name):
            slots.set(name, value)
        else:
            slots.define(name, value)

        return receiver
