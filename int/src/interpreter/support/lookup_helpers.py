"""
@file lookup_helpers.py
@brief Shared send-lookup helpers are defined here.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Helpers shared by the send layer are stored here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from ..model.runtime_class import RuntimeClass
from ..support.send_types import LookupMode
from ..support.typing_helpers import MethodReceiver

if TYPE_CHECKING:
    from ..model.invocation_context import InvocationContext


def resolve_lookup_start_class(
    receiver: MethodReceiver,
    lookup_mode: LookupMode,
    ctx: InvocationContext,
) -> RuntimeClass:
    """
    @brief The starting class for method lookup is resolved.

    @param receiver A method receiver for which lookup is to be started.
    @param lookup_mode One lookup mode of the current send.
    @param ctx One invocation context carrying self/super information.
    @return One runtime class from which method lookup should start.
    """
    if lookup_mode == LookupMode.NORMAL:
        if isinstance(receiver, RuntimeClass):
            return receiver
        return receiver.get_class()

    start_class = ctx.super_start()
    if start_class is None:
        raise InterpreterError(
            ErrorCode.INT_DNU,
            "Super lookup has no starting superclass.",
        )

    return start_class
