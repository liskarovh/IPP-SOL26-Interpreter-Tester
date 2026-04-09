"""
@file typing_helpers.py
@brief Shared typing aliases are defined for the interpreter package.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Only shared aliases needed across multiple interpreter modules are stored
in this file. Forward references are used so that import cycles are avoided.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..model.invocation_context import InvocationContext
    from ..model.runtime_class import RuntimeClass
    from ..model.values import RuntimeValue

type RuntimeValueList = list[RuntimeValue]
type MethodReceiver = RuntimeValue | RuntimeClass
type InstanceBuiltinCallback = Callable[
    ["RuntimeValue", RuntimeValueList, "InvocationContext"],
    "RuntimeValue",
]

type ClassBuiltinCallback = Callable[
    ["RuntimeClass", RuntimeValueList, "InvocationContext"],
    "RuntimeValue",
]
