/**
 * @file run_tester.ts
 * @brief Main tester workflow is implemented.
 * @author Hana Liškařová xliskah00
 *
 * DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
 *
 * Test cases are loaded, optionally filtered, optionally executed,
 * resolved into final reports, and assembled into the final TestReport model.
 */

import {
  TestReport,
  UnexecutedReason,
  UnexecutedReasonCode,
  type TestCaseDefinition,
} from "./models.js";
import {
  loadTestCaseDefinitions,
  type LoadedTestCase,
} from "./discovery/load_test_case_definitions.js";
import {
  matchesConfiguredFilters,
  type TestCaseFilterOptions,
} from "./discovery/filter_matcher.js";
import { executeTestCase } from "./execution/test_case_executor.js";
import { resolveTestCase } from "./evaluation/test_resolver.js";
import {
  buildDryRunReport,
  buildReport,
  buildUnexecuted,
  type ResolvedTestCase,
} from "./report/report_builder.js";

/**
 * @brief Execution configuration needed by the tester workflow is described.
 */
export interface ExecutionConfiguration {
  /** Command used to start the compiler. */
  compiler_command: string;
  /** Arguments passed to the compiler command. */
  compiler_args: string[];
  /** Command used to start the interpreter. */
  interpreter_command: string;
  /** Arguments passed to the interpreter command. */
  interpreter_args: string[];
}

/**
 * @brief Input data needed to run the main tester workflow are described.
 */
export interface RunTesterRequest extends TestCaseFilterOptions {
  /** Path to the directory with SOLtest files. */
  tests_dir: string;
  /** Flag indicating whether subdirectories should also be searched. */
  recursive: boolean;
  /** Flag indicating whether dry-run mode is enabled. */
  dry_run: boolean;
  /** Execution configuration used to start the compiler and interpreter. */
  execution: ExecutionConfiguration;
}

/**
 * @brief Result of executing selected test cases is described.
 */
interface ExecutedSelectionResult {
  /** Final resolved reports of executed test cases. */
  resolved_test_cases: ResolvedTestCase[];
  /** Execution failures recorded as unexecuted reasons. */
  execution_failures: Record<string, UnexecutedReason>;
}

/**
 * @brief Discovered test case definitions are extracted from loaded test cases.
 *
 * @param loadedTestCases Successfully loaded test cases.
 * @returns Final discovered test case definitions.
 */
function getDiscoveredTestCaseDefinitions(
  loadedTestCases: LoadedTestCase[]
): TestCaseDefinition[] {
  const discoveredTestCases: TestCaseDefinition[] = [];

  for (const loadedTestCase of loadedTestCases) {
    discoveredTestCases.push(loadedTestCase.definition);
  }

  return discoveredTestCases;
}

/**
 * @brief Loaded test cases selected by configured filters are collected.
 *
 * @param loadedTestCases Successfully loaded test cases.
 * @param request Main tester workflow request.
 * @returns Selected test cases that should be executed.
 */
function selectTestCasesForExecution(
  loadedTestCases: LoadedTestCase[],
  request: RunTesterRequest
): LoadedTestCase[] {
  const selectedTestCases: LoadedTestCase[] = [];

  for (const loadedTestCase of loadedTestCases) {
    //skip filtered-out test cases
    if (!matchesConfiguredFilters(loadedTestCase.definition, request)) {
      continue;
    }

    selectedTestCases.push(loadedTestCase);
  }

  return selectedTestCases;
}

/**
 * @brief Execution failure type is derived from the error message.
 *
 * Errors caused by missing commands, failed process spawning, or missing
 * execution permissions are treated as cannot-execute failures.
 * All other errors are treated as generic execution failures.
 *
 * @param errorMessage Human-readable execution error message.
 * @returns Matching unexecuted reason code.
 */
function getExecutionFailureReasonCode(errorMessage: string): UnexecutedReasonCode {
  const normalizedMessage = errorMessage.toLowerCase();

  //detect command startup failures
  if (normalizedMessage.includes("enoent")) {
    return UnexecutedReasonCode.CANNOT_EXECUTE;
  }

  if (normalizedMessage.includes("eacces")) {
    return UnexecutedReasonCode.CANNOT_EXECUTE;
  }

  if (normalizedMessage.includes("spawn")) {
    return UnexecutedReasonCode.CANNOT_EXECUTE;
  }

  return UnexecutedReasonCode.OTHER;
}

