/**
 * @file test_resolver.ts
 * @brief Resolution of one executed test case into a final test report is implemented.
 * @author Hana Liškařová xliskah00
 * DOXYGEN COMMENTS ARE AI GENERATED AND PROOF READ BY ME
 *
 * Raw execution results are evaluated against the expected exit codes stored
 * in the final test case definition. When an expected standard output file is
 * available, actual interpreter output is also compared against it.
 *
 * The result of this module is one final TestCaseReport instance defined by
 * the provided project template.
 */

import { TestCaseDefinition, TestCaseReport, TestCaseType, TestResult } from "../models.js";
import { compareStdout } from "./comparator.js";
import { TestCaseExecutionResult } from "../execution/test_case_executor.js";

/**
 * @brief Matching of one actual exit code against expected exit codes is determined.
 *
 * A null exit code is always treated as a mismatch. Otherwise, the actual exit
 * code is considered matching when it is contained in the expected exit code list.
 *
 * @param actualExitCode Actual exit code produced by the executed tool.
 * @param expectedExitCodes Expected exit codes from the test case definition.
 * @returns True when the actual exit code matches one of the expected values, otherwise false.
 */
function matchesExpectedExitCode(
  actualExitCode: number | null,
  expectedExitCodes: number[]
): boolean {
  if (actualExitCode === null) {
    return false;
  }

  return expectedExitCodes.includes(actualExitCode);
}

/**
 * @brief Expected parser exit codes are prepared for evaluation.
 *
 * Combined test cases are allowed by the template model to omit parser exit
 * codes, but successful combined execution still implies parser exit code zero.
 * When parser exit codes are missing for a combined test case, the expected
 * parser exit code is therefore treated as zero.
 *
 * @param testCaseDefinition Final test case definition.
 * @returns Expected parser exit codes used for evaluation.
 */
function getExpectedParserExitCodes(testCaseDefinition: TestCaseDefinition): number[] {
  if (
    testCaseDefinition.test_type === TestCaseType.COMBINED &&
    testCaseDefinition.expected_parser_exit_codes === null
  ) {
    return [0];
  }

  return testCaseDefinition.expected_parser_exit_codes ?? [];
}

/**
 * @brief One final test case report is created from raw execution data.
 *
 * Parser and interpreter raw outputs are copied into the final template report.
 * A diff output is attached only when output comparison found a mismatch.
 *
 * @param result Final resolved test result.
 * @param executionResult Raw execution result of the test case.
 * @param diffOutput Output of the diff comparison, or null when no diff output exists.
 * @returns Final test case report.
 */
function createTestCaseReport(
  result: TestResult,
  executionResult: TestCaseExecutionResult,
  diffOutput: string | null
): TestCaseReport {
  const parserResult = executionResult.parser_result;
  const interpreterResult = executionResult.interpreter_result;

  return new TestCaseReport(
    result,
    parserResult?.exit_code ?? null,
    interpreterResult?.exit_code ?? null,
    parserResult?.stdout ?? null,
    parserResult?.stderr ?? null,
    interpreterResult?.stdout ?? null,
    interpreterResult?.stderr ?? null,
    diffOutput
  );
}

/**
 * @brief Interpreter output is resolved after interpreter exit code already matched.
 *
 * When an expected output file exists, actual interpreter output is compared
 * against it. When the outputs differ, the corresponding report is created.
 * Otherwise, a passed report is created.
 *
 * @param testCaseDefinition Final test case definition.
 * @param executionResult Raw execution result of the test case.
 * @returns Promise resolving to the final test case report.
 */
async function resolveInterpreterOutput(
  testCaseDefinition: TestCaseDefinition,
  executionResult: TestCaseExecutionResult
): Promise<TestCaseReport> {
  const actualStdout = executionResult.interpreter_result?.stdout ?? "";

  const comparisonResult = await compareStdout({
    expected_stdout_file: testCaseDefinition.expected_stdout_file,
    actual_stdout: actualStdout,
  });

  if (!comparisonResult.matches) {
    return createTestCaseReport(
      TestResult.INTERPRETER_RESULT_DIFFERS,
      executionResult,
      comparisonResult.diff_output
    );
  }

  return createTestCaseReport(TestResult.PASSED, executionResult, null);
}

