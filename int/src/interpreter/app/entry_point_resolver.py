"""
@file entry_point_resolver.py
@brief Runtime entry-point resolution is implemented.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

The validated program entry point is resolved from the built runtime here.
"""

from __future__ import annotations

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from ..model.runtime_methods import RuntimeMethod
from ..model.user_object import UserObject
from ..runtime.runtime import Runtime


class EntryPointResolver:
    """
    @brief The runtime entry point is resolved by this class.
    """

    @staticmethod
    def resolve(
        runtime: Runtime,
    ) -> tuple[UserObject, RuntimeMethod]:
        """
        @brief The runtime entry point is resolved.

        @param runtime The built runtime.
        @return The resolved entry receiver and entry method.
        """

        # SOL26 entry point Main>>run.
        entry_class_name = "Main"
        entry_method_name = "run"

        entry_class = runtime.class_registry.get(entry_class_name)

        if entry_class is None:
            raise InterpreterError(
                ErrorCode.INT_DNU,
                f"Entry class '{entry_class_name}' was not found.",
            )

        # instance of entry class created as initial receiver
        entry_receiver = runtime.object_factory.new_user_object(entry_class)
        entry_method = entry_class.lookup_instance(entry_method_name)

        if entry_method is None:
            raise (
                InterpreterError(
                    ErrorCode.GENERAL_OTHER,
                    f"Entry point method {entry_method_name} "
                    f"is not defined in class {entry_class_name}.",
                )
            )
        return entry_receiver, entry_method
