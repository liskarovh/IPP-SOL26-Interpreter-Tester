"""
@file values.py
@brief Core runtime value classes are declared.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

The core runtime value hierarchy is declared here according to the current
UML class diagram. UserObject and BlockClosure are intentionally kept in
their own files.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .object_slots import ObjectSlots
    from .runtime_class import RuntimeClass


class RuntimeValue:
    """
    @brief A common base class for runtime values is represented.
    """

    def __init__(
        self,
        runtime_class: RuntimeClass,
        slots: ObjectSlots | None = None,
    ) -> None:
        """
        @brief A runtime value is initialized.

        @param runtime_class Runtime class of the represented value.
        @param slots Optional instance slot storage of the value.
        """
        self.runtime_class = runtime_class
        self.slots = slots

    def get_class(self) -> RuntimeClass:
        """
        @brief The runtime class of the value is returned.

        @return Runtime class of the value.
        """
        return self.runtime_class

    def debug_repr(self) -> str:
        """
        @brief A debug representation of the value is returned.

        @return Debug string representation of the value.
        """
        child_type = self.__class__.__name__
        runtime_class_name = self.runtime_class.name

        parts: list[str] = [f"runtime_class={runtime_class_name!r}"]

        for attribute_name in sorted(self.__dict__.keys()):
            if attribute_name == "runtime_class":
                continue

            attribute_value = self.__dict__[attribute_name]
            parts.append(f"{attribute_name}={attribute_value!r}")

        joined_parts = ", ".join(parts)

        return f"{child_type}({joined_parts})"


class IntegerValue(RuntimeValue):
    """
    @brief A runtime integer value is represented.
    """

    def __init__(
        self,
        runtime_class: RuntimeClass,
        value: int,
        slots: ObjectSlots | None = None,
    ) -> None:
        """
        @brief An integer runtime value is initialized.

        @param runtime_class Runtime class of the integer value.
        @param value Wrapped integer payload.
        @param slots Optional instance slot storage of the value.
        """
        super().__init__(runtime_class, slots)
        self.value = value

    def raw(self) -> int:
        """
        @brief The wrapped integer payload is returned.

        @return Wrapped integer payload.
        """
        return self.value


class StringValue(RuntimeValue):
    """
    @brief A runtime string value is represented.
    """

    def __init__(
        self,
        runtime_class: RuntimeClass,
        value: str,
        slots: ObjectSlots | None = None,
    ) -> None:
        """
        @brief An string runtime value is initialized.

        @param runtime_class Runtime class of the string value.
        @param value Wrapped integer payload.
        @param slots Optional instance slot storage of the value.
        """
        super().__init__(runtime_class, slots)
        self.value = value

    def raw(self) -> str:
        """
        @brief The wrapped string payload is returned.

        @return Wrapped string payload.
        """
        return self.value


class BooleanValue(RuntimeValue):
    """
    @brief A runtime boolean value is represented.
    """

    def __init__(self, runtime_class: RuntimeClass, value: bool) -> None:
        """
        @brief A boolean runtime value is initialized.

        @param runtime_class Runtime class of the boolean value.
        @param value Wrapped boolean payload.
        """
        super().__init__(runtime_class)
        self.value = value

    def raw(self) -> bool:
        """
        @brief The wrapped boolean payload is returned.

        @return Wrapped boolean payload.
        """
        return self.value


class NilValue(RuntimeValue):
    """
    @brief A runtime nil value is represented.
    """

    def __init__(self, runtime_class: RuntimeClass) -> None:
        """
        @brief A nil runtime value is initialized.

        @param runtime_class Runtime class of the nil value.
        """
        super().__init__(runtime_class)
        self.value = None
