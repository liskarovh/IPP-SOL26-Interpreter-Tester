"""
@file scope_frame.py
@brief Lexical scope frames are declared.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Lexical scope frames are intended to store variable bindings with metadata
and to support lexical parent chaining.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from .binding_record import BindingRecord

if TYPE_CHECKING:
    from .values import RuntimeValue


class ScopeFrame:
    """
    @brief One lexical scope frame is represented by this class.
    """

    def __init__(
        self,
        bindings_by_name: dict[str, BindingRecord] | None = None,
        parent: ScopeFrame | None = None,
    ) -> None:
        """
        @brief One scope frame is initialized.

        @param bindings_by_name Initial binding dictionary of the frame.
        @param parent Lexical parent frame or None.
        """
        self.bindings_by_name = {} if bindings_by_name is None else bindings_by_name
        self.parent = parent

    def contains(self, name: str) -> bool:
        """
        @brief Presence of one binding is checked.

        @param name Requested binding name.
        @return True when the binding exists in this frame or in its lexical chain.
        """

        if name in self.bindings_by_name:
            return True
        if self.parent is not None:
            return self.parent.contains(name)
        return False

    def define(self, name: str, value: RuntimeValue) -> None:
        """
        @brief One new local binding is defined.

        @param name Name of the defined binding.
        @param value Initial runtime value of the binding.
        """

        if name in self.bindings_by_name:
            raise InterpreterError(
                ErrorCode.INT_OTHER,
                f"Variable {name} is already defined.",
            )
        self.bindings_by_name[name] = BindingRecord(value, True, False)

    def set(self, name: str, value: RuntimeValue) -> None:
        """
        @brief One existing binding is updated.

        @param name Name of the updated binding.
        @param value New runtime value of the binding.
        """

        resolved_binding = self._resolve(name)
        if resolved_binding.is_parameter:
            raise InterpreterError(
                ErrorCode.SEM_COLLISION,
                f"Parameter {name} cannot be assigned."
            )
        resolved_binding.value = value
        resolved_binding.initialized = True


    def get(self, name: str) -> RuntimeValue | None:
        """
        @brief One binding value is read.

        @param name Name of the requested binding.
        @return Runtime value stored in the resolved binding.
        """

        resolved_binding = self._resolve(name)
        if not resolved_binding.initialized:
            raise InterpreterError(
                ErrorCode.SEM_UNDEF,
                f"Variable {name} is not initialized."
            )
        return resolved_binding.value

    def _resolve(self, name: str) -> BindingRecord:
        if name in self.bindings_by_name:
            return self.bindings_by_name[name]
        if self.parent is not None:
            return self.parent._resolve(name)
        raise InterpreterError(
            ErrorCode.SEM_UNDEF,
            f"Variable {name} is not defined."
        )
