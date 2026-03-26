"""
This module contains the main logic of the interpreter.

IPP: You must definitely modify this file. Bend it to your will.

Author: Ondřej Ondryáš <iondryas@fit.vut.cz>
Author:
"""

import logging
from pathlib import Path

from lxml import etree
from lxml.etree import ParseError
from pydantic import ValidationError

from .app.program_runner import ProgramRunner
from .error_codes import ErrorCode
from .exceptions import InterpreterError
from .input_model import Arg, Assign, Block, ClassDef, Expr, Method, Program
from .input_model import Literal as AstLiteral
from .input_model import Send as AstSend
from .input_model import Var as AstVar

logger = logging.getLogger(__name__)


# ALL OF AST PRINT FUNCTIONS ARE AI GENERATED https://chatgpt.com/share/69bffe90-dcb4-800b-a921-2062efeb157a
def dump_program_ast(program: Program | None) -> None:
    """
    @brief A loaded AST is printed to standard output in a structured form.

    A readable tree-like dump is produced for debugging purposes.
    If no program is loaded, an informative message is printed instead.

    @param program A loaded SOL-XML program AST, or None.
    """
    if program is None:
        print("AST: <no program loaded>")
        return

    _dump_program(program, indent=0)


def _print_ast_line(indent: int, text: str) -> None:
    """
    @brief One indented AST output line is printed.

    A two-space indentation unit is used.

    @param indent The indentation depth.
    @param text The text to be printed.
    """
    print(f"{'  ' * indent}{text}")


def _dump_program(program: Program, indent: int) -> None:
    """
    @brief A program node is printed.

    The program metadata and all contained classes are printed.

    @param program The program AST node.
    @param indent The current indentation depth.
    """
    _print_ast_line(
        indent,
        f"Program(language={program.language!r}, description={program.description!r})",
    )
    _print_ast_line(indent + 1, f"classes[{len(program.classes)}]")

    for class_index, class_def in enumerate(program.classes, start=1):
        _dump_class_def(class_def, indent + 2, class_index)


def _dump_class_def(class_def: ClassDef, indent: int, class_index: int) -> None:
    """
    @brief A class definition node is printed.

    The class metadata and all contained methods are printed.

    @param class_def The class definition AST node.
    @param indent The current indentation depth.
    @param class_index The one-based class index within the program.
    """
    _print_ast_line(
        indent,
        f"Class[{class_index}] name={class_def.name!r} parent={class_def.parent!r}",
    )
    _print_ast_line(indent + 1, f"methods[{len(class_def.methods)}]")

    for method_index, method in enumerate(class_def.methods, start=1):
        _dump_method(method, indent + 2, method_index)


def _dump_method(method: Method, indent: int, method_index: int) -> None:
    """
    @brief A method node is printed.

    The selector and method block are printed.

    @param method The method AST node.
    @param indent The current indentation depth.
    @param method_index The one-based method index within the class.
    """
    _print_ast_line(indent, f"Method[{method_index}] selector={method.selector!r}")
    _dump_block(method.block, indent + 1)


def _dump_block(block: Block, indent: int) -> None:
    """
    @brief A block node is printed.

    The block arity, parameters, and assignments are printed.

    @param block The block AST node.
    @param indent The current indentation depth.
    """
    _print_ast_line(
        indent,
        (
            f"Block(arity={block.arity}, "
            f"parameters={len(block.parameters)}, assigns={len(block.assigns)})"
        ),
    )

    _print_ast_line(indent + 1, f"parameters[{len(block.parameters)}]")
    for parameter in block.parameters:
        _print_ast_line(
            indent + 2,
            f"Parameter(order={parameter.order}, name={parameter.name!r})",
        )

    _print_ast_line(indent + 1, f"assigns[{len(block.assigns)}]")
    for assign_index, assign in enumerate(block.assigns, start=1):
        _dump_assign(assign, indent + 2, assign_index)


def _dump_assign(assign: Assign, indent: int, assign_index: int) -> None:
    """
    @brief An assignment node is printed.

    The assignment order, target variable, and assigned expression are printed.

    @param assign The assignment AST node.
    @param indent The current indentation depth.
    @param assign_index The one-based assignment index within the block.
    """
    _print_ast_line(
        indent,
        f"Assign[{assign_index}] order={assign.order} target={assign.target.name!r}",
    )
    _dump_expr(assign.expr, indent + 1)


