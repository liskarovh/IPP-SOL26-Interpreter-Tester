"""
@file object_factory.py
@brief Runtime value creation is declared.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

RuntimeValue children are intended to be created here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..input_model import Block as AstBlock
from ..model.block_closure import BlockClosure
from ..model.invocation_context import InvocationContext
from ..model.object_slots import ObjectSlots
from ..model.scope_frame import ScopeFrame
from ..model.user_object import UserObject
from ..model.values import BooleanValue, IntegerValue, NilValue, RuntimeValue, StringValue

if TYPE_CHECKING:
    from ..input_model import Block as AstBlock
    from ..model.invocation_context import InvocationContext
    from ..model.runtime_class import RuntimeClass
    from ..model.scope_frame import ScopeFrame
    from ..runtime.builtin_registry import BuiltinRegistry
    from ..runtime.class_registry import ClassRegistry


class ObjectFactory:
    """
    @brief Runtime values are created by this factory.
    """

    def __init__(
        self,
        class_registry: ClassRegistry,
        builtin_registry: BuiltinRegistry,
    ) -> None:
        """
        @brief An object factory is initialized.

        @param class_registry Registry of runtime classes.
        @param builtin_registry Registry of canonical builtin values and methods.
        """
        self.class_registry = class_registry
        self.builtin_registry = builtin_registry

    def new_user_object(self, runtime_class: RuntimeClass) -> UserObject:
        """
        @brief A new user object is created.

        @param runtime_class Runtime class of the created user object.
        @return Newly created user object.
        """
        initial_slots: dict[str, RuntimeValue] = {}
        slot_storage = ObjectSlots(initial_slots)
        return UserObject(runtime_class, slot_storage)

    def _new_slot_storage(self) -> ObjectSlots:
        """
        @brief One empty instance slot storage is created.

        @return One empty slot storage.
        """
        return ObjectSlots({})

    def new_integer(
            self,
            value: int,
            runtime_class: RuntimeClass | None = None,
    ) -> IntegerValue:
        """
        @brief One new integer runtime value is created.

        @param value One wrapped integer payload.
        @param runtime_class One runtime class of the created integer, or None for builtin Integer.
        @return One newly created integer runtime value.
        """
        effective_class = runtime_class
        if effective_class is None:
            effective_class = self._require_builtin_class("Integer")

        slot_storage: ObjectSlots | None = None
        if effective_class.name != "Integer":
            slot_storage = self._new_slot_storage()

        return IntegerValue(effective_class, value, slot_storage)

    def new_string(
            self,
            value: str,
            runtime_class: RuntimeClass | None = None,
    ) -> StringValue:
        """
        @brief One new string runtime value is created.

        @param value One wrapped string payload.
        @param runtime_class One runtime class of the created string, or None for builtin String.
        @return One newly created string runtime value.
        """
        effective_class = runtime_class
        if effective_class is None:
            effective_class = self._require_builtin_class("String")

        slot_storage: ObjectSlots | None = None
        if effective_class.name != "String":
            slot_storage = self._new_slot_storage()

        return StringValue(effective_class, value, slot_storage)

    def new_boolean(self, value: bool) -> BooleanValue:
        """
        @brief A canonical boolean runtime value is returned.

        @param value Wrapped boolean payload.
        @return Canonical boolean runtime value.
        """
        if value:
            return self.builtin_registry.get_true_value()

        return self.builtin_registry.get_false_value()

    def new_nil(self) -> NilValue:
        """
        @brief The canonical nil runtime value is returned.

        @return Canonical nil runtime value.
        """
        return self.builtin_registry.get_nil_value()

    def new_block_closure(
        self,
        ast: AstBlock,
        frame: ScopeFrame,
        ctx: InvocationContext,
    ) -> BlockClosure:
        """
        @brief A new block closure is created.

        @param ast AST of the captured block.
        @param frame Captured lexical scope frame.
        @param ctx Captured invocation context.
        @return Newly created block closure.
        """

        runtime_class = self._require_builtin_class("Block")
        return BlockClosure(
            runtime_class,
            ast,
            frame,
            ctx,
        )

    def _require_builtin_class(self, class_name: str) -> RuntimeClass:
        """
        @brief One builtin runtime class is required.

        @param class_name Name of the required builtin runtime class.
        @return Resolved runtime class.
        """
        return self.class_registry.require(class_name)

    def new_empty_block_closure(self) -> BlockClosure:
        """
        @brief One empty block closure is created.

        @return One new empty zero-arity block closure.
        """
        runtime_class = self._require_builtin_class("Block")
        empty_block_ast = AstBlock(
            arity=0,
            parameters=[],
            assigns=[],
        )
        empty_frame = ScopeFrame()
        empty_ctx = InvocationContext(
            self.builtin_registry.get_nil_value(),
            self.class_registry.require("Object"),
        )
        return BlockClosure(
            runtime_class,
            empty_block_ast,
            empty_frame,
            empty_ctx,
        )

    def copy_block_closure(self, source: BlockClosure) -> BlockClosure:
        """
        @brief One block closure is shallow-copied.

        @param source One source block closure.
        @return One copied block closure.
        """
        runtime_class = self._require_builtin_class("Block")
        return BlockClosure(
            runtime_class,
            source.block_ast,
            source.captured_frame,
            source.closure_ctx,
        )
