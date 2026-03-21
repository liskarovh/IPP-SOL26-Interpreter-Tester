/**
 * @file filter_matcher.ts
 * @brief Matching of loaded test case definitions against configured filters is implemented.
 * @author Hana Liškařová xliskah00
 * DOXYGEN COMMENTS ARE AI GENERATED AND PROOF READ BY ME
 *
 * Include and exclude filters configured by the command-line interface are
 * evaluated against final TestCaseDefinition instances. Literal matching and
 * regular-expression-based matching are both supported.
 *
 * Only matching of one already loaded test case definition is performed here.
 * Loading, reporting, and execution are intentionally left to later stages.
 */

import { TestCaseDefinition } from "../models.js";

/**
 * @brief Filter options relevant to test case matching are described.
 *
 * The field names are intentionally aligned with the CLI argument structure
 * used in tester.ts so that the parsed CLI object can later be passed directly.
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
 * @brief Filter values are normalized before matching is performed.
 *
 * Null is converted into an empty array. Individual values are trimmed, and
 * empty values are removed so that later matching code can work with one clean
 * representation.
 *
 * @param filterValues Raw filter values.
 * @returns Normalized non-empty filter values.
 */
function normalizeFilterValues(filterValues: string[] | null): string[] {
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
 * @brief One filter value is matched against one actual value.
 *
 * Literal equality is used when regex matching is disabled. Otherwise, the
 * filter value is compiled into a regular expression and tested against the
 * actual value.
 *
 * @param actualValue Actual value taken from a test case definition.
 * @param filterValue One configured filter value.
 * @param useRegexMatching Flag indicating whether regex matching is enabled.
 * @returns True when the value matches, otherwise false.
 * @throws Error when the filter value is not a valid regular expression.
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
 * @brief A value is matched against any configured filter value.
 *
 * The first successful match causes the function to return true. When no filter
 * value matches, false is returned.
 *
 * @param actualValue Actual value taken from a test case definition.
 * @param filterValues Configured filter values.
 * @param useRegexMatching Flag indicating whether regex matching is enabled.
 * @returns True when any filter value matches, otherwise false.
 * @throws Error when one of the filter values is not a valid regular expression.
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
 * @brief Include filters are matched against one loaded test case definition.
 *
 * When no include filters are configured, the test case is considered included
 * by default. Otherwise, the test case is considered included only when at
 * least one include rule matches.
 *
 * General include filters are matched against the test case name and category.
 * Test-only include filters are matched only against the name. Category-only
 * include filters are matched only against the category.
 *
 * @param testCaseDefinition Loaded final test case definition.
 * @param filterOptions Configured test case filter options.
 * @returns True when the test case passes include matching, otherwise false.
 * @throws Error when one of the configured include filters is not a valid regular expression.
 */
function matchesIncludeFilters(
  testCaseDefinition: TestCaseDefinition,
  filterOptions: TestCaseFilterOptions
): boolean {
  const generalIncludeFilters = normalizeFilterValues(filterOptions.include);
  const categoryIncludeFilters = normalizeFilterValues(filterOptions.include_category);
  const testIncludeFilters = normalizeFilterValues(filterOptions.include_test);

  const hasAtLeastOneIncludeFilter =
    generalIncludeFilters.length > 0 ||
    categoryIncludeFilters.length > 0 ||
    testIncludeFilters.length > 0;

  if (!hasAtLeastOneIncludeFilter) {
    return true;
  }

  if (
    matchesAnyFilterValue(
      testCaseDefinition.name,
      generalIncludeFilters,
      filterOptions.regex_filters
    )
  ) {
    return true;
  }

  if (
    matchesAnyFilterValue(
      testCaseDefinition.category,
      generalIncludeFilters,
      filterOptions.regex_filters
    )
  ) {
    return true;
  }

  if (
    matchesAnyFilterValue(testCaseDefinition.name, testIncludeFilters, filterOptions.regex_filters)
  ) {
    return true;
  }

  return matchesAnyFilterValue(
    testCaseDefinition.category,
    categoryIncludeFilters,
    filterOptions.regex_filters
  );
}

/**
 * @brief Exclude filters are matched against one loaded test case definition.
 *
 * When at least one exclude rule matches, the test case is considered excluded.
 *
 * General exclude filters are matched against the test case name and category.
 * Test-only exclude filters are matched only against the name. Category-only
 * exclude filters are matched only against the category.
 *
 * @param testCaseDefinition Loaded final test case definition.
 * @param filterOptions Configured test case filter options.
 * @returns True when the test case matches at least one exclude rule, otherwise false.
 * @throws Error when one of the configured exclude filters is not a valid regular expression.
 */
function matchesExcludeFilters(
  testCaseDefinition: TestCaseDefinition,
  filterOptions: TestCaseFilterOptions
): boolean {
  const generalExcludeFilters = normalizeFilterValues(filterOptions.exclude);
  const categoryExcludeFilters = normalizeFilterValues(filterOptions.exclude_category);
  const testExcludeFilters = normalizeFilterValues(filterOptions.exclude_test);

  if (
    matchesAnyFilterValue(
      testCaseDefinition.name,
      generalExcludeFilters,
      filterOptions.regex_filters
    )
  ) {
    return true;
  }

  if (
    matchesAnyFilterValue(
      testCaseDefinition.category,
      generalExcludeFilters,
      filterOptions.regex_filters
    )
  ) {
    return true;
  }

  if (
    matchesAnyFilterValue(testCaseDefinition.name, testExcludeFilters, filterOptions.regex_filters)
  ) {
    return true;
  }

  return matchesAnyFilterValue(
    testCaseDefinition.category,
    categoryExcludeFilters,
    filterOptions.regex_filters
  );
}

/**
 * @brief Final inclusion of one loaded test case definition is determined.
 *
 * A test case is included only when it passes include matching and does not
 * match any exclude rule. Exclude rules always take precedence over include
 * rules.
 *
 * @param testCaseDefinition Loaded final test case definition.
 * @param filterOptions Configured test case filter options.
 * @returns True when the test case should remain in the selected set, otherwise false.
 * @throws Error when one of the configured filters is not a valid regular expression.
 */
export function matchesConfiguredFilters(
  testCaseDefinition: TestCaseDefinition,
  filterOptions: TestCaseFilterOptions
): boolean {
  if (!matchesIncludeFilters(testCaseDefinition, filterOptions)) {
    return false;
  }

  return !matchesExcludeFilters(testCaseDefinition, filterOptions);
}
