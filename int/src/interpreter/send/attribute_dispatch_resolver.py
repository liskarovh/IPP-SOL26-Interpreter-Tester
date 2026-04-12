"""
@file attribute_dispatch_resolver.py
@brief Attribute-dispatch resolution is implemented.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Selector meaning for instance sends is resolved here.
This module decides whether a selector should be treated as a method call,
an attribute read/write, or an attribute conflict.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ..model.values import RuntimeValue
from ..support.lookup_helpers import resolve_lookup_start_class
from ..support.send_types import AttributeDispatchDecision, LookupMode, ReceiverOrigin
from ..support.typing_helpers import MethodReceiver

if TYPE_CHECKING:
    from ..model.invocation_context import InvocationContext


# rgex is ai generated - https://chatgpt.com/share/69d39320-00bc-8387-bb25-1ee66b02d9ed
ATTRIBUTE_SELECTOR_REGEX = re.compile(
    r"^(?!(?:class|self|super|nil|true|false):?$)[a-z][A-Za-z0-9]*:?$"
)


def _get_attribute_name(selector: str) -> str | None:
    """
    @brief An attribute name is extracted from a valid attribute selector.

    @param selector Selector whose attribute form is checked.
    @return Attribute name for selectors shaped as name or name:, otherwise None.
    """
    # only selectors shaped like name or name: can map to attribute access
    if not ATTRIBUTE_SELECTOR_REGEX.fullmatch(selector):
        return None

    if selector.endswith(":"):
        return selector[:-1]

    return selector


def _is_write_selector(selector: str) -> bool:
    """
    @brief Whether a selector has write-selector shape is checked.

    @param selector Selector whose shape is checked.
    @return True when the selector has shape name:, otherwise False.
    """
    return selector.endswith(":")


def _has_matching_write_method(
    receiver: RuntimeValue,
    selector: str,
    lookup_mode: LookupMode,
    ctx: InvocationContext,
) -> bool:
    """
    @brief Existence of a matching write-selector method is checked.

    @param receiver Runtime receiver whose class hierarchy is checked.
    @param selector Write selector whose method form is checked.
    @param lookup_mode Lookup mode of the current send.
    @param ctx Invocation context carrying self/super information.
    @return True when a matching method exists, otherwise False.
    """
    start_class = resolve_lookup_start_class(receiver, lookup_mode, ctx)
    return start_class.lookup_instance(selector) is not None


def _has_conflicting_zero_arg_method_for_new_write(
    receiver: RuntimeValue,
    attribute_name: str,
    lookup_mode: LookupMode,
    receiver_origin: ReceiverOrigin,
    ctx: InvocationContext,
) -> bool:
    """
    @brief Existence of a conflicting zero-argument method for a new attribute write is checked.

    @param receiver Runtime receiver whose class hierarchy is checked.
    @param attribute_name Attribute name whose read-form selector is checked.
    @param lookup_mode Lookup mode of the current send.
    @param receiver_origin Syntactic origin of the current receiver.
    @param ctx Invocation context carrying self/super information.
    @return True when a conflicting zero-argument method exists, otherwise False.
    """
    if receiver_origin == ReceiverOrigin.EXPLICIT_SELF:
        start_class = ctx.current_owner
    else:
        start_class = resolve_lookup_start_class(receiver, lookup_mode, ctx)

    return start_class.lookup_instance(attribute_name) is not None


def _has_matching_zero_arg_method(
    receiver: RuntimeValue,
    attribute_name: str,
    lookup_mode: LookupMode,
    ctx: InvocationContext,
) -> bool:
    """
    @brief Existence of a matching zero-argument method is checked.

    @param receiver Runtime receiver whose class hierarchy is checked.
    @param attribute_name Attribute name whose read-form selector is checked.
    @param lookup_mode Lookup mode of the current send.
    @param ctx Invocation context carrying self/super information.
    @return True when a matching zero-argument method exists, otherwise False.
    """
    start_class = resolve_lookup_start_class(receiver, lookup_mode, ctx)
    return start_class.lookup_instance(attribute_name) is not None


class AttributeDispatchResolver:
    """
    @brief Attribute-dispatch decisions are resolved by this class.
    """

    @staticmethod
    def _resolve_read_dispatch(
        runtime_receiver: RuntimeValue,
        attribute_name: str,
        lookup_mode: LookupMode,
        ctx: InvocationContext,
    ) -> AttributeDispatchDecision:
        """
        @brief A read-form attribute-dispatch decision is resolved.

        @param runtime_receiver Runtime receiver whose selector meaning is resolved.
        @param attribute_name Resolved attribute name.
        @param lookup_mode Lookup mode of the current send.
        @param ctx Invocation context carrying self/super information.
        @return Resolved read-form attribute-dispatch decision.
        """
        slot_storage = runtime_receiver.slots
        if slot_storage is None:
            return AttributeDispatchDecision.METHOD

        # methods win over attribute reads when same zero arg selector exists
        if _has_matching_zero_arg_method(
            runtime_receiver,
            attribute_name,
            lookup_mode,
            ctx,
        ):
            return AttributeDispatchDecision.METHOD

        if slot_storage.has(attribute_name):
            return AttributeDispatchDecision.ATTRIBUTE_READ

        return AttributeDispatchDecision.METHOD

    @staticmethod
    def _resolve_write_dispatch(
        runtime_receiver: RuntimeValue,
        selector: str,
        attribute_name: str,
        lookup_mode: LookupMode,
        receiver_origin: ReceiverOrigin,
        ctx: InvocationContext,
    ) -> AttributeDispatchDecision:
        """
        @brief A write-form attribute-dispatch decision is resolved.

        @param runtime_receiver Runtime receiver whose selector meaning is resolved.
        @param selector Write selector whose meaning is resolved.
        @param attribute_name Resolved attribute name.
        @param lookup_mode Lookup mode of the current send.
        @param receiver_origin Syntactic origin of the current receiver.
        @param ctx Invocation context carrying self/super information.
        @return Resolved write-form attribute-dispatch decision.
        """
        slot_storage = runtime_receiver.slots
        if slot_storage is None:
            return AttributeDispatchDecision.METHOD

        # write selector methods win over attribute writes
        if _has_matching_write_method(
            runtime_receiver,
            selector,
            lookup_mode,
            ctx,
        ):
            return AttributeDispatchDecision.METHOD

        if slot_storage.has(attribute_name):
            return AttributeDispatchDecision.ATTRIBUTE_WRITE

        # new attribute rejected when it would collide with read method
        if _has_conflicting_zero_arg_method_for_new_write(
            runtime_receiver,
            attribute_name,
            lookup_mode,
            receiver_origin,
            ctx,
        ):
            return AttributeDispatchDecision.CONFLICT

        return AttributeDispatchDecision.ATTRIBUTE_WRITE

    @staticmethod
    def resolve(
        receiver: MethodReceiver,
        selector: str,
        lookup_mode: LookupMode,
        receiver_origin: ReceiverOrigin,
        ctx: InvocationContext,
    ) -> AttributeDispatchDecision:
        """
        @brief An attribute-dispatch decision is resolved.

        @param receiver Receiver whose selector meaning is resolved.
        @param selector Selector whose meaning is resolved.
        @param lookup_mode Lookup mode of the current send.
        @param receiver_origin Syntactic origin of the current receiver.
        @param ctx Invocation context carrying self/super information.
        @return Resolved attribute-dispatch decision.
        """
        attribute_name = _get_attribute_name(selector)
        if attribute_name is None:
            return AttributeDispatchDecision.NOT_APPLICABLE

        # class receivers handled as method sends
        if not isinstance(receiver, RuntimeValue):
            return AttributeDispatchDecision.METHOD

        runtime_receiver = receiver

        if _is_write_selector(selector):
            return AttributeDispatchResolver._resolve_write_dispatch(
                runtime_receiver,
                selector,
                attribute_name,
                lookup_mode,
                receiver_origin,
                ctx,
            )

        return AttributeDispatchResolver._resolve_read_dispatch(
            runtime_receiver,
            attribute_name,
            lookup_mode,
            ctx,
        )
