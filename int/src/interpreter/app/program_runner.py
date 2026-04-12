"""
@file program_runner.py
@brief Program execution orchestration is implemented.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

A loaded AST program is validated, converted into a runtime,
resolved to the program entry point, and executed here.
"""

from __future__ import annotations

from ..execution.block_executor import BlockExecutor
from ..execution.expression_dispatcher import ExpressionDispatcher
from ..execution.method_executor import MethodExecutor
from ..input_model import Program
from ..model.invocation_context import InvocationContext
from ..model.runtime_methods import UserMethod
from ..model.values import RuntimeValue
from ..runtime.runtime import Runtime
from ..runtime.runtime_io import RuntimeIO
from ..send.attribute_accessor import AttributeAccessor
from ..send.attribute_dispatch_resolver import AttributeDispatchResolver
from ..send.send_expr_evaluator import ClassSendExprEvaluator, InstanceSendExprEvaluator
from .entry_point_resolver import EntryPointResolver
from .program_validator import ProgramValidator
from .runtime_builder import RuntimeBuilder


class ProgramRunner:
    """
    @brief The current interpreter pipeline is orchestrated by this class.
    """

    def __init__(self) -> None:
        """
        @brief Stateless pipeline collaborators are initialized.

        The execution chain is not created here because it must be bound
        to the concrete runtime built for one program run.
        """
        self.program_validator = ProgramValidator()
        self.runtime_builder = RuntimeBuilder()

    @staticmethod
    def _wire_user_methods(
        runtime: Runtime,
        block_executor: BlockExecutor,
    ) -> None:
        """
        @brief One block executor is wired into all user-defined runtime methods.

        @param runtime A runtime with registered runtime classes.
        @param block_executor A block executor used for user-method execution.
        """

        # user methods created during runtime build and wired after
        # avoid circular dependencies between runtime and execution classes
        for runtime_class in runtime.class_registry.classes.values():
            for method in runtime_class.instance_methods_by_selector.values():
                if isinstance(method, UserMethod):
                    method.wire_block_executor(block_executor)

            for method in runtime_class.class_methods_by_selector.values():
                if isinstance(method, UserMethod):
                    method.wire_block_executor(block_executor)

    def run(self, program: Program, input_io: RuntimeIO) -> None:
        """
        @brief One loaded program is validated, built, resolved, and executed.

        The program is validated first. A runtime is then built,
        the entry point is resolved, and the entry method is executed.

        @param program A previously loaded AST program.
        @param input_io An input/output adapter passed from the interpreter.
        """
        self.program_validator.validate(program)

        # send evaluation wiring
        attribute_resolver = AttributeDispatchResolver()
        attribute_accessor = AttributeAccessor()

        instance_send_evaluator = InstanceSendExprEvaluator(
            attribute_resolver,
            None,
            attribute_accessor,
        )

        class_send_evaluator = ClassSendExprEvaluator(
            attribute_resolver,
            None,
            attribute_accessor,
        )

        # runtime builtins need callbacks for instance sends
        def send_zero_arg_message(
            target_value: RuntimeValue,
            selector: str,
            ctx: InvocationContext,
        ) -> RuntimeValue:
            from ..send.resolved_receiver import ResolvedReceiver
            from ..support.send_types import LookupMode

            return instance_send_evaluator.dispatch_send(
                ResolvedReceiver(target_value, LookupMode.NORMAL),
                selector,
                [],
                ctx,
            )

        # runtime build binds builtin send callbacks
        def send_one_arg_message(
            target_value: RuntimeValue,
            selector: str,
            arg_value: RuntimeValue,
            ctx: InvocationContext,
        ) -> RuntimeValue:
            from ..send.resolved_receiver import ResolvedReceiver
            from ..support.send_types import LookupMode

            return instance_send_evaluator.dispatch_send(
                ResolvedReceiver(target_value, LookupMode.NORMAL),
                selector,
                [arg_value],
                ctx,
            )

        # runtime model creation
        runtime = self.runtime_builder.build(
            program,
            input_io,
            send_zero_arg_message,
            send_one_arg_message,
        )

        # execution chain creation
        expression_dispatcher = ExpressionDispatcher(
            runtime.object_factory,
            instance_send_evaluator,
            class_send_evaluator,
        )

        block_executor = BlockExecutor(expression_dispatcher)
        method_executor = MethodExecutor(block_executor)

        instance_send_evaluator.wire_method_executor(method_executor)
        class_send_evaluator.wire_method_executor(method_executor)

        self._wire_user_methods(runtime, block_executor)

        # execution starts from the resolved SOL26 entry point
        entry_receiver, entry_method = EntryPointResolver.resolve(runtime)
        method_executor.execute(entry_method, entry_receiver, [])
