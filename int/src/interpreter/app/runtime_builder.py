"""
@file runtime_builder.py
@brief Runtime construction from the validated AST program is defined.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

A validated AST program is intended to be converted into runtime structures
in this module. Only runtime construction is expected to be performed here.
No execution of the program is expected to be started here.
"""

from __future__ import annotations

from ..input_model import ClassDef as AstClassDef
from ..input_model import Method as AstMethod
from ..input_model import Program
from ..model.runtime_class import RuntimeClass
from ..model.runtime_methods import UserMethod
from ..model.values import BooleanValue, NilValue
from ..runtime.builtin_registry import BuiltinRegistry
from ..runtime.builtins import (
    SendOneArgMessageCallback,
    SendZeroArgMessageCallback,
    register_builtins,
)
from ..runtime.class_registry import ClassRegistry
from ..runtime.object_factory import ObjectFactory
from ..runtime.runtime import Runtime
from ..runtime.runtime_io import RuntimeIO


class RuntimeBuilder:
    """
    @brief A validated AST program is converted into a runtime here.
    """

    def __init__(self) -> None:
        """
        @brief A runtime builder is initialized.

        The builder is intentionally kept simple at this stage.
        """

    def build(
        self,
        program: Program,
        input_io: RuntimeIO,
        send_zero_arg_message: SendZeroArgMessageCallback,
        send_one_arg_message: SendOneArgMessageCallback,
    ) -> Runtime:
        """
        @brief A runtime is built from the validated AST program.

        @param program A validated AST program.
        @param input_io A runtime input/output adapter.
        @param send_zero_arg_message A helper sending one zero-argument runtime message.
        @param send_one_arg_message A helper sending one one-argument runtime message.
        @return A newly built runtime container.
        """
        new_runtime = self._create_empty_runtime(input_io)
        self._register_builtin_runtime_content(
            new_runtime,
            send_zero_arg_message,
            send_one_arg_message,
        )
        self._register_user_runtime_classes(program, new_runtime)
        self._attach_user_runtime_methods(program, new_runtime)
        return new_runtime

    @staticmethod
    def _create_empty_runtime(input_io: RuntimeIO) -> Runtime:
        """
        @brief An empty runtime container is created.

        @param input_io A runtime input/output adapter.
        @return A runtime container with empty runtime services.
        """
        class_registry = ClassRegistry()
        builtin_registry = BuiltinRegistry()
        object_factory = ObjectFactory(class_registry, builtin_registry)

        return Runtime(
            class_registry,
            builtin_registry,
            object_factory,
            input_io,
        )

    @staticmethod
    def _register_builtin_runtime_content(
        runtime: Runtime,
        send_zero_arg_message: SendZeroArgMessageCallback,
        send_one_arg_message: SendOneArgMessageCallback,
    ) -> None:
        """
        @brief Built-in runtime classes, values, and methods are registered.

        @param runtime A runtime container that is being built.
        @param send_zero_arg_message A helper sending one zero-argument runtime message.
        @param send_one_arg_message A helper sending one one-argument runtime message.
        """
        RuntimeBuilder._register_builtin_runtime_classes(runtime)
        RuntimeBuilder._register_canonical_builtin_values(runtime)
        RuntimeBuilder._register_builtin_runtime_methods(
            runtime,
            send_zero_arg_message,
            send_one_arg_message,
        )

    @staticmethod
    def _register_builtin_runtime_classes(runtime: Runtime) -> None:
        """
        @brief Built-in runtime classes are registered.

        @param runtime A runtime container that is being built.
        """
        object_class = RuntimeClass("Object", None)
        nil_class = RuntimeClass("Nil", object_class)
        integer_class = RuntimeClass("Integer", object_class)
        string_class = RuntimeClass("String", object_class)
        block_class = RuntimeClass("Block", object_class)
        true_class = RuntimeClass("True", object_class)
        false_class = RuntimeClass("False", object_class)

        runtime.class_registry.add(object_class)
        runtime.class_registry.add(nil_class)
        runtime.class_registry.add(integer_class)
        runtime.class_registry.add(string_class)
        runtime.class_registry.add(block_class)
        runtime.class_registry.add(true_class)
        runtime.class_registry.add(false_class)

    @staticmethod
    def _register_canonical_builtin_values(runtime: Runtime) -> None:
        """
        @brief Canonical built-in runtime values are registered.

        @param runtime A runtime container that is being built.
        """
        true_class = runtime.class_registry.require("True")
        false_class = runtime.class_registry.require("False")
        nil_class = runtime.class_registry.require("Nil")

        true_value = BooleanValue(true_class, True)
        false_value = BooleanValue(false_class, False)
        nil_value = NilValue(nil_class)

        runtime.builtin_registry.set_true_value(true_value)
        runtime.builtin_registry.set_false_value(false_value)
        runtime.builtin_registry.set_nil_value(nil_value)

    @staticmethod
    def _register_builtin_runtime_methods(
        runtime: Runtime,
        send_zero_arg_message: SendZeroArgMessageCallback,
        send_one_arg_message: SendOneArgMessageCallback,
    ) -> None:
        """
        @brief Built-in runtime methods are registered.

        @param runtime A runtime container that is being built.
        @param send_zero_arg_message A helper sending one zero-argument runtime message.
        @param send_one_arg_message A helper sending one one-argument runtime message.
        """
        register_builtins(
            runtime.class_registry,
            runtime.builtin_registry,
            runtime.object_factory,
            runtime.io,
            send_zero_arg_message,
            send_one_arg_message,
        )

    def _register_user_runtime_classes(self, program: Program, runtime: Runtime) -> None:
        """
        @brief User-defined runtime classes are registered.

        @param program A validated AST program.
        @param runtime A runtime container that is being built.
        """
        for class_ast in program.classes:
            runtime_class = RuntimeClass(class_ast.name, None)
            runtime.class_registry.add(runtime_class)

        for class_ast in program.classes:
            runtime_class = runtime.class_registry.require(class_ast.name)
            runtime_class.parent = self._resolve_parent_runtime_class(class_ast, runtime)

    def _attach_user_runtime_methods(self, program: Program, runtime: Runtime) -> None:
        """
        @brief User-defined runtime methods are attached to runtime classes.

        @param program A validated AST program.
        @param runtime A runtime container that is being built.
        """
        for class_ast in program.classes:
            runtime_class = runtime.class_registry.require(class_ast.name)

            for method_ast in class_ast.methods:
                user_method = self._build_user_method(method_ast, runtime_class)
                runtime_class.add_instance_method(user_method)

    @staticmethod
    def _resolve_parent_runtime_class(
        class_ast: AstClassDef,
        runtime: Runtime,
    ) -> RuntimeClass:
        """
        @brief A parent runtime class is resolved for one AST class.

        @param class_ast One source AST class definition.
        @param runtime A partially built runtime container.
        @return A resolved parent runtime class.
        """
        parent_name = class_ast.parent
        return runtime.class_registry.require(parent_name)

    @staticmethod
    def _build_user_method(
        method_ast: AstMethod,
        owner: RuntimeClass,
    ) -> UserMethod:
        """
        @brief One user-defined runtime method is built from AST.

        @param method_ast One source AST method definition.
        @param owner An owning runtime class.
        @return A runtime user method.
        """
        selector = method_ast.selector
        return UserMethod(selector, owner, method_ast)
