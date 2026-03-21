/**
 * @file build_dry_run_report.ts
 * @brief Construction of a dry-run test report is implemented.
 * @author Hana Liškařová xliskah00
 * DOXYGEN COMMENTS ARE AI GENERATED AND PROOF READ BY ME
 *
 * A dry-run report is constructed from already loaded test case definitions and
 * from test case loading failures. Successfully loaded test cases are included
 * in the discovered_test_cases collection. Test cases that failed to load or
 * were filtered out are stored in the unexecuted mapping.
 *
 * No execution results are produced here. The report is therefore returned with
 * results set to null.
 */

import { TestReport } from "../models.js";
import { LoadedTestCases } from "../discovery/load_test_case_definitions.js";
import { TestCaseFilterOptions } from "../discovery/filter_matcher.js";
import { buildUnexecuted } from "./report_builder.js";

/**
 * @brief A dry-run test report is constructed.
 *
 * Successfully loaded test case definitions are included in the discovered
 * test case list. Unexecuted reasons are created for failed loads and for
 * filtered-out test cases. Execution results are intentionally omitted.
 *
 * @param loadedTestCases Loaded test case definitions and loading failures.
 * @param filterOptions Configured test case filter options.
 * @returns Final dry-run test report.
 */
export function buildDryRunReport(
  loadedTestCases: LoadedTestCases,
  filterOptions: TestCaseFilterOptions
): TestReport {
  const unexecuted = buildUnexecuted(loadedTestCases, filterOptions);

  return new TestReport({
    discovered_test_cases: loadedTestCases.loaded_test_cases.map(
      (loadedTestCase) => loadedTestCase.definition
    ),
    unexecuted,
    results: null,
  });
}
