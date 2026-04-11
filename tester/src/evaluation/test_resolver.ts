/**
 * @file test_resolver.ts
 * @brief Resolution of one executed test case into a final test report is implemented.
 * @author Hana Liškařová xliskah00
 *
 * DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
 *
 * Raw execution results are evaluated against expected exit codes here.
 * When an expected output file is available, actual interpreter output
 * is also compared with it.
 */

import { TestCaseDefinition, TestCaseReport, TestCaseType, TestResult } from "../models.js";
import { compareStdout } from "./stdout_comparator.js";
import { TestCaseExecutionResult } from "../execution/test_case_executor.js";

/**
 * @brief Matching of one actual exit code against expected exit codes is determined.
 *
 * A null exit code means mismatch. Otherwise, the actual exit code
 * matches when it is present in the expected exit-code list.
 *
 * @param actualExitCode Actual exit code produced by the executed tool.
 * @param expectedExitCodes Expected exit codes from the test case definition.
 * @returns True if the actual exit code matches one of the expected values, otherwise false.
 */
function matchesExpectedExitCode(
  actualExitCode: number | null,
  expectedExitCodes: number[]
): boolean {
  //missing exit code
  if (actualExitCode === null) {
    return false;
  }

  for (const expectedExitCode of expectedExitCodes) {
    if (expectedExitCode === actualExitCode) {
      return true;
    }
  }

  return false;
}

/**
 * @brief Expected parser exit codes are prepared for evaluation.
 *
 * Combined test cases may omit parser exit codes in the template model.
 * In that case, parser exit code zero is treated as expected.
 *
 * @param testCaseDefinition Final test case definition.
 * @returns Expected parser exit codes used for evaluation.
 */
function getExpectedParserExitCodes(testCaseDefinition: TestCaseDefinition): number[] {
  //combined tests default missing parser code to zero
  if (
    testCaseDefinition.test_type === TestCaseType.COMBINED &&
    testCaseDefinition.expected_parser_exit_codes === null
  ) {
    return [0];
  }

  if (testCaseDefinition.expected_parser_exit_codes === null) {
    return [];
  }

  return testCaseDefinition.expected_parser_exit_codes;
}

/**
 * @brief Expected interpreter exit codes are prepared for evaluation.
 *
 * @param testCaseDefinition Final test case definition.
 * @returns Expected interpreter exit codes used for evaluation.
 */
function getExpectedInterpreterExitCodes(testCaseDefinition: TestCaseDefinition): number[] {
  if (testCaseDefinition.expected_interpreter_exit_codes === null) {
    return [];
  }

  return testCaseDefinition.expected_interpreter_exit_codes;
}

/**
 * @brief One final test case report is created from raw execution data.
 *
 * Parser and interpreter outputs are copied into the final template report.
 * Diff output is attached only when output comparison found a mismatch.
 *
 * @param result Final resolved test result.
 * @param executionResult Raw execution result of the test case.
 * @param diffOutput Diff output, or null when no diff output exists.
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
 * @brief A passed test case report is created.
 *
 * @param executionResult Raw execution result of the test case.
 * @returns Final passed test case report.
 */
function createPassedReport(executionResult: TestCaseExecutionResult): TestCaseReport {
  return createTestCaseReport(TestResult.PASSED, executionResult, null);
}

/**
 * @brief Success of interpreter execution is determined.
 *
 * Standard output is compared only when the interpreted program
 * finished successfully with exit code zero.
 *
 * @param executionResult Raw execution result of the test case.
 * @returns True if the interpreter finished with exit code zero, otherwise false.
 */
function hasSuccessfulInterpreterExitCode(executionResult: TestCaseExecutionResult): boolean {
  if (executionResult.interpreter_result === null) {
    return false;
  }

  return executionResult.interpreter_result.exit_code === 0;
}

/**
 * @brief The parser stage result is resolved.
 *
 * When the parser exit code does not match the expected values,
 * a failure report is returned. Otherwise, null is returned and
 * evaluation may continue.
 *
 * @param testCaseDefinition Final test case definition.
 * @param executionResult Raw execution result of the test case.
 * @returns Failure report, or null when the parser stage passed.
 */
function resolveParserStage(
  testCaseDefinition: TestCaseDefinition,
  executionResult: TestCaseExecutionResult
): TestCaseReport | null {
  const expectedParserExitCodes = getExpectedParserExitCodes(testCaseDefinition);

  let actualParserExitCode: number | null = null;

  if (executionResult.parser_result !== null) {
    actualParserExitCode = executionResult.parser_result.exit_code;
  }

  if (!matchesExpectedExitCode(actualParserExitCode, expectedParserExitCodes)) {
    return createTestCaseReport(TestResult.UNEXPECTED_PARSER_EXIT_CODE, executionResult, null);
  }

  return null;
}

