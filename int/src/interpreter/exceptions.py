"""
This module defines the custom exception classes used by the interpreter to represent various error
conditions that can occur during interpretation.

IPP: You can freely modify this file and add any additional exception classes.
     However, the InterpreterError class must be used as a base for any exceptions that control
     the outcome of the interpretation (i.e., those that are caught in solint.py and cause
     the interpreter to exit with a specific error code).
"""

from .error_codes import ErrorCode


class InterpreterError(Exception):
    """
    Base class for all interpreter-controlled errors.

    Any exception that should be caught in solint.py and translated to a specific
    interpreter exit code must inherit from this class.
    """

    def __init__(self, error_code: ErrorCode, message: str | None = None) -> None:
        resolved_message = message or error_code.name
        super().__init__(resolved_message)
        self.error_code = error_code
        self.message = resolved_message


# ============================================================================
# XML / input interpretation errors
# ============================================================================


class XmlError(InterpreterError):
    """Base class for XML-related interpreter errors."""

    def __init__(self, error_code: ErrorCode, message: str | None = None) -> None:
        super().__init__(error_code, message)


class XmlFormatError(XmlError):
    """Error 20: malformed / unparsable XML input."""

    def __init__(self, message: str = "Invalid XML input.") -> None:
        super().__init__(ErrorCode.INT_XML, message)


class XmlStructureError(XmlError):
    """Error 42: unexpected SOL-XML structure."""

    def __init__(self, message: str = "Invalid SOL-XML structure.") -> None:
        super().__init__(ErrorCode.INT_STRUCTURE, message)


# ============================================================================
# Static semantic errors
# ============================================================================


class StaticSemanticError(InterpreterError):
    """Base class for static semantic errors."""

    def __init__(self, error_code: ErrorCode, message: str | None = None) -> None:
        super().__init__(error_code, message)


class MissingMainRunError(StaticSemanticError):
    """Error 31: missing Main class or its instance method run."""

    def __init__(self, message: str = "Missing class Main or its instance method run.") -> None:
        super().__init__(ErrorCode.SEM_MAIN, message)


class UndefinedEntityError(StaticSemanticError):
    """Error 32: undefined variable / parameter / class / class method."""

    def __init__(self, message: str = "Use of an undefined entity.") -> None:
        super().__init__(ErrorCode.SEM_UNDEF, message)


class MethodBlockArityError(StaticSemanticError):
    """Error 33: method selector arity does not match method block arity."""

    def __init__(
        self,
        message: str = "Method selector arity does not match block arity.",
    ) -> None:
        super().__init__(ErrorCode.SEM_ARITY, message)


class AssignmentToParameterError(StaticSemanticError):
    """Error 34: assignment to a formal block parameter."""

    def __init__(self, message: str = "Assignment to a formal block parameter.") -> None:
        super().__init__(ErrorCode.SEM_COLLISION, message)


class OtherStaticSemanticError(StaticSemanticError):
    """Error 35: other static semantic error."""

    def __init__(self, message: str = "Other static semantic error.") -> None:
        super().__init__(ErrorCode.SEM_ERROR, message)


# ============================================================================
# Runtime interpretation errors
# ============================================================================


class RuntimeInterpretationError(InterpreterError):
    """Base class for runtime interpretation errors."""

    def __init__(self, error_code: ErrorCode, message: str | None = None) -> None:
        super().__init__(error_code, message)


class DoesNotUnderstandError(RuntimeInterpretationError):
    """Error 51: receiver does not understand the message."""

    def __init__(self, message: str = "Receiver does not understand the message.") -> None:
        super().__init__(ErrorCode.INT_DNU, message)


class OtherRuntimeError(RuntimeInterpretationError):
    """Error 52: other runtime interpretation error."""

    def __init__(self, message: str = "Other runtime interpretation error.") -> None:
        super().__init__(ErrorCode.INT_OTHER, message)


class InvalidArgumentValueError(RuntimeInterpretationError):
    """Error 53: invalid argument value."""

    def __init__(self, message: str = "Invalid argument value.") -> None:
        super().__init__(ErrorCode.INT_INVALID_ARG, message)


class InstanceAttributeCollisionError(RuntimeInterpretationError):
    """Error 54: attempted instance attribute creation collides with a method."""

    def __init__(
        self,
        message: str = "Instance attribute name collides with an existing method.",
    ) -> None:
        super().__init__(ErrorCode.INT_INST_ATTR, message)


# ============================================================================
# Internal interpreter error
# ============================================================================


class InternalInterpreterError(InterpreterError):
    """Error 99: unexpected internal interpreter error."""

    def __init__(self, message: str = "Unexpected internal interpreter error.") -> None:
        super().__init__(ErrorCode.GENERAL_OTHER, message)
