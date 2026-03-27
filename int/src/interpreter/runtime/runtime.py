"""
@file runtime.py
@brief Runtime container is defined.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

The runtime is used as a small container for the core runtime services.
Class lookup is intended to be forwarded through this object.
"""

from __future__ import annotations

from ..model.runtime_class import RuntimeClass
from .builtin_registry import BuiltinRegistry
from .class_registry import ClassRegistry
from .object_factory import ObjectFactory
from .runtime_io import RuntimeIO


class Runtime:
    """
    @brief Core runtime services are grouped by this class.
    """

    def __init__(
        self,
        class_registry: ClassRegistry,
        builtin_registry: BuiltinRegistry,
        object_factory: ObjectFactory,
        io: RuntimeIO,
    ) -> None:
        """
        @brief The runtime container is initialized.

        @param class_registry A runtime class registry.
        @param builtin_registry A built-in registry.
        @param object_factory A runtime object factory.
        @param io A runtime input/output adapter.
        """
        self.class_registry = class_registry
        self.builtin_registry = builtin_registry
        self.object_factory = object_factory
        self.io = io

    def get_class(self, name: str) -> RuntimeClass | None:
        """
        @brief A runtime class is looked up by name.

        @param name A runtime class name.
        @return A runtime class, or None when no class is found.
        """

        looked_up_class = self.class_registry.get(name)
        if looked_up_class is not None:
            return looked_up_class
        return None

    def require_class(self, name: str) -> RuntimeClass | None:
        """
        @brief A runtime class is required by name.

        @param name A runtime class name.
        @return A runtime class that must exist.
        """
        required_class = self.class_registry.require(name)
        if required_class is not None:
            return required_class
        return None
