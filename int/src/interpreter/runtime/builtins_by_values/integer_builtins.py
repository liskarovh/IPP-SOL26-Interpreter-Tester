"""
@file integer_builtins.py
@brief Integer built-in callbacks and their registration are implemented.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
REPETITIVE PARTS OF THIS FILE HAVE BEEN AI GENERATED - CHATGPT CHAT HERE https://chatgpt.com/share/69d2e81e-87d0-838e-afb8-efddf21b5d69

Integer instance-side built-in methods are grouped in this module.
Shared helpers from runtime.builtins_by_values are reused to keep behavior unchanged.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...error_codes import ErrorCode
from ...exceptions import InterpreterError
from ...model.runtime_class import RuntimeClass
from ...model.values import RuntimeValue
from ..builtins import (
    _expect_integer,
    _false_value,
    _make_return_receiver,
    _make_return_true,
    _make_runtime_integer,
    _make_runtime_string,
    _nil_value,
    _register_one_instance_builtin,
    _require_arg_count,
    _send_one_arg_runtime_message,
    _true_value,
)

if TYPE_CHECKING:
    from ...model.invocation_context import InvocationContext
    from ...support.typing_helpers import (
        InstanceBuiltinCallback,
        RuntimeValueList,
        SendOneArgMessageCallback,
    )
    from ..builtin_registry import BuiltinRegistry
    from ..object_factory import ObjectFactory


def register_integer_builtins(
    integer_class: RuntimeClass,
    builtin_registry: BuiltinRegistry,
    object_factory: ObjectFactory,
    send_one_arg_message: SendOneArgMessageCallback,
) -> None:
    """
    @brief Integer built-ins are registered.

    @param integer_class The runtime class Integer.
    @param builtin_registry A registry of canonical built-in values and methods.
    @param object_factory A runtime value factory.
    @param send_one_arg_message A helper sending one one-argument runtime message.
    """
    return_true = _make_return_true(builtin_registry)
    return_receiver = _make_return_receiver()

    #
    # Integer instance-side methods
    #
    _register_one_instance_builtin(
        owner=integer_class,
        selector="equalTo:",
        builtin_callback=_make_integer_equal_to(builtin_registry),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=integer_class,
        selector="greaterThan:",
        builtin_callback=_make_integer_greater_than(builtin_registry),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=integer_class,
        selector="plus:",
        builtin_callback=_make_integer_plus(object_factory),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=integer_class,
        selector="minus:",
        builtin_callback=_make_integer_minus(object_factory),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=integer_class,
        selector="multiplyBy:",
        builtin_callback=_make_integer_multiply_by(object_factory),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=integer_class,
        selector="divBy:",
        builtin_callback=_make_integer_div_by(object_factory),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=integer_class,
        selector="asString",
        builtin_callback=_make_integer_as_string(object_factory),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=integer_class,
        selector="asInteger",
        builtin_callback=return_receiver,
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=integer_class,
        selector="isNumber",
        builtin_callback=return_true,
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=integer_class,
        selector="timesRepeat:",
        builtin_callback=_make_integer_times_repeat(
            builtin_registry=builtin_registry,
            object_factory=object_factory,
            send_one_arg_message=send_one_arg_message,
        ),
        builtin_registry=builtin_registry,
    )


def _make_integer_equal_to(
    builtin_registry: BuiltinRegistry,
) -> InstanceBuiltinCallback:
    """
    @brief Callback for Integer>>equalTo: is created.

    @param builtin_registry Registry providing canonical boolean values.
    @return Callback implementing Integer>>equalTo:.
    """

    def builtin_integer_equal_to(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 1, "equalTo:")
        left = _expect_integer(receiver, "equalTo:")
        right = _expect_integer(args[0], "equalTo:")

        if left.raw() == right.raw():
            return _true_value(builtin_registry)

        return _false_value(builtin_registry)

    return builtin_integer_equal_to


def _make_integer_greater_than(
    builtin_registry: BuiltinRegistry,
) -> InstanceBuiltinCallback:
    """
    @brief Callback for Integer>>greaterThan: is created.

    @param builtin_registry Registry providing canonical boolean values.
    @return Callback implementing Integer>>greaterThan:.
    """

    def builtin_integer_greater_than(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 1, "greaterThan:")
        left = _expect_integer(receiver, "greaterThan:")
        right = _expect_integer(args[0], "greaterThan:")

        if left.raw() > right.raw():
            return _true_value(builtin_registry)

        return _false_value(builtin_registry)

    return builtin_integer_greater_than


def _make_integer_plus(object_factory: ObjectFactory) -> InstanceBuiltinCallback:
    """
    @brief Callback for Integer>>plus: is created.

    @param object_factory Factory used for runtime values.
    @return Callback implementing Integer>>plus:.
    """

    def builtin_integer_plus(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 1, "plus:")
        left = _expect_integer(receiver, "plus:")
        right = _expect_integer(args[0], "plus:")
        return _make_runtime_integer(left.raw() + right.raw(), object_factory)

    return builtin_integer_plus


def _make_integer_minus(object_factory: ObjectFactory) -> InstanceBuiltinCallback:
    """
    @brief Callback for Integer>>minus: is created.

    @param object_factory Factory used for runtime values.
    @return Callback implementing Integer>>minus:.
    """

    def builtin_integer_minus(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 1, "minus:")
        left = _expect_integer(receiver, "minus:")
        right = _expect_integer(args[0], "minus:")
        return _make_runtime_integer(left.raw() - right.raw(), object_factory)

    return builtin_integer_minus


def _make_integer_multiply_by(
    object_factory: ObjectFactory,
) -> InstanceBuiltinCallback:
    """
    @brief Callback for Integer>>multiplyBy: is created.

    @param object_factory Factory used for runtime values.
    @return Callback implementing Integer>>multiplyBy:.
    """

    def builtin_integer_multiply_by(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 1, "multiplyBy:")
        left = _expect_integer(receiver, "multiplyBy:")
        right = _expect_integer(args[0], "multiplyBy:")
        return _make_runtime_integer(left.raw() * right.raw(), object_factory)

    return builtin_integer_multiply_by


def _make_integer_div_by(object_factory: ObjectFactory) -> InstanceBuiltinCallback:
    """
    @brief Callback for Integer>>divBy: is created.

    @param object_factory Factory used for runtime values.
    @return Callback implementing Integer>>divBy:.
    """

    def builtin_integer_div_by(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 1, "divBy:")
        left = _expect_integer(receiver, "divBy:")
        right = _expect_integer(args[0], "divBy:")

        if right.raw() == 0:
            raise InterpreterError(
                ErrorCode.INT_INVALID_ARG,
                "Division by zero is not allowed.",
            )

        return _make_runtime_integer(left.raw() // right.raw(), object_factory)

    return builtin_integer_div_by


def _make_integer_as_string(object_factory: ObjectFactory) -> InstanceBuiltinCallback:
    """
    @brief Callback for Integer>>asString is created.

    @param object_factory Factory used for runtime values.
    @return Callback implementing Integer>>asString.
    """

    def builtin_integer_as_string(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 0, "asString")
        integer_value = _expect_integer(receiver, "asString")
        return _make_runtime_string(str(integer_value.raw()), object_factory)

    return builtin_integer_as_string


def _make_integer_times_repeat(
    builtin_registry: BuiltinRegistry,
    object_factory: ObjectFactory,
    send_one_arg_message: SendOneArgMessageCallback,
) -> InstanceBuiltinCallback:
    """
    @brief Callback for Integer>>timesRepeat: is created.

    @param builtin_registry Registry providing canonical nil.
    @param object_factory Factory used for runtime values.
    @param send_one_arg_message Injected helper for one-argument runtime sends.
    @return Callback implementing Integer>>timesRepeat:.
    """

    def builtin_integer_times_repeat(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 1, "timesRepeat:")

        integer_receiver = _expect_integer(receiver, "timesRepeat:")
        delayed_value = args[0]
        repeat_count = integer_receiver.raw()

        # negative return nil
        if repeat_count <= 0:
            return _nil_value(builtin_registry)

        last_result: RuntimeValue = _nil_value(builtin_registry)

        for iteration_index in range(1, repeat_count + 1):
            # passes iteration index to the block
            iteration_value = _make_runtime_integer(iteration_index, object_factory)
            current_result = _send_one_arg_runtime_message(
                delayed_value,
                "value:",
                iteration_value,
                ctx,
                send_one_arg_message,
            )
            last_result = current_result

        return last_result

    return builtin_integer_times_repeat
