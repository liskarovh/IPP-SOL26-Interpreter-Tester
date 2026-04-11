/**
 * @file report_builder.ts
 * @brief Construction of final tester reports is implemented.
 * @author Hana Liškařová xliskah00
 *
 * DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
 *
 * Final report construction is centralized in this module.
 * Both the normal execution report and the dry-run report are built here.
 */

import {
  CategoryReport,
  TestCaseDefinition,
  TestCaseReport,
  TestReport,
  TestResult,
  UnexecutedReason,
  UnexecutedReasonCode,
} from "../models.js";

import { LoadedTestCases, TestCaseLoadFailure } from "../discovery/load_test_case_definitions.js";
import { matchesConfiguredFilters, TestCaseFilterOptions } from "../discovery/filter_matcher.js";

/**
 * @brief One resolved executed test case is described.
 *
 * Final test case definition is paired with its resolved test case report.
 */
export interface ResolvedTestCase {
  /** Final test case definition. */
  definition: TestCaseDefinition;
  /** Final resolved report of the test case. */
  report: TestCaseReport;
}

/**
 * @brief Input data needed to build the final execution report are described.
 */
export interface ReportBuilderRequest {
  /** All successfully discovered test case definitions. */
  discovered_test_cases: TestCaseDefinition[];
  /** Test cases that were not executed together with their reasons. */
  unexecuted: Record<string, UnexecutedReason>;
  /** Already resolved executed test cases. */
  resolved_test_cases: ResolvedTestCase[];
}

/**
 * @brief Mutable category data are described.
 *
 * Category totals are collected into this internal structure first
 * and converted into the final CategoryReport model afterwards.
 */
interface Category {
  /** Sum of points for all executed test cases in the category. */
  total_points: number;
  /** Sum of points for all passed test cases in the category. */
  passed_points: number;
  /** Mapping from test case names to their final reports. */
  test_results: Record<string, TestCaseReport>;
}

/**
 * @brief One named category entry is described.
 *
 * Category data are stored together with category name.
 */
interface NamedCategory {
  /** Category name. */
  name: string;
  /** Mutable category data. */
  category: Category;
}

/**
 * @brief Empty mutable category data are created.
 *
 * @returns Empty mutable category data.
 */
function createEmptyCategory(): Category {
  return {
    total_points: 0,
    passed_points: 0,
    test_results: {},
  };
}

/**
 * @brief Existing category data are found by category name.
 *
 * @param categories Existing named categories.
 * @param categoryName Name of the searched category.
 * @returns Found category data, or undefined if no such category exists.
 */
function findCategory(categories: NamedCategory[], categoryName: string): Category | undefined {
  for (const namedCategory of categories) {
    if (namedCategory.name === categoryName) {
      return namedCategory.category;
    }
  }

  return undefined;
}

/**
 * @brief One load failure is converted into an unexecuted reason.
 *
 * Parse failures are treated as malformed test case files.
 * Type-resolution failures are mapped to the dedicated cannot-determine-type
 * code when the error message clearly indicates that situation.
 * All remaining loading failures use the generic other reason code.
 *
 * @param loadFailure Failed test case load information.
 * @returns Unexecuted reason corresponding to the failure.
 */
function createUnexecutedReasonFromLoadFailure(
  loadFailure: TestCaseLoadFailure
): UnexecutedReason {
  //malformed test file
  if (loadFailure.stage === "parse") {
    return new UnexecutedReason(
      UnexecutedReasonCode.MALFORMED_TEST_CASE_FILE,
      loadFailure.error_message
    );
  }

  if (loadFailure.error_message.toLowerCase().includes("determine")) {
    return new UnexecutedReason(
      UnexecutedReasonCode.CANNOT_DETERMINE_TYPE,
      loadFailure.error_message
    );
  }

  return new UnexecutedReason(UnexecutedReasonCode.OTHER, loadFailure.error_message);
}

/**
 * @brief Unexecuted test cases are built from loading failures and filters.
 *
 * Failed test case loads are converted into unexecuted reasons first.
 * Afterwards, loaded test cases are checked against configured filters and
 * filtered-out test cases are added to the same mapping.
 *
 * @param loadedTestCases Loaded test cases and loading failures.
 * @param filterOptions Configured test case filter options.
 * @returns Final unexecuted mapping.
 */
