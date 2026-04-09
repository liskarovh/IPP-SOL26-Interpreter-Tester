"""
@file builtins.py
@brief Built-in method callbacks and registration are defined.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
REPETITIVE PARTS OF THIS FILE HAVE BEEN AI GENERATED - CHATGPT CHAT HERE https://chatgpt.com/share/69d2e81e-87d0-838e-afb8-efddf21b5d69

Registration of built-in runtime methods is centralized here.
Concrete built-in behavior is represented through callback functions that are
wrapped into CallbackBuiltinImplementation instances.
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

    @param class_registry A registry of runtime classes.
    @param builtin_registry A registry of canonical built-in values and methods.
    @param object_factory A runtime value factory.
    @param runtime_io A runtime input/output service.
    @param send_zero_arg_message A helper sending one zero-argument runtime message.
    @param send_one_arg_message A helper sending one one-argument runtime message.
    """
    object_class = class_registry.require("Object")
    nil_class = class_registry.require("Nil")
    integer_class = class_registry.require("Integer")
    string_class = class_registry.require("String")
    block_class = class_registry.require("Block")
    true_class = class_registry.require("True")
    false_class = class_registry.require("False")

    _register_object_builtins(
        object_class=object_class,
        builtin_registry=builtin_registry,
        object_factory=object_factory,
    )
    _register_nil_builtins(
        nil_class=nil_class,
        builtin_registry=builtin_registry,
        object_factory=object_factory,
    )
    _register_integer_builtins(
        integer_class=integer_class,
        builtin_registry=builtin_registry,
        object_factory=object_factory,
        send_one_arg_message=send_one_arg_message,
    )
    _register_string_builtins(
        string_class=string_class,
        builtin_registry=builtin_registry,
        object_factory=object_factory,
        runtime_io=runtime_io,
    )
    _register_block_builtins(
        block_class=block_class,
        builtin_registry=builtin_registry,
        send_zero_arg_message=send_zero_arg_message,
    )
    _register_true_builtins(
        true_class=true_class,
        builtin_registry=builtin_registry,
        object_factory=object_factory,
        send_zero_arg_message=send_zero_arg_message,
    )
    _register_false_builtins(
        false_class=false_class,
        builtin_registry=builtin_registry,
        object_factory=object_factory,
        send_zero_arg_message=send_zero_arg_message,
    )


def _register_object_builtins(
    object_class: RuntimeClass,
    builtin_registry: BuiltinRegistry,
    object_factory: ObjectFactory,
) -> None:
    """
    @brief Object built-ins are registered.

    @param object_class The runtime class Object.
    @param builtin_registry A registry of canonical built-in values and methods.
    @param object_factory A runtime value factory.
    """
    return_false = _make_return_false(builtin_registry)

    #
    # Object instance-side methods
    #
    _register_one_instance_builtin(
        owner=object_class,
        selector="identicalTo:",
        builtin_callback=_make_object_identical_to(builtin_registry),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=object_class,
        selector="equalTo:",
        builtin_callback=_make_object_equal_to(builtin_registry),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=object_class,
        selector="asString",
        builtin_callback=_make_object_as_string(object_factory),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=object_class,
        selector="isNumber",
        builtin_callback=return_false,
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=object_class,
        selector="isString",
        builtin_callback=return_false,
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=object_class,
        selector="isBlock",
        builtin_callback=return_false,
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=object_class,
        selector="isNil",
        builtin_callback=return_false,
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=object_class,
        selector="isBoolean",
        builtin_callback=return_false,
        builtin_registry=builtin_registry,
    )

    #
    # Object class-side methods
    #
    _register_one_class_builtin(
        owner=object_class,
        selector="new",
        builtin_callback=_make_object_new(builtin_registry, object_factory),
        builtin_registry=builtin_registry,
    )
    _register_one_class_builtin(
        owner=object_class,
        selector="from:",
        builtin_callback=_make_object_from(builtin_registry, object_factory),
        builtin_registry=builtin_registry,
    )


