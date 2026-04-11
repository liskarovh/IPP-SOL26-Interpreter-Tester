/**
 * @file load_test_case_definitions.ts
 * @brief Loading of final test case definitions from discovered SOLtest files is implemented.
 * @author Hana Liškařová xliskah00
 *
 * DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
 *
 * Discovered ".test" files are parsed and converted into final test case
 * definitions here. Successful loads and load failures are returned separately.
 */

import type { TestCaseDefinition, TestCaseDefinitionFile } from "../models.js";

import { parseTestCaseFile, ParsedTestCase } from "./parse_test.js";
import { createTestCaseDefinition } from "./test_case_factory.js";
import { discoverTestCaseFiles } from "./test_case_file_discovery.js";

/**
 * @brief The stage of a test case load failure is described.
 *
 * Parse failures are distinguished from build failures.
 */
export type TestCaseLoadFailureStage = "parse" | "build";

/**
 * @brief One successfully loaded test case is described.
 *
 * The final test case definition and the original source code are both kept.
 */
export interface LoadedTestCase {
  /** Final template test case definition. */
  definition: TestCaseDefinition;
  /** Source code loaded from the original SOLtest file. */
  source_code: string;
}

/**
 * @brief One failed test case load is described.
 *
 * The test case name, source path, failure stage, and error message are kept.
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
 * @brief The result of loading test cases is described.
 *
 * Successful loads and failed loads are returned separately.
 */
export interface LoadedTestCases {
  /** Successfully loaded test cases with final definitions and source code. */
  loaded_test_cases: LoadedTestCase[];
  /** Failed test case loads. */
  failed_test_cases: TestCaseLoadFailure[];
}

/**
 * @brief One successful single-file load result is described.
 *
 * This internal helper keeps the main loading loop simple.
 */
interface SuccessfulLoadAttempt {
  /** Discriminator of a successful load attempt. */
  kind: "success";
  /** Successfully loaded test case. */
  loaded_test_case: LoadedTestCase;
}

/**
 * @brief One failed single-file load result is described.
 *
 * This internal helper keeps the main loading loop simple.
 */
interface FailedLoadAttempt {
  /** Discriminator of a failed load attempt. */
  kind: "failure";
  /** Failed test case load record. */
  failed_test_case: TestCaseLoadFailure;
}

/**
 * @brief One single-file load attempt result is described.
 *
 * A discovered file either produces a loaded test case or a load failure.
 */
type LoadAttempt = SuccessfulLoadAttempt | FailedLoadAttempt;

/**
 * @brief One test case name occurrence counter is described.
 *
 * A simple array is used instead of a map to keep the logic explicit.
 */
interface NameOccurrence {
  /** Test case name being counted. */
  name: string;
  /** Number of occurrences of the test case name. */
  count: number;
}

/**
 * @brief A human-readable error message is extracted from a thrown value.
 *
 * Native Error instances provide their message. Other values are replaced
 * with a generic fallback message.
 *
 * @param error Thrown value.
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
 * @param testCaseName Name of the failed test case.
 * @param testSourcePath Path to the failed ".test" file.
 * @param stage Stage at which loading failed.
 * @param error Thrown value describing the failure.
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
 * @brief One discovered test case file is parsed.
 *
 * This helper keeps parsing separated from final model construction.
 *
 * @param discoveredFile Metadata of one discovered ".test" file.
 * @returns Parsed SOLtest test case.
 */
function parseDiscoveredTestCaseFile(discoveredFile: TestCaseDefinitionFile): ParsedTestCase {
  return parseTestCaseFile(discoveredFile);
}

/**
 * @brief One loaded test case is created from parsed data.
 *
 * The final definition is paired with the original source code.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Successfully loaded test case.
 */
function createLoadedTestCase(parsedTestCase: ParsedTestCase): LoadedTestCase {
  const definition = createTestCaseDefinition(parsedTestCase);

  return {
    definition,
    source_code: parsedTestCase.source_code,
  };
}

/**
 * @brief One discovered test case file is loaded.
 *
 * Parsing is attempted first. If parsing succeeds, final definition
 * construction is attempted afterwards.
 *
 * @param discoveredFile Metadata of one discovered ".test" file.
 * @returns Result of loading the discovered test case file.
 */
function loadOneDiscoveredTestCase(discoveredFile: TestCaseDefinitionFile): LoadAttempt {
  let parsedTestCase: ParsedTestCase;

  try {
    parsedTestCase = parseDiscoveredTestCaseFile(discoveredFile);
  } catch (error: unknown) {
    return {
      kind: "failure",
      failed_test_case: createLoadFailure(
        discoveredFile.name,
        discoveredFile.test_source_path,
        "parse",
        error
      ),
    };
  }

  try {
    return {
      kind: "success",
      loaded_test_case: createLoadedTestCase(parsedTestCase),
    };
  } catch (error: unknown) {
    return {
      kind: "failure",
      failed_test_case: createLoadFailure(
        discoveredFile.name,
        discoveredFile.test_source_path,
        "build",
        error
      ),
    };
  }
}

