"""
@file xml_validator.py
@brief XML structure validation is coordinated here.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
"""

from __future__ import annotations

from pathlib import Path

from lxml import etree

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError
from ..input_model import Block, Expr, Program
from ..input_model import Literal as AstLiteral
from ..input_model import Send as AstSend


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


def _validate_order_values(order_values: list[int], what: str) -> None:
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

        _validate_identifier_lexeme(
            keyword_part,
            "selector keyword part",
        )


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
        _validate_class_identifier_lexeme(
            literal.value,
            "class literal value",
        )
        return


def _validate_assign_target_lexeme(target_name: str) -> None:
    """
    @brief One assignment target lexeme is validated.

    @param target_name An assignment target name to be inspected.
    """
    if target_name in {"self", "super", "nil", "true", "false"}:
        return

    _validate_identifier_lexeme(target_name, "variable name")


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


class XmlValidator:
    """
    @brief XML structure validation is coordinated by this class.
    """

    def validate_xml_document(
        self,
        source_file_path: Path,
        xml_tree: etree._ElementTree,
    ) -> etree._Element:
        """
        @brief Document-level SOL-XML validation is performed over a parsed XML tree.

        @param source_file_path A path to the source SOL-XML file.
        @param xml_tree A parsed XML tree.
        @return A validated SOL-XML root element.
        """
        xml_prefix = _read_xml_prefix(source_file_path)
        xml_root = xml_tree.getroot()
        _validate_sol_xml_document(xml_prefix, xml_tree, xml_root)
        return xml_root

    def validate_program_ast(self, program: Program) -> None:
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
            _validate_class_identifier_lexeme(
                class_def.parent,
                "parent class name",
            )

            for method in class_def.methods:
                _validate_selector_lexeme(method.selector)
                self._validate_block_xml_ast(method.block)

    def _validate_block_xml_ast(self, block: Block) -> None:
        """
        @brief One block AST node is validated for additional XML-structure rules.

        @param block A block AST node to be inspected.
        """
        parameter_orders = [parameter.order for parameter in block.parameters]
        _validate_order_values(parameter_orders, "block parameter order")

        for parameter in block.parameters:
            _validate_identifier_lexeme(parameter.name, "parameter name")

        assign_orders = [assign.order for assign in block.assigns]
        _validate_order_values(assign_orders, "assign order")

        for assign in block.assigns:
            _validate_assign_target_lexeme(assign.target.name)
            self._validate_expr_xml_ast(assign.expr)

    def _validate_expr_xml_ast(self, expr: Expr) -> None:
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
            self._validate_block_xml_ast(expr.block)
            return

        if expr.send is not None:
            self._validate_send_xml_ast(expr.send)
            return

    def _validate_send_xml_ast(self, send: AstSend) -> None:
        """
        @brief One send AST node is validated for additional XML-structure rules.

        @param send A send AST node to be inspected.
        """
        _validate_selector_lexeme(send.selector)
        self._validate_expr_xml_ast(send.receiver)

        arg_orders = [arg.order for arg in send.args]
        _validate_order_values(arg_orders, "send argument order")

        for arg in send.args:
            self._validate_expr_xml_ast(arg.expr)
