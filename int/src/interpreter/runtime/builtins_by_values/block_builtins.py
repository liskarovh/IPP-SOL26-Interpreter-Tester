"""
@file block_builtins.py
@brief Block built-in method callbacks and registration are implemented.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
REPETITIVE PARTS OF THIS FILE HAVE BEEN AI GENERATED - CHATGPT CHAT HERE https://chatgpt.com/share/69d2e81e-87d0-838e-afb8-efddf21b5d69

Block-related built-in runtime methods are grouped in this module.
Shared helper utilities from runtime.builtins are reused here
so the existing behavior stays unchanged.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...model.runtime_class import RuntimeClass
from ...model.values import RuntimeValue
from ..builtins import (
    _expect_boolean,
    _make_return_true,
    _nil_value,
    _register_one_instance_builtin,
    _require_arg_count,
    _send_zero_arg_runtime_message,
)

if TYPE_CHECKING:
    from ...model.invocation_context import InvocationContext
    from ...support.typing_helpers import (
        InstanceBuiltinCallback,
        RuntimeValueList,
        SendZeroArgMessageCallback,
    )
    from ..builtin_registry import BuiltinRegistry


def register_block_builtins(
    block_class: RuntimeClass,
    builtin_registry: BuiltinRegistry,
    send_zero_arg_message: SendZeroArgMessageCallback,
) -> None:
    """
    @brief Block built-ins are registered.

    @param block_class The runtime class Block.
    @param builtin_registry A registry of canonical built-in values and methods.
    @param send_zero_arg_message A helper sending one zero-argument runtime message.
    """
    return_true = _make_return_true(builtin_registry)

    #
    # Block instance-side methods
    #
    _register_one_instance_builtin(
        owner=block_class,
        selector="isBlock",
        builtin_callback=return_true,
        builtin_registry=builtin_registry,
    )

    # whileTrue: is built from runtime send helpers
    _register_one_instance_builtin(
        owner=block_class,
        selector="whileTrue:",
        builtin_callback=_make_block_while_true(
            builtin_registry=builtin_registry,
            send_zero_arg_message=send_zero_arg_message,
        ),
        builtin_registry=builtin_registry,
    )


def _make_block_while_true(
    builtin_registry: BuiltinRegistry,
    send_zero_arg_message: SendZeroArgMessageCallback,
) -> InstanceBuiltinCallback:
    """
    @brief One Block>>whileTrue: callback is created.

    @param builtin_registry A registry of canonical built-in values.
    @param send_zero_arg_message One injected zero-argument send helper.
    @return One Block>>whileTrue: callback.
    """

    def builtin_block_while_true(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 1, "whileTrue:")

        # receiver is condition block, first argument is loop body block
        condition_target = receiver
        body_target = args[0]

        # SOL26 whileTrue: returns nil when body never runs
        last_result: RuntimeValue = _nil_value(builtin_registry)

        while True:
            condition_value = _send_zero_arg_runtime_message(
                target_value=condition_target,
                selector="value",
                ctx=ctx,
                send_zero_arg_message=send_zero_arg_message,
            )

            # whileTrue: requires the condition result to be a boolean
            condition_boolean = _expect_boolean(
                condition_value,
                "whileTrue:",
            )

            if not condition_boolean.raw():
                return last_result

            # result is always the last body evaluation result
            last_result = _send_zero_arg_runtime_message(
                target_value=body_target,
                selector="value",
                ctx=ctx,
                send_zero_arg_message=send_zero_arg_message,
            )

    return builtin_block_while_true
