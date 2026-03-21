/**
 * @file test_type_resolver.ts
 * @brief Resolution of the implicit SOLtest test case type is implemented.
 * @author   Hana Liškařová xliskah00
 * DOXYGEN COMMENTS ARE AI GENERATED AND PROOF READ BY ME
 *
 * The SOLtest format does not store the test case type explicitly. The type
 * therefore has to be inferred from the parsed test case contents, from the
 * presence of expected exit codes, and from the presence of optional input or
 * output files.
 */

import { TestCaseType } from "../models.js";
import { ParsedTestCase } from "./parse_test.js";

/**
 * @brief Presence of parser exit codes is determined.
 *
 * A parser exit code list is considered present when it contains at least one
 * value.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns True when parser exit codes are present, otherwise false.
 */
function hasParserExitCodes(parsedTestCase: ParsedTestCase): boolean {
  return parsedTestCase.expected_parser_exit_codes.length > 0;
}

/**
 * @brief Presence of interpreter exit codes is determined.
 *
 * An interpreter exit code list is considered present when it contains at least
 * one value.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns True when interpreter exit codes are present, otherwise false.
 */
function hasInterpreterExitCodes(parsedTestCase: ParsedTestCase): boolean {
  return parsedTestCase.expected_interpreter_exit_codes.length > 0;
}

/**
 * @brief Presence of interpreter input or expected output files is determined.
 *
 * Interpreter-side files are considered present when either a ".in" file or
 * a ".out" file was discovered for the test case.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns True when interpreter-related files are present, otherwise false.
 */
function hasInterpreterFiles(parsedTestCase: ParsedTestCase): boolean {
  return parsedTestCase.stdin_file !== null || parsedTestCase.expected_stdout_file !== null;
}

/**
 * @brief A best-effort check of whether the source code looks like XML is performed.
 *
 * The parsed source code is trimmed on the left side and then checked for the
 * typical XML opening syntax. This heuristic is intentionally simple, because
 * only rough type resolution is needed here.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns True when the source code looks like XML, otherwise false.
 */
function looksLikeXmlSourceCode(parsedTestCase: ParsedTestCase): boolean {
  const trimmedSourceCode = parsedTestCase.source_code.trimStart();

  return trimmedSourceCode.startsWith("<");
}

/**
 * @brief Execute-only type resolution is performed for XML-like source code.
 *
 * XML source code is expected to be interpreted directly. Parser exit codes are
 * therefore not allowed here. Interpreter exit codes must be present so that
 * the execution result can be evaluated.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Resolved execute-only test case type.
 * @throws Error when the XML-like test case contains conflicting or insufficient metadata.
 */
function resolveXmlLikeTestCaseType(parsedTestCase: ParsedTestCase): TestCaseType {
  if (hasParserExitCodes(parsedTestCase)) {
    throw new Error(
      `The test case "${parsedTestCase.name}" looks like XML source code, so parser exit codes must not be provided.`
    );
  }

  if (!hasInterpreterExitCodes(parsedTestCase)) {
    throw new Error(
      `The test case "${parsedTestCase.name}" looks like XML source code, but interpreter exit codes are missing.`
    );
  }

  return TestCaseType.EXECUTE_ONLY;
}

/**
 * @brief Parse-only type resolution is performed for SOL26-like source code.
 *
 * Parser-only test cases are recognized when parser exit codes are present and
 * no interpreter-side metadata is present.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Resolved parse-only test case type.
 */
function resolveParseOnlyTestCaseType(parsedTestCase: ParsedTestCase): TestCaseType {
  void parsedTestCase;
  return TestCaseType.PARSE_ONLY;
}

/**
 * @brief Combined type resolution is performed for SOL26-like source code.
 *
 * Combined test cases are recognized when interpreter-related expectations are
 * present for non-XML source code. Parser exit codes are optional here. When
 * they are present, they are validated later by the final template model.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Resolved combined test case type.
 * @throws Error when interpreter exit codes are missing.
 */
function resolveCombinedTestCaseType(parsedTestCase: ParsedTestCase): TestCaseType {
  if (!hasInterpreterExitCodes(parsedTestCase)) {
    throw new Error(
      `The test case "${parsedTestCase.name}" requires combined execution, but interpreter exit codes are missing.`
    );
  }

  return TestCaseType.COMBINED;
}

/**
 * @brief Necessity of combined execution is determined for SOL26-like source code.
 *
 * Combined execution is considered necessary when interpreter exit codes are
 * present or when interpreter-related input/output files were discovered.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns True when combined execution is required, otherwise false.
 */
function requiresCombinedExecution(parsedTestCase: ParsedTestCase): boolean {
  return hasInterpreterExitCodes(parsedTestCase) || hasInterpreterFiles(parsedTestCase);
}

/**
 * @brief Type resolution is performed for SOL26-like source code.
 *
 * SOL26-like source code may represent either a parser-only test case or
 * a combined test case. The decision is made from the presence of parser
 * and interpreter-related metadata.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Resolved test case type.
 * @throws Error when the provided metadata are insufficient to determine the type.
 */
function resolveSol26LikeTestCaseType(parsedTestCase: ParsedTestCase): TestCaseType {
  if (requiresCombinedExecution(parsedTestCase)) {
    return resolveCombinedTestCaseType(parsedTestCase);
  }

  if (hasParserExitCodes(parsedTestCase)) {
    return resolveParseOnlyTestCaseType(parsedTestCase);
  }

  throw new Error(
    `The test case "${parsedTestCase.name}" does not provide enough information to determine whether it is parse-only or combined.`
  );
}

/**
 * @brief The implicit SOLtest test case type is resolved.
 *
 * XML-like source code is resolved as execute-only when interpreter metadata are
 * present. Non-XML source code is resolved either as parse-only or as combined,
 * depending on the presence of parser and interpreter-related metadata.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Resolved test case type.
 * @throws Error when the test case type cannot be determined unambiguously.
 */
export function resolveTestCaseType(parsedTestCase: ParsedTestCase): TestCaseType {
  if (looksLikeXmlSourceCode(parsedTestCase)) {
    return resolveXmlLikeTestCaseType(parsedTestCase);
  }

  return resolveSol26LikeTestCaseType(parsedTestCase);
}