/**
 * @brief One parse-only test case result is resolved.
 *
 * Only the parser exit code is evaluated for parse-only test cases.
 *
 * @param testCaseDefinition Final test case definition.
 * @param executionResult Raw execution result of the test case.
 * @returns Final resolved test case report.
 */
function resolveParseOnlyTestCase(
  testCaseDefinition: TestCaseDefinition,
  executionResult: TestCaseExecutionResult
): TestCaseReport {
  const expectedParserExitCodes = getExpectedParserExitCodes(testCaseDefinition);
  const actualParserExitCode = executionResult.parser_result?.exit_code ?? null;

  if (!matchesExpectedExitCode(actualParserExitCode, expectedParserExitCodes)) {
    return createTestCaseReport(TestResult.UNEXPECTED_PARSER_EXIT_CODE, executionResult, null);
  }

  return createTestCaseReport(TestResult.PASSED, executionResult, null);
}

/**
 * @brief One execute-only test case result is resolved.
 *
 * First, the interpreter exit code is evaluated. When it matches the expected
 * values, interpreter output is resolved afterwards.
 *
 * @param testCaseDefinition Final test case definition.
 * @param executionResult Raw execution result of the test case.
 * @returns Promise resolving to the final resolved test case report.
 */
async function resolveExecuteOnlyTestCase(
  testCaseDefinition: TestCaseDefinition,
  executionResult: TestCaseExecutionResult
): Promise<TestCaseReport> {
  const expectedInterpreterExitCodes = testCaseDefinition.expected_interpreter_exit_codes ?? [];
  const actualInterpreterExitCode = executionResult.interpreter_result?.exit_code ?? null;

  if (!matchesExpectedExitCode(actualInterpreterExitCode, expectedInterpreterExitCodes)) {
    return createTestCaseReport(
      TestResult.UNEXPECTED_INTERPRETER_EXIT_CODE,
      executionResult,
      null
    );
  }

  return resolveInterpreterOutput(testCaseDefinition, executionResult);
}

/**
 * @brief One combined test case result is resolved.
 *
 * First, the parser exit code is evaluated. When it matches the expected
 * values, the interpreter exit code is evaluated. When both stages match,
 * interpreter output is resolved afterwards.
 *
 * @param testCaseDefinition Final test case definition.
 * @param executionResult Raw execution result of the test case.
 * @returns Promise resolving to the final resolved test case report.
 */
async function resolveCombinedTestCase(
  testCaseDefinition: TestCaseDefinition,
  executionResult: TestCaseExecutionResult
): Promise<TestCaseReport> {
  const expectedParserExitCodes = getExpectedParserExitCodes(testCaseDefinition);
  const actualParserExitCode = executionResult.parser_result?.exit_code ?? null;

  if (!matchesExpectedExitCode(actualParserExitCode, expectedParserExitCodes)) {
    return createTestCaseReport(TestResult.UNEXPECTED_PARSER_EXIT_CODE, executionResult, null);
  }

  const expectedInterpreterExitCodes = testCaseDefinition.expected_interpreter_exit_codes ?? [];
  const actualInterpreterExitCode = executionResult.interpreter_result?.exit_code ?? null;

  if (!matchesExpectedExitCode(actualInterpreterExitCode, expectedInterpreterExitCodes)) {
    return createTestCaseReport(
      TestResult.UNEXPECTED_INTERPRETER_EXIT_CODE,
      executionResult,
      null
    );
  }

  return resolveInterpreterOutput(testCaseDefinition, executionResult);
}

/**
 * @brief One executed test case is resolved into a final test report.
 *
 * The evaluation flow is selected from the test case type stored in the final
 * test case definition.
 *
 * @param testCaseDefinition Final test case definition.
 * @param executionResult Raw execution result of the test case.
 * @returns Promise resolving to the final resolved test case report.
 */
export async function resolveTestCase(
  testCaseDefinition: TestCaseDefinition,
  executionResult: TestCaseExecutionResult
): Promise<TestCaseReport> {
  const testCaseType = testCaseDefinition.test_type;

  if (testCaseType === TestCaseType.PARSE_ONLY) {
    return resolveParseOnlyTestCase(testCaseDefinition, executionResult);
  }

  if (testCaseType === TestCaseType.EXECUTE_ONLY) {
    return resolveExecuteOnlyTestCase(testCaseDefinition, executionResult);
  }

  return resolveCombinedTestCase(testCaseDefinition, executionResult);
}
