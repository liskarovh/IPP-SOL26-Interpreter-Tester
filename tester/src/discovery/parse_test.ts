/**
 * @file parse_test.ts
 * @brief Parsing of one SOLtest test case file is implemented.
 * @author    Hana Liškařová xliskah00
 * DOXYGEN COMMENTS ARE AI GENERATED AND PROOF READ BY ME
 *
 * A discovered ".test" file is read, split into its header part and source code
 * part, and its SOLtest directives are parsed into an internal representation.
 *
 * Only syntactic parsing of the SOLtest format is performed here. Test type
 * resolution and construction of the final TestCaseDefinition model are intended
 * to be implemented in later steps.
 */

import { readFileSync } from "node:fs";

import { TestCaseDefinitionFile } from "../models.js";

/**
 * @brief Parsed data of one SOLtest test case are stored.
 *
 * This internal structure is used after the textual SOLtest file has been parsed
 * and before the final template model is constructed.
 */
export interface ParsedTestCase {
  /** Test case name derived from the discovered file metadata. */
  name: string;
  /** Path to the ".test" source file. */
  test_source_path: string;
  /** Optional path to the ".in" file. */
  stdin_file: string | null;
  /** Optional path to the ".out" file. */
  expected_stdout_file: string | null;
  /** Optional test case description. */
  description: string | null;
  /** Required category of the test case. */
  category: string;
  /** Required point value of the test case. */
  points: number;
  /** Parser exit codes collected from "!C!" directives. */
  expected_parser_exit_codes: number[];
  /** Interpreter exit codes collected from "!I!" directives. */
  expected_interpreter_exit_codes: number[];
  /** Source code part of the test case. */
  source_code: string;
}

/**
 * @brief Parsed header values are stored during header processing.
 *
 * Some values are kept nullable until all header lines have been processed
 * and required fields have been validated.
 */
interface ParsedHeader {
  /** Optional test case description. */
  description: string | null;
  /** Required category, stored as nullable until validation is performed. */
  category: string | null;
  /** Required point value, stored as nullable until validation is performed. */
  points: number | null;
  /** Parser exit codes collected from "!C!" directives. */
  expected_parser_exit_codes: number[];
  /** Interpreter exit codes collected from "!I!" directives. */
  expected_interpreter_exit_codes: number[];
}

/**
 * @brief File contents are split into header lines and source code.
 *
 * The first blank line is treated as the separator between the SOLtest header
 * section and the source code section. A missing separator or missing source
 * code is rejected as malformed input.
 *
 * @param fileContents Full contents of the SOLtest file.
 * @param testSourcePath Path to the parsed ".test" file.
 * @returns Object containing header lines and source code.
 * @throws Error when the required separator or source code is missing.
 */
function splitTestFileContent(
  fileContents: string,
  testSourcePath: string
): { headerLines: string[]; sourceCode: string } {
  const normalizedContents = fileContents.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  const allLines = normalizedContents.split("\n");

  let separatorIndex = -1;
  let currentIndex = 0;

  for (const currentLine of allLines) {
    if (currentLine.trim() === "") {
      separatorIndex = currentIndex;
      break;
    }

    currentIndex += 1;
  }

  if (separatorIndex === -1) {
    throw new Error(
      `The SOLtest file "${testSourcePath}" does not contain the required blank line separator.`
    );
  }

  const headerLines = allLines.slice(0, separatorIndex);
  const sourceLines = allLines.slice(separatorIndex + 1);
  const sourceCode = sourceLines.join("\n");

  if (sourceCode.trim() === "") {
    throw new Error(`The SOLtest file "${testSourcePath}" does not contain source code.`);
  }

  return {
    headerLines,
    sourceCode,
  };
}

/**
 * @brief A directive value is extracted from a header line.
 *
 * The directive prefix is removed, surrounding whitespace is trimmed,
 * and an empty value is rejected.
 *
 * @param headerLine Header line being processed.
 * @param prefix Directive prefix that is expected at the beginning of the line.
 * @param directiveName Human-readable directive name used in error messages.
 * @param testSourcePath Path to the parsed ".test" file.
 * @returns Extracted directive value.
 * @throws Error when the directive value is empty.
 */
function extractDirectiveValue(
  headerLine: string,
  prefix: string,
  directiveName: string,
  testSourcePath: string
): string {
  const value = headerLine.slice(prefix.length).trim();

  if (value === "") {
    throw new Error(
      `The directive "${directiveName}" in "${testSourcePath}" does not contain a value.`
    );
  }

  return value;
}

/**
 * @brief A non-negative integer value is parsed from text.
 *
 * Only whole numbers greater than or equal to zero are accepted.
 *
 * @param valueText Textual value that is to be parsed.
 * @param valueName Human-readable value name used in error messages.
 * @param testSourcePath Path to the parsed ".test" file.
 * @returns Parsed integer value.
 * @throws Error when the provided value is not a valid non-negative integer.
 */
function parseNonNegativeInteger(
  valueText: string,
  valueName: string,
  testSourcePath: string
): number {
  const parsedValue = Number(valueText);

  if (!Number.isInteger(parsedValue) || parsedValue < 0) {
    throw new Error(
      `The value "${valueText}" for ${valueName} in "${testSourcePath}" is not a valid non-negative integer.`
    );
  }

  return parsedValue;
}

/**
 * @brief Repetition of a single-value directive is rejected.
 *
 * Directives that are expected to appear only once are validated here.
 *
 * @param currentValue Current stored value of the directive.
 * @param directiveName Human-readable directive name used in error messages.
 * @param testSourcePath Path to the parsed ".test" file.
 * @throws Error when the directive is repeated.
 */
