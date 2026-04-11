/**
 * @file filter_matcher.ts
 * @brief Matching of test cases against configured filters is implemented.
 * @author Hana Liškařová xliskah00
 *
 * DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
 *
 * One loaded test case definition is checked against include and exclude
 * filters here. Both literal and regex-based matching are supported.
 */

import { TestCaseDefinition } from "../models.js";

/**
 * @brief Filter options used for test case matching are described.
 *
 * Field names are aligned with the CLI options used in tester.ts.
 */
export interface TestCaseFilterOptions {
  /** Include filters matching either test case name or category. */
  include: string[] | null;
  /** Include filters matching only category. */
  include_category: string[] | null;
  /** Include filters matching only test case name. */
  include_test: string[] | null;
  /** Exclude filters matching either test case name or category. */
  exclude: string[] | null;
  /** Exclude filters matching only category. */
  exclude_category: string[] | null;
  /** Exclude filters matching only test case name. */
  exclude_test: string[] | null;
  /** Flag indicating whether filters are to be interpreted as regular expressions. */
  regex_filters: boolean;
}

/**
 * @brief Normalized filter options are described.
 *
 * Null values are converted to arrays, values are trimmed,
 * and empty entries are removed.
 */
interface NormalizedFilterOptions {
  /** Include filters matching either test case name or category. */
  include: string[];
  /** Include filters matching only category. */
  include_category: string[];
  /** Include filters matching only test case name. */
  include_test: string[];
  /** Exclude filters matching either test case name or category. */
  exclude: string[];
  /** Exclude filters matching only category. */
  exclude_category: string[];
  /** Exclude filters matching only test case name. */
  exclude_test: string[];
  /** Flag indicating whether filters are interpreted as regular expressions. */
  regex_filters: boolean;
}

/**
 * @brief Filter values are normalized.
 *
 * Null is converted to an empty array, values are trimmed,
 * and empty entries are removed.
 *
 * @param filterValues Raw filter values.
 * @returns Normalized filter values.
 */
function normalizeFilterValues(filterValues: string[] | null): string[] {
  //treat as no filter list
  if (filterValues === null) {
    return [];
  }

  const normalizedValues: string[] = [];

  for (const filterValue of filterValues) {
    const trimmedValue = filterValue.trim();

    if (trimmedValue === "") {
      continue;
    }

    normalizedValues.push(trimmedValue);
  }

  return normalizedValues;
}

/**
 * @brief Filter options are normalized.
 *
 * @param filterOptions Raw filter options.
 * @returns Normalized filter options.
 */
function normalizeFilterOptions(filterOptions: TestCaseFilterOptions): NormalizedFilterOptions {
  return {
    include: normalizeFilterValues(filterOptions.include),
    include_category: normalizeFilterValues(filterOptions.include_category),
    include_test: normalizeFilterValues(filterOptions.include_test),
    exclude: normalizeFilterValues(filterOptions.exclude),
    exclude_category: normalizeFilterValues(filterOptions.exclude_category),
    exclude_test: normalizeFilterValues(filterOptions.exclude_test),
    regex_filters: filterOptions.regex_filters,
  };
}

/**
 * @brief One filter value is matched against one actual value.
 *
 * Literal equality is used when regex matching is disabled.
 * Otherwise, the filter value is treated as a regular expression.
 *
 * @param actualValue Actual value from the test case definition.
 * @param filterValue One configured filter value.
 * @param useRegexMatching Indicates whether regex matching is enabled.
 * @returns True if the value matches, otherwise false.
 * @throws Error If the filter value is not a valid regular expression.
 */
function matchesFilterValue(
  actualValue: string,
  filterValue: string,
  useRegexMatching: boolean
): boolean {
  if (!useRegexMatching) {
    return actualValue === filterValue;
  }

  const filterPattern = new RegExp(filterValue);

  return filterPattern.test(actualValue);
}

/**
 * @brief A value is matched against multiple filter values.
 *
 * The first successful match returns true. If no filter matches,
 * false is returned.
 *
 * @param actualValue Actual value from the test case definition.
 * @param filterValues Configured filter values.
 * @param useRegexMatching Indicates whether regex matching is enabled.
 * @returns True if any filter value matches, otherwise false.
 * @throws Error If one of the filter values is not a valid regular expression.
 */
function matchesAnyFilterValue(
  actualValue: string,
  filterValues: string[],
  useRegexMatching: boolean
): boolean {
  for (const filterValue of filterValues) {
    if (matchesFilterValue(actualValue, filterValue, useRegexMatching)) {
      return true;
    }
  }

  return false;
}

/**
 * @brief General filters are matched against test case name and category.
 *
 * @param testCaseDefinition Loaded test case definition.
 * @param filterValues General filter values.
 * @param useRegexMatching Indicates whether regex matching is enabled.
 * @returns True if either the name or the category matches.
 */
