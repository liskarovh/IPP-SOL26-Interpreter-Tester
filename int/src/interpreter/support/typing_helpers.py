"""
@file typing_helpers.py
@brief Shared typing aliases are defined for the interpreter implementation.
DOXYGEN COMMENTS ARE AI GENERATED AND PROOF READ BY ME

Type aliases used across the interpreter are centralized in this module.
Import cycles are reduced by TYPE_CHECKING-based imports.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from interpreter.model.invocation_context import InvocationContext
    from interpreter.model.runtime_methods import RuntimeMethod
    from interpreter.model.values import RuntimeValue

type Selector = str
type ClassName = str
type VariableName = str
type SlotName = str

type RuntimeValueList = list["RuntimeValue"]
type BuiltinMethodKey = tuple[ClassName, Selector]

type MethodTable = dict[Selector, "RuntimeMethod"]
type VariableBindings = dict[VariableName, "RuntimeValue"]
type SlotStorage = dict[SlotName, "RuntimeValue"]

type BuiltinCallback = Callable[
    ["RuntimeValue", RuntimeValueList, "InvocationContext"],
    "RuntimeValue",
]
