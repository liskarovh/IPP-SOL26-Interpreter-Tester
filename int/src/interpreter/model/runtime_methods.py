"""
@file runtime_methods.py
@brief Runtime method abstractions are defined.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Runtime methods are represented by a small hierarchy. User-defined methods
and built-in methods share a common selector/owner interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..input_model import Method as AstMethod
from ..runtime.builtin_implementation import BuiltinImplementation
from ..support.typing_helpers import MethodReceiver, RuntimeValueList

if TYPE_CHECKING:
    from .invocation_context import InvocationContext
    from .runtime_class import RuntimeClass
    from .values import RuntimeValue


class RuntimeMethod(ABC):
    """
    @brief A runtime method base abstraction is defined.
    """

    def __init__(self, selector: str, owner: RuntimeClass) -> None:
        """
        @brief Shared runtime-method state is initialized.

        @param selector A method selector.
        @param owner An owning runtime class.
        """
        self.selector = selector
        self.owner = owner

    @abstractmethod
    def call(
        self,
        receiver: MethodReceiver,
        args: RuntimeValueList,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief A runtime method call is performed.

        @param receiver A method receiver.
        @param args Runtime call arguments.
        @param ctx An invocation context.
        @return A produced runtime value.
        """

    @abstractmethod
    def arity(self) -> int:
        """
        @brief The expected method arity is returned.

        @return The expected runtime-method arity.
        """


class UserMethod(RuntimeMethod):
    """
    @brief A user-defined runtime method is represented.
    """

    def __init__(
        self,
        selector: str,
        owner: RuntimeClass,
        method_ast: AstMethod,
    ) -> None:
        """
        @brief A user-defined runtime method is initialized.

        @param selector A method selector.
        @param owner An owning runtime class.
        @param method_ast A source AST method definition.
        """
        super().__init__(selector, owner)
        self.method_ast = method_ast

    def call(
        self,
        receiver: MethodReceiver,
        args: RuntimeValueList,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief A user-defined runtime method call is performed.

        @param receiver A method receiver.
        @param args Runtime call arguments.
        @param ctx An invocation context.
        @return A produced runtime value.
        """
        # TODO:
        # 1. Create or request the execution context for this user method call.
        # 2. Ensure the current owner is this method's owning runtime class.
        # 3. Bind method arguments to the method frame.
        # 4. Delegate execution of method_ast.block to MethodExecutor / BlockExecutor.
        # 5. Return the produced RuntimeValue.
        _ = receiver
        _ = args
        _ = ctx
        raise NotImplementedError("User method execution has not been implemented yet.")

    def arity(self) -> int:
        """
        @brief The expected user-method arity is returned.

        @return The number of block parameters of the source AST method.
        """
        return self.method_ast.block.arity


class BuiltinMethod(RuntimeMethod):
    """
    @brief A built-in runtime method is represented.
    """

    def __init__(
        self,
        selector: str,
        owner: RuntimeClass,
        impl: BuiltinImplementation,
    ) -> None:
        """
        @brief A built-in runtime method is initialized.

        @param selector A method selector.
        @param owner An owning runtime class.
        @param impl A built-in implementation strategy.
        """
        super().__init__(selector, owner)
        self.impl = impl

    def call(
        self,
        receiver: MethodReceiver,
        args: RuntimeValueList,
        ctx: InvocationContext,
    ) -> RuntimeValue:
        """
        @brief A built-in runtime method call is performed.

        @param receiver A method receiver.
        @param args Runtime call arguments.
        @param ctx An invocation context.
        @return A produced runtime value.
        """
        return self.impl.invoke(receiver, args, ctx)

    def arity(self) -> int:
        """
        @brief The expected built-in method arity is returned.

        @return The expected built-in-method arity.
        """
        return self.selector.count(":")
