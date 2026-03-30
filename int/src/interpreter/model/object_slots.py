"""
@file object_slots.py
@brief Object slot storage is declared.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Slot storage for user objects is represented here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError

if TYPE_CHECKING:
    from .values import RuntimeValue


class ObjectSlots:
    """
    @brief Slot storage for a runtime user object is represented.
    """

    slots_by_name: dict[str, RuntimeValue]

    def __init__(self, slots_by_name: dict[str, RuntimeValue]) -> None:
        """
        @brief Slot storage is initialized.

        @param slots_by_name Initial mapping of slot names to runtime values.
        """
        self.slots_by_name = slots_by_name

    def has(self, name: str) -> bool:
        """
        @brief Presence of a slot name is checked.

        @param name Name of the requested slot.
        @return True if the slot exists, otherwise False.
        """
        return name in self.slots_by_name

    def get(self, name: str) -> RuntimeValue:
        """
        @brief A slot value is returned by name.

        @param name Name of the requested slot.
        @return Runtime value stored under the given slot name.
        """
        self._require_existing_slot(name)
        return self.slots_by_name[name]

    def set(self, name: str, value: RuntimeValue) -> None:
        """
        @brief A slot value is stored by name.

        @param name Name of the target slot.
        @param value Runtime value to be stored.
        """
        self._require_existing_slot(name)
        self.slots_by_name[name] = value

    def define(self, name: str, value: RuntimeValue) -> None:
        """
        @brief A new slot is defined.

        @param name Name of the new slot.
        @param value Initial value of the new slot.
        """

        if name in self.slots_by_name:
            raise InterpreterError(
                ErrorCode.INT_INST_ATTR,
                f"Slot '{name}' is already defined.",
            )
        self.slots_by_name[name] = value

    def _require_existing_slot(self, name: str) -> None:
        """
        @brief Existence of a slot is required.

        @param name Name of the required slot.
        """
        if not self.has(name):
            raise InterpreterError(
                ErrorCode.INT_INST_ATTR,
                f"Object does not have slot '{name}'.",
            )
