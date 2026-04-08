"""
@file xml_validator.py
@brief XML structure validation is coordinated here.
@author Hana Liškařová xliskah00

DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
"""

from __future__ import annotations

from pathlib import Path

from lxml import etree
from lxml.etree import ParseError

from ..error_codes import ErrorCode
from ..exceptions import InterpreterError


class XmlValidator:
    """
    @brief XML structure validation is coordinated by this class.
    """

    def validate_xml(self, source_file_path: Path) -> etree._Element:
        """
        @brief The source SOL-XML file is validated.

        @param source_file_path A path to the source SOL-XML file.
        @return A validated SOL-XML root element.
        """
        xml_prefix = self._read_xml_prefix(source_file_path)

        try:
            xml_tree = etree.parse(source_file_path)
        except ParseError as error:
            raise InterpreterError(
                error_code=ErrorCode.INT_XML,
                message="Error parsing input XML.",
            ) from error

        xml_root = xml_tree.getroot()
        self._validate_sol_xml_document(xml_prefix, xml_tree, xml_root)

        return xml_root

    def _read_xml_prefix(self, source_file_path: Path) -> bytes:
        """
        @brief A short initial XML file prefix is read.

        Only a small byte prefix is read so that the XML declaration can
        be checked without loading the entire file for that purpose.

        @param source_file_path A path to the source SOL-XML file.
        @return A short initial byte prefix of the source file.
        """
        with source_file_path.open("rb") as source_file:
            return source_file.read(512)

    def _validate_root_language(self, xml_root: etree._Element) -> None:
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

    def _validate_root_tag(self, xml_root: etree._Element) -> None:
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
        self,
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
        self,
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
        self._validate_xml_declaration(xml_prefix, xml_tree)
        self._validate_root_tag(xml_root)
        self._validate_root_language(xml_root)
