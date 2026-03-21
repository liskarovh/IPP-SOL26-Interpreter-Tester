/**
 * @file test_case_builder.ts
 * @brief Construction of the final TestCaseDefinition model is implemented.
 * @author   Hana Liškařová xliskah00
 * DOXYGEN COMMENTS ARE AI GENERATED AND PROOF READ BY ME
 *
 * A parsed SOLtest test case is converted into the final TestCaseDefinition
 * model defined by the provided project template. The implicit test case type
 * is resolved first, and then the final model is constructed according to the
 * resolved execution mode.
 */

import { TestCaseDefinition, TestCaseType } from "../models.js";
import { resolveTestCaseType } from "./test_type_resolver.js";
import { ParsedTestCase } from "./parse_test.js";

/**
 * @brief Parser exit codes for a combined test case are prepared.
 *
 * The provided template model allows combined test cases to use either null or
 * exactly one parser exit code equal to zero. When no parser exit code is
 * present in the parsed test case, null is returned. Otherwise, the parsed
 * values are returned unchanged and their validity is left to the final model.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Parser exit codes for a combined test case, or null when none were provided.
 */
function getCombinedParserExitCodes(parsedTestCase: ParsedTestCase): number[] | null {
  if (parsedTestCase.expected_parser_exit_codes.length === 0) {
    return null;
  }

  return parsedTestCase.expected_parser_exit_codes;
}

/**
 * @brief A parse-only TestCaseDefinition model is created.
 *
 * Parser exit codes are transferred from the parsed test case. Interpreter exit
 * codes are explicitly omitted, because they are not valid for parse-only test
 * cases in the provided template model.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Final parse-only TestCaseDefinition model.
 */
function buildParseOnlyTestCaseDefinition(parsedTestCase: ParsedTestCase): TestCaseDefinition {
  return new TestCaseDefinition({
    name: parsedTestCase.name,
    test_source_path: parsedTestCase.test_source_path,
    stdin_file: parsedTestCase.stdin_file,
    expected_stdout_file: parsedTestCase.expected_stdout_file,
    test_type: TestCaseType.PARSE_ONLY,
    description: parsedTestCase.description,
    category: parsedTestCase.category,
    points: parsedTestCase.points,
    expected_parser_exit_codes: parsedTestCase.expected_parser_exit_codes,
    expected_interpreter_exit_codes: null,
  });
}

/**
 * @brief An execute-only TestCaseDefinition model is created.
 *
 * Interpreter exit codes are transferred from the parsed test case. Parser exit
 * codes are explicitly omitted, because they are not valid for execute-only test
 * cases in the provided template model.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Final execute-only TestCaseDefinition model.
 */
function buildExecuteOnlyTestCaseDefinition(parsedTestCase: ParsedTestCase): TestCaseDefinition {
  return new TestCaseDefinition({
    name: parsedTestCase.name,
    test_source_path: parsedTestCase.test_source_path,
    stdin_file: parsedTestCase.stdin_file,
    expected_stdout_file: parsedTestCase.expected_stdout_file,
    test_type: TestCaseType.EXECUTE_ONLY,
    description: parsedTestCase.description,
    category: parsedTestCase.category,
    points: parsedTestCase.points,
    expected_parser_exit_codes: null,
    expected_interpreter_exit_codes: parsedTestCase.expected_interpreter_exit_codes,
  });
}

/**
 * @brief A combined TestCaseDefinition model is created.
 *
 * Parser exit codes are passed as null when they were not provided in the
 * parsed test case. Otherwise, the parsed values are forwarded unchanged and
 * are validated by the final template model.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Final combined TestCaseDefinition model.
 */
function buildCombinedTestCaseDefinition(parsedTestCase: ParsedTestCase): TestCaseDefinition {
  const combinedParserExitCodes = getCombinedParserExitCodes(parsedTestCase);

  return new TestCaseDefinition({
    name: parsedTestCase.name,
    test_source_path: parsedTestCase.test_source_path,
    stdin_file: parsedTestCase.stdin_file,
    expected_stdout_file: parsedTestCase.expected_stdout_file,
    test_type: TestCaseType.COMBINED,
    description: parsedTestCase.description,
    category: parsedTestCase.category,
    points: parsedTestCase.points,
    expected_parser_exit_codes: combinedParserExitCodes,
    expected_interpreter_exit_codes: parsedTestCase.expected_interpreter_exit_codes,
  });
}

/**
 * @brief A parsed SOLtest test case is converted into the final template model.
 *
 * The implicit test case type is resolved first. Based on the resolved type,
 * the parsed test case is then converted into the corresponding
 * TestCaseDefinition model.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Final TestCaseDefinition model.
 * @throws Error when the test case type cannot be resolved or when the parsed data are inconsistent.
 */
export function buildTestCaseDefinition(parsedTestCase: ParsedTestCase): TestCaseDefinition {
  const resolvedTestCaseType = resolveTestCaseType(parsedTestCase);

  switch (resolvedTestCaseType) {
    case TestCaseType.PARSE_ONLY:
      return buildParseOnlyTestCaseDefinition(parsedTestCase);

    case TestCaseType.EXECUTE_ONLY:
      return buildExecuteOnlyTestCaseDefinition(parsedTestCase);

    case TestCaseType.COMBINED:
      return buildCombinedTestCaseDefinition(parsedTestCase);
  }
}
