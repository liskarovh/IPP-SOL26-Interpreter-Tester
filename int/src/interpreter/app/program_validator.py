"""
@file program_validator.py
@brief Static validation of a loaded AST program is defined.

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY THE AUTHOR.

The validator is responsible only for static checks over the AST model.
No runtime structures are built here, and no expressions are executed here.
"""

from __future__ import annotations

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from ..input_model import ClassDef as AstClassDef
from ..input_model import Method as AstMethod
from ..input_model import Program


class ProgramValidator:
    """
    @brief Static AST validation is performed by this class.
    """

    def __init__(self) -> None:
        """
        @brief Small validator configuration data is initialized.
        """
        self._builtin_parent_names: set[str] = {
            "Object",
            "Nil",
            "True",
            "False",
            "Integer",
            "String",
            "Block",
        }

    def validate(self, program: Program) -> None:
        """
        @brief The complete static validation pipeline is executed.

        @param program A loaded AST program to be validated.
        """
        self._validate_program_header(program)
        self._validate_unique_class_names(program)
        self._validate_class_definitions(program)
        self._validate_methods_in_program(program)
        self._validate_entry_point(program)

    @staticmethod
    def _validate_program_header(program: Program) -> None:
        """
        @brief The top-level program header is validated.

        Only program-level checks are expected to be performed here.
        Class-level and method-level checks should be kept in later steps.

        @param program A loaded AST program to be inspected.
        """
        if program.language != "SOL26":
            raise InterpreterError(
                ErrorCode.INT_STRUCTURE,
                "Unsupported program language, must be 'SOL26'.",
            )

    @staticmethod
    def _validate_unique_class_names(program: Program) -> None:
        """
        @brief Class-name uniqueness is validated.

        @param program A loaded AST program whose classes are to be inspected.
        """
        seen_class_names: set[str] = set()
        for class_def in program.classes:
            if class_def.name in seen_class_names:
                raise InterpreterError(
                    ErrorCode.SEM_ERROR,
                    f"Duplicate class name: {class_def.name}",
                )
            seen_class_names.add(class_def.name)

    def _validate_class_definitions(self, program: Program) -> None:
        """
        @brief Class-level static rules are validated.

        Parent references and other class-definition rules are expected to be
        validated here. Method signatures should not be handled here.

        @param program A loaded AST program to be inspected.
        """
        for class_def in program.classes:
            parent_class = class_def.parent
            if parent_class not in self._builtin_parent_names:
                parent_class_def = self._find_class_by_name(program, parent_class)
                if parent_class_def is None:
                    raise InterpreterError(
                        ErrorCode.SEM_UNDEF,
                        f"Class {class_def.name} "
                        f"references undefined parent class {parent_class}.",
                    )

    def _validate_methods_in_program(self, program: Program) -> None:
        """
        @brief Method-level validation is executed for all classes.

        @param program A loaded AST program to be inspected.
        """
        for class_def in program.classes:
            seen_selectors: set[str] = set()
            for method in class_def.methods:
                if method.selector in seen_selectors:
                    raise InterpreterError(
                        ErrorCode.SEM_ERROR,
                        f"Duplicate selector {method.selector} in class {class_def.name}.",
                    )
                seen_selectors.add(method.selector)
                self._validate_method_signature(method)

    def _validate_method_signature(self, method: AstMethod) -> None:
        """
        @brief The selector and block arity of one method are validated.
        @param method A method definition to be inspected.
        """
        expected_arity = self._selector_arity(method.selector)
        if method.block.arity != expected_arity:
            raise InterpreterError(
                ErrorCode.SEM_ARITY,
                f"Method {method.selector} has arity {method.block.arity}, "
                f"expected {expected_arity}.",
            )

    def _validate_entry_point(self, program: Program) -> None:
        """
        @brief The required program entry point is validated.

        The agreed entry point is expected to be ``Main>>run`` with zero
        arguments. Only that requirement should be checked here.

        @param program A loaded AST program to be inspected.
        """
        main_class = self._find_class_by_name(program, "Main")

        if main_class is None:
            raise InterpreterError(
                ErrorCode.SEM_MAIN,
                "Entry point class 'Main' is not defined.",
            )

        run_method = self._find_method_by_selector(main_class, "run")

        if run_method is None:
            raise InterpreterError(
                ErrorCode.SEM_MAIN,
                "Entry point method 'run' is not defined in class 'Main'.",
            )

        if run_method.block.arity != 0:
            raise InterpreterError(
                ErrorCode.SEM_MAIN,
                "Entry point method 'Main>>run' must not accept arguments.",
            )

    def _find_class_by_name(
        self,
        program: Program,
        class_name: str,
    ) -> AstClassDef | None:
        """
        @brief A class is searched by name in the loaded program.

        @param program A loaded AST program whose classes are to be searched.
        @param class_name A class name to be looked up.
        @return The matching class definition, or ``None`` when no match is found.
        """
        for class_def in program.classes:
            if class_def.name == class_name:
                return class_def

        return None

    def _find_method_by_selector(
        self,
        class_def: AstClassDef,
        selector: str,
    ) -> AstMethod | None:
        """
        @brief A method is searched by selector in one class.

        @param class_def A class whose methods are to be searched.
        @param selector A selector to be looked up.
        @return The matching method, or ``None`` when no match is found.
        """
        for method in class_def.methods:
            if method.selector == selector:
                return method

        return None

    def _selector_arity(self, selector: str) -> int:
        """
        @brief The expected selector arity is computed.

        @param selector A selector whose arity is to be computed.
        @return The expected selector arity.
        """
        return selector.count(":")
