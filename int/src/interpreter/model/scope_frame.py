"""
@file scope_frame.py
@brief Lexical scope frames are implemented.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Lexical scope frames store variable bindings with metadata
and support lexical parent chaining during execution.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from .binding_record import BindingRecord

if TYPE_CHECKING:
    from ..input_model import Parameter
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

        # each frame owns its local bindings
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

        # binding lookup upward
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

    def assign_or_define(self, name: str, value: RuntimeValue) -> None:
        """
        @brief One binding is updated or newly defined.

        @param name Name of the assigned binding.
        @param value Runtime value to be stored.
        """

        # update
        if self.contains(name):
            self.set(name, value)
        # create
        else:
            self.define(name, value)

    def set(self, name: str, value: RuntimeValue) -> None:
        """
        @brief One existing binding is updated.

        @param name Name of the updated binding.
        @param value New runtime value of the binding.
        """

        resolved_binding = self._resolve(name)
        if resolved_binding.is_parameter:
            raise InterpreterError(
                ErrorCode.SEM_COLLISION, f"Parameter {name} cannot be assigned."
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
            raise InterpreterError(ErrorCode.SEM_UNDEF, f"Variable {name} is not initialized.")
        return resolved_binding.value

    def define_parameter(self, name: str, value: RuntimeValue) -> None:
        """
        @brief One parameter binding is defined in the current frame.

        @param name Name of the parameter binding.
        @param value Runtime value bound to the parameter.
        """
        self.bindings_by_name[name] = BindingRecord(value, True, True)

    def bind_method_parameters(
        self,
        parameters: list[Parameter],
        args: list[RuntimeValue],
    ) -> None:
        """
        @brief Method parameters are bound into the current frame.

        @param parameters Declared AST parameters of the method block.
        @param args Actual runtime arguments of the method call.
        """
        self._bind_parameters(parameters, args, False)

    def bind_block_parameters(
        self,
        parameters: list[Parameter],
        args: list[RuntimeValue],
    ) -> None:
        """
        @brief Block parameters are bound into the current frame.

        @param parameters Declared AST parameters of the block.
        @param args Actual runtime arguments of the block call.
        """
        self._bind_parameters(parameters, args, True)

    def _resolve(self, name: str) -> BindingRecord:
        """
        @brief One binding record is resolved through the lexical chain.

        @param name Name of the requested binding.
        @return Resolved binding record.
        @throws InterpreterError If the binding does not exist in the lexical chain.
        """

        # local binding wins over parent
        if name in self.bindings_by_name:
            return self.bindings_by_name[name]

        # binding lookup upward
        if self.parent is not None:
            return self.parent._resolve(name)
        raise InterpreterError(ErrorCode.SEM_UNDEF, f"Variable {name} is not defined.")

    def _bind_parameters(
        self,
        parameters: list[Parameter],
        args: list[RuntimeValue],
        bind_as_parameters: bool,
    ) -> None:
        """
        @brief Runtime arguments are bound to declared parameters.

        This helper is shared by method calls and block calls.
        The difference is whether created bindings should carry
        parameter metadata.

        @param parameters Declared AST parameters.
        @param args Actual runtime arguments.
        @param bind_as_parameters True when bound names should be marked
                                  as parameter bindings.
        """
        parameter_count = len(parameters)
        index = 0

        while index < parameter_count:
            parameter = parameters[index]
            argument_value = args[index]

            # block calls and method calls differ in binding metadata
            if bind_as_parameters:
                self.define_parameter(parameter.name, argument_value)
            else:
                self.define(parameter.name, argument_value)

            index += 1
