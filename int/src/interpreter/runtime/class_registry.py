"""
@file class_registry.py
@brief Runtime class registry is defined.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Runtime classes are stored by name in this registry. Controlled lookup is
intended to be centralized here.
"""

from __future__ import annotations

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from ..model.runtime_class import RuntimeClass


class ClassRegistry:
    """
    @brief Runtime classes are stored in this registry.
    """

    def __init__(self) -> None:
        """
        @brief An empty runtime class registry is initialized.
        """
        self.classes: dict[str, RuntimeClass] = {}

    def add(self, runtime_class: RuntimeClass) -> None:
        """
        @brief A runtime class is registered.

        @param runtime_class A runtime class to be stored.
        """
        name = runtime_class.name
        if self.contains(name):
            raise InterpreterError(
                ErrorCode.GENERAL_OTHER,
                f"Class '{name}' is already defined.",
            )
        self.classes[name] = runtime_class

    def get(self, name: str) -> RuntimeClass | None:
        """
        @brief A runtime class is looked up by name.

        @param name A runtime class name.
        @return A runtime class, or None when no class is found.
        """

        return self.classes.get(name)

    def require(self, name: str) -> RuntimeClass:
        """
        @brief A runtime class is required by name.

        @param name A runtime class name.
        @return A runtime class that must exist.
        """

        found = self.get(name)
        if found is not None:
            return found
        raise InterpreterError(ErrorCode.GENERAL_OTHER, f"Class {name} is not defined.")

    def contains(self, name: str) -> bool:
        """
        @brief Presence of a runtime class is checked.

        @param name A runtime class name.
        @return True when the class exists, otherwise False.
        """
        return name in self.classes
