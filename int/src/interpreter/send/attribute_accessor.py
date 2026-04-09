"""
@file attribute_accessor.py
@brief Attribute slot access is coordinated here.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Low-level attribute presence checks and slot reads/writes are intended to
be performed here. Selector meaning is not intended to be decided here.
"""

from __future__ import annotations

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from ..model.object_slots import ObjectSlots
from ..model.values import RuntimeValue


def _get_receiver_slots(receiver: RuntimeValue) -> ObjectSlots | None:
    """
    @brief Attribute slots of one runtime receiver are returned when available.

    @param receiver A runtime receiver whose slots are to be accessed.
    @return Slot storage of the receiver, or None when no slot storage exists.
    """
    return receiver.slots


class AttributeAccessor:
    """
    @brief Attribute slot access is coordinated by this class.
    """

    @staticmethod
    def read(receiver: RuntimeValue, name: str) -> RuntimeValue:
        """
        @brief One attribute slot value is read.

        @param receiver A runtime receiver whose attribute is to be read.
        @param name A slot name to be read.
        @return A runtime value stored in the requested attribute slot.
        """
        slots = _get_receiver_slots(receiver)
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
        @brief One attribute slot value is written.

        @param receiver A runtime receiver whose attribute is to be written.
        @param name A slot name to be written.
        @param value A runtime value to be stored into the requested attribute slot.
        @return The receiver after the attribute slot is written.
        """
        slots = _get_receiver_slots(receiver)
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