/**
 * @brief One execution failure is recorded.
 *
 * @param executionFailures Recorded execution failures.
 * @param testCaseName Name of the failed test case.
 * @param error Unknown execution error.
 */
function recordExecutionFailure(
  executionFailures: Record<string, UnexecutedReason>,
  testCaseName: string,
  error: unknown
): void {
  let errorMessage = "An unknown error occurred.";

  //extract best available error message
  if (error instanceof Error) {
    errorMessage = error.message;
  } else if (typeof error === "string") {
    errorMessage = error;
  }

  const reasonCode = getExecutionFailureReasonCode(errorMessage);

  executionFailures[testCaseName] = new UnexecutedReason(reasonCode, errorMessage);
}

/**
 * @brief Recorded execution failures are merged into unexecuted test cases.
 *
 * @param unexecuted Already collected unexecuted test cases.
 * @param executionFailures Execution failures collected during execution.
 */
function mergeExecutionFailures(
  unexecuted: Record<string, UnexecutedReason>,
  executionFailures: Record<string, UnexecutedReason>
): void {
  const failedTestCaseNames = Object.keys(executionFailures);

  for (const testCaseName of failedTestCaseNames) {
    const reason = executionFailures[testCaseName];

    if (reason === undefined) {
      continue;
    }

    unexecuted[testCaseName] = reason;
  }
}

/**
 * @brief Selected test cases are executed and resolved.
 *
 * @param selectedTestCases Selected test cases that should be executed.
 * @param execution Execution configuration.
 * @returns Final resolved reports and execution failures.
 */
async function executeSelectedTestCases(
  selectedTestCases: LoadedTestCase[],
  execution: ExecutionConfiguration
): Promise<ExecutedSelectionResult> {
  const resolvedTestCases: ResolvedTestCase[] = [];
  const executionFailures: Record<string, UnexecutedReason> = {};

  for (const selectedTestCase of selectedTestCases) {
    const testCaseName = selectedTestCase.definition.name;

    try {
      //execute first and resolve after successful execution
      const executionResult = await executeTestCase({
        loaded_test_case: selectedTestCase,
        compiler_command: execution.compiler_command,
        compiler_args: execution.compiler_args,
        interpreter_command: execution.interpreter_command,
        interpreter_args: execution.interpreter_args,
      });

      const resolvedReport = await resolveTestCase(selectedTestCase.definition, executionResult);

      resolvedTestCases.push({
        definition: selectedTestCase.definition,
        report: resolvedReport,
      });
    } catch (error: unknown) {
      recordExecutionFailure(executionFailures, testCaseName, error);
    }
  }

  return {
    resolved_test_cases: resolvedTestCases,
    execution_failures: executionFailures,
  };
}

/**
 * @brief Main tester workflow is performed.
 *
 * Test cases are loaded first. In dry-run mode, only discovery and filtering
 * results are reported. Otherwise, selected test cases are executed and
 * resolved into the final report.
 *
 * @param request Main tester workflow request.
 * @returns Final tester report.
 */
export async function runTester(request: RunTesterRequest): Promise<TestReport> {
  const loadedTestCases = loadTestCaseDefinitions(request.tests_dir, request.recursive);

  //stop dry run before execution
  if (request.dry_run) {
    return buildDryRunReport(loadedTestCases, request);
  }

  const selectedTestCases = selectTestCasesForExecution(
    loadedTestCases.loaded_test_cases,
    request
  );

  const executedSelection = await executeSelectedTestCases(selectedTestCases, request.execution);

  const unexecuted = buildUnexecuted(loadedTestCases, request);

  //execution failure to unresolved
  mergeExecutionFailures(unexecuted, executedSelection.execution_failures);

  return buildReport({
    discovered_test_cases: getDiscoveredTestCaseDefinitions(loadedTestCases.loaded_test_cases),
    unexecuted,
    resolved_test_cases: executedSelection.resolved_test_cases,
  });
}