export function buildUnexecuted(
  loadedTestCases: LoadedTestCases,
  filterOptions: TestCaseFilterOptions
): Record<string, UnexecutedReason> {
  const unexecuted: Record<string, UnexecutedReason> = {};

  for (const failedTestCase of loadedTestCases.failed_test_cases) {
    unexecuted[failedTestCase.name] = createUnexecutedReasonFromLoadFailure(failedTestCase);
  }

  for (const loadedTestCase of loadedTestCases.loaded_test_cases) {
    //skip tests that stay selected
    if (matchesConfiguredFilters(loadedTestCase.definition, filterOptions)) {
      continue;
    }

    unexecuted[loadedTestCase.definition.name] = new UnexecutedReason(
      UnexecutedReasonCode.FILTERED_OUT,
      "Test case was excluded by include/exclude filters."
    );
  }

  return unexecuted;
}

/**
 * @brief One resolved test case is added into a category.
 *
 * Category totals are updated and individual test case report is stored
 * under the test case name.
 *
 * @param category Mutable category data.
 * @param resolvedTestCase One resolved executed test case.
 */
function addResolvedTestCaseToCategory(
  category: Category,
  resolvedTestCase: ResolvedTestCase
): void {
  const testCasePoints = resolvedTestCase.definition.points;

  category.total_points += testCasePoints;
  category.test_results[resolvedTestCase.definition.name] = resolvedTestCase.report;

  if (resolvedTestCase.report.result === TestResult.PASSED) {
    category.passed_points += testCasePoints;
  }
}

/**
 * @brief Final category reports are built from resolved test cases.
 *
 * Resolved test cases are grouped by category and converted into
 * the final CategoryReport model.
 *
 * @param resolvedTestCases Already resolved executed test cases.
 * @returns Final mapping from category names to category reports.
 */
function buildCategoryReports(
  resolvedTestCases: ResolvedTestCase[]
): Record<string, CategoryReport> {
  const categories: NamedCategory[] = [];

  for (const resolvedTestCase of resolvedTestCases) {
    const categoryName = resolvedTestCase.definition.category;
    let category = findCategory(categories, categoryName);

    if (category === undefined) {
      category = createEmptyCategory();
      categories.push({
        name: categoryName,
        category,
      });
    }

    addResolvedTestCaseToCategory(category, resolvedTestCase);
  }

  const categoryReports: Record<string, CategoryReport> = {};

  for (const namedCategory of categories) {
    categoryReports[namedCategory.name] = new CategoryReport(
      namedCategory.category.total_points,
      namedCategory.category.passed_points,
      namedCategory.category.test_results
    );
  }

  return categoryReports;
}

/**
 * @brief Discovered test case definitions are extracted from loaded test cases.
 *
 * Only successfully loaded test case definitions are included
 * in the final discovered test case list.
 *
 * @param loadedTestCases Loaded test cases and loading failures.
 * @returns Successfully discovered test case definitions.
 */
function getDiscoveredTestCaseDefinitions(loadedTestCases: LoadedTestCases): TestCaseDefinition[] {
  const discoveredTestCases: TestCaseDefinition[] = [];

  //keep only successfully loaded definitions
  for (const loadedTestCase of loadedTestCases.loaded_test_cases) {
    discoveredTestCases.push(loadedTestCase.definition);
  }

  return discoveredTestCases;
}

/**
 * @brief Final dry-run report is built.
 *
 * Successfully loaded test case definitions are included in the discovered
 * test case list. Unexecuted reasons are created for failed loads and for
 * filtered-out test cases.
 *
 * @param loadedTestCases Loaded test cases and loading failures.
 * @param filterOptions Configured test case filter options.
 * @returns Final dry-run test report.
 */
export function buildDryRunReport(
  loadedTestCases: LoadedTestCases,
  filterOptions: TestCaseFilterOptions
): TestReport {
  const unexecuted = buildUnexecuted(loadedTestCases, filterOptions);

  return new TestReport({
    discovered_test_cases: getDiscoveredTestCaseDefinitions(loadedTestCases),
    unexecuted,
    results: null,
  });
}

/**
 * @brief Final execution report is built.
 *
 * Already resolved executed test cases are grouped into category reports
 * and combined with discovered and unexecuted test cases into
 * the final TestReport model.
 *
 * @param request Input data needed to build the final report.
 * @returns Final execution report.
 */
export function buildReport(request: ReportBuilderRequest): TestReport {
  //group resolved tests before final report assembly
  const categoryReports = buildCategoryReports(request.resolved_test_cases);

  return new TestReport({
    discovered_test_cases: request.discovered_test_cases,
    unexecuted: request.unexecuted,
    results: categoryReports,
  });
}