def _dump_expr(expr: Expr, indent: int) -> None:
    """
    @brief An expression node is printed.

    The active expression variant is detected and printed recursively.

    @param expr The expression AST node.
    @param indent The current indentation depth.
    """
    if expr.literal is not None:
        _print_ast_line(indent, "Expr(kind='literal')")
        _dump_literal(expr.literal, indent + 1)
        return

    if expr.var is not None:
        _print_ast_line(indent, "Expr(kind='var')")
        _dump_var(expr.var, indent + 1)
        return

    if expr.block is not None:
        _print_ast_line(indent, "Expr(kind='block')")
        _dump_block(expr.block, indent + 1)
        return

    if expr.send is not None:
        _print_ast_line(indent, "Expr(kind='send')")
        _dump_send(expr.send, indent + 1)
        return

    _print_ast_line(indent, "Expr(kind='<invalid>')")


def _dump_literal(literal: AstLiteral, indent: int) -> None:
    """
    @brief A literal node is printed.

    The literal class identifier and raw value are printed.

    @param literal The literal AST node.
    @param indent The current indentation depth.
    """
    _print_ast_line(
        indent,
        f"Literal(class_id={literal.class_id!r}, value={literal.value!r})",
    )


def _dump_var(var: AstVar, indent: int) -> None:
    """
    @brief A variable node is printed.

    The variable name is printed.

    @param var The variable AST node.
    @param indent The current indentation depth.
    """
    _print_ast_line(indent, f"Var(name={var.name!r})")


def _dump_send(send: AstSend, indent: int) -> None:
    """
    @brief A send node is printed.

    The selector, receiver expression, and ordered arguments are printed.

    @param send The send AST node.
    @param indent The current indentation depth.
    """
    _print_ast_line(
        indent,
        f"Send(selector={send.selector!r}, args={len(send.args)})",
    )

    _print_ast_line(indent + 1, "receiver")
    _dump_expr(send.receiver, indent + 2)

    _print_ast_line(indent + 1, f"args[{len(send.args)}]")
    for arg in send.args:
        _dump_arg(arg, indent + 2)


def _dump_arg(arg: Arg, indent: int) -> None:
    """
    @brief An argument node is printed.

    The argument order and expression are printed.

    @param arg The argument AST node.
    @param indent The current indentation depth.
    """
    _print_ast_line(indent, f"Arg(order={arg.order})")
    _dump_expr(arg.expr, indent + 1)


def _read_xml_prefix(source_file_path: Path) -> bytes:
    """
    @brief A short initial XML file prefix is read.

    Only a small byte prefix is read so that the XML declaration can
    be checked without loading the entire file for that purpose.

    @param source_file_path A path to the source SOL-XML file.
    @return A short initial byte prefix of the source file.
    """
    with source_file_path.open("rb") as source_file:
        return source_file.read(512)

def _validate_root_language(xml_root: etree._Element) -> None:
    """
    @brief The root language attribute is validated.

    @param xml_root A parsed XML root element.
    """
    language = xml_root.get("language")

    if language != "SOL26":
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            "Root 'language' attribute must be 'SOL26'.",
        )


def _validate_root_tag(xml_root: etree._Element) -> None:
    """
    @brief The XML root tag is validated.

    The root tag is expected to be checked before the XML tree is converted
    into the AST model.

    @param xml_root A parsed XML root element.
    """
    if xml_root.tag != "program":
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            "Root tag must be 'program'.",
        )

def _validate_xml_declaration(
        xml_prefix: bytes,
        xml_tree: etree._ElementTree,
) -> None:
    """
    @brief The XML declaration is validated.

    The declaration presence is checked over the raw file prefix.
    Parsed declaration values are then checked over XML document info.

    @param xml_prefix A short initial byte prefix of the input file.
    @param xml_tree A parsed XML tree.
    """
    stripped_prefix = xml_prefix.lstrip()

    if not stripped_prefix.startswith(b"<?xml"):
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            "XML declaration is missing or not at the beginning of the file.",
        )

    declaration_end = stripped_prefix.find(b"?>")
    if declaration_end == -1:
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            "XML declaration is not properly closed.",
        )

    if xml_tree.docinfo.xml_version != "1.0":
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            'XML declaration must specify version "1.0".',
        )

    if xml_tree.docinfo.encoding != "UTF-8":
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            'XML declaration must specify encoding "UTF-8".',
        )

def _validate_sol_xml_document(
        xml_prefix: bytes,
        xml_tree: etree._ElementTree,
        xml_root: etree._Element,
) -> None:
    """
    @brief Document-level SOL-XML rules are validated.

    @param xml_prefix A short initial byte prefix of the input file.
    @param xml_tree A parsed XML tree.
    @param xml_root A parsed XML root element.
    """
    _validate_xml_declaration(xml_prefix, xml_tree)
    _validate_root_tag(xml_root)
    _validate_root_language(xml_root)