/**
 * @brief The interpreter stage result is resolved.
 *
 * When the interpreter exit code does not match the expected values,
 * a failure report is returned. Otherwise, null is returned and
 * evaluation may continue.
 *
 * @param testCaseDefinition Final test case definition.
 * @param executionResult Raw execution result of the test case.
 * @returns Failure report, or null when the interpreter stage passed.
 */
function resolveInterpreterStage(
  testCaseDefinition: TestCaseDefinition,
  executionResult: TestCaseExecutionResult
): TestCaseReport | null {
  const expectedInterpreterExitCodes = getExpectedInterpreterExitCodes(testCaseDefinition);

  let actualInterpreterExitCode: number | null = null;

  if (executionResult.interpreter_result !== null) {
    actualInterpreterExitCode = executionResult.interpreter_result.exit_code;
  }

  if (!matchesExpectedExitCode(actualInterpreterExitCode, expectedInterpreterExitCodes)) {
    return createTestCaseReport(
      TestResult.UNEXPECTED_INTERPRETER_EXIT_CODE,
      executionResult,
      null
    );
  }

  return null;
}

/**
 * @brief The interpreter standard output result is resolved.
 *
 * When an expected output file exists, actual interpreter output is compared
 * with it. A diff failure report is returned when outputs differ.
 * Otherwise, a passed report is created.
 *
 * @param testCaseDefinition Final test case definition.
 * @param executionResult Raw execution result of the test case.
 * @returns Promise resolving to the final test case report.
 */
async function resolveStdoutStage(
  testCaseDefinition: TestCaseDefinition,
  executionResult: TestCaseExecutionResult
): Promise<TestCaseReport> {
  let actualStdout = "";

  if (executionResult.interpreter_result !== null) {
    actualStdout = executionResult.interpreter_result.stdout;
  }

  const comparisonResult = await compareStdout({
    expected_stdout_file: testCaseDefinition.expected_stdout_file,
    actual_stdout: actualStdout,
  });

  //stdout mismatch = diff failure
  if (!comparisonResult.matches) {
    return createTestCaseReport(
      TestResult.INTERPRETER_RESULT_DIFFERS,
      executionResult,
      comparisonResult.diff_output
    );
  }

  return createPassedReport(executionResult);
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
  const parserStageReport = resolveParserStage(testCaseDefinition, executionResult);

  if (parserStageReport !== null) {
    return parserStageReport;
  }

  return createPassedReport(executionResult);
}

/**
 * @brief One execute-only test case result is resolved.
 *
 * The interpreter exit code is evaluated first.
 * If it matches, interpreter output is resolved afterwards.
 *
 * @param testCaseDefinition Final test case definition.
 * @param executionResult Raw execution result of the test case.
 * @returns Promise resolving to the final resolved test case report.
 */
async function resolveExecuteOnlyTestCase(
  testCaseDefinition: TestCaseDefinition,
  executionResult: TestCaseExecutionResult
): Promise<TestCaseReport> {
  const interpreterStageReport = resolveInterpreterStage(testCaseDefinition, executionResult);

  if (interpreterStageReport !== null) {
    return interpreterStageReport;
  }

  if (!hasSuccessfulInterpreterExitCode(executionResult)) {
    return createPassedReport(executionResult);
  }

  return resolveStdoutStage(testCaseDefinition, executionResult);
}

/**
 * @brief One combined test case result is resolved.
 *
 * The parser exit code is evaluated first. If it matches, the interpreter
 * exit code is evaluated next. If both stages match, interpreter output
 * is resolved afterwards.
 *
 * @param testCaseDefinition Final test case definition.
 * @param executionResult Raw execution result of the test case.
 * @returns Promise resolving to the final resolved test case report.
 */
async function resolveCombinedTestCase(
  testCaseDefinition: TestCaseDefinition,
  executionResult: TestCaseExecutionResult
): Promise<TestCaseReport> {
  const parserStageReport = resolveParserStage(testCaseDefinition, executionResult);

  if (parserStageReport !== null) {
    return parserStageReport;
  }

  const interpreterStageReport = resolveInterpreterStage(testCaseDefinition, executionResult);

  if (interpreterStageReport !== null) {
    return interpreterStageReport;
  }

  if (!hasSuccessfulInterpreterExitCode(executionResult)) {
    return createPassedReport(executionResult);
  }

  return resolveStdoutStage(testCaseDefinition, executionResult);
}

/**
 * @brief One executed test case is resolved into a final test report.
 *
 * Evaluation flow is selected from the test case type stored
 * in the final test case definition.
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

  //pick resolver by test type
  if (testCaseType === TestCaseType.PARSE_ONLY) {
    return resolveParseOnlyTestCase(testCaseDefinition, executionResult);
  }

  if (testCaseType === TestCaseType.EXECUTE_ONLY) {
    return resolveExecuteOnlyTestCase(testCaseDefinition, executionResult);
  }

  return resolveCombinedTestCase(testCaseDefinition, executionResult);
}
