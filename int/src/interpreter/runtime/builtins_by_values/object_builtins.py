"""
@file object_builtins.py
@brief Object built-in method callbacks and registration are defined.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
REPETITIVE PARTS OF THIS FILE HAVE BEEN AI GENERATED - CHATGPT CHAT HERE https://chatgpt.com/share/69d2e81e-87d0-838e-afb8-efddf21b5d69

Object-related built-in runtime methods are grouped in this module.
Shared helper utilities are intentionally reused from runtime.builtins_by_values
so that the overall behavior remains unchanged.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...error_codes import ErrorCode
from ...exceptions import InterpreterError
from ...model.runtime_class import RuntimeClass
from ...model.values import BooleanValue, IntegerValue, RuntimeValue, StringValue
from ..builtins import (
    _copy_runtime_slots,
    _expect_block_closure,
    _expect_integer,
    _expect_string,
    _false_value,
    _make_return_false,
    _make_runtime_string,
    _nil_value,
    _register_one_class_builtin,
    _register_one_instance_builtin,
    _true_value,
)

if TYPE_CHECKING:
    from ...model.invocation_context import InvocationContext
    from ...support.typing_helpers import (
        ClassBuiltinCallback,
        InstanceBuiltinCallback,
        RuntimeValueList,
    )
    from ..builtin_registry import BuiltinRegistry
    from ..object_factory import ObjectFactory


def register_object_builtins(
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
        from ..builtins import _require_arg_count

        _require_arg_count(args, 1, "identicalTo:")
        other = args[0]

        if receiver is other:
            return _true_value(builtin_registry)

        return _false_value(builtin_registry)

    return builtin_object_identical_to


def _make_object_equal_to(
    builtin_registry: BuiltinRegistry,
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
        from ..builtins import _require_arg_count

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
        from ..builtins import _require_arg_count

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
        from ..builtins import _require_arg_count

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
        from ..builtins import _require_arg_count

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
