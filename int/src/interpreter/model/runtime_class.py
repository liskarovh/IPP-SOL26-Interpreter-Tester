"""
@file runtime_class.py
@brief Runtime class representation is defined.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

A runtime class stores its name, parent reference, and runtime methods.
Method lookup over the inheritance chain is intended to be performed here.
"""

from __future__ import annotations

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from .runtime_methods import RuntimeMethod


class RuntimeClass:
    """
    @brief One runtime class is represented by this class.
    """

    def __init__(self, name: str, parent: RuntimeClass | None = None) -> None:
        """
        @brief A runtime class is initialized.

        @param name A runtime class name.
        @param parent A parent runtime class, if one exists.
        """
        self.name = name
        self.parent = parent
        self.methods_by_selector: dict[str, RuntimeMethod] = {}

    def add_method(self, method: RuntimeMethod) -> None:
        """
        @brief A runtime method is added to this class.

        @param method A runtime method to be attached to this class.
        """

        selector = method.selector
        if selector in self.methods_by_selector:
            raise InterpreterError(
                ErrorCode.GENERAL_OTHER,
                (
                    f"Runtime class '{self.name}' already contains "
                    f"local selector '{selector}'."
                ),
            )

        self.methods_by_selector[selector] = method

    def has_local_method(self, selector: str) -> bool:
        """
        @brief Existence of a local method is checked.

        @param selector A selector to be looked up locally.
        @return True when a local method exists, otherwise False.
        """

        return selector in self.methods_by_selector

    def has_method(self, selector: str) -> bool:
        """
        @brief Existence of a method in the inheritance chain is checked.

        @param selector A selector to be looked up.
        @return True when the method exists locally or in an ancestor.
        """

        if self.has_local_method(selector):
            return True
        if self.parent is None:
            return False
        return self.parent.has_method(selector)

    def lookup_local(self, selector: str) -> RuntimeMethod | None:
        """
        @brief A local runtime method is looked up by selector.

        @param selector A selector to be looked up locally.
        @return A local runtime method, or None when no match is found.
        """
        return self.methods_by_selector.get(selector)
    def lookup(self, selector: str) -> RuntimeMethod | None:
        """
        @brief A runtime method is looked up through the inheritance chain.

        @param selector A selector to be looked up.
        @return A runtime method, or None when no match is found.
        """
        local_method = self.lookup_local(selector)
        if local_method is not None:
            return local_method
        if self.parent is None:
            return None
        return self.parent.lookup(selector)
