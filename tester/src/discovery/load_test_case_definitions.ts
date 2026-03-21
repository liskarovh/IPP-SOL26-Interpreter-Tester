/**
 * @file load_test_case_definitions.ts
 * @brief Loading of final test case definitions from discovered SOLtest files is implemented.
 * @author   Hana Liškařová xliskah00
 * DOXYGEN COMMENTS ARE AI GENERATED AND PROOF READ BY ME
 *
 * Test case source files are first discovered in the provided directory tree.
 * Each discovered ".test" file is then parsed into an intermediate parsed model
 * and converted into the final TestCaseDefinition model defined by the project
 * template.
 *
 * Successfully loaded test case definitions are collected separately from
 * failed test case loads. Only loading is performed here. Filtering, report
 * generation, and execution are intentionally left for later stages.
 */

import { TestCaseDefinition } from "../models.js";
import { buildTestCaseDefinition } from "./test_case_builder.js";
import { parseTestCaseFile } from "./parse_test.js";
import { discoverTestCaseFiles } from "./test_case_file_discovery.js";

/**
 * @brief The stage at which test case loading failed is described.
 *
 * Parsing failures are distinguished from model-construction failures so that
 * later processing can react to them more clearly.
 */
export type TestCaseLoadFailureStage = "parse" | "build";

/**
 * @brief Information about one failed test case load is stored.
 *
 * The test case name and source path are preserved together with the stage of
 * failure and with a human-readable error message.
 */
export interface TestCaseLoadFailure {
  /** Name of the failed test case. */
  name: string;
  /** Path to the ".test" file of the failed test case. */
  test_source_path: string;
  /** Stage at which loading failed. */
  stage: TestCaseLoadFailureStage;
  /** Human-readable error message describing the failure. */
  error_message: string;
}

/**
 * @brief The result of loading all test case definitions is stored.
 *
 * Successfully loaded definitions and failed test case loads are returned
 * separately so that later pipeline stages can process them independently.
 */
export interface LoadedTestCaseDefinitions {
  /** Successfully loaded final test case definitions. */
  test_case_definitions: TestCaseDefinition[];
  /** Failed test case loads. */
  failed_test_cases: TestCaseLoadFailure[];
}

/**
 * @brief A human-readable error message is extracted from an unknown thrown value.
 *
 * Native Error instances are unwrapped to their message text. Non-Error values
 * are converted into a generic fallback message.
 *
 * @param error Unknown thrown value.
 * @returns Human-readable error message.
 */
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "An unknown error occurred while the test case was being loaded.";
}

/**
 * @brief A failed test case load record is created.
 *
 * The provided metadata are copied into a simple structure that can later be
 * transformed into a reporting model.
 *
 * @param testCaseName Name of the failed test case.
 * @param testSourcePath Path to the ".test" file of the failed test case.
 * @param stage Stage at which loading failed.
 * @param error Unknown thrown value that describes the failure.
 * @returns Failed test case load record.
 */
function createLoadFailure(
  testCaseName: string,
  testSourcePath: string,
  stage: TestCaseLoadFailureStage,
  error: unknown
): TestCaseLoadFailure {
  return {
    name: testCaseName,
    test_source_path: testSourcePath,
    stage,
    error_message: getErrorMessage(error),
  };
}

/**
 * @brief All final test case definitions are loaded from the provided test directory.
 *
 * First, discovered SOLtest files are collected. Afterwards, each discovered file
 * is parsed and converted into the final TestCaseDefinition model. Successful
 * definitions and failed loads are returned separately.
 *
 * @param testsDir Path to the root directory with SOLtest files.
 * @param recursive Flag indicating whether subdirectories are also to be searched.
 * @returns Loaded final test case definitions and failed test case loads.
 */
export function loadTestCaseDefinitions(
  testsDir: string,
  recursive: boolean
): LoadedTestCaseDefinitions {
  const discoveredFiles = discoverTestCaseFiles(testsDir, recursive);
  const loadedDefinitions: TestCaseDefinition[] = [];
  const failedTestCases: TestCaseLoadFailure[] = [];

  for (const discoveredFile of discoveredFiles) {
    let parsedTestCase;

    try {
      parsedTestCase = parseTestCaseFile(discoveredFile);
    } catch (error: unknown) {
      const loadFailure = createLoadFailure(
        discoveredFile.name,
        discoveredFile.test_source_path,
        "parse",
        error
      );

      failedTestCases.push(loadFailure);
      continue;
    }

    try {
      const loadedDefinition = buildTestCaseDefinition(parsedTestCase);
      loadedDefinitions.push(loadedDefinition);
    } catch (error: unknown) {
      const loadFailure = createLoadFailure(
        discoveredFile.name,
        discoveredFile.test_source_path,
        "build",
        error
      );

      failedTestCases.push(loadFailure);
    }
  }

  return {
    test_case_definitions: loadedDefinitions,
    failed_test_cases: failedTestCases,
  };
}