function matchesGeneralFilters(
  testCaseDefinition: TestCaseDefinition,
  filterValues: string[],
  useRegexMatching: boolean
): boolean {
  if (matchesAnyFilterValue(testCaseDefinition.name, filterValues, useRegexMatching)) {
    return true;
  }

  return matchesAnyFilterValue(testCaseDefinition.category, filterValues, useRegexMatching);
}

/**
 * @brief Test-only filters are matched against test case name.
 *
 * @param testCaseDefinition Loaded test case definition.
 * @param filterValues Test-only filter values.
 * @param useRegexMatching Indicates whether regex matching is enabled.
 * @returns True if the test case name matches.
 */
function matchesTestFilters(
  testCaseDefinition: TestCaseDefinition,
  filterValues: string[],
  useRegexMatching: boolean
): boolean {
  return matchesAnyFilterValue(testCaseDefinition.name, filterValues, useRegexMatching);
}

/**
 * @brief Category-only filters are matched against test case category.
 *
 * @param testCaseDefinition Loaded test case definition.
 * @param filterValues Category-only filter values.
 * @param useRegexMatching Indicates whether regex matching is enabled.
 * @returns True if the test case category matches.
 */
function matchesCategoryFilters(
  testCaseDefinition: TestCaseDefinition,
  filterValues: string[],
  useRegexMatching: boolean
): boolean {
  return matchesAnyFilterValue(testCaseDefinition.category, filterValues, useRegexMatching);
}

/**
 * @brief Presence of include filters is checked.
 *
 * @param filterOptions Normalized filter options.
 * @returns True if at least one include filter is configured, otherwise false.
 */
function hasIncludeFilters(filterOptions: NormalizedFilterOptions): boolean {
  if (filterOptions.include.length > 0) {
    return true;
  }

  if (filterOptions.include_category.length > 0) {
    return true;
  }

  return filterOptions.include_test.length > 0;
}

/**
 * @brief Include filters are matched against one test case definition.
 *
 * If no include filters are configured, the test case is included by default.
 * Otherwise, at least one include rule must match.
 *
 * @param testCaseDefinition Loaded test case definition.
 * @param filterOptions Normalized filter options.
 * @returns True if the test case passes include matching, otherwise false.
 */
function matchesIncludeFilters(
  testCaseDefinition: TestCaseDefinition,
  filterOptions: NormalizedFilterOptions
): boolean {
  if (!hasIncludeFilters(filterOptions)) {
    return true;
  }

  if (
    matchesGeneralFilters(testCaseDefinition, filterOptions.include, filterOptions.regex_filters)
  ) {
    return true;
  }

  if (
    matchesTestFilters(testCaseDefinition, filterOptions.include_test, filterOptions.regex_filters)
  ) {
    return true;
  }

  return matchesCategoryFilters(
    testCaseDefinition,
    filterOptions.include_category,
    filterOptions.regex_filters
  );
}

/**
 * @brief Exclude filters are matched against one test case definition.
 *
 * If at least one exclude rule matches, the test case is excluded.
 *
 * @param testCaseDefinition Loaded test case definition.
 * @param filterOptions Normalized filter options.
 * @returns True if the test case matches at least one exclude rule, otherwise false.
 */
function matchesExcludeFilters(
  testCaseDefinition: TestCaseDefinition,
  filterOptions: NormalizedFilterOptions
): boolean {
  if (
    matchesGeneralFilters(testCaseDefinition, filterOptions.exclude, filterOptions.regex_filters)
  ) {
    return true;
  }

  if (
    matchesTestFilters(testCaseDefinition, filterOptions.exclude_test, filterOptions.regex_filters)
  ) {
    return true;
  }

  return matchesCategoryFilters(
    testCaseDefinition,
    filterOptions.exclude_category,
    filterOptions.regex_filters
  );
}

/**
 * @brief Final filter result for one test case definition is determined.
 *
 * A test case is selected only if it passes include matching and does not
 * match any exclude rule. Exclude rules always take precedence.
 *
 * @param testCaseDefinition Loaded test case definition.
 * @param filterOptions Configured filter options.
 * @returns True if the test case should remain selected, otherwise false.
 * @throws Error If one of the configured filters is not a valid regular expression.
 */
export function matchesConfiguredFilters(
  testCaseDefinition: TestCaseDefinition,
  filterOptions: TestCaseFilterOptions
): boolean {
  const normalizedFilterOptions = normalizeFilterOptions(filterOptions);

  if (!matchesIncludeFilters(testCaseDefinition, normalizedFilterOptions)) {
    return false;
  }

  //exclude rules override include rules
  if (matchesExcludeFilters(testCaseDefinition, normalizedFilterOptions)) {
    return false;
  }

  return true;
}