def _register_nil_builtins(
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


def _register_integer_builtins(
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


def _register_string_builtins(
    string_class: RuntimeClass,
    builtin_registry: BuiltinRegistry,
    object_factory: ObjectFactory,
    runtime_io: RuntimeIO,
) -> None:
    """
    @brief String built-ins are registered.

    @param string_class The runtime class String.
    @param builtin_registry A registry of canonical built-in values and methods.
    @param object_factory A runtime value factory.
    @param runtime_io A runtime input/output service.
    """
    return_true = _make_return_true(builtin_registry)
    return_receiver = _make_return_receiver()

    #
    # String instance-side methods
    #
    _register_one_instance_builtin(
        owner=string_class,
        selector="print",
        builtin_callback=_make_string_print(runtime_io),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=string_class,
        selector="equalTo:",
        builtin_callback=_make_string_equal_to(builtin_registry),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=string_class,
        selector="asString",
        builtin_callback=return_receiver,
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=string_class,
        selector="asInteger",
        builtin_callback=_make_string_as_integer(builtin_registry, object_factory),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=string_class,
        selector="isString",
        builtin_callback=return_true,
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=string_class,
        selector="concatenateWith:",
        builtin_callback=_make_string_concatenate_with(builtin_registry, object_factory),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=string_class,
        selector="startsWith:endsBefore:",
        builtin_callback=_make_string_starts_with_ends_before(builtin_registry, object_factory),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=string_class,
        selector="length",
        builtin_callback=_make_string_length(object_factory),
        builtin_registry=builtin_registry,
    )

    #
    # String class-side methods
    #
    _register_one_class_builtin(
        owner=string_class,
        selector="read",
        builtin_callback=_make_string_read(object_factory, runtime_io),
        builtin_registry=builtin_registry,
    )


def _register_block_builtins(
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
    _register_one_instance_builtin(
        owner=block_class,
        selector="whileTrue:",
        builtin_callback=_make_block_while_true(
            builtin_registry=builtin_registry,
            send_zero_arg_message=send_zero_arg_message,
        ),
        builtin_registry=builtin_registry,
    )


def _register_true_builtins(
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


def _register_false_builtins(
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


def _make_object_identical_to(
    builtin_registry: BuiltinRegistry,
) -> InstanceBuiltinCallback:
    """
    @brief One Object>>identicalTo: callback is created.

    @param builtin_registry A registry of canonical built-in values.
    @return One Object>>identicalTo: callback.
    """

    def builtin_object_identical_to(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 1, "identicalTo:")
        other = args[0]

        if receiver is other:
            return _true_value(builtin_registry)

        return _false_value(builtin_registry)

    return builtin_object_identical_to


def _make_object_equal_to(builtin_registry: BuiltinRegistry) -> InstanceBuiltinCallback:
    """
    @brief One Object>>equalTo: callback is created.

    @param builtin_registry A registry of canonical built-in values.
    @return One Object>>equalTo: callback.
    """

    def builtin_object_equal_to(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 1, "equalTo:")
        other = args[0]

        if type(receiver) is not type(other):
            return _false_value(builtin_registry)

        if isinstance(receiver, (IntegerValue, StringValue, BooleanValue)) and isinstance(
            other,
            (IntegerValue, StringValue, BooleanValue),
        ):
            if receiver.raw() == other.raw():
                return _true_value(builtin_registry)

            return _false_value(builtin_registry)

        if receiver is other:
            return _true_value(builtin_registry)

        return _false_value(builtin_registry)

    return builtin_object_equal_to


def _make_object_as_string(object_factory: ObjectFactory) -> InstanceBuiltinCallback:
    """
    @brief One Object>>asString callback is created.

    @param object_factory A runtime value factory.
    @return One Object>>asString callback.
    """

    def builtin_object_as_string(
        _receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 0, "asString")
        return _make_runtime_string("", object_factory)

    return builtin_object_as_string


def _make_object_new(
    builtin_registry: BuiltinRegistry,
    object_factory: ObjectFactory,
) -> ClassBuiltinCallback:
    """
    @brief One Object class-side >>new callback is created.

    @param builtin_registry A registry of canonical built-in values.
    @param object_factory A runtime value factory.
    @return One Object class-side >>new callback.
    """

    def builtin_object_new(
        receiver: RuntimeClass,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 0, "new")
        target_class = receiver

        if target_class.name == "Nil":
            return _nil_value(builtin_registry)

        if target_class.inherits_from_name("Integer"):
            return object_factory.new_integer(0, target_class)

        if target_class.inherits_from_name("String"):
            return object_factory.new_string("", target_class)

        if target_class.name == "True":
            return _true_value(builtin_registry)

        if target_class.name == "False":
            return _false_value(builtin_registry)

        if target_class.name == "Block":
            return object_factory.new_empty_block_closure()

        return object_factory.new_user_object(target_class)

    return builtin_object_new


def _make_object_from(
    builtin_registry: BuiltinRegistry,
    object_factory: ObjectFactory,
) -> ClassBuiltinCallback:
    """
    @brief One Object class-side >>from: callback is created.

    @param builtin_registry A registry of canonical built-in values.
    @param object_factory A runtime value factory.
    @return One Object class-side >>from: callback.
    """

    def builtin_object_from(
        receiver: RuntimeClass,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 1, "from:")
        source = args[0]
        target_class = receiver

        if target_class.name == "Nil":
            return _nil_value(builtin_registry)

        if target_class.inherits_from_name("Integer"):
            source_integer = _expect_integer(source, "from:")
            new_integer = object_factory.new_integer(source_integer.raw(), target_class)
            _copy_runtime_slots(source_integer, new_integer)
            return new_integer

        if target_class.inherits_from_name("String"):
            source_string = _expect_string(source, "from:")
            new_string = object_factory.new_string(source_string.raw(), target_class)
            _copy_runtime_slots(source_string, new_string)
            return new_string

        if target_class.name == "True":
            if isinstance(source, BooleanValue) and source.raw() is True:
                return _true_value(builtin_registry)
            raise InterpreterError(
                ErrorCode.INT_INVALID_ARG,
                "True from: requires a true boolean payload.",
            )

        if target_class.name == "False":
            if isinstance(source, BooleanValue) and source.raw() is False:
                return _false_value(builtin_registry)
            raise InterpreterError(
                ErrorCode.INT_INVALID_ARG,
                "False from: requires a false boolean payload.",
            )

        if target_class.name == "Block":
            source_block = _expect_block_closure(source, "from:")
            return object_factory.copy_block_closure(source_block)

        new_object = object_factory.new_user_object(target_class)

        _copy_runtime_slots(source, new_object)

        return new_object

    return builtin_object_from


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


def _make_integer_equal_to(
    builtin_registry: BuiltinRegistry,
) -> InstanceBuiltinCallback:
    """
    @brief One Integer>>equalTo: callback is created.

    @param builtin_registry A registry of canonical built-in values.
    @return One Integer>>equalTo: callback.
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
    @brief One Integer>>greaterThan: callback is created.

    @param builtin_registry A registry of canonical built-in values.
    @return One Integer>>greaterThan: callback.
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
    @brief One Integer>>plus: callback is created.

    @param object_factory A runtime value factory.
    @return One Integer>>plus: callback.
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
    @brief One Integer>>minus: callback is created.

    @param object_factory A runtime value factory.
    @return One Integer>>minus: callback.
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


def _make_integer_multiply_by(object_factory: ObjectFactory) -> InstanceBuiltinCallback:
    """
    @brief One Integer>>multiplyBy: callback is created.

    @param object_factory A runtime value factory.
    @return One Integer>>multiplyBy: callback.
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
    @brief One Integer>>divBy: callback is created.

    @param object_factory A runtime value factory.
    @return One Integer>>divBy: callback.
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
    @brief One Integer>>asString callback is created.

    @param object_factory A runtime value factory.
    @return One Integer>>asString callback.
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
    @brief One Integer>>timesRepeat: callback is created.

    @param builtin_registry A registry of canonical built-in values.
    @param object_factory A runtime value factory.
    @param send_one_arg_message One injected one-argument send helper.
    @return One Integer>>timesRepeat: callback.
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

        if repeat_count <= 0:
            return _nil_value(builtin_registry)

        last_result: RuntimeValue = _nil_value(builtin_registry)

        for iteration_index in range(1, repeat_count + 1):
            iteration_value = _make_runtime_integer(iteration_index, object_factory)
            current_result: RuntimeValue = _send_one_arg_runtime_message(
                delayed_value,
                "value:",
                iteration_value,
                ctx,
                send_one_arg_message,
            )
            last_result = current_result

        return last_result

    return builtin_integer_times_repeat


def _make_string_print(runtime_io: RuntimeIO) -> InstanceBuiltinCallback:
    """
    @brief One String>>print callback is created.

    @param runtime_io A runtime input/output service.
    @return One String>>print callback.
    """

    def builtin_string_print(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 0, "print")
        string_value = _expect_string(receiver, "print")
        runtime_io.write(string_value.raw())
        return receiver

    return builtin_string_print


def _make_string_equal_to(
    builtin_registry: BuiltinRegistry,
) -> InstanceBuiltinCallback:
    """
    @brief One String>>equalTo: callback is created.

    @param builtin_registry A registry of canonical built-in values.
    @return One String>>equalTo: callback.
    """

    def builtin_string_equal_to(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 1, "equalTo:")
        left = _expect_string(receiver, "equalTo:")
        right = args[0]

        if not isinstance(right, StringValue):
            return _false_value(builtin_registry)

        if left.raw() == right.raw():
            return _true_value(builtin_registry)

        return _false_value(builtin_registry)

    return builtin_string_equal_to


def _make_string_as_integer(
    builtin_registry: BuiltinRegistry, object_factory: ObjectFactory
) -> InstanceBuiltinCallback:
    """
    @brief One String>>asInteger callback is created.

    @param builtin_registry A registry of canonical built-in values.
    @param object_factory A runtime value factory.
    @return One String>>asInteger callback.
    """

    def builtin_string_as_integer(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 0, "asInteger")
        string_value = _expect_string(receiver, "asInteger")
        text = string_value.raw()

        try:
            parsed_value = int(text)
        except ValueError:
            return _nil_value(builtin_registry)

        return _make_runtime_integer(parsed_value, object_factory)

    return builtin_string_as_integer


def _make_string_concatenate_with(
    builtin_registry: BuiltinRegistry, object_factory: ObjectFactory
) -> InstanceBuiltinCallback:
    """
    @brief One String>>concatenateWith: callback is created.

    @param builtin_registry A registry of canonical built-in values.
    @param object_factory A runtime value factory.
    @return One String>>concatenateWith: callback.
    """

    def builtin_string_concatenate_with(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 1, "concatenateWith:")
        left = _expect_string(receiver, "concatenateWith:")
        right = args[0]

        if not isinstance(right, StringValue):
            return _nil_value(builtin_registry)

        return _make_runtime_string(left.raw() + right.raw(), object_factory)

    return builtin_string_concatenate_with


def _make_string_starts_with_ends_before(
    builtin_registry: BuiltinRegistry, object_factory: ObjectFactory
) -> InstanceBuiltinCallback:
    """
    @brief One String>>startsWith:endsBefore: callback is created.

    @param builtin_registry A registry of canonical built-in values.
    @param object_factory A runtime value factory.
    @return One String>>startsWith:endsBefore: callback.
    """

    def builtin_string_starts_with_ends_before(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 2, "startsWith:endsBefore:")
        string_value = _expect_string(receiver, "startsWith:endsBefore:")
        start_value = args[0]
        end_value = args[1]

        if not isinstance(start_value, IntegerValue):
            return _nil_value(builtin_registry)
        if not isinstance(end_value, IntegerValue):
            return _nil_value(builtin_registry)

        start_index = start_value.raw()
        end_index = end_value.raw()
        text = string_value.raw()

        if start_index <= 0 or end_index <= 0:
            return _nil_value(builtin_registry)

        slice_start = start_index - 1
        slice_end = min(end_index - 1, len(text))

        if slice_end - slice_start <= 0:
            return _make_runtime_string("", object_factory)

        sliced_text = text[slice_start:slice_end]
        return _make_runtime_string(sliced_text, object_factory)

    return builtin_string_starts_with_ends_before


def _make_string_length(object_factory: ObjectFactory) -> InstanceBuiltinCallback:
    """
    @brief One String>>length callback is created.

    @param object_factory A runtime value factory.
    @return One String>>length callback.
    """

    def builtin_string_length(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 0, "length")
        string_value = _expect_string(receiver, "length")
        return _make_runtime_integer(len(string_value.raw()), object_factory)

    return builtin_string_length


def _make_string_read(
    object_factory: ObjectFactory, runtime_io: RuntimeIO
) -> ClassBuiltinCallback:
    """
    @brief One String class-side >>read callback is created.

    @param object_factory A runtime value factory.
    @param runtime_io A runtime input/output service.
    @return One String class-side >>read callback.
    """

    def builtin_string_read(
        receiver: RuntimeClass,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 0, "read")
        read_text = runtime_io.read_line()
        normalized_text = read_text.removesuffix("\n")
        return object_factory.new_string(normalized_text, receiver)

    return builtin_string_read


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

        condition_target = receiver
        body_target = args[0]
        last_result: RuntimeValue = _nil_value(builtin_registry)

        while True:
            condition_value = _send_zero_arg_runtime_message(
                target_value=condition_target,
                selector="value",
                ctx=ctx,
                send_zero_arg_message=send_zero_arg_message,
            )
            condition_boolean = _expect_boolean(
                condition_value,
                "whileTrue:",
            )

            if not condition_boolean.raw():
                return last_result

            last_result = _send_zero_arg_runtime_message(
                target_value=body_target,
                selector="value",
                ctx=ctx,
                send_zero_arg_message=send_zero_arg_message,
            )

    return builtin_block_while_true


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
