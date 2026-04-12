"""
@file runtime_methods.py
@brief Runtime method abstractions are implemented.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Runtime methods are represented by a small hierarchy.
User-defined methods and built-in methods share the same selector/owner interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from ..input_model import Method as AstMethod
from ..runtime.builtin_implementation import BuiltinImplementation
from ..support.typing_helpers import MethodReceiver, RuntimeValueList
from .scope_frame import ScopeFrame

if TYPE_CHECKING:
    from ..execution.block_executor import BlockExecutor
    from .invocation_context import InvocationContext
    from .runtime_class import RuntimeClass
    from .values import RuntimeValue


class RuntimeMethod(ABC):
    """
    @brief A runtime method base abstraction is represented.
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
        self.block_executor: BlockExecutor | None = None

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
        # receiver already carried by the invocation context during block execution
        _ = receiver

        block_executor = self.block_executor
        if block_executor is None:
            raise InterpreterError(
                ErrorCode.GENERAL_OTHER,
                "User method block executor is not wired.",
            )

        method_block = self.method_ast.block

        # for each method call fresh local frame for its parameters and locals
        frame = ScopeFrame()
        frame.bind_method_parameters(method_block.parameters, args)

        # delegate method body execution to the block executor
        return block_executor.execute(method_block, frame, ctx)

    def arity(self) -> int:
        """
        @brief The expected user-method arity is returned.

        @return The number of block parameters of the source AST method.
        """
        return self.method_ast.block.arity

    def wire_block_executor(self, block_executor: BlockExecutor) -> None:
        """
        @brief A block executor is wired into this user-defined runtime method.
        @param block_executor A block executor.
        """
        self.block_executor = block_executor


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

        # builtin execution delegated to stored implementation
        return self.impl.invoke(receiver, args, ctx)

    def arity(self) -> int:
        """
        @brief The expected built-in method arity is returned.

        @return The expected built-in-method arity.
        """
        return self.selector.count(":")
