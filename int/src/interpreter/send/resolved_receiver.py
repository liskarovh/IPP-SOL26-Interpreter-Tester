"""
@file resolved_receiver.py
@brief Resolved send-receiver data is represented.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

A resolved receiver carries the effective method receiver together with
the lookup mode and receiver origin selected for one send operation.
"""

from __future__ import annotations

from ..support.send_types import LookupMode, ReceiverOrigin
from ..support.typing_helpers import MethodReceiver


class ResolvedReceiver:
    """
    @brief One resolved send receiver is represented.
    """

    receiver: MethodReceiver
    lookup_mode: LookupMode
    origin: ReceiverOrigin

    def __init__(
        self,
        receiver: MethodReceiver,
        lookup_mode: LookupMode,
        origin: ReceiverOrigin = ReceiverOrigin.ORDINARY,
    ) -> None:
        """
        @brief One resolved send receiver is initialized.

        @param receiver Effective method receiver for the send.
        @param lookup_mode Lookup mode selected for the send.
        @param origin Syntactic receiver origin selected for the send.
        """
        self.receiver = receiver
        self.lookup_mode = lookup_mode
        self.origin = origin
