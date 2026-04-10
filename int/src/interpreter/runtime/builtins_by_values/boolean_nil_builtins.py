"""
@file boolean_nil_builtins.py
@brief Boolean and Nil built-in method callbacks and registration are defined.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
REPETITIVE PARTS OF THIS FILE HAVE BEEN AI GENERATED - CHATGPT CHAT HERE https://chatgpt.com/share/69d2e81e-87d0-838e-afb8-efddf21b5d69

Nil-, True-, and False-related built-in runtime methods are grouped in this
module. Shared helper utilities are intentionally reused from runtime.builtins_by_values
so that the overall behavior remains unchanged.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...model.runtime_class import RuntimeClass
from ...model.values import RuntimeValue
from ..builtins import (
    _expect_boolean,
    _false_value,
    _make_return_true,
    _make_runtime_string,
    _register_one_instance_builtin,
    _require_arg_count,
    _send_zero_arg_runtime_message,
    _true_value,
)

if TYPE_CHECKING:
    from ...model.invocation_context import InvocationContext
    from ...support.typing_helpers import (
        InstanceBuiltinCallback,
        RuntimeValueList,
        SendZeroArgMessageCallback,
    )
    from ..builtin_registry import BuiltinRegistry
    from ..object_factory import ObjectFactory


def register_nil_builtins(
    nil_class: RuntimeClass,
    builtin_registry: BuiltinRegistry,
    object_factory: ObjectFactory,
) -> None:
    """
    @brief Nil built-ins are registered.

    @param nil_class The runtime class Nil.
    @param builtin_registry A registry of canonical built-in values and methods.
    @param object_factory A runtime value factory.
    """
    return_true = _make_return_true(builtin_registry)

    #
    # Nil instance-side methods
    #
    _register_one_instance_builtin(
        owner=nil_class,
        selector="asString",
        builtin_callback=_make_nil_as_string(object_factory),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=nil_class,
        selector="isNil",
        builtin_callback=return_true,
        builtin_registry=builtin_registry,
    )


def register_true_builtins(
    true_class: RuntimeClass,
    builtin_registry: BuiltinRegistry,
    object_factory: ObjectFactory,
    send_zero_arg_message: SendZeroArgMessageCallback,
) -> None:
    """
    @brief True built-ins are registered.

    @param true_class The runtime class True.
    @param builtin_registry A registry of canonical built-in values and methods.
    @param object_factory A runtime value factory.
    @param send_zero_arg_message A helper sending one zero-argument runtime message.
    """
    return_true = _make_return_true(builtin_registry)

    #
    # True instance-side methods
    #
    _register_one_instance_builtin(
        owner=true_class,
        selector="asString",
        builtin_callback=_make_true_as_string(object_factory),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=true_class,
        selector="isBoolean",
        builtin_callback=return_true,
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=true_class,
        selector="not",
        builtin_callback=_make_true_not(builtin_registry),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=true_class,
        selector="and:",
        builtin_callback=_make_boolean_and(
            builtin_registry=builtin_registry,
            send_zero_arg_message=send_zero_arg_message,
        ),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=true_class,
        selector="or:",
        builtin_callback=_make_boolean_or(
            builtin_registry=builtin_registry,
            send_zero_arg_message=send_zero_arg_message,
        ),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=true_class,
        selector="ifTrue:ifFalse:",
        builtin_callback=_make_boolean_if_true_if_false(
            send_zero_arg_message=send_zero_arg_message,
        ),
        builtin_registry=builtin_registry,
    )


def register_false_builtins(
    false_class: RuntimeClass,
    builtin_registry: BuiltinRegistry,
    object_factory: ObjectFactory,
    send_zero_arg_message: SendZeroArgMessageCallback,
) -> None:
    """
    @brief False built-ins are registered.

    @param false_class The runtime class False.
    @param builtin_registry A registry of canonical built-in values and methods.
    @param object_factory A runtime value factory.
    @param send_zero_arg_message A helper sending one zero-argument runtime message.
    """
    return_true = _make_return_true(builtin_registry)

    #
    # False instance-side methods
    #
    _register_one_instance_builtin(
        owner=false_class,
        selector="asString",
        builtin_callback=_make_false_as_string(object_factory),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=false_class,
        selector="isBoolean",
        builtin_callback=return_true,
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=false_class,
        selector="not",
        builtin_callback=_make_false_not(builtin_registry),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=false_class,
        selector="and:",
        builtin_callback=_make_boolean_and(
            builtin_registry=builtin_registry,
            send_zero_arg_message=send_zero_arg_message,
        ),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=false_class,
        selector="or:",
        builtin_callback=_make_boolean_or(
            builtin_registry=builtin_registry,
            send_zero_arg_message=send_zero_arg_message,
        ),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=false_class,
        selector="ifTrue:ifFalse:",
        builtin_callback=_make_boolean_if_true_if_false(
            send_zero_arg_message=send_zero_arg_message,
        ),
        builtin_registry=builtin_registry,
    )


def _make_nil_as_string(object_factory: ObjectFactory) -> InstanceBuiltinCallback:
    """
    @brief One Nil>>asString callback is created.

    @param object_factory A runtime value factory.
    @return One Nil>>asString callback.
    """

    def builtin_nil_as_string(
        _receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 0, "asString")
        return _make_runtime_string("nil", object_factory)

    return builtin_nil_as_string


def _make_true_as_string(object_factory: ObjectFactory) -> InstanceBuiltinCallback:
    """
    @brief One True>>asString callback is created.

    @param object_factory A runtime value factory.
    @return One True>>asString callback.
    """

    def builtin_true_as_string(
        _receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 0, "asString")
        return _make_runtime_string("true", object_factory)

    return builtin_true_as_string


def _make_true_not(builtin_registry: BuiltinRegistry) -> InstanceBuiltinCallback:
    """
    @brief One True>>not callback is created.

    @param builtin_registry A registry of canonical built-in values.
    @return One True>>not callback.
    """

    def builtin_true_not(
        _receiver: RuntimeValue,
        _args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        return _false_value(builtin_registry)

    return builtin_true_not


def _make_boolean_and(
    builtin_registry: BuiltinRegistry,
    send_zero_arg_message: SendZeroArgMessageCallback,
) -> InstanceBuiltinCallback:
    """
    @brief One Boolean>>and: callback is created.

    @param builtin_registry A registry of canonical built-in values.
    @param send_zero_arg_message One injected zero-argument send helper.
    @return One Boolean>>and: callback.
    """

    def builtin_boolean_and(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 1, "and:")

        boolean_receiver = _expect_boolean(receiver, "and:")
        delayed_value = args[0]

        if not boolean_receiver.raw():
            return _false_value(builtin_registry)

        return _send_zero_arg_runtime_message(
            target_value=delayed_value,
            selector="value",
            ctx=ctx,
            send_zero_arg_message=send_zero_arg_message,
        )

    return builtin_boolean_and


def _make_boolean_or(
    builtin_registry: BuiltinRegistry,
    send_zero_arg_message: SendZeroArgMessageCallback,
) -> InstanceBuiltinCallback:
    """
    @brief One Boolean>>or: callback is created.

    @param builtin_registry A registry of canonical built-in values.
    @param send_zero_arg_message One injected zero-argument send helper.
    @return One Boolean>>or: callback.
    """

    def builtin_boolean_or(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 1, "or:")

        boolean_receiver = _expect_boolean(receiver, "or:")
        delayed_value = args[0]

        if boolean_receiver.raw():
            return _true_value(builtin_registry)

        return _send_zero_arg_runtime_message(
            target_value=delayed_value,
            selector="value",
            ctx=ctx,
            send_zero_arg_message=send_zero_arg_message,
        )

    return builtin_boolean_or


def _make_boolean_if_true_if_false(
    send_zero_arg_message: SendZeroArgMessageCallback,
) -> InstanceBuiltinCallback:
    """
    @brief One Boolean>>ifTrue:ifFalse: callback is created.

    @param send_zero_arg_message One injected zero-argument send helper.
    @return One Boolean>>ifTrue:ifFalse: callback.
    """

    def builtin_boolean_if_true_if_false(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 2, "ifTrue:ifFalse:")

        boolean_receiver = _expect_boolean(receiver, "ifTrue:ifFalse:")
        true_branch = args[0]
        false_branch = args[1]

        selected_branch = false_branch
        if boolean_receiver.raw():
            selected_branch = true_branch

        return _send_zero_arg_runtime_message(
            target_value=selected_branch,
            selector="value",
            ctx=ctx,
            send_zero_arg_message=send_zero_arg_message,
        )

    return builtin_boolean_if_true_if_false


def _make_false_as_string(object_factory: ObjectFactory) -> InstanceBuiltinCallback:
    """
    @brief One False>>asString callback is created.

    @param object_factory A runtime value factory.
    @return One False>>asString callback.
    """

    def builtin_false_as_string(
        _receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 0, "asString")
        return _make_runtime_string("false", object_factory)

    return builtin_false_as_string


def _make_false_not(builtin_registry: BuiltinRegistry) -> InstanceBuiltinCallback:
    """
    @brief One False>>not callback is created.

    @param builtin_registry A registry of canonical built-in values.
    @return One False>>not callback.
    """

    def builtin_false_not(
        _receiver: RuntimeValue,
        _args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        return _true_value(builtin_registry)

    return builtin_false_not
