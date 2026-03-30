"""
@file user_object.py
@brief The runtime user object class is declared.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

The UserObject runtime value is declared here according to the current
UML class diagram.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .values import RuntimeValue

if TYPE_CHECKING:
    from .object_slots import ObjectSlots
    from .runtime_class import RuntimeClass


class UserObject(RuntimeValue):
    """
    @brief A runtime user object is represented.
    """

    def __init__(self, runtime_class: RuntimeClass, slots: ObjectSlots) -> None:
        """
        @brief A user object is initialized.

        @param runtime_class Runtime class of the object instance.
        @param slots Slot storage owned by the object instance.
        """
        super().__init__(runtime_class)
        self.slots = slots

    def read_slot(self, name: str) -> RuntimeValue:
        """
        @brief A slot value is read by name.

        @param name Requested slot name.
        @return Value stored in the requested slot.
        """

        return self.slots.get(name)

    def write_slot(self, name: str, value: RuntimeValue) -> None:
        """
        @brief A slot value is written by name.

        @param name Target slot name.
        @param value Value to be stored into the slot.
        """

        self.slots.set(name, value)

    def define_slot(self, name: str, value: RuntimeValue) -> None:
        """
        @brief A new slot is defined.

        @param name Name of the new slot.
        @param value Initial value of the new slot.
        """
        self.slots.define(name, value)