def _validate_sol_xml_ast(program: Program) -> None:
    """
    @brief Additional SOL-XML structure checks over the parsed AST are validated.

    This validation pass is executed only after:
    - the XML document is well-formed,
    - document-level XML checks succeed,
    - and Program.from_xml_tree() already created the AST model.

    @param program A parsed SOL-XML program AST.
    """
    for class_def in program.classes:
        _validate_class_identifier_lexeme(class_def.name, "class name")
        _validate_class_identifier_lexeme(class_def.parent, "parent class name")

        for method in class_def.methods:
            _validate_selector_lexeme(method.selector)
            _validate_block_xml_ast(method.block)


def _validate_block_xml_ast(block: Block) -> None:
    """
    @brief One block AST node is validated for additional XML-structure rules.

    @param block A block AST node to be inspected.
    """
    parameter_orders = [parameter.order for parameter in block.parameters]
    _validate_contiguous_order_values(parameter_orders, "block parameter order")

    for parameter in block.parameters:
        _validate_identifier_lexeme(parameter.name, "parameter name")

    assign_orders = [assign.order for assign in block.assigns]
    _validate_contiguous_order_values(assign_orders, "assign order")

    for assign in block.assigns:
        _validate_assign_target_lexeme(assign.target.name)
        _validate_expr_xml_ast(assign.expr)


def _validate_expr_xml_ast(expr: Expr) -> None:
    """
    @brief One expression AST node is validated for additional XML-structure rules.

    @param expr An expression AST node to be inspected.
    """
    if expr.literal is not None:
        _validate_literal_xml_ast(expr.literal)
        return

    if expr.var is not None:
        if expr.var.name in {"self", "super", "nil", "true", "false"}:
            return

        _validate_identifier_lexeme(expr.var.name, "variable name")
        return

    if expr.block is not None:
        _validate_block_xml_ast(expr.block)
        return

    if expr.send is not None:
        _validate_send_xml_ast(expr.send)
        return


def _validate_send_xml_ast(send: AstSend) -> None:
    """
    @brief One send AST node is validated for additional XML-structure rules.

    @param send A send AST node to be inspected.
    """
    _validate_selector_lexeme(send.selector)
    _validate_expr_xml_ast(send.receiver)

    arg_orders = [arg.order for arg in send.args]
    _validate_contiguous_order_values(arg_orders, "send argument order")

    for arg in send.args:
        _validate_expr_xml_ast(arg.expr)


def _validate_literal_xml_ast(literal: AstLiteral) -> None:
    """
    @brief One literal AST node is validated for additional XML-structure rules.

    @param literal A literal AST node to be inspected.
    """
    allowed_literal_classes = {
        "Integer",
        "String",
        "Nil",
        "True",
        "False",
        "class",
    }

    if literal.class_id not in allowed_literal_classes:
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            f"Unsupported literal class: {literal.class_id}",
        )

    if literal.class_id == "Integer":
        value = literal.value

        if not value:
            raise InterpreterError(
                ErrorCode.INT_STRUCTURE,
                "Integer literal value must not be empty.",
            )

        start_index = 0
        if value[0] in {"+", "-"}:
            if len(value) == 1:
                raise InterpreterError(
                    ErrorCode.INT_STRUCTURE,
                    f"Invalid integer literal value: {literal.value}",
                )
            start_index = 1

        for character in value[start_index:]:
            if not character.isdigit():
                raise InterpreterError(
                    ErrorCode.INT_STRUCTURE,
                    f"Invalid integer literal value: {literal.value}",
                )

        return

    if literal.class_id == "Nil":
        if literal.value != "nil":
            raise InterpreterError(
                ErrorCode.INT_STRUCTURE,
                f"Invalid Nil literal value: {literal.value}",
            )
        return

    if literal.class_id == "True":
        if literal.value != "true":
            raise InterpreterError(
                ErrorCode.INT_STRUCTURE,
                f"Invalid True literal value: {literal.value}",
            )
        return

    if literal.class_id == "False":
        if literal.value != "false":
            raise InterpreterError(
                ErrorCode.INT_STRUCTURE,
                f"Invalid False literal value: {literal.value}",
            )
        return

    if literal.class_id == "class":
        _validate_class_identifier_lexeme(literal.value, "class literal value")
        return


