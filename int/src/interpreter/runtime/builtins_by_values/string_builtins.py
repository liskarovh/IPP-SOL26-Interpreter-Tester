"""
@file string_builtins.py
@brief String built-in callbacks and their registration are implemented.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
REPETITIVE PARTS OF THIS FILE HAVE BEEN AI GENERATED - CHATGPT CHAT HERE https://chatgpt.com/share/69d2e81e-87d0-838e-afb8-efddf21b5d69

String instance-side and class-side built-in methods are grouped in this module.
Shared helpers from runtime.builtins_by_values are reused to keep behavior unchanged.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...model.runtime_class import RuntimeClass
from ...model.values import IntegerValue, RuntimeValue, StringValue
from ..builtins import (
    _expect_string,
    _false_value,
    _make_return_receiver,
    _make_return_true,
    _make_runtime_integer,
    _make_runtime_string,
    _nil_value,
    _register_one_class_builtin,
    _register_one_instance_builtin,
    _require_arg_count,
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
    from ..runtime_io import RuntimeIO


def register_string_builtins(
    string_class: RuntimeClass,
    builtin_registry: BuiltinRegistry,
    object_factory: ObjectFactory,
    runtime_io: RuntimeIO,
) -> None:
    """
    @brief String built-ins are registered.

    @param string_class Runtime class for String.
    @param builtin_registry Registry holding canonical values and built-in methods.
    @param object_factory Factory used for runtime values.
    @param runtime_io Runtime input/output service.
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
        builtin_callback=_make_string_as_integer(
            builtin_registry,
            object_factory,
        ),
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
        builtin_callback=_make_string_concatenate_with(
            builtin_registry,
            object_factory,
        ),
        builtin_registry=builtin_registry,
    )
    _register_one_instance_builtin(
        owner=string_class,
        selector="startsWith:endsBefore:",
        builtin_callback=_make_string_starts_with_ends_before(
            builtin_registry,
            object_factory,
        ),
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


def _make_string_print(runtime_io: RuntimeIO) -> InstanceBuiltinCallback:
    """
    @brief Callback for String>>print is created.

    @param runtime_io Runtime input/output service.
    @return Callback implementing String>>print.
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
    @brief Callback for String>>equalTo: is created.

    @param builtin_registry Registry providing canonical boolean values.
    @return Callback implementing String>>equalTo:.
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
    builtin_registry: BuiltinRegistry,
    object_factory: ObjectFactory,
) -> InstanceBuiltinCallback:
    """
    @brief Callback for String>>asInteger is created.

    @param builtin_registry Registry providing canonical nil.
    @param object_factory Factory used for runtime values.
    @return Callback implementing String>>asInteger.
    """

    def builtin_string_as_integer(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 0, "asInteger")
        string_value = _expect_string(receiver, "asInteger")
        text = string_value.raw()

        # failed parse returns nil
        try:
            parsed_value = int(text)
        except ValueError:
            return _nil_value(builtin_registry)

        return _make_runtime_integer(parsed_value, object_factory)

    return builtin_string_as_integer


def _make_string_concatenate_with(
    builtin_registry: BuiltinRegistry,
    object_factory: ObjectFactory,
) -> InstanceBuiltinCallback:
    """
    @brief Callback for String>>concatenateWith: is created.

    @param builtin_registry Registry providing canonical nil.
    @param object_factory Factory used for runtime values.
    @return Callback implementing String>>concatenateWith:.
    """

    def builtin_string_concatenate_with(
        receiver: RuntimeValue,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 1, "concatenateWith:")
        left = _expect_string(receiver, "concatenateWith:")
        right = args[0]

        # only accepts strings
        if not isinstance(right, StringValue):
            return _nil_value(builtin_registry)

        return _make_runtime_string(left.raw() + right.raw(), object_factory)

    return builtin_string_concatenate_with


def _make_string_starts_with_ends_before(
    builtin_registry: BuiltinRegistry,
    object_factory: ObjectFactory,
) -> InstanceBuiltinCallback:
    """
    @brief Callback for String>>startsWith:endsBefore: is created.

    @param builtin_registry Registry providing canonical nil.
    @param object_factory Factory used for runtime values.
    @return Callback implementing String>>startsWith:endsBefore:.
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

        # if both not int then nil
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

        # empty or inverted ranges produce empty string
        if slice_end - slice_start <= 0:
            return _make_runtime_string("", object_factory)

        sliced_text = text[slice_start:slice_end]
        return _make_runtime_string(sliced_text, object_factory)

    return builtin_string_starts_with_ends_before


def _make_string_length(object_factory: ObjectFactory) -> InstanceBuiltinCallback:
    """
    @brief Callback for String>>length is created.

    @param object_factory Factory used for runtime values.
    @return Callback implementing String>>length.
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
    runtime_io: RuntimeIO,
) -> ClassBuiltinCallback:
    """
    @brief Callback for String class-side>>read is created.

    @param object_factory Factory used for runtime values.
    @param runtime_io Runtime input/output service.
    @return Callback implementing String class-side>>read.
    """

    def builtin_string_read(
        receiver: RuntimeClass,
        args: RuntimeValueList,
        _ctx: InvocationContext,
    ) -> RuntimeValue:
        _require_arg_count(args, 0, "read")
        read_text = runtime_io.read_line()

        # string read strips trailing input newline
        normalized_text = read_text.removesuffix("\n")
        return object_factory.new_string(normalized_text, receiver)

    return builtin_string_read
