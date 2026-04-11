/**
 * @file test_case_classifier.ts
 * @brief Classification of the implicit SOLtest test case type is implemented.
 * @author Hana Liškařová xliskah00
 *
 * DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
 *
 * The SOLtest format does not store the test case type explicitly.
 * The type is inferred here from parsed test case data and related files.
 */

import { TestCaseType } from "../models.js";
import { ParsedTestCase } from "./parse_test.js";

/**
 * @brief Presence of parser exit codes is determined.
 *
 * Parser exit codes are considered present when at least one value exists.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns True if parser exit codes are present, otherwise false.
 */
function hasParserExitCodes(parsedTestCase: ParsedTestCase): boolean {
  return parsedTestCase.expected_parser_exit_codes.length > 0;
}

/**
 * @brief Presence of interpreter exit codes is determined.
 *
 * Interpreter exit codes are considered present when at least one value exists.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns True if interpreter exit codes are present, otherwise false.
 */
function hasInterpreterExitCodes(parsedTestCase: ParsedTestCase): boolean {
  return parsedTestCase.expected_interpreter_exit_codes.length > 0;
}

/**
 * @brief Presence of interpreter input or output files is determined.
 *
 * Interpreter-side files are considered present when either a ".in" file
 * or a ".out" file exists for the test case.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns True if interpreter-related files are present, otherwise false.
 */
function hasInterpreterFiles(parsedTestCase: ParsedTestCase): boolean {
  return parsedTestCase.stdin_file !== null || parsedTestCase.expected_stdout_file !== null;
}

/**
 * @brief A simple check of whether the source code looks like XML is performed.
 *
 * The source code is trimmed on the left side and checked for the usual
 * XML opening syntax.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns True if the source code looks like XML, otherwise false.
 */
function looksLikeXmlSourceCode(parsedTestCase: ParsedTestCase): boolean {
  //ignore leading whitespace
  const trimmedSourceCode = parsedTestCase.source_code.trimStart();

  return trimmedSourceCode.startsWith("<");
}

/**
 * @brief Necessity of combined execution is determined for SOL26-like source code.
 *
 * Combined execution is required when interpreter exit codes are present
 * or when interpreter-related files exist.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns True if combined execution is required, otherwise false.
 */
function requiresCombinedExecution(parsedTestCase: ParsedTestCase): boolean {
  return hasInterpreterExitCodes(parsedTestCase) || hasInterpreterFiles(parsedTestCase);
}

/**
 * @brief Execute-only classification is performed for XML-like source code.
 *
 * XML-like source code is interpreted directly. Parser exit codes are not
 * allowed here, and interpreter exit codes must be present.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Execute-only test case type.
 * @throws Error If the XML-like test case contains conflicting or missing metadata.
 */
function classifyXmlLikeTestCase(parsedTestCase: ParsedTestCase): TestCaseType {
  //xml input - skip parser stage
  if (hasParserExitCodes(parsedTestCase)) {
    throw new Error(
      `"${parsedTestCase.name}" XML source code, parser exit codes shouldnt be provided.`
    );
  }

  if (!hasInterpreterExitCodes(parsedTestCase)) {
    throw new Error(`"${parsedTestCase.name}" XML source code, interpreter exit codes missing.`);
  }

  return TestCaseType.EXECUTE_ONLY;
}

/**
 * @brief Parse-only classification is performed for SOL26-like source code.
 *
 * Parser-only test cases are recognized when parser exit codes are present.
 *
 * @returns Parse-only test case type.
 */
function classifyParseOnlyTestCase(): TestCaseType {
  return TestCaseType.PARSE_ONLY;
}

/**
 * @brief Combined classification is performed for SOL26-like source code.
 *
 * Combined test cases are recognized when interpreter-related expectations
 * are present for non-XML source code.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Combined test case type.
 * @throws Error If interpreter exit codes are missing.
 */
function classifyCombinedTestCase(parsedTestCase: ParsedTestCase): TestCaseType {
  if (!hasInterpreterExitCodes(parsedTestCase)) {
    throw new Error(
      `"${parsedTestCase.name}" requires combined execution, interpreter exit codes missing.`
    );
  }

  return TestCaseType.COMBINED;
}

/**
 * @brief Classification is performed for SOL26-like source code.
 *
 * SOL26-like source code may represent either a parse-only or a combined
 * test case. The decision is made from parser and interpreter metadata.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Resolved test case type.
 * @throws Error If the provided metadata are not sufficient to determine the type.
 */
function classifySol26LikeTestCase(parsedTestCase: ParsedTestCase): TestCaseType {
  //interpreter metadata - combined test
  if (requiresCombinedExecution(parsedTestCase)) {
    return classifyCombinedTestCase(parsedTestCase);
  }

  if (hasParserExitCodes(parsedTestCase)) {
    return classifyParseOnlyTestCase();
  }

  throw new Error(`"${parsedTestCase.name}" does not provide enough information.`);
}

/**
 * @brief One parsed test case is classified.
 *
 * XML-like source code is classified as execute-only.
 * Non-XML source code is classified as parse-only or combined.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Resolved test case type.
 * @throws Error If the test case type cannot be determined unambiguously.
 */
export function classifyTestCase(parsedTestCase: ParsedTestCase): TestCaseType {
  //check for xml
  if (looksLikeXmlSourceCode(parsedTestCase)) {
    return classifyXmlLikeTestCase(parsedTestCase);
  }

  return classifySol26LikeTestCase(parsedTestCase);
}