def _validate_identifier_lexeme(identifier: str, what: str) -> None:
    """
    @brief One normal identifier lexeme is validated.

    @param identifier An identifier value to be inspected.
    @param what A short label describing what is being validated.
    """
    if identifier == "_":
        return

    reserved_keywords = {"class", "self", "super", "nil", "true", "false"}
    if identifier in reserved_keywords:
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            f"Reserved keyword cannot be used as {what}: {identifier}",
        )

    if not identifier:
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            f"Invalid {what}: identifier must not be empty.",
        )

    first_character = identifier[0]
    if not first_character.islower():
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            f"Invalid {what}: {identifier}",
        )

    for character in identifier[1:]:
        if character.isalnum() or character == "_":
            continue

        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            f"Invalid {what}: {identifier}",
        )

def _validate_assign_target_lexeme(target_name: str) -> None:
    """
    @brief One assignment target lexeme is validated.

    @param target_name An assignment target name to be inspected.
    """
    if target_name in {"self", "super", "nil", "true", "false"}:
        return

    _validate_identifier_lexeme(target_name, "variable name")

def _validate_class_identifier_lexeme(identifier: str, what: str) -> None:
    """
    @brief One class identifier lexeme is validated.

    @param identifier A class identifier value to be inspected.
    @param what A short label describing what is being validated.
    """
    if not identifier:
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            f"Invalid {what}: identifier must not be empty.",
        )

    first_character = identifier[0]
    if not first_character.isupper():
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            f"Invalid {what}: {identifier}",
        )

    for character in identifier[1:]:
        if character.isalnum() or character == "_":
            continue

        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            f"Invalid {what}: {identifier}",
        )


def _validate_selector_lexeme(selector: str) -> None:
    """
    @brief One selector lexeme is validated.

    @param selector A selector value to be inspected.
    """
    reserved_keywords = {"class", "self", "super", "nil", "true", "false"}
    if selector in reserved_keywords:
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            f"Reserved keyword cannot be used as selector: {selector}",
        )

    if not selector:
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            "Selector must not be empty.",
        )

    if ":" not in selector:
        _validate_identifier_lexeme(selector, "selector")
        return

    if not selector.endswith(":"):
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            f"Invalid selector: {selector}",
        )

    selector_parts = selector.split(":")
    keyword_parts = selector_parts[:-1]

    if not keyword_parts:
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            f"Invalid selector: {selector}",
        )

    for keyword_part in keyword_parts:
        if keyword_part == "":
            raise InterpreterError(
                ErrorCode.INT_STRUCTURE,
                f"Invalid selector: {selector}",
            )

        _validate_identifier_lexeme(keyword_part, "selector keyword part")


def _validate_contiguous_order_values(order_values: list[int], what: str) -> None:
    """
    @brief A list of order values is validated as contiguous from one.

    @param order_values Order values to be inspected.
    @param what A short label describing what is being validated.
    """
    sorted_order_values = sorted(order_values)
    expected_order_values = list(range(1, len(order_values) + 1))

    if sorted_order_values != expected_order_values:
        raise InterpreterError(
            ErrorCode.INT_STRUCTURE,
            f"Invalid {what}: {order_values}",
        )


class Interpreter:
    """
    @brief The main interpreter object is defined.

    The source file is loaded, converted to the AST model, and later
    forwarded to the program runner.
    """

    def __init__(self) -> None:
        """
        @brief The interpreter is initialized.

        A program runner is prepared, and no program is loaded initially.
        """
        self.program_runner = ProgramRunner()
        self.loaded_program: Program | None = None

    def load_program(self, source_file_path: Path) -> None:
        """
        @brief The source SOL-XML file is loaded and converted to AST.

        The XML file is first parsed as a well-formed XML document. After that,
        document-level SOL-XML checks are performed. Finally, the AST model is
        built from the validated XML root.

        @param source_file_path A path to the source SOL-XML file.
        """
        logger.info("Opening source file: %s", source_file_path)

        xml_prefix = _read_xml_prefix(source_file_path)

        try:
            xml_tree = etree.parse(source_file_path)
        except ParseError as error:
            raise InterpreterError(
                error_code=ErrorCode.INT_XML,
                message="Error parsing input XML.",
            ) from error

        xml_root = xml_tree.getroot()
        _validate_sol_xml_document(xml_prefix, xml_tree, xml_root)

        try:
            parsed_program = Program.from_xml_tree(xml_root)  # type: ignore[arg-type]
        except ValidationError as error:
            raise InterpreterError(
                error_code=ErrorCode.INT_STRUCTURE,
                message="Invalid SOL-XML structure.",
            ) from error

        _validate_sol_xml_ast(parsed_program)
        self.loaded_program = parsed_program

    def execute(self, input_io: object) -> None:
        """
        @brief A previously loaded program is forwarded to the runner.

        @param input_io An input/output adapter.
        """
        program = self.loaded_program
        if program is None:
            return

        dump_program_ast(program)
        self.program_runner.run(program, input_io)
