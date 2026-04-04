"""
@file builtins.py
@brief Built-in method callbacks and registration are defined.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Registration of built-in runtime methods is centralized here.
Concrete built-in behavior is represented through callback functions that are
wrapped into CallbackBuiltinImplementation instances.

FUTURE ADJUSTMENTS:
- This module intentionally contains both already implementable runtime-only
  builtins and placeholders for builtins that still depend on the future
  execution layer.
- Block-related builtins cannot be considered final until BlockExecutor,
  MethodExecutor, ExpressionDispatcher, SendExprEvaluator, ScopeFrame, and
  InvocationContext are fully implemented and wired together.
- The SOL26 language defines the Block family value:...: for general block
  arity. The current runtime registry stores builtins under explicit selector
  strings, so support for arbitrary-arity selectors must be extended later
  together with the final execution and dispatch design.
- Lazy boolean builtins (and:, or:, ifTrue:ifFalse:) must stay aligned with
  the final execution semantics so that blocks are evaluated only when the
  language specification requires it.
- Integer>>timesRepeat: and Block>>whileTrue: must be revisited once block
  execution is final, because their behavior depends on real block invocation.
- Block class-side >>new and Block class-side >>from: must also be revisited
  once the final representation of runtime blocks is settled.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from ..model.runtime_class import RuntimeClass
from ..model.runtime_methods import BuiltinMethod
from ..model.user_object import UserObject
from ..model.values import BooleanValue, IntegerValue, NilValue, RuntimeValue, StringValue
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
) -> None:
    """
    @brief Built-in runtime methods are registered.

    @param class_registry A registry of runtime classes.
    @param builtin_registry A registry of canonical built-in values and methods.
    @param object_factory A runtime value factory.
    @param runtime_io A runtime input/output service.
    """
    object_class = class_registry.require("Object")
    nil_class = class_registry.require("Nil")
    integer_class = class_registry.require("Integer")
    string_class = class_registry.require("String")
    block_class = class_registry.require("Block")
    true_class = class_registry.require("True")
    false_class = class_registry.require("False")

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
        builtin_callback=_make_return_false(builtin_registry),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=object_class,
        selector="isString",
        builtin_callback=_make_return_false(builtin_registry),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=object_class,
        selector="isBlock",
        builtin_callback=_make_return_false(builtin_registry),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=object_class,
        selector="isNil",
        builtin_callback=_make_return_false(builtin_registry),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=object_class,
        selector="isBoolean",
        builtin_callback=_make_return_false(builtin_registry),
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
        builtin_callback=_make_return_true(builtin_registry),
        builtin_registry=builtin_registry,
    )

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
        builtin_callback=_make_return_receiver(),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=integer_class,
        selector="isNumber",
        builtin_callback=_make_return_true(builtin_registry),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=integer_class,
        selector="timesRepeat:",
        builtin_callback=_make_integer_times_repeat_deferred(),
        builtin_registry=builtin_registry,
    )

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
        builtin_callback=_make_return_receiver(),
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
        builtin_callback=_make_return_true(builtin_registry),
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

    #
    # Block class-side methods
    #
    _register_one_class_builtin(
        owner=block_class,
        selector="new",
        builtin_callback=_make_block_new_deferred(),
        builtin_registry=builtin_registry,
    )

    #
    # Block instance-side methods
    #
    _register_one_instance_builtin(
        owner=block_class,
        selector="isBlock",
        builtin_callback=_make_return_true(builtin_registry),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=block_class,
        selector="value",
        builtin_callback=_make_block_value_deferred(),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=block_class,
        selector="value:",
        builtin_callback=_make_block_value_deferred(),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=block_class,
        selector="value:value:",
        builtin_callback=_make_block_value_deferred(),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=block_class,
        selector="whileTrue:",
        builtin_callback=_make_block_while_true_deferred(),
        builtin_registry=builtin_registry,
    )

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
        builtin_callback=_make_return_true(builtin_registry),
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
        builtin_callback=_make_true_and_deferred(),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=true_class,
        selector="or:",
        builtin_callback=_make_true_or_deferred(),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=true_class,
        selector="ifTrue:ifFalse:",
        builtin_callback=_make_true_if_true_if_false_deferred(),
        builtin_registry=builtin_registry,
    )

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
        builtin_callback=_make_return_true(builtin_registry),
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
        builtin_callback=_make_false_and_deferred(),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=false_class,
        selector="or:",
        builtin_callback=_make_false_or_deferred(),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=false_class,
        selector="ifTrue:ifFalse:",
        builtin_callback=_make_false_if_true_if_false_deferred(),
        builtin_registry=builtin_registry,
    )

    #
    # FUTURE ADJUSTMENT:
    # The SOL26 language defines the Block>>value:...: family for general block
    # arity. The current runtime registry stores explicit selector strings, so
    # support for arbitrary-arity selectors must be extended later together
    # with the final execution and dispatch design.
    #


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


def _make_return_true(
        builtin_registry: BuiltinRegistry
) -> InstanceBuiltinCallback:
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


def _make_return_false(
        builtin_registry: BuiltinRegistry
) -> InstanceBuiltinCallback:
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


def _true_value(
        builtin_registry: BuiltinRegistry
) -> BooleanValue:
    """
    @brief The canonical true value is returned.

    @param builtin_registry A registry of canonical built-in values.
    @return The canonical true value.
    """
    return builtin_registry.get_true_value()


def _false_value(
        builtin_registry: BuiltinRegistry
) -> BooleanValue:
    """
    @brief The canonical false value is returned.

    @param builtin_registry A registry of canonical built-in values.
    @return The canonical false value.
    """
    return builtin_registry.get_false_value()


def _nil_value(
        builtin_registry: BuiltinRegistry
) -> NilValue:
    """
    @brief The canonical nil value is returned.

    @param builtin_registry A registry of canonical built-in values.
    @return The canonical nil value.
    """
    return builtin_registry.get_nil_value()


def _require_arg_count(
        args: RuntimeValueList,
        expected: int,
        selector: str
) -> None:
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
            f"Built-in method {selector} expected {expected} arguments, "
            f"got {actual}.",
        )


def _expect_integer(
        value: RuntimeValue,
        selector: str
) -> IntegerValue:
    """
    @brief One runtime integer value is required.

    @param value One runtime value.
    @param selector Current built-in selector.
    @return The checked runtime integer value.
    """
    if isinstance(value, IntegerValue):
        return value

    raise InterpreterError(
        ErrorCode.INT_OTHER,
        f"Built-in method {selector} expected Integer, "
        f"got {value.get_class().name}.",
    )


def _expect_string(
        value: RuntimeValue,
        selector: str
) -> StringValue:
    """
    @brief One runtime string value is required.

    @param value One runtime value.
    @param selector Current built-in selector.
    @return The checked runtime string value.
    """
    if isinstance(value, StringValue):
        return value

    raise InterpreterError(
        ErrorCode.INT_OTHER,
        f"Built-in method {selector} expected String, "
        f"got {value.get_class().name}.",
    )


def _expect_user_object(
        value: RuntimeValue,
        selector: str
) -> UserObject:
    """
    @brief One user object is required.

    @param value One runtime value.
    @param selector Current built-in selector.
    @return The checked user object.
    """
    if isinstance(value, UserObject):
        return value

    raise InterpreterError(
        ErrorCode.INT_OTHER,
        f"Built-in method {selector} expected a user object, got {value.get_class().name}.",
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


def _make_runtime_integer(
        value: int,
        object_factory: ObjectFactory
) -> IntegerValue:
    """
    @brief One runtime integer value is created.

    @param value Wrapped integer payload.
    @param class_registry A registry of runtime classes.
    @param object_factory A runtime value factory.
    @return One runtime integer value.
    """
    return object_factory.new_integer(value)


def _copy_user_slots(source: UserObject, target: UserObject) -> None:
    """
    @brief Regular instance slots are copied with shallow-copy semantics.

    @param source One source user object.
    @param target One target user object.
    """
    for slot_name, slot_value in source.slots.slots_by_name.items():
        target.define_slot(slot_name, slot_value)


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


def _make_object_equal_to(
        builtin_registry: BuiltinRegistry
) -> InstanceBuiltinCallback:
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

        if isinstance(receiver, IntegerValue) and isinstance(other, IntegerValue):
            if receiver.raw() == other.raw():
                return _true_value(builtin_registry)
            return _false_value(builtin_registry)

        if isinstance(receiver, StringValue) and isinstance(other, StringValue):
            if receiver.raw() == other.raw():
                return _true_value(builtin_registry)
            return _false_value(builtin_registry)

        if isinstance(receiver, BooleanValue) and isinstance(other, BooleanValue):
            if receiver.raw() == other.raw():
                return _true_value(builtin_registry)
            return _false_value(builtin_registry)

        if receiver is other:
            return _true_value(builtin_registry)

        return _false_value(builtin_registry)

    return builtin_object_equal_to


def _make_object_as_string(
        object_factory: ObjectFactory
) -> InstanceBuiltinCallback:
    """
    @brief One Object>>asString callback is created.

    @param class_registry A registry of runtime classes.
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

        if target_class.name == "Integer":
            return object_factory.new_integer(0)

        if target_class.name == "String":
            return object_factory.new_string("")

        if target_class.name == "True":
            return _true_value(builtin_registry)

        if target_class.name == "False":
            return _false_value(builtin_registry)

        if target_class.name == "Block":
            raise NotImplementedError(
                "Block class-side >>new must be finalized after the execution layer "
                "and empty-block representation are settled.",
            )

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

        if target_class.name == "Integer":
            source_integer = _expect_integer(source, "from:")
            return object_factory.new_integer(source_integer.raw())

        if target_class.name == "String":
            source_string = _expect_string(source, "from:")
            return object_factory.new_string(source_string.raw())

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
            raise NotImplementedError(
                "Block class-side >>from: requires the future block representation.",
            )

        new_object = object_factory.new_user_object(target_class)

        if isinstance(source, UserObject):
            _copy_user_slots(source, new_object)

        return new_object

    return builtin_object_from


