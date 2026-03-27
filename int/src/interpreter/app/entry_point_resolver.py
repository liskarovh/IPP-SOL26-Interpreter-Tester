"""
@file entry_point_resolver.py
@brief Runtime entry-point resolution is defined.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

The already validated program entry point is intended to be resolved here
from the built runtime. No execution is expected to be started here.
"""

from __future__ import annotations

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from ..model.runtime_methods import RuntimeMethod
from ..model.values import UserObject
from ..runtime.runtime import Runtime


class EntryPointResolver:
    """
    @brief The runtime entry point is resolved by this class.
    """

    def __init__(self) -> None:
        """
        @brief An entry-point resolver is initialized.

        The resolver is intentionally kept simple and nearly stateless.
        """

    @staticmethod
    def resolve(
            runtime: Runtime,
    ) -> tuple[UserObject, RuntimeMethod]:
        """
        @brief The runtime entry point is resolved.

        @param program A validated AST program.
        @param runtime A built runtime container.
        @return The resolved runtime entry data needed by the execution layer.
        """

        entry_class_name = "Main"
        entry_method_name = "run"

        entry_class = runtime.require_class(entry_class_name)
        entry_receiver = runtime.object_factory.new_user_object(entry_class)
        entry_method = entry_class.lookup(entry_method_name)

        if entry_method is None:
            raise (InterpreterError(
                ErrorCode.GENERAL_OTHER,
                f"Entry point method {entry_method_name} "
                f"is not defined in class {entry_class_name}."))
        return entry_receiver, entry_method