function ensureSingleDirectiveOccurrence(
  currentValue: string | number | null,
  directiveName: string,
  testSourcePath: string
): void {
  if (currentValue !== null) {
    throw new Error(
      `The directive "${directiveName}" is repeated in the SOLtest file "${testSourcePath}".`
    );
  }
}

/**
 * @brief One SOLtest header directive is parsed.
 *
 * Supported directives are processed explicitly. Repeated "!C!" and "!I!"
 * directives are collected, while repeated single-value directives are rejected.
 *
 * @param headerLine Header line being processed.
 * @param parsedHeader Mutable parsed header structure.
 * @param testSourcePath Path to the parsed ".test" file.
 * @throws Error when an unsupported directive or invalid value is encountered.
 */
function parseHeaderDirective(
  headerLine: string,
  parsedHeader: ParsedHeader,
  testSourcePath: string
): void {
  if (headerLine.startsWith("***")) {
    ensureSingleDirectiveOccurrence(parsedHeader.description, "***", testSourcePath);
    parsedHeader.description = extractDirectiveValue(headerLine, "***", "***", testSourcePath);
    return;
  }

  if (headerLine.startsWith("+++")) {
    ensureSingleDirectiveOccurrence(parsedHeader.category, "+++", testSourcePath);
    parsedHeader.category = extractDirectiveValue(headerLine, "+++", "+++", testSourcePath);
    return;
  }

  if (headerLine.startsWith(">>>")) {
    ensureSingleDirectiveOccurrence(parsedHeader.points, ">>>", testSourcePath);
    const pointsText = extractDirectiveValue(headerLine, ">>>", ">>>", testSourcePath);
    parsedHeader.points = parseNonNegativeInteger(pointsText, "points", testSourcePath);
    return;
  }

  if (headerLine.startsWith("!C!")) {
    const exitCodeText = extractDirectiveValue(headerLine, "!C!", "!C!", testSourcePath);
    const exitCode = parseNonNegativeInteger(exitCodeText, "parser exit code", testSourcePath);
    parsedHeader.expected_parser_exit_codes.push(exitCode);
    return;
  }

  if (headerLine.startsWith("!I!")) {
    const exitCodeText = extractDirectiveValue(headerLine, "!I!", "!I!", testSourcePath);
    const exitCode = parseNonNegativeInteger(
      exitCodeText,
      "interpreter exit code",
      testSourcePath
    );
    parsedHeader.expected_interpreter_exit_codes.push(exitCode);
    return;
  }

  throw new Error(
    `The header line "${headerLine}" in "${testSourcePath}" does not contain a supported SOLtest directive.`
  );
}

/**
 * @brief Header lines are parsed into a structured header representation.
 *
 * Empty header lines are ignored defensively. Required values are validated
 * separately after all lines have been processed.
 *
 * @param headerLines Header lines extracted from the SOLtest file.
 * @param testSourcePath Path to the parsed ".test" file.
 * @returns Parsed header representation.
 */
function parseHeader(headerLines: string[], testSourcePath: string): ParsedHeader {
  const parsedHeader: ParsedHeader = {
    description: null,
    category: null,
    points: null,
    expected_parser_exit_codes: [],
    expected_interpreter_exit_codes: [],
  };

  for (const headerLine of headerLines) {
    if (headerLine.trim() === "") {
      continue;
    }

    parseHeaderDirective(headerLine, parsedHeader, testSourcePath);
  }

  return parsedHeader;
}

/**
 * @brief Presence of required header values is validated.
 *
 * Category and points are required at this stage of parsing.
 *
 * @param parsedHeader Parsed header representation.
 * @param testSourcePath Path to the parsed ".test" file.
 * @throws Error when a required value is missing.
 */
function validateParsedHeader(parsedHeader: ParsedHeader, testSourcePath: string): void {
  if (parsedHeader.category === null) {
    throw new Error(`The SOLtest file "${testSourcePath}" does not define the required category.`);
  }

  if (parsedHeader.points === null) {
    throw new Error(`The SOLtest file "${testSourcePath}" does not define the required points.`);
  }
}

/**
 * @brief One discovered SOLtest file is parsed into an internal representation.
 *
 * The file contents are read, split into header and source code, directives
 * are parsed, required values are validated, and the resulting parsed test
 * case is returned.
 *
 * @param discoveredFile Discovered test case file metadata.
 * @returns Parsed SOLtest test case.
 * @throws Error when the SOLtest file is malformed.
 */
export function parseTestCaseFile(discoveredFile: TestCaseDefinitionFile): ParsedTestCase {
  const fileContents = readFileSync(discoveredFile.test_source_path, "utf-8");
  const splitContent = splitTestFileContent(fileContents, discoveredFile.test_source_path);
  const parsedHeader = parseHeader(splitContent.headerLines, discoveredFile.test_source_path);

  validateParsedHeader(parsedHeader, discoveredFile.test_source_path);

  return {
    name: discoveredFile.name,
    test_source_path: discoveredFile.test_source_path,
    stdin_file: discoveredFile.stdin_file,
    expected_stdout_file: discoveredFile.expected_stdout_file,
    description: parsedHeader.description,
    category: parsedHeader.category as string,
    points: parsedHeader.points as number,
    expected_parser_exit_codes: parsedHeader.expected_parser_exit_codes,
    expected_interpreter_exit_codes: parsedHeader.expected_interpreter_exit_codes,
    source_code: splitContent.sourceCode,
  };
}