def _make_nil_as_string(
        object_factory: ObjectFactory
) -> InstanceBuiltinCallback:
    """
    @brief One Nil>>asString callback is created.

    @param class_registry A registry of runtime classes.
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


def _make_integer_plus(
        object_factory: ObjectFactory
) -> InstanceBuiltinCallback:
    """
    @brief One Integer>>plus: callback is created.

    @param class_registry A registry of runtime classes.
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


def _make_integer_minus(
        object_factory: ObjectFactory
) -> InstanceBuiltinCallback:
    """
    @brief One Integer>>minus: callback is created.

    @param class_registry A registry of runtime classes.
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


def _make_integer_multiply_by(
        object_factory: ObjectFactory
) -> InstanceBuiltinCallback:
    """
    @brief One Integer>>multiplyBy: callback is created.

    @param class_registry A registry of runtime classes.
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


def _make_integer_div_by(
        object_factory: ObjectFactory
) -> InstanceBuiltinCallback:
    """
    @brief One Integer>>divBy: callback is created.

    @param class_registry A registry of runtime classes.
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


def _make_integer_as_string(
        object_factory: ObjectFactory
) -> InstanceBuiltinCallback:
    """
    @brief One Integer>>asString callback is created.

    @param class_registry A registry of runtime classes.
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


