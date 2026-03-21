/**
 * @file report_builder.ts
 * @brief Construction of the final execution report is implemented.
 * @author Hana Liškařová xliskah00
 * DOXYGEN COMMENTS ARE AI GENERATED AND PROOF READ BY ME
 *
 * Already resolved executed test cases are grouped by category and converted
 * into the final report structures defined by the provided project template.
 *
 * Only final report construction is implemented here. Test loading, filtering,
 * execution, and result resolution are intentionally left to earlier layers.
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
 * The final test case definition is paired with its already resolved
 * individual test case report.
 */
export interface ResolvedTestCase {
  /** Final test case definition. */
  definition: TestCaseDefinition;
  /** Final resolved report of the test case. */
  report: TestCaseReport;
}

/**
 * @brief Input data needed to build the final report are described.
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
 * Category totals are first collected into this internal structure and are
 * converted into the final CategoryReport model afterwards.
 */
interface CategoryBucket {
  /** Sum of points for all executed test cases in the category. */
  total_points: number;
  /** Sum of points for all passed test cases in the category. */
  passed_points: number;
  /** Mapping from test case names to their final reports. */
  test_results: Record<string, TestCaseReport>;
}

/**
 * @brief Empty mutable category data are created.
 *
 * @returns Empty mutable category data.
 */
function createEmptyCategoryBucket(): CategoryBucket {
  return {
    total_points: 0,
    passed_points: 0,
    test_results: {},
  };
}

/**
 * @brief One load failure is converted into an unexecuted reason.
 *
 * Parsing failures are treated as malformed test case files. Type-resolution
 * failures are mapped to the dedicated cannot-determine-type code when the
 * error message clearly indicates that situation. All remaining loading
 * failures are mapped to the generic other reason code.
 *
 * @param loadFailure Failed test case load information.
 * @returns Unexecuted reason corresponding to the failure.
 */
function createUnexecutedReasonFromLoadFailure(
  loadFailure: TestCaseLoadFailure
): UnexecutedReason {
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
 * Failed test case loads are first converted into unexecuted reasons. Afterwards,
 * loaded test cases are checked against configured filters and filtered-out
 * test cases are added to the same mapping.
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
    if (matchesConfiguredFilters(loadedTestCase.definition, filterOptions)) {
      continue;
    }

    unexecuted[loadedTestCase.definition.name] = new UnexecutedReason(
      UnexecutedReasonCode.FILTERED_OUT,
      "The test case was excluded by the configured include/exclude filters."
    );
  }

  return unexecuted;
}

/**
 * @brief One resolved test case is added into a category bucket.
 *
 * Category totals are updated and the individual test case report is stored
 * under the test case name.
 *
 * @param bucket Mutable category bucket.
 * @param resolvedTestCase One resolved executed test case.
 */
function addResolvedTestCaseToBucket(
  bucket: CategoryBucket,
  resolvedTestCase: ResolvedTestCase
): void {
  const testCasePoints = resolvedTestCase.definition.points;

  bucket.total_points += testCasePoints;
  bucket.test_results[resolvedTestCase.definition.name] = resolvedTestCase.report;

  if (resolvedTestCase.report.result === TestResult.PASSED) {
    bucket.passed_points += testCasePoints;
  }
}

/**
 * @brief Final category reports are built from resolved test cases.
 *
 * Resolved test cases are grouped by category and converted into the
 * final CategoryReport model defined by the template.
 *
 * @param resolvedTestCases Already resolved executed test cases.
 * @returns Final mapping from category names to category reports.
 */
function buildCategoryReports(
  resolvedTestCases: ResolvedTestCase[]
): Record<string, CategoryReport> {
  const categoryBuckets: Record<string, CategoryBucket> = {};

  for (const resolvedTestCase of resolvedTestCases) {
    const categoryName = resolvedTestCase.definition.category;

    if (categoryBuckets[categoryName] === undefined) {
      categoryBuckets[categoryName] = createEmptyCategoryBucket();
    }

    addResolvedTestCaseToBucket(categoryBuckets[categoryName], resolvedTestCase);
  }

  const categoryReports: Record<string, CategoryReport> = {};

  for (const [categoryName, bucket] of Object.entries(categoryBuckets)) {
    categoryReports[categoryName] = new CategoryReport(
      bucket.total_points,
      bucket.passed_points,
      bucket.test_results
    );
  }

  return categoryReports;
}

/**
 * @brief The final execution report is built.
 *
 * Already resolved executed test cases are grouped into category reports and
 * are combined with discovered test cases and unexecuted test cases into the
 * final TestReport model.
 *
 * @param request Input data needed to build the final report.
 * @returns Final execution report.
 */
export function buildReport(request: ReportBuilderRequest): TestReport {
  const categoryReports = buildCategoryReports(request.resolved_test_cases);

  return new TestReport({
    discovered_test_cases: request.discovered_test_cases,
    unexecuted: request.unexecuted,
    results: categoryReports,
  });
}
