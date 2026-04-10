"""
@file builtins_by_values.py
@brief Built-in method callbacks and registration are defined.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
REPETITIVE PARTS OF THIS FILE HAVE BEEN AI GENERATED - CHATGPT CHAT HERE https://chatgpt.com/share/69d2e81e-87d0-838e-afb8-efddf21b5d69

Registration of built-in runtime methods is centralized here.
Concrete built-in behavior is represented through callback functions that are
wrapped into CallbackBuiltinImplementation instances.

This module now serves as the orchestration entry point for built-in
registration and as the home of shared helper utilities reused by
class-specific built-in modules.
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

    Registration is coordinated here, while concrete built-in groups are
    implemented in dedicated modules grouped by built-in classes.

    @param class_registry A registry of runtime classes.
    @param builtin_registry A registry of canonical built-in values and methods.
    @param object_factory A runtime value factory.
    @param runtime_io A runtime input/output service.
    @param send_zero_arg_message A helper sending one zero-argument runtime message.
    @param send_one_arg_message A helper sending one one-argument runtime message.
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
    @brief One instance-side built-in runtime method is created and registered.

    @param owner An owning runtime class.
    @param selector A built-in method selector.
    @param builtin_callback A callback implementing built-in behavior.
    @param builtin_registry A registry receiving the built-in method.
    """
    implementation = InstanceCallbackBuiltinImplementation(builtin_callback)
    method = BuiltinMethod(selector, owner, implementation)

    builtin_registry.register_instance_builtin_method(owner.name, selector, method)
    owner.add_instance_method(method)


def _register_one_class_builtin(
    owner: RuntimeClass,
    selector: str,
    builtin_callback: ClassBuiltinCallback,
    builtin_registry: BuiltinRegistry,
) -> None:
    """
    @brief One class-side built-in runtime method is created and registered.

    @param owner An owning runtime class.
    @param selector A built-in method selector.
    @param builtin_callback A callback implementing built-in behavior.
    @param builtin_registry A registry receiving the built-in method.
    """
    implementation = ClassCallbackBuiltinImplementation(builtin_callback)
    method = BuiltinMethod(selector, owner, implementation)

    builtin_registry.register_class_builtin_method(owner.name, selector, method)
    owner.add_class_method(method)


def _make_return_receiver() -> InstanceBuiltinCallback:
    """
    @brief One callback returning the receiver is created.

    @return One built-in callback returning the receiver unchanged.
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
    @brief One callback returning canonical true is created.

    @param builtin_registry A registry of canonical built-in values.
    @return One built-in callback returning canonical true.
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
    @brief One callback returning canonical false is created.

    @param builtin_registry A registry of canonical built-in values.
    @return One built-in callback returning canonical false.
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

    @param builtin_registry A registry of canonical built-in values.
    @return The canonical true value.
    """
    return builtin_registry.get_true_value()


def _false_value(builtin_registry: BuiltinRegistry) -> BooleanValue:
    """
    @brief The canonical false value is returned.

    @param builtin_registry A registry of canonical built-in values.
    @return The canonical false value.
    """
    return builtin_registry.get_false_value()


def _nil_value(builtin_registry: BuiltinRegistry) -> NilValue:
    """
    @brief The canonical nil value is returned.

    @param builtin_registry A registry of canonical built-in values.
    @return The canonical nil value.
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

    @param target_value One runtime object receiving the message.
    @param selector One selector of the sent message.
    @param ctx One invocation context of the current built-in call.
    @param send_zero_arg_message One injected zero-argument send helper.
    @return One runtime value returned by the sent message.
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

    @param target_value One runtime object receiving the message.
    @param selector One selector of the sent message.
    @param arg_value One runtime argument value.
    @param ctx One invocation context of the current built-in call.
    @param send_one_arg_message One injected one-argument send helper.
    @return One runtime value returned by the sent message.
    """
    return send_one_arg_message(target_value, selector, arg_value, ctx)


def _require_arg_count(args: RuntimeValueList, expected: int, selector: str) -> None:
    """
    @brief The runtime argument count is checked.

    @param args Runtime call arguments.
    @param expected Expected runtime argument count.
    @param selector Selector used by the current built-in method.
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

    @param value One runtime value.
    @param selector Current built-in selector.
    @return The checked block closure.
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

    @param value One runtime value.
    @param selector Current built-in selector.
    @return The checked runtime boolean value.
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

    @param value One runtime value.
    @param selector Current built-in selector.
    @return The checked runtime integer value.
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

    @param value One runtime value.
    @param selector Current built-in selector.
    @return The checked runtime string value.
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
    @param object_factory A runtime value factory.
    @return One runtime string value.
    """
    return object_factory.new_string(value)


def _make_runtime_integer(value: int, object_factory: ObjectFactory) -> IntegerValue:
    """
    @brief One runtime integer value is created.

    @param value Wrapped integer payload.
    @param object_factory A runtime value factory.
    @return One runtime integer value.
    """
    return object_factory.new_integer(value)


def _copy_runtime_slots(source: RuntimeValue, target: RuntimeValue) -> None:
    """
    @brief Regular instance slots are copied with shallow-copy semantics.

    @param source One source runtime value.
    @param target One target runtime value.
    """
    source_slots = source.slots
    if source_slots is None:
        return

    target_slots = target.slots
    if target_slots is None:
        return

    source_slots.copy_into(target_slots)
