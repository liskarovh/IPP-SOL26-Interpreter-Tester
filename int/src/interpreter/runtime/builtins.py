"""
@file builtins_by_values.py
@brief Built-in registration orchestration and shared runtime helpers are implemented.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
REPETITIVE PARTS OF THIS FILE HAVE BEEN AI GENERATED - CHATGPT CHAT HERE https://chatgpt.com/share/69d2e81e-87d0-838e-afb8-efddf21b5d69

Built-in registration is coordinated here.
Shared helper utilities reused by class-specific built-in modules are also kept here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from ..model.block_closure import BlockClosure
from ..model.runtime_class import RuntimeClass
from ..model.runtime_methods import BuiltinMethod
from ..model.values import BooleanValue, IntegerValue, NilValue, RuntimeValue, StringValue
from ..support.typing_helpers import SendOneArgMessageCallback, SendZeroArgMessageCallback
from .builtin_implementation import (
    ClassCallbackBuiltinImplementation,
    InstanceCallbackBuiltinImplementation,
)

if TYPE_CHECKING:
    from ..model.invocation_context import InvocationContext
    from ..support.typing_helpers import (
        ClassBuiltinCallback,
        InstanceBuiltinCallback,
        RuntimeValueList,
    )
    from .builtin_registry import BuiltinRegistry
    from .class_registry import ClassRegistry
    from .object_factory import ObjectFactory
    from .runtime_io import RuntimeIO


def register_builtins(
    class_registry: ClassRegistry,
    builtin_registry: BuiltinRegistry,
    object_factory: ObjectFactory,
    runtime_io: RuntimeIO,
    send_zero_arg_message: SendZeroArgMessageCallback,
    send_one_arg_message: SendOneArgMessageCallback,
) -> None:
    """
    @brief Built-in runtime methods are registered.

    This function coordinates registration of built-in groups split by built-in class.

    @param class_registry Registry of runtime classes.
    @param builtin_registry Registry of canonical built-in values and methods.
    @param object_factory Factory used for runtime values.
    @param runtime_io Runtime input/output service.
    @param send_zero_arg_message Injected helper for zero-argument runtime sends.
    @param send_one_arg_message Injected helper for one-argument runtime sends.
    """

    from .builtins_by_values.block_builtins import register_block_builtins
    from .builtins_by_values.boolean_nil_builtins import (
        register_false_builtins,
        register_nil_builtins,
        register_true_builtins,
    )
    from .builtins_by_values.integer_builtins import register_integer_builtins
    from .builtins_by_values.object_builtins import register_object_builtins
    from .builtins_by_values.string_builtins import register_string_builtins

    # all builtin root classes must exist in runtime before registration
    object_class = class_registry.require("Object")
    nil_class = class_registry.require("Nil")
    integer_class = class_registry.require("Integer")
    string_class = class_registry.require("String")
    block_class = class_registry.require("Block")
    true_class = class_registry.require("True")
    false_class = class_registry.require("False")

    register_object_builtins(
        object_class=object_class,
        builtin_registry=builtin_registry,
        object_factory=object_factory,
    )
    register_nil_builtins(
        nil_class=nil_class,
        builtin_registry=builtin_registry,
        object_factory=object_factory,
    )
    register_integer_builtins(
        integer_class=integer_class,
        builtin_registry=builtin_registry,
        object_factory=object_factory,
        send_one_arg_message=send_one_arg_message,
    )
    register_string_builtins(
        string_class=string_class,
        builtin_registry=builtin_registry,
        object_factory=object_factory,
        runtime_io=runtime_io,
    )
    register_block_builtins(
        block_class=block_class,
        builtin_registry=builtin_registry,
        send_zero_arg_message=send_zero_arg_message,
    )
    register_true_builtins(
        true_class=true_class,
        builtin_registry=builtin_registry,
        object_factory=object_factory,
        send_zero_arg_message=send_zero_arg_message,
    )
    register_false_builtins(
        false_class=false_class,
        builtin_registry=builtin_registry,
        object_factory=object_factory,
        send_zero_arg_message=send_zero_arg_message,
    )


def _register_one_instance_builtin(
    owner: RuntimeClass,
    selector: str,
    builtin_callback: InstanceBuiltinCallback,
    builtin_registry: BuiltinRegistry,
) -> None:
    """
    @brief One instance-side built-in method is created and registered.

    @param owner Owning runtime class.
    @param selector Built-in method selector.
    @param builtin_callback Callback implementing built-in behavior.
    @param builtin_registry Registry receiving the built-in method.
    """
    implementation = InstanceCallbackBuiltinImplementation(builtin_callback)
    method = BuiltinMethod(selector, owner, implementation)

    # method is registered globally and attached to owning runtime class
    builtin_registry.register_instance_builtin_method(owner.name, selector, method)
    owner.add_instance_method(method)


def _register_one_class_builtin(
    owner: RuntimeClass,
    selector: str,
    builtin_callback: ClassBuiltinCallback,
    builtin_registry: BuiltinRegistry,
) -> None:
    """
    @brief One class-side built-in method is created and registered.

    @param owner Owning runtime class.
    @param selector Built-in method selector.
    @param builtin_callback Callback implementing built-in behavior.
    @param builtin_registry Registry receiving the built-in method.
    """
    implementation = ClassCallbackBuiltinImplementation(builtin_callback)
    method = BuiltinMethod(selector, owner, implementation)

    builtin_registry.register_class_builtin_method(owner.name, selector, method)
    owner.add_class_method(method)


def _make_return_receiver() -> InstanceBuiltinCallback:
    """
    @brief Callback returning the receiver is created.

    @return Built-in callback returning the receiver unchanged.
    """

    def builtin_return_receiver(
        receiver: RuntimeValue,
        _args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        return receiver

    return builtin_return_receiver


def _make_return_true(builtin_registry: BuiltinRegistry) -> InstanceBuiltinCallback:
    """
    @brief Callback returning canonical true is created.

    @param builtin_registry Registry of canonical built-in values.
    @return Built-in callback returning canonical true.
    """

    def builtin_return_true(
        _receiver: RuntimeValue,
        _args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        return builtin_registry.get_true_value()

    return builtin_return_true


def _make_return_false(builtin_registry: BuiltinRegistry) -> InstanceBuiltinCallback:
    """
    @brief Callback returning canonical false is created.

    @param builtin_registry Registry of canonical built-in values.
    @return Built-in callback returning canonical false.
    """

    def builtin_return_false(
        _receiver: RuntimeValue,
        _args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        return builtin_registry.get_false_value()

    return builtin_return_false


def _true_value(builtin_registry: BuiltinRegistry) -> BooleanValue:
    """
    @brief The canonical true value is returned.

    @param builtin_registry Registry of canonical built-in values.
    @return Canonical true value.
    """
    return builtin_registry.get_true_value()


def _false_value(builtin_registry: BuiltinRegistry) -> BooleanValue:
    """
    @brief The canonical false value is returned.

    @param builtin_registry Registry of canonical built-in values.
    @return Canonical false value.
    """
    return builtin_registry.get_false_value()


def _nil_value(builtin_registry: BuiltinRegistry) -> NilValue:
    """
    @brief The canonical nil value is returned.

    @param builtin_registry Registry of canonical built-in values.
    @return Canonical nil value.
    """
    return builtin_registry.get_nil_value()


def _send_zero_arg_runtime_message(
    target_value: RuntimeValue,
    selector: str,
    ctx: InvocationContext,
    send_zero_arg_message: SendZeroArgMessageCallback,
) -> RuntimeValue:
    """
    @brief One zero-argument runtime message is sent.

    @param target_value Runtime object receiving the message.
    @param selector Selector of the sent message.
    @param ctx Invocation context of the current built-in call.
    @param send_zero_arg_message Injected zero-argument send helper.
    @return Runtime value returned by the sent message.
    """
    return send_zero_arg_message(target_value, selector, ctx)


def _send_one_arg_runtime_message(
    target_value: RuntimeValue,
    selector: str,
    arg_value: RuntimeValue,
    ctx: InvocationContext,
    send_one_arg_message: SendOneArgMessageCallback,
) -> RuntimeValue:
    """
    @brief One one-argument runtime message is sent.

    @param target_value Runtime object receiving the message.
    @param selector Selector of the sent message.
    @param arg_value Runtime argument value.
    @param ctx Invocation context of the current built-in call.
    @param send_one_arg_message Injected one-argument send helper.
    @return Runtime value returned by the sent message.
    """
    return send_one_arg_message(target_value, selector, arg_value, ctx)


def _require_arg_count(args: RuntimeValueList, expected: int, selector: str) -> None:
    """
    @brief The runtime argument count is checked.

    @param args Runtime call arguments.
    @param expected Expected runtime argument count.
    @param selector Selector of the current built-in method.
    """
    actual = len(args)
    if actual != expected:
        raise InterpreterError(
            ErrorCode.INT_OTHER,
            f"Built-in method {selector} expected {expected} arguments, got {actual}.",
        )


def _expect_block_closure(
    value: RuntimeValue,
    selector: str,
) -> BlockClosure:
    """
    @brief One runtime block closure is required.

    @param value Runtime value to check.
    @param selector Current built-in selector.
    @return Checked block closure.
    """
    if isinstance(value, BlockClosure):
        return value

    raise InterpreterError(
        ErrorCode.INT_INVALID_ARG,
        f"Built-in method {selector} expected Block, got {value.get_class().name}.",
    )


def _expect_boolean(value: RuntimeValue, selector: str) -> BooleanValue:
    """
    @brief One runtime boolean value is required.

    @param value Runtime value to check.
    @param selector Current built-in selector.
    @return Checked runtime boolean value.
    """
    if isinstance(value, BooleanValue):
        return value

    raise InterpreterError(
        ErrorCode.INT_INVALID_ARG,
        f"Built-in method {selector} expected Boolean, got {value.get_class().name}.",
    )


def _expect_integer(value: RuntimeValue, selector: str) -> IntegerValue:
    """
    @brief One runtime integer value is required.

    @param value Runtime value to check.
    @param selector Current built-in selector.
    @return Checked runtime integer value.
    """
    if isinstance(value, IntegerValue):
        return value

    raise InterpreterError(
        ErrorCode.INT_INVALID_ARG,
        f"Built-in method {selector} expected Integer, got {value.get_class().name}.",
    )


def _expect_string(value: RuntimeValue, selector: str) -> StringValue:
    """
    @brief One runtime string value is required.

    @param value Runtime value to check.
    @param selector Current built-in selector.
    @return Checked runtime string value.
    """
    if isinstance(value, StringValue):
        return value

    raise InterpreterError(
        ErrorCode.INT_INVALID_ARG,
        f"Built-in method {selector} expected String, got {value.get_class().name}.",
    )


def _make_runtime_string(
    value: str,
    object_factory: ObjectFactory,
) -> StringValue:
    """
    @brief One runtime string value is created.

    @param value Wrapped textual payload.
    @param object_factory Factory used for runtime values.
    @return Runtime string value.
    """
    return object_factory.new_string(value)


def _make_runtime_integer(value: int, object_factory: ObjectFactory) -> IntegerValue:
    """
    @brief One runtime integer value is created.

    @param value Wrapped integer payload.
    @param object_factory Factory used for runtime values.
    @return Runtime integer value.
    """
    return object_factory.new_integer(value)


def _copy_runtime_slots(source: RuntimeValue, target: RuntimeValue) -> None:
    """
    @brief Regular instance slots are copied with shallow-copy semantics.

    @param source Source runtime value.
    @param target Target runtime value.
    """
    source_slots = source.slots
    if source_slots is None:
        return

    target_slots = target.slots
    if target_slots is None:
        return

    source_slots.copy_into(target_slots)
