"""
@file user_object.py
@brief Runtime user object is implemented.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Runtime user objects are represented here as runtime values
with attached slot storage.
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
        super().__init__(runtime_class, slots)
