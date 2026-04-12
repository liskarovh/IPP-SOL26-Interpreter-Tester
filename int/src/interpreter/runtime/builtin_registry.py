"""
@file builtin_registry.py
@brief Built-in runtime values and methods are stored.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Canonical true, false, and nil values are stored here together with
registered built-in methods.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError

if TYPE_CHECKING:
    from ..model.runtime_methods import BuiltinMethod
    from ..model.values import BooleanValue, NilValue


class BuiltinRegistry:
    """
    @brief Canonical built-in values and built-in methods are stored here.
    """

    true_value: BooleanValue | None
    false_value: BooleanValue | None
    nil_value: NilValue | None
    class_builtin_methods: dict[tuple[str, str], BuiltinMethod]
    instance_builtin_methods: dict[tuple[str, str], BuiltinMethod]

    def __init__(self) -> None:
        """
        @brief The built-in registry is initialized.
        """
        self.true_value = None
        self.false_value = None
        self.nil_value = None
        self.class_builtin_methods = {}
        self.instance_builtin_methods = {}

    def set_true_value(self, value: BooleanValue) -> None:
        """
        @brief The canonical true value is stored.

        @param value A canonical true runtime value.
        """
        self.true_value = value

    def set_false_value(self, value: BooleanValue) -> None:
        """
        @brief The canonical false value is stored.

        @param value A canonical false runtime value.
        """
        self.false_value = value

    def set_nil_value(self, value: NilValue) -> None:
        """
        @brief The canonical nil value is stored.

        @param value A canonical nil runtime value.
        """
        self.nil_value = value

    def get_true_value(self) -> BooleanValue:
        """
        @brief The canonical true value is returned.

        @return A canonical true runtime value.
        """
        if self.true_value is None:
            raise InterpreterError(ErrorCode.INT_OTHER, "The true value is not set.")
        return self.true_value

    def get_false_value(self) -> BooleanValue:
        """
        @brief The canonical false value is returned.

        @return A canonical false runtime value.
        """
        if self.false_value is None:
            raise InterpreterError(ErrorCode.INT_OTHER, "The false value is not set.")
        return self.false_value

    def get_nil_value(self) -> NilValue:
        """
        @brief The canonical nil value is returned.

        @return A canonical nil runtime value.
        """
        if self.nil_value is None:
            raise InterpreterError(ErrorCode.INT_OTHER, "The nil value is not set.")
        return self.nil_value

    def register_instance_builtin_method(
        self,
        class_name: str,
        selector: str,
        method: BuiltinMethod,
    ) -> None:
        """
        @brief One instance-side built-in method is registered.

        @param class_name Name of the runtime class owning the built-in method.
        @param selector Built-in method selector.
        @param method Built-in runtime method instance.
        """

        dict_key = (class_name, selector)
        if dict_key in self.instance_builtin_methods:
            raise InterpreterError(
                ErrorCode.INT_OTHER,
                f"A built-in method {selector} is already registered for class {class_name}.",
            )
        self.instance_builtin_methods[dict_key] = method

    def register_class_builtin_method(
        self,
        class_name: str,
        selector: str,
        method: BuiltinMethod,
    ) -> None:
        """
        @brief One class-side built-in method is registered.

        @param class_name Name of the runtime class owning the built-in method.
        @param selector Built-in method selector.
        @param method Built-in runtime method instance.
        """

        dict_key = (class_name, selector)
        if dict_key in self.class_builtin_methods:
            raise InterpreterError(
                ErrorCode.INT_OTHER,
                f"A built-in method {selector} is already registered for class {class_name}.",
            )
        self.class_builtin_methods[dict_key] = method
