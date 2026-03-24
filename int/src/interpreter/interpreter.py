"""
This module contains the main logic of the interpreter.

IPP: You must definitely modify this file. Bend it to your will.

Author: Ondřej Ondryáš <iondryas@fit.vut.cz>
Author:
"""

import logging
import re
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

    @staticmethod
    def _validate_xml_declaration(raw_source: bytes) -> None:
        """
        @brief The XML declaration is validated before XML parsing is started.

        The declaration presence, XML version, and encoding are checked here.
        Exact whitespace formatting is not enforced.

        @param raw_source Raw source file content.
        """
        text_prefix = raw_source[:200].decode("ascii", errors="ignore")

        if not text_prefix.startswith("<?xml"):
            raise InterpreterError(
                error_code=ErrorCode.INT_STRUCTURE,
                message="The XML declaration must be present at the beginning of the file.",
            )

        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', text_prefix)
        encoding_match = re.search(r'encoding\s*=\s*["\']([^"\']+)["\']', text_prefix)

        if version_match is None:
            raise InterpreterError(
                error_code=ErrorCode.INT_STRUCTURE,
                message="The XML declaration must define version='1.0'.",
            )

        if encoding_match is None:
            raise InterpreterError(
                error_code=ErrorCode.INT_STRUCTURE,
                message="The XML declaration must define encoding='UTF-8'.",
            )

        xml_version = version_match.group(1)
        xml_encoding = encoding_match.group(1)

        if xml_version != "1.0":
            raise InterpreterError(
                error_code=ErrorCode.INT_STRUCTURE,
                message="The XML declaration must use version='1.0'.",
            )

        if xml_encoding.upper() != "UTF-8":
            raise InterpreterError(
                error_code=ErrorCode.INT_STRUCTURE,
                message="The XML declaration must use encoding='UTF-8'.",
            )

    def load_program(self, source_file_path: Path) -> None:
        """
        @brief The source SOL-XML file is loaded and converted to AST.

        The XML declaration is first validated over the raw input. The XML
        document is then parsed, and the AST model is built from the XML root.

        @param source_file_path A path to the source SOL-XML file.
        """
        logger.info("Opening source file: %s", source_file_path)

        raw_source = source_file_path.read_bytes()
        self._validate_xml_declaration(raw_source)

        try:
            xml_tree = etree.parse(source_file_path)
        except ParseError as error:
            raise InterpreterError(
                error_code=ErrorCode.INT_XML,
                message="Error parsing input XML.",
            ) from error

        try:
            self.loaded_program = Program.from_xml_tree(xml_tree.getroot())  # type: ignore[arg-type]
        except ValidationError as error:
            raise InterpreterError(
                error_code=ErrorCode.INT_STRUCTURE,
                message="Invalid SOL-XML structure.",
            ) from error

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
