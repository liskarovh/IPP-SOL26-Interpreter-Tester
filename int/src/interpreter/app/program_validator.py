"""
@file program_validator.py
@brief Static validation of a loaded AST program is implemented.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME

Only static checks over the AST model are performed here.

This module may raise InterpreterError with these codes:
- INT_STRUCTURE for invalid top-level program structure
- SEM_ERROR for general static semantic errors
- SEM_ARITY for selector/block arity mismatches
- SEM_MAIN for missing or invalid entry point
- SEM_COLLISION for assignment to a block parameter
- SEM_UNDEF for undefined classes, selectors, or variables
"""

from __future__ import annotations

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from ..input_model import Assign as AstAssign
from ..input_model import Block as AstBlock
from ..input_model import ClassDef as AstClassDef
from ..input_model import Expr as AstExpr
from ..input_model import Method as AstMethod
from ..input_model import Program
from ..input_model import Send as AstSend
from ..input_model import Var as AstVar


class ProgramValidator:
    """
    @brief Static AST validation is performed by this class.
    """

    def __init__(self) -> None:
        """
        @brief Small validator configuration data is initialized.
        """
        self._builtin_class_names: set[str] = {
            "Object",
            "Nil",
            "True",
            "False",
            "Integer",
            "String",
            "Block",
        }

        self._class_index: dict[str, AstClassDef] = {}

        # class side selectors accepted on every known class
        self._class_side_selectors_on_all_classes: set[str] = {
            "new",
            "from:",
        }

        self._string_class_side_selectors: set[str] = {
            "read",
        }

        # names that cant appear on left side of assignment
        self._special_immutable_names: set[str] = {
            "self",
            "super",
            "nil",
            "true",
            "false",
        }

    def validate(self, program: Program) -> None:
        """
        @brief The complete static validation pipeline is executed.

        @param program A loaded AST program to be validated.
        """
        self._reset_validation_state()
        self._validate_program_header(program)
        self._validate_program_shape(program)
        self._validate_class_semantics(program)
        self._validate_method_semantics(program)
        self._validate_entry_point()

    def _reset_validation_state(self) -> None:
        """
        @brief Validator state from one previous run is cleared.
        """
        self._class_index = {}

    @staticmethod
    def _validate_program_header(program: Program) -> None:
        """
        @brief The top-level program header is validated.

        Only program-level checks are performed here.

        @param program A loaded AST program to be inspected.
        """
        if program.language != "SOL26":
            raise InterpreterError(
                ErrorCode.INT_STRUCTURE,
                "Unsupported program language, must be 'SOL26'.",
            )

    def _validate_program_shape(self, program: Program) -> None:
        """
        @brief Program-shape validation is executed.

        Class-name uniqueness is validated first.
        Class index is prepared for later phases.

        @param program A loaded AST program to be inspected.
        """
        self._validate_unique_class_names(program)
        self._prepare_program_index(program)

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

    def _prepare_program_index(self, program: Program) -> None:
        """
        @brief A user-defined class index is prepared for later validation steps.

        @param program A loaded AST program whose classes are to be indexed.
        """
        for class_def in program.classes:
            self._class_index[class_def.name] = class_def

    def _validate_class_semantics(self, program: Program) -> None:
        """
        @brief Class-level semantic validation is executed.

        @param program A loaded AST program to be inspected.
        """
        for class_def in program.classes:
            self._validate_one_class_semantics(class_def)

        self._validate_inheritance_cycles(program)

    def _validate_one_class_semantics(self, class_def: AstClassDef) -> None:
        """
        @brief One class definition is validated.

        Built-in class-name redefinition and parent-reference validity are
        checked here.

        @param class_def A class definition to be inspected.
        """
        self._validate_builtin_class_redefinition(class_def)
        self._validate_parent_reference(class_def)

    def _validate_method_semantics(self, program: Program) -> None:
        """
        @brief Method-level semantic validation is executed.

        @param program A loaded AST program to be inspected.
        """
        for class_def in program.classes:
            self._validate_one_class_method_semantics(class_def)

    def _validate_one_class_method_semantics(self, class_def: AstClassDef) -> None:
        """
        @brief All methods of one class are validated.

        Duplicate selectors are checked first.
        Method signatures and bodies are then validated in program order.

        @param class_def A class whose methods are inspected.
        """
        seen_selectors: set[str] = set()

        for method in class_def.methods:
            if method.selector in seen_selectors:
                raise InterpreterError(
                    ErrorCode.SEM_ERROR,
                    f"Duplicate selector {method.selector} in class {class_def.name}.",
                )

            seen_selectors.add(method.selector)
            self._validate_method_signature(method)
            self._validate_method_body(method)

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

    def _validate_entry_point(self) -> None:
        """
        @brief The required program entry point is validated.
        """

        # SOL26 requires the entry point Main>>run
        main_class = self._class_index.get("Main")

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

    def _validate_method_body(self, method: AstMethod) -> None:
        """
        @brief The body of one method is validated.

        @param method A method whose body is to be validated.
        """
        visible_names = self._create_initial_method_visible_names()
        parameter_names = self._create_initial_method_parameter_names()
        special_immutable_names = self._create_initial_method_immutable_names()

        self._validate_block(
            method.block,
            visible_names,
            parameter_names,
            special_immutable_names,
        )

    def _create_initial_method_visible_names(self) -> set[str]:
        """
        @brief Initial visible names for one method body are created.

        @return One initial set of names visible in one method body.
        """
        return set(self._special_immutable_names)

    @staticmethod
    def _create_initial_method_parameter_names() -> set[str]:
        """
        @brief Initial method-parameter name storage is created.

        @return One empty set of method-parameter names.
        """
        return set()

    def _create_initial_method_immutable_names(self) -> set[str]:
        """
        @brief Initial immutable names for one method body are created.

        @return One initial set of immutable names in one method body.
        """
        return set(self._special_immutable_names)

    def _validate_block(
        self,
        block: AstBlock,
        visible_names: set[str],
        parameter_names: set[str],
        special_immutable_names: set[str],
    ) -> None:
        """
        @brief One block is validated in its lexical visibility context.

        Current lexical scope is represented by visible names,
        parameter names, and special immutable names.

        @param block A block to be validated.
        @param visible_names Names that may currently be read.
        @param parameter_names Formal block parameters visible in current scope.
        @param special_immutable_names Special names that must never be assigned to.
        """
        # each block gets its own lexical extension of the incoming scope
        local_block_parameter_names = self._validate_one_block_parameters(block)

        (
            local_visible_names,
            local_parameter_names,
            local_special_immutable_names,
        ) = self._extend_scope_for_block(
            visible_names,
            parameter_names,
            special_immutable_names,
            local_block_parameter_names,
        )

        self._validate_block_assignments(
            block,
            local_visible_names,
            local_parameter_names,
            local_special_immutable_names,
        )

    @staticmethod
    def _validate_one_block_parameters(block: AstBlock) -> set[str]:
        """
        @brief Parameter-name uniqueness in one block is validated.

        @param block A block whose parameters are to be inspected.
        @return A set of unique parameter names from the block.
        """
        seen_params: set[str] = set()

        for param in block.parameters:
            if param.name in seen_params:
                raise InterpreterError(
                    ErrorCode.SEM_ERROR,
                    f"Duplicate parameter name: {param.name}",
                )

            seen_params.add(param.name)

        return seen_params

    @staticmethod
    def _extend_scope_for_block(
        visible_names: set[str],
        parameter_names: set[str],
        special_immutable_names: set[str],
        local_block_parameter_names: set[str],
    ) -> tuple[set[str], set[str], set[str]]:
        """
        @brief Lexical scope for one nested block is created.

        @param visible_names Names that may currently be read.
        @param parameter_names Formal block parameters visible in current scope.
        @param special_immutable_names Special names that must never be assigned to.
        @param local_block_parameter_names Unique parameter names of current block.
        @return Extended local visible names, local parameter names,
                and local immutable names.
        """
        local_visible_names = set(visible_names)
        local_parameter_names = set(parameter_names)
        local_special_immutable_names = set(special_immutable_names)

        # block parameters become visible inside the block body
        local_visible_names.update(local_block_parameter_names)
        local_parameter_names.update(local_block_parameter_names)

        return (
            local_visible_names,
            local_parameter_names,
            local_special_immutable_names,
        )

    def _validate_block_assignments(
        self,
        block: AstBlock,
        visible_names: set[str],
        parameter_names: set[str],
        special_immutable_names: set[str],
    ) -> None:
        """
        @brief All assignments of one block are validated.

        Assignment targets are added to visible names only after
        the corresponding assignment has been validated.

        @param block A block whose assignments are inspected.
        @param visible_names Names that may currently be read.
        @param parameter_names Formal block parameters visible in current scope.
        @param special_immutable_names Special names that must never be assigned to.
        """
        for assign in block.assigns:
            target_name = self._validate_assign(
                assign,
                visible_names,
                parameter_names,
                special_immutable_names,
            )

            # name becomes visible
            visible_names.add(target_name)

    def _validate_assign(
        self,
        assign: AstAssign,
        visible_names: set[str],
        parameter_names: set[str],
        special_immutable_names: set[str],
    ) -> str:
        """
        @brief One assignment is validated.

        Assignment target is classified first.
        Formal block parameters are rejected with SEM_COLLISION.
        Special built-in names are rejected with SEM_ERROR.
        Right-hand expression is validated only after target is accepted.

        @param assign An assignment to be inspected.
        @param visible_names Names that may currently be read.
        @param parameter_names Formal block parameters visible in current scope.
        @param special_immutable_names Special names that must never be assigned to.
        @return Validated assignment target name.
        """
        target_name = assign.target.name

        self._validate_assignment_target(
            target_name,
            parameter_names,
            special_immutable_names,
        )
        self._validate_assignment_expr(
            assign,
            visible_names,
            parameter_names,
            special_immutable_names,
        )

        return target_name

    @staticmethod
    def _validate_assignment_target(
        target_name: str,
        parameter_names: set[str],
        special_immutable_names: set[str],
    ) -> None:
        """
        @brief One assignment target is validated.

        @param target_name One assignment target name to be inspected.
        @param parameter_names Formal block parameters visible in the current scope.
        @param special_immutable_names Special names that must never be assigned to.
        """
        if target_name in parameter_names:
            raise InterpreterError(
                ErrorCode.SEM_COLLISION,
                f"Cannot assign to block parameter {target_name}.",
            )

        if target_name in special_immutable_names:
            raise InterpreterError(
                ErrorCode.SEM_ERROR,
                f"Cannot assign to special name {target_name}.",
            )

    def _validate_assignment_expr(
        self,
        assign: AstAssign,
        visible_names: set[str],
        parameter_names: set[str],
        special_immutable_names: set[str],
    ) -> None:
        """
        @brief The right-hand side of one assignment is validated.

        @param assign One assignment whose expression is to be inspected.
        @param visible_names Names that may currently be read.
        @param parameter_names Formal block parameters visible in the current scope.
        @param special_immutable_names Special names that must never be assigned to.
        """
        self._validate_expr(
            assign.expr,
            visible_names,
            parameter_names,
            special_immutable_names,
        )

    def _validate_expr(
        self,
        expr: AstExpr,
        visible_names: set[str],
        parameter_names: set[str],
        special_immutable_names: set[str],
    ) -> None:
        """
        @brief One expression is validated.

        @param expr An expression to be inspected.
        @param visible_names Names that may currently be read.
        @param parameter_names Formal block parameters visible in the current scope.
        @param special_immutable_names Special names that must never be assigned to.
        """
        if self._validate_literal_expr(expr):
            return

        if self._validate_var_expr(expr, visible_names):
            return

        if self._validate_block_expr(
            expr,
            visible_names,
            parameter_names,
            special_immutable_names,
        ):
            return

        if self._validate_send_expr(
            expr,
            visible_names,
            parameter_names,
            special_immutable_names,
        ):
            return

    @staticmethod
    def _validate_literal_expr(expr: AstExpr) -> bool:
        """
        @brief One literal expression shape is checked.

        @param expr An expression to be inspected.
        @return True when the expression is one literal, otherwise False.
        """
        return expr.literal is not None

    def _validate_var_expr(
        self,
        expr: AstExpr,
        visible_names: set[str],
    ) -> bool:
        """
        @brief One variable-read expression is validated.

        @param expr An expression to be inspected.
        @param visible_names Names that may currently be read.
        @return True when the expression is one variable-read expression,
                otherwise False.
        """
        if expr.var is None:
            return False

        self._validate_variable_read(expr.var, visible_names)
        return True

    def _validate_block_expr(
        self,
        expr: AstExpr,
        visible_names: set[str],
        parameter_names: set[str],
        special_immutable_names: set[str],
    ) -> bool:
        """
        @brief One block expression is validated.

        @param expr An expression to be inspected.
        @param visible_names Names that may currently be read.
        @param parameter_names Formal block parameters visible in the current scope.
        @param special_immutable_names Special names that must never be assigned to.
        @return True when the expression is one block expression,
                otherwise False.
        """
        if expr.block is None:
            return False

        self._validate_block(
            expr.block,
            visible_names,
            parameter_names,
            special_immutable_names,
        )
        return True

    def _validate_send_expr(
        self,
        expr: AstExpr,
        visible_names: set[str],
        parameter_names: set[str],
        special_immutable_names: set[str],
    ) -> bool:
        """
        @brief One send expression is validated.

        @param expr An expression to be inspected.
        @param visible_names Names that may currently be read.
        @param parameter_names Formal block parameters visible in the current scope.
        @param special_immutable_names Special names that must never be assigned to.
        @return True when the expression is one send expression,
                otherwise False.
        """
        if expr.send is None:
            return False

        self._validate_send(
            expr.send,
            visible_names,
            parameter_names,
            special_immutable_names,
        )
        return True

    @staticmethod
    def _validate_variable_read(
        var: AstVar,
        visible_names: set[str],
    ) -> None:
        """
        @brief A variable read is validated.

        A variable is expected to be visible at the point where it is read.

        @param var A variable reference to be inspected.
        @param visible_names Names that may currently be read.
        """
        var_name = var.name

        if var_name not in visible_names:
            raise InterpreterError(
                ErrorCode.SEM_UNDEF,
                f"Variable {var_name} is not visible here.",
            )

    def _validate_send(
        self,
        send: AstSend,
        visible_names: set[str],
        parameter_names: set[str],
        special_immutable_names: set[str],
    ) -> None:
        """
        @brief A send expression is validated.

        The receiver and all argument expressions are validated first.
        After that, a special static check is performed only for sends
        whose receiver is a class literal.

        @param send A send expression to be inspected.
        @param visible_names Names that may currently be read.
        @param parameter_names Formal block parameters visible in the current scope.
        @param special_immutable_names Special names that must never be assigned to.
        """
        self._validate_send_receiver(
            send,
            visible_names,
            parameter_names,
            special_immutable_names,
        )
        self._validate_send_arguments(
            send,
            visible_names,
            parameter_names,
            special_immutable_names,
        )
        self._validate_send_class_literal_rules(send)

    def _validate_send_receiver(
        self,
        send: AstSend,
        visible_names: set[str],
        parameter_names: set[str],
        special_immutable_names: set[str],
    ) -> None:
        """
        @brief The receiver of one send expression is validated.

        @param send A send expression whose receiver is to be inspected.
        @param visible_names Names that may currently be read.
        @param parameter_names Formal block parameters visible in the current scope.
        @param special_immutable_names Special names that must never be assigned to.
        """
        self._validate_expr(
            send.receiver,
            visible_names,
            parameter_names,
            special_immutable_names,
        )

    def _validate_send_arguments(
        self,
        send: AstSend,
        visible_names: set[str],
        parameter_names: set[str],
        special_immutable_names: set[str],
    ) -> None:
        """
        @brief All argument expressions of one send are validated.

        @param send A send expression whose arguments are to be inspected.
        @param visible_names Names that may currently be read.
        @param parameter_names Formal block parameters visible in the current scope.
        @param special_immutable_names Special names that must never be assigned to.
        """
        for arg in send.args:
            self._validate_expr(
                arg.expr,
                visible_names,
                parameter_names,
                special_immutable_names,
            )

    def _validate_send_class_literal_rules(self, send: AstSend) -> None:
        """
        @brief Static class-literal receiver rules of one send are validated.

        @param send A send expression to be inspected.
        """
        receiver_literal = send.receiver.literal
        if receiver_literal is None:
            return

        if receiver_literal.class_id != "class":
            return

        self._validate_class_literal_send(send)

    def _validate_builtin_class_redefinition(self, class_def: AstClassDef) -> None:
        """
        @brief Redefinition of a built-in class name is validated.

        @param class_def A class definition to be inspected.
        """
        if class_def.name in self._builtin_class_names:
            raise InterpreterError(
                ErrorCode.SEM_ERROR,
                f"Cannot redefine built-in class {class_def.name}.",
            )

    def _validate_parent_reference(self, class_def: AstClassDef) -> None:
        """
        @brief Existence of one class parent is validated.

        @param class_def A class definition to be inspected.
        """
        parent_class = class_def.parent

        if parent_class in self._builtin_class_names:
            return

        if parent_class not in self._class_index:
            raise InterpreterError(
                ErrorCode.SEM_UNDEF,
                f"Class {class_def.name} references undefined parent class {parent_class}.",
            )

    def _validate_inheritance_cycles(self, program: Program) -> None:
        """
        @brief Cycles in the inheritance graph are validated.

        @param program A loaded AST program whose inheritance graph is to be inspected.
        """
        for class_def in program.classes:
            visited_in_this_chain: set[str] = set()
            current_class_name = class_def.name

            while current_class_name in self._class_index:
                if current_class_name in visited_in_this_chain:
                    raise InterpreterError(
                        ErrorCode.SEM_ERROR,
                        f"Inheritance cycle detected at class {current_class_name}.",
                    )

                visited_in_this_chain.add(current_class_name)
                current_class_name = self._class_index[current_class_name].parent

                if current_class_name in self._builtin_class_names:
                    break

    def _validate_class_literal_send(self, send: AstSend) -> None:
        """
        @brief A send on a class-literal receiver is validated.

        @param send A send expression whose receiver is expected to be a class literal.
        """
        receiver_literal = send.receiver.literal
        if receiver_literal is None:
            return

        target_class_name = receiver_literal.value

        if not self._is_known_class_name(target_class_name):
            raise InterpreterError(
                ErrorCode.SEM_UNDEF,
                f"Unknown class literal {target_class_name}.",
            )

        if not self._class_understands_class_side_selector(
            target_class_name,
            send.selector,
        ):
            raise InterpreterError(
                ErrorCode.SEM_UNDEF,
                f"Class {target_class_name} does not understand class selector {send.selector}.",
            )

    def _is_known_class_name(self, class_name: str) -> bool:
        """
        @brief Existence of a class name is checked.

        @param class_name A class name to be checked.
        @return True when the class name is known, otherwise False.
        """
        if class_name in self._builtin_class_names:
            return True

        return class_name in self._class_index

    def _class_understands_class_side_selector(
        self,
        class_name: str,
        selector: str,
    ) -> bool:
        """
        @brief Availability of a class-side selector is checked.

        Class-side constructors new and from: are accepted on all existing
        classes. The extra class-side selector read is accepted only on
        String and its subclasses.

        @param class_name A target class name.
        @param selector A class-side selector to be checked.
        @return True when the selector is valid for the class, otherwise False.
        """
        if selector in self._class_side_selectors_on_all_classes:
            return True

        if selector in self._string_class_side_selectors:
            return self._inherits_from_class(class_name, "String")

        return False

    def _inherits_from_class(
        self,
        class_name: str,
        expected_ancestor_name: str,
    ) -> bool:
        """
        @brief Inheritance from one ancestor class is checked.

        @param class_name A class name from which the check is started.
        @param expected_ancestor_name An ancestor class name to be looked for.
        @return True when the ancestor is found, otherwise False.
        """
        current_class_name = class_name

        while True:
            if current_class_name == expected_ancestor_name:
                return True

            if current_class_name in self._builtin_class_names:
                return False

            current_class_def = self._class_index.get(current_class_name)
            if current_class_def is None:
                return False

            current_class_name = current_class_def.parent

    @staticmethod
    def _find_method_by_selector(
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

    @staticmethod
    def _selector_arity(selector: str) -> int:
        """
        @brief The expected selector arity is computed.

        @param selector A selector whose arity is to be computed.
        @return The expected selector arity.
        """
        return selector.count(":")