def _make_integer_times_repeat_deferred() -> InstanceBuiltinCallback:
    """
    @brief One deferred Integer>>timesRepeat: callback is created.

    @return One deferred Integer>>timesRepeat: callback.
    """

    def builtin_integer_times_repeat(
        _receiver: RuntimeValue,
        _args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        raise NotImplementedError(
            "Integer>>timesRepeat: requires the future execution layer.",
        )

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
        right = _expect_string(args[0], "equalTo:")

        if left.raw() == right.raw():
            return _true_value(builtin_registry)

        return _false_value(builtin_registry)

    return builtin_string_equal_to


def _make_string_as_integer(
        builtin_registry: BuiltinRegistry,
        object_factory: ObjectFactory
) -> InstanceBuiltinCallback:
    """
    @brief One String>>asInteger callback is created.

    @param class_registry A registry of runtime classes.
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
        builtin_registry: BuiltinRegistry,
        object_factory: ObjectFactory
) -> InstanceBuiltinCallback:
    """
    @brief One String>>concatenateWith: callback is created.

    @param class_registry A registry of runtime classes.
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
        builtin_registry: BuiltinRegistry,
        object_factory: ObjectFactory
) -> InstanceBuiltinCallback:
    """
    @brief One String>>startsWith:endsBefore: callback is created.

    @param class_registry A registry of runtime classes.
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
        if start_index > end_index:
            return _nil_value(builtin_registry)
        if end_index > len(text) + 1:
            return _nil_value(builtin_registry)

        sliced_text = text[start_index - 1 : end_index - 1]
        return _make_runtime_string(sliced_text, object_factory)

    return builtin_string_starts_with_ends_before


def _make_string_length(
        object_factory: ObjectFactory
) -> InstanceBuiltinCallback:
    """
    @brief One String>>length callback is created.

    @param class_registry A registry of runtime classes.
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
        object_factory: ObjectFactory,
        runtime_io: RuntimeIO
) -> ClassBuiltinCallback:
    """
    @brief One String class-side >>read callback is created.

    @param class_registry A registry of runtime classes.
    @param object_factory A runtime value factory.
    @param runtime_io A runtime input/output service.
    @return One String class-side >>read callback.
    """

    def builtin_string_read(
        _receiver: RuntimeClass,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 0, "read")
        read_text = runtime_io.read_line()
        normalized_text = read_text.removesuffix("\n")
        return _make_runtime_string(normalized_text, object_factory)

    return builtin_string_read


