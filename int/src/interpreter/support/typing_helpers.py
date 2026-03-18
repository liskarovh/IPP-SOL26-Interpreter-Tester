from typing import TYPE_CHECKING, TypeAlias
from collections.abc import Callable

if TYPE_CHECKING:
    from interpreter.model.invocation_context import InvocationContext
    from interpreter.model.runtime_methods import RuntimeMethod
    from interpreter.model.values import RuntimeValue


Selector: TypeAlias = str
ClassName: TypeAlias = str
VariableName: TypeAlias = str
SlotName: TypeAlias = str


RuntimeValueList: TypeAlias = list["RuntimeValue"]
BuiltinMethodKey: TypeAlias = tuple[ClassName, Selector]

MethodTable: TypeAlias = dict[Selector, "RuntimeMethod"]
VariableBindings: TypeAlias = dict[VariableName, "RuntimeValue"]
SlotStorage: TypeAlias = dict[SlotName, "RuntimeValue"]


BuiltinCallback: TypeAlias = Callable[
    ["RuntimeValue", RuntimeValueList, "InvocationContext"],
    "RuntimeValue",
]
