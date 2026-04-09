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
        self.class_methods_by_selector: dict[str, RuntimeMethod] = {}
        self.instance_methods_by_selector: dict[str, RuntimeMethod] = {}

    def inherits_from_name(self, ancestor_name: str) -> bool:
        """
        @brief Whether this runtime class is one named ancestor or inherits from it is checked.

        @param ancestor_name One ancestor class name to be checked.
        @return True when this class is the named ancestor or inherits from it, otherwise False.
        """
        current: RuntimeClass | None = self

        while current is not None:
            if current.name == ancestor_name:
                return True

            current = current.parent

        return False

    def add_instance_method(self, method: RuntimeMethod) -> None:
        """
        @brief A runtime instance method is added to this class.

        @param method A runtime method to be attached to this class.
        """
        selector = method.selector
        if selector in self.instance_methods_by_selector:
            raise InterpreterError(
                ErrorCode.GENERAL_OTHER,
                f"Runtime class '{self.name}' already contains local selector '{selector}'.",
            )
        self.instance_methods_by_selector[selector] = method

    def add_class_method(self, method: RuntimeMethod) -> None:
        """
        @brief A runtime class method is added to this class.

        @param method A runtime method to be attached to this class.
        """

        selector = method.selector
        if selector in self.class_methods_by_selector:
            raise InterpreterError(
                ErrorCode.GENERAL_OTHER,
                f"Runtime class '{self.name}' already contains local selector '{selector}'.",
            )

        self.class_methods_by_selector[selector] = method

    def _lookup_instance_local(self, selector: str) -> RuntimeMethod | None:
        """
        @brief A local instance runtime method is looked up by selector.

        @param selector A selector to be looked up locally.
        @return A local runtime method, or None when no match is found.
        """
        return self.instance_methods_by_selector.get(selector)

    def _lookup_class_local(self, selector: str) -> RuntimeMethod | None:
        """
        @brief A local class runtime method is looked up by selector.

        @param selector A selector to be looked up locally.
        @return A local runtime method, or None when no match is found.
        """
        return self.class_methods_by_selector.get(selector)

    def lookup_instance(self, selector: str) -> RuntimeMethod | None:
        """
        @brief A runtime instance method is looked up through the inheritance chain.

        @param selector A selector to be looked up.
        @return A runtime method, or None when no match is found.
        """
        local_method = self._lookup_instance_local(selector)
        if local_method is not None:
            return local_method
        if self.parent is None:
            return None
        return self.parent.lookup_instance(selector)

    def lookup_class(self, selector: str) -> RuntimeMethod | None:
        """
        @brief A runtime class method is looked up through the inheritance chain.

        @param selector A selector to be looked up.
        @return A runtime method, or None when no match is found.
        """
        local_method = self._lookup_class_local(selector)
        if local_method is not None:
            return local_method
        if self.parent is None:
            return None
        return self.parent.lookup_class(selector)
