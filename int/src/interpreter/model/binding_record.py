"""
@file binding_record.py
@brief Variable-binding metadata is declared.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

A binding record is intended to store one variable binding together with
its initialization and parameter metadata.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .values import RuntimeValue


class BindingRecord:
    """
    @brief One scope binding record is represented by this class.
    """

    value: RuntimeValue | None
    initialized: bool
    is_parameter: bool
    def __init__(
        self,
        value: RuntimeValue | None,
        initialized: bool,
        is_parameter: bool,
    ) -> None:
        """
        @brief One binding record is initialized.

        @param value Stored runtime value or None when no value is currently stored.
        @param initialized Initialization flag of the binding.
        @param is_parameter Parameter flag of the binding.
        """
        self.value = value
        self.initialized = initialized
        self.is_parameter = is_parameter
