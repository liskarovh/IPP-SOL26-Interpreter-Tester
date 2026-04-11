/**
 * @file parse_test_header.ts
 * @brief Parsing of SOLtest header directives is implemented.
 * @author Hana Liškařová xliskah00
 *
 * DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
 *
 * Only SOLtest header directives are handled here. The source code part
 * of the test file is processed elsewhere.
 */

/**
 * @brief One parsed SOLtest header is described.
 *
 * Some fields stay nullable until all header lines are processed
 * and required values are validated.
 */
export interface ParsedHeader {
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
 * @brief An empty parsed header is created.
 *
 * @returns Empty parsed header data.
 */
function createEmptyParsedHeader(): ParsedHeader {
  return {
    description: null,
    category: null,
    points: null,
    expected_parser_exit_codes: [],
    expected_interpreter_exit_codes: [],
  };
}

/**
 * @brief A directive value is extracted from a header line.
 *
 * The directive prefix is removed, surrounding whitespace is trimmed,
 * and an empty value is rejected.
 *
 * @param headerLine Header line being processed.
 * @param prefix Directive prefix expected at the beginning of the line.
 * @param directiveName Directive name used in error messages.
 * @param testSourcePath Path to the parsed ".test" file.
 * @returns Extracted directive value.
 * @throws Error If the directive value is empty.
 */
function extractDirectiveValue(
  headerLine: string,
  prefix: string,
  directiveName: string,
  testSourcePath: string
): string {
  const value = headerLine.slice(prefix.length).trim();

  //directive value cant be empty
  if (value === "") {
    throw new Error(`"${directiveName}" in "${testSourcePath}" does not contain a value.`);
  }

  return value;
}

/**
 * @brief A non-negative integer value is parsed from text.
 *
 * Only whole numbers greater than or equal to zero are accepted.
 *
 * @param valueText Text value that is being parsed.
 * @param valueName Value name used in error messages.
 * @param testSourcePath Path to the parsed ".test" file.
 * @returns Parsed integer value.
 * @throws Error If the value is not a valid non-negative integer.
 */
function parseNonNegativeInteger(
  valueText: string,
  valueName: string,
  testSourcePath: string
): number {
  const parsedValue = Number(valueText);

  if (!Number.isInteger(parsedValue) || parsedValue < 0) {
    throw new Error(
      `"${valueText}" for ${valueName} in "${testSourcePath}" not a valid non-negative integer.`
    );
  }

  return parsedValue;
}

/**
 * @brief Repeated single-value directive is rejected.
 *
 * Directives expected to appear at most once are checked here.
 *
 * @param currentValue Current stored value of the directive.
 * @param directiveName Directive name used in error messages.
 * @param testSourcePath Path to the parsed ".test" file.
 * @throws Error If the directive is repeated.
 */
function ensureSingleDirectiveOccurrence(
  currentValue: string | number | null,
  directiveName: string,
  testSourcePath: string
): void {
  if (currentValue !== null) {
    throw new Error(
      `Directive "${directiveName}" is repeated in SOLtest file "${testSourcePath}".`
    );
  }
}

/**
 * @brief A description directive is parsed.
 *
 * @param headerLine Header line being processed.
 * @param parsedHeader Mutable parsed header data.
 * @param testSourcePath Path to the parsed ".test" file.
 */
function parseDescriptionDirective(
  headerLine: string,
  parsedHeader: ParsedHeader,
  testSourcePath: string
): void {
  ensureSingleDirectiveOccurrence(parsedHeader.description, "***", testSourcePath);
  parsedHeader.description = extractDirectiveValue(headerLine, "***", "***", testSourcePath);
}

/**
 * @brief A category directive is parsed.
 *
 * @param headerLine Header line being processed.
 * @param parsedHeader Mutable parsed header data.
 * @param testSourcePath Path to the parsed ".test" file.
 */
function parseCategoryDirective(
  headerLine: string,
  parsedHeader: ParsedHeader,
  testSourcePath: string
): void {
  ensureSingleDirectiveOccurrence(parsedHeader.category, "+++", testSourcePath);
  parsedHeader.category = extractDirectiveValue(headerLine, "+++", "+++", testSourcePath);
}

/**
 * @brief A points directive is parsed.
 *
 * @param headerLine Header line being processed.
 * @param parsedHeader Mutable parsed header data.
 * @param testSourcePath Path to the parsed ".test" file.
 */
function parsePointsDirective(
  headerLine: string,
  parsedHeader: ParsedHeader,
  testSourcePath: string
): void {
  ensureSingleDirectiveOccurrence(parsedHeader.points, ">>>", testSourcePath);

  const pointsText = extractDirectiveValue(headerLine, ">>>", ">>>", testSourcePath);
  parsedHeader.points = parseNonNegativeInteger(pointsText, "points", testSourcePath);
}

/**
 * @brief A parser exit-code directive is parsed.
 *
 * @param headerLine Header line being processed.
 * @param parsedHeader Mutable parsed header data.
 * @param testSourcePath Path to the parsed ".test" file.
 */
function parseParserExitCodeDirective(
  headerLine: string,
  parsedHeader: ParsedHeader,
  testSourcePath: string
): void {
  const exitCodeText = extractDirectiveValue(headerLine, "!C!", "!C!", testSourcePath);
  const exitCode = parseNonNegativeInteger(exitCodeText, "parser exit code", testSourcePath);

  parsedHeader.expected_parser_exit_codes.push(exitCode);
}

/**
 * @brief An interpreter exit-code directive is parsed.
 *
 * @param headerLine Header line being processed.
 * @param parsedHeader Mutable parsed header data.
 * @param testSourcePath Path to the parsed ".test" file.
 */
function parseInterpreterExitCodeDirective(
  headerLine: string,
  parsedHeader: ParsedHeader,
  testSourcePath: string
): void {
  const exitCodeText = extractDirectiveValue(headerLine, "!I!", "!I!", testSourcePath);
  const exitCode = parseNonNegativeInteger(exitCodeText, "interpreter exit code", testSourcePath);

  parsedHeader.expected_interpreter_exit_codes.push(exitCode);
}

/**
 * @brief One SOLtest header directive is parsed.
 *
 * Supported directives are handled explicitly. Repeated "!C!" and "!I!"
 * directives are collected, while repeated single-value directives are rejected.
 *
 * @param headerLine Header line being processed.
 * @param parsedHeader Mutable parsed header structure.
 * @param testSourcePath Path to the parsed ".test" file.
 * @throws Error If an unsupported directive or invalid value is encountered.
 */
function parseHeaderDirective(
  headerLine: string,
  parsedHeader: ParsedHeader,
  testSourcePath: string
): void {
  //dispatch by directive prefix
  if (headerLine.startsWith("***")) {
    parseDescriptionDirective(headerLine, parsedHeader, testSourcePath);
    return;
  }

  if (headerLine.startsWith("+++")) {
    parseCategoryDirective(headerLine, parsedHeader, testSourcePath);
    return;
  }

  if (headerLine.startsWith(">>>")) {
    parsePointsDirective(headerLine, parsedHeader, testSourcePath);
    return;
  }

  if (headerLine.startsWith("!C!")) {
    parseParserExitCodeDirective(headerLine, parsedHeader, testSourcePath);
    return;
  }

  if (headerLine.startsWith("!I!")) {
    parseInterpreterExitCodeDirective(headerLine, parsedHeader, testSourcePath);
    return;
  }

  throw new Error(
    `Header line "${headerLine}" in "${testSourcePath}" does not contain SOLtest directive.`
  );
}

/**
 * @brief Required header values are validated.
 *
 * Category and points are required at this stage.
 *
 * @param parsedHeader Parsed header representation.
 * @param testSourcePath Path to the parsed ".test" file.
 * @throws Error If a required value is missing.
 */
function validateParsedHeader(parsedHeader: ParsedHeader, testSourcePath: string): void {
  //category is required
  if (parsedHeader.category === null) {
    throw new Error(`SOLtest file "${testSourcePath}" does not define category.`);
  }

  //points are required
  if (parsedHeader.points === null) {
    throw new Error(`SOLtest file "${testSourcePath}" does not define points.`);
  }
}

/**
 * @brief SOLtest header lines are parsed and validated.
 *
 * Empty header lines are ignored defensively. Required values are validated
 * after all header lines have been processed.
 *
 * @param headerLines Header lines extracted from the SOLtest file.
 * @param testSourcePath Path to the parsed ".test" file.
 * @returns Parsed and validated header representation.
 */
export function parseTestHeader(headerLines: string[], testSourcePath: string): ParsedHeader {
  const parsedHeader = createEmptyParsedHeader();

  for (const headerLine of headerLines) {
    //ignore empty header lines
    if (headerLine.trim() === "") {
      continue;
    }

    parseHeaderDirective(headerLine, parsedHeader, testSourcePath);
  }

  validateParsedHeader(parsedHeader, testSourcePath);

  return parsedHeader;
}
