"""
@file send_types.py
@brief Send-specific enumerations are defined.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Only small enumerations needed by the send layer are stored in this file.
General typing aliases are intended to remain in typing_helpers.py.
"""

from __future__ import annotations

from enum import Enum, auto


class LookupMode(Enum):
    """
    @brief Lookup mode variants for send resolution are represented.
    """

    NORMAL = auto()
    SUPER = auto()


class AttributeDispatchDecision(Enum):
    """
    @brief Attribute-dispatch decision variants are represented.
    """

    METHOD = auto()
    ATTRIBUTE_READ = auto()
    ATTRIBUTE_WRITE = auto()
    CONFLICT = auto()
    NOT_APPLICABLE = auto()


class ReceiverOrigin(Enum):
    """
    @brief Receiver-origin variants for send resolution are represented.
    """

    ORDINARY = auto()
    EXPLICIT_SELF = auto()
    EXPLICIT_SUPER = auto()
