"""
@file typing_helpers.py
@brief Shared typing aliases for the interpreter package are defined.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Only shared aliases used across multiple interpreter modules are stored here.
Forward references are used to avoid import cycles.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..model.invocation_context import InvocationContext
    from ..model.runtime_class import RuntimeClass
    from ..model.values import RuntimeValue

type RuntimeValueList = list["RuntimeValue"]
type MethodReceiver = "RuntimeValue" | "RuntimeClass"

type InstanceBuiltinCallback = Callable[
    ["RuntimeValue", RuntimeValueList, "InvocationContext"],
    "RuntimeValue",
]

type ClassBuiltinCallback = Callable[
    ["RuntimeClass", RuntimeValueList, "InvocationContext"],
    "RuntimeValue",
]

type SendZeroArgMessageCallback = Callable[
    ["RuntimeValue", str, "InvocationContext"],
    "RuntimeValue",
]

type SendOneArgMessageCallback = Callable[
    ["RuntimeValue", str, "RuntimeValue", "InvocationContext"],
    "RuntimeValue",
]
