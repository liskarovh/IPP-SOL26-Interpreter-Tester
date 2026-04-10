"""
@file attribute_dispatch_resolver.py
@brief Attribute-dispatch resolution is coordinated here.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

The meaning of one selector for one receiver is intended to be resolved
here for the instance-send branch.
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
    @brief One attribute name is extracted from one valid attribute selector.

    @param selector One selector whose attribute name is to be extracted.
    @return One attribute name when the selector has shape name or name:,
            otherwise None.
    """
    if not ATTRIBUTE_SELECTOR_REGEX.fullmatch(selector):
        return None

    if selector.endswith(":"):
        return selector[:-1]

    return selector


def _is_write_selector(selector: str) -> bool:
    """
    @brief Whether one selector has one write-selector shape is checked.

    @param selector One selector whose shape is to be checked.
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
    @brief Existence of one matching write-selector method is checked.

    @param receiver One runtime receiver whose class hierarchy is to be checked.
    @param selector One write selector whose method form is to be checked.
    @param lookup_mode One lookup mode of the current send.
    @param ctx One invocation context carrying self/super information.
    @return True when one matching method exists, otherwise False.
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
    @brief Existence of one conflicting zero-argument method
    for one new attribute write is checked.

    @param receiver One runtime receiver whose class hierarchy is to be checked.
    @param attribute_name One attribute name whose zero-argument method form is to be checked.
    @param lookup_mode One lookup mode of the current send.
    @param receiver_origin One syntactic origin of the current receiver.
    @param ctx One invocation context carrying self/super information.
    @return True when one conflicting zero-argument method exists, otherwise False.
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
    @brief Existence of one matching zero-argument method is checked.

    @param receiver One runtime receiver whose class hierarchy is to be checked.
    @param attribute_name One attribute name whose read-form selector is to be checked.
    @param lookup_mode One lookup mode of the current send.
    @param ctx One invocation context carrying self/super information.
    @return True when one matching zero-argument method exists, otherwise False.
    """
    start_class = resolve_lookup_start_class(receiver, lookup_mode, ctx)
    return start_class.lookup_instance(attribute_name) is not None


class AttributeDispatchResolver:
    """
    @brief Attribute-dispatch resolution is coordinated by this class.
    """

    @staticmethod
    def _resolve_read_dispatch(
        runtime_receiver: RuntimeValue,
        attribute_name: str,
        lookup_mode: LookupMode,
        ctx: InvocationContext,
    ) -> AttributeDispatchDecision:
        """
        @brief One read-form attribute-dispatch decision is resolved.

        @param runtime_receiver One runtime receiver whose selector meaning is to be resolved.
        @param attribute_name One resolved attribute name.
        @param lookup_mode One lookup mode of the current send.
        @param ctx An invocation context carrying self/super information.
        @return One resolved read-form attribute-dispatch decision.
        """
        slot_storage = runtime_receiver.slots
        if slot_storage is None:
            return AttributeDispatchDecision.METHOD

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
        @brief One write-form attribute-dispatch decision is resolved.

        @param runtime_receiver One runtime receiver whose selector meaning is to be resolved.
        @param selector One write selector whose meaning is to be resolved.
        @param attribute_name One resolved attribute name.
        @param lookup_mode One lookup mode of the current send.
        @param receiver_origin One syntactic origin of the current receiver.
        @param ctx An invocation context carrying self/super information.
        @return One resolved write-form attribute-dispatch decision.
        """
        slot_storage = runtime_receiver.slots
        if slot_storage is None:
            return AttributeDispatchDecision.METHOD

        if _has_matching_write_method(
            runtime_receiver,
            selector,
            lookup_mode,
            ctx,
        ):
            return AttributeDispatchDecision.METHOD

        if slot_storage.has(attribute_name):
            return AttributeDispatchDecision.ATTRIBUTE_WRITE

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
        @brief One attribute-dispatch decision is resolved.

        @param receiver A receiver for which selector meaning is to be resolved.
        @param selector A selector whose meaning is to be resolved.
        @param lookup_mode One lookup mode of the current send.
        @param receiver_origin One syntactic origin of the current receiver.
        @param ctx An invocation context carrying self/super information.
        @return One resolved attribute-dispatch decision.
        """
        attribute_name = _get_attribute_name(selector)
        if attribute_name is None:
            return AttributeDispatchDecision.NOT_APPLICABLE

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