/**
 * @brief Existing name occurrence data are found.
 *
 * @param occurrences Stored name occurrence data.
 * @param testCaseName Name being searched.
 * @returns Matching occurrence data, or undefined if no such name is stored.
 */
function findNameOccurrence(
  occurrences: NameOccurrence[],
  testCaseName: string
): NameOccurrence | undefined {
  for (const occurrence of occurrences) {
    if (occurrence.name === testCaseName) {
      return occurrence;
    }
  }

  return undefined;
}

/**
 * @brief All loaded and failed test case names are collected.
 *
 * Names from successful and failed loads are both included.
 *
 * @param loadedTestCases Successfully loaded test cases.
 * @param failedTestCases Failed test case loads.
 * @returns All collected test case names.
 */
function collectAllTestCaseNames(
  loadedTestCases: LoadedTestCase[],
  failedTestCases: TestCaseLoadFailure[]
): string[] {
  const allNames: string[] = [];

  for (const loadedTestCase of loadedTestCases) {
    allNames.push(loadedTestCase.definition.name);
  }

  for (const failedTestCase of failedTestCases) {
    allNames.push(failedTestCase.name);
  }

  return allNames;
}

/**
 * @brief Two test case names are compared lexicographically.
 *
 * @param left Left test case name.
 * @param right Right test case name.
 * @returns Negative when left is less than right, positive when left is greater
 * than right, or zero when both names are equal.
 */
function compareTestCaseNames(left: string, right: string): number {
  if (left < right) {
    return -1;
  }

  if (left > right) {
    return 1;
  }

  return 0;
}

/**
 * @brief Duplicate test case names are collected.
 *
 * Names are counted using a simple explicit array of occurrence counters.
 *
 * @param loadedTestCases Successfully loaded test cases.
 * @param failedTestCases Failed test case loads.
 * @returns Sorted duplicate test case names.
 */
function collectDuplicateTestCaseNames(
  loadedTestCases: LoadedTestCase[],
  failedTestCases: TestCaseLoadFailure[]
): string[] {
  const allNames = collectAllTestCaseNames(loadedTestCases, failedTestCases);
  const occurrences: NameOccurrence[] = [];

  for (const testCaseName of allNames) {
    const occurrence = findNameOccurrence(occurrences, testCaseName);

    if (occurrence === undefined) {
      occurrences.push({
        name: testCaseName,
        count: 1,
      });
      continue;
    }

    occurrence.count += 1;
  }

  const duplicateNames: string[] = [];

  for (const occurrence of occurrences) {
    if (occurrence.count > 1) {
      duplicateNames.push(occurrence.name);
    }
  }

  duplicateNames.sort(compareTestCaseNames);

  return duplicateNames;
}

/**
 * @brief Uniqueness of all loaded and failed test case names is validated.
 *
 * Duplicate names are rejected because later report structures use test case
 * names as keys.
 *
 * @param loadedTestCases Successfully loaded test cases.
 * @param failedTestCases Failed test case loads.
 * @throws Error If duplicate test case names are found.
 */
function ensureUniqueTestCaseNames(
  loadedTestCases: LoadedTestCase[],
  failedTestCases: TestCaseLoadFailure[]
): void {
  const duplicateNames = collectDuplicateTestCaseNames(loadedTestCases, failedTestCases);

  if (duplicateNames.length === 0) {
    return;
  }

  const duplicateNameList = duplicateNames.join(", ");

  //report keys must stay unique
  throw new Error(
    `Duplicate test case names were found: ${duplicateNameList}. ` +
      "Test case names must be unique."
  );
}

/**
 * @brief All final test case definitions are loaded from the given test directory.
 *
 * Discovered SOLtest files are parsed and converted into final definitions.
 * Successful loads and failed loads are returned separately.
 *
 * @param testsDir Path to the root directory with SOLtest files.
 * @param recursive Indicates whether subdirectories are also searched.
 * @returns Loaded test cases and failed test case loads.
 */
export function loadTestCaseDefinitions(testsDir: string, recursive: boolean): LoadedTestCases {
  const discoveredFiles = discoverTestCaseFiles(testsDir, recursive);
  const loadedTestCases: LoadedTestCase[] = [];
  const failedTestCases: TestCaseLoadFailure[] = [];

  for (const discoveredFile of discoveredFiles) {
    const loadAttempt = loadOneDiscoveredTestCase(discoveredFile);

    if (loadAttempt.kind === "success") {
      loadedTestCases.push(loadAttempt.loaded_test_case);
      continue;
    }

    failedTestCases.push(loadAttempt.failed_test_case);
  }

  ensureUniqueTestCaseNames(loadedTestCases, failedTestCases);

  return {
    loaded_test_cases: loadedTestCases,
    failed_test_cases: failedTestCases,
  };
}