def _make_block_new_deferred() -> ClassBuiltinCallback:
    """
    @brief One deferred Block class-side >>new callback is created.

    @return One deferred Block class-side >>new callback.
    """

    def builtin_block_new(
        _receiver: RuntimeClass,
        _args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        raise NotImplementedError(
            "Block class-side >>new requires the future execution layer.",
        )

    return builtin_block_new


def _make_block_value_deferred() -> InstanceBuiltinCallback:
    """
    @brief One deferred Block>>value... callback is created.

    @return One deferred Block>>value... callback.
    """

    def builtin_block_value(
        _receiver: RuntimeValue,
        _args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        raise NotImplementedError(
            "Block>>value... requires the future execution layer.",
        )

    return builtin_block_value


def _make_block_while_true_deferred() -> InstanceBuiltinCallback:
    """
    @brief One deferred Block>>whileTrue: callback is created.

    @return One deferred Block>>whileTrue: callback.
    """

    def builtin_block_while_true(
        _receiver: RuntimeValue,
        _args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        raise NotImplementedError(
            "Block>>whileTrue: requires the future execution layer.",
        )

    return builtin_block_while_true


def _make_true_as_string(
        object_factory: ObjectFactory
) -> InstanceBuiltinCallback:
    """
    @brief One True>>asString callback is created.

    @param class_registry A registry of runtime classes.
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


def _make_true_not(
        builtin_registry: BuiltinRegistry
) -> InstanceBuiltinCallback:
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


def _make_true_and_deferred() -> InstanceBuiltinCallback:
    """
    @brief One deferred True>>and: callback is created.

    @return One deferred True>>and: callback.
    """

    def builtin_true_and(
        _receiver: RuntimeValue,
        _args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        raise NotImplementedError(
            "True>>and: requires the future execution layer.",
        )

    return builtin_true_and


def _make_true_or_deferred() -> InstanceBuiltinCallback:
    """
    @brief One deferred True>>or: callback is created.

    @return One deferred True>>or: callback.
    """

    def builtin_true_or(
        _receiver: RuntimeValue,
        _args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        raise NotImplementedError(
            "True>>or: requires the future execution layer.",
        )

    return builtin_true_or


def _make_true_if_true_if_false_deferred() -> InstanceBuiltinCallback:
    """
    @brief One deferred True>>ifTrue:ifFalse: callback is created.

    @return One deferred True>>ifTrue:ifFalse: callback.
    """

    def builtin_true_if_true_if_false(
        _receiver: RuntimeValue,
        _args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        raise NotImplementedError(
            "True>>ifTrue:ifFalse: requires the future execution layer.",
        )

    return builtin_true_if_true_if_false


def _make_false_as_string(
        object_factory: ObjectFactory
) -> InstanceBuiltinCallback:
    """
    @brief One False>>asString callback is created.

    @param class_registry A registry of runtime classes.
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


def _make_false_not(
        builtin_registry: BuiltinRegistry
) -> InstanceBuiltinCallback:
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


def _make_false_and_deferred() -> InstanceBuiltinCallback:
    """
    @brief One deferred False>>and: callback is created.

    @return One deferred False>>and: callback.
    """

    def builtin_false_and(
        _receiver: RuntimeValue,
        _args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        raise NotImplementedError(
            "False>>and: requires the future execution layer.",
        )

    return builtin_false_and


def _make_false_or_deferred() -> InstanceBuiltinCallback:
    """
    @brief One deferred False>>or: callback is created.

    @return One deferred False>>or: callback.
    """

    def builtin_false_or(
        _receiver: RuntimeValue,
        _args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        raise NotImplementedError(
            "False>>or: requires the future execution layer.",
        )

    return builtin_false_or


def _make_false_if_true_if_false_deferred() -> InstanceBuiltinCallback:
    """
    @brief One deferred False>>ifTrue:ifFalse: callback is created.

    @return One deferred False>>ifTrue:ifFalse: callback.
    """

    def builtin_false_if_true_if_false(
        _receiver: RuntimeValue,
        _args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        raise NotImplementedError(
            "False>>ifTrue:ifFalse: requires the future execution layer.",
        )

    return builtin_false_if_true_if_false
