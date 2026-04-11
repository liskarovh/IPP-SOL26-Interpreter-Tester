/**
 * @file test_case_factory.ts
 * @brief Construction of the final TestCaseDefinition model is implemented.
 * @author Hana Liškařová xliskah00
 *
 * DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
 *
 * A parsed SOLtest test case is converted into the final TestCaseDefinition
 * model here.
 */

import { TestCaseDefinition, TestCaseType } from "../models.js";
import { classifyTestCase } from "./test_case_classifier.js";
import { ParsedTestCase } from "./parse_test.js";

/**
 * @brief Common data shared by all final test case definitions are described.
 *
 * These values are copied from the parsed test case and combined later
 * with type-specific exit-code fields.
 */
interface CommonDefinitionData {
  /** Test case name. */
  name: string;
  /** Path to the ".test" source file. */
  test_source_path: string;
  /** Optional path to the ".in" file. */
  stdin_file: string | null;
  /** Optional path to the ".out" file. */
  expected_stdout_file: string | null;
  /** Optional test case description. */
  description: string | null;
  /** Required category of the test case. */
  category: string;
  /** Required point value of the test case. */
  points: number;
}

/**
 * @brief Common final-definition data are extracted from the parsed test case.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Common data shared by all final test case definitions.
 */
function getCommonDefinitionData(parsedTestCase: ParsedTestCase): CommonDefinitionData {
  return {
    name: parsedTestCase.name,
    test_source_path: parsedTestCase.test_source_path,
    stdin_file: parsedTestCase.stdin_file,
    expected_stdout_file: parsedTestCase.expected_stdout_file,
    description: parsedTestCase.description,
    category: parsedTestCase.category,
    points: parsedTestCase.points,
  };
}

/**
 * @brief Parser exit codes for a combined test case are prepared.
 *
 * Combined test cases use null when parser exit codes were not provided.
 * Otherwise, the parsed parser exit codes are forwarded unchanged.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Parser exit codes for a combined test case, or null if none were provided.
 */
function getCombinedParserExitCodes(parsedTestCase: ParsedTestCase): number[] | null {
  //combined tests possible no parser exit codes
  if (parsedTestCase.expected_parser_exit_codes.length === 0) {
    return null;
  }

  return parsedTestCase.expected_parser_exit_codes;
}

/**
 * @brief A parse-only TestCaseDefinition model is created.
 *
 * Parser exit codes are copied from the parsed test case.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Final parse-only TestCaseDefinition model.
 */
function createParseOnlyDefinition(parsedTestCase: ParsedTestCase): TestCaseDefinition {
  const commonData = getCommonDefinitionData(parsedTestCase);

  return new TestCaseDefinition({
    ...commonData,
    test_type: TestCaseType.PARSE_ONLY,
    expected_parser_exit_codes: parsedTestCase.expected_parser_exit_codes,
    expected_interpreter_exit_codes: null,
  });
}

/**
 * @brief An execute-only TestCaseDefinition model is created.
 *
 * Interpreter exit codes are copied from the parsed test case.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Final execute-only TestCaseDefinition model.
 */
function createExecuteOnlyDefinition(parsedTestCase: ParsedTestCase): TestCaseDefinition {
  const commonData = getCommonDefinitionData(parsedTestCase);

  return new TestCaseDefinition({
    ...commonData,
    test_type: TestCaseType.EXECUTE_ONLY,
    expected_parser_exit_codes: null,
    expected_interpreter_exit_codes: parsedTestCase.expected_interpreter_exit_codes,
  });
}

/**
 * @brief A combined TestCaseDefinition model is created.
 *
 * Parser exit codes are stored as null when they were not provided.
 * Otherwise, the parsed parser exit codes are forwarded unchanged.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Final combined TestCaseDefinition model.
 */
function createCombinedDefinition(parsedTestCase: ParsedTestCase): TestCaseDefinition {
  const commonData = getCommonDefinitionData(parsedTestCase);
  const combinedParserExitCodes = getCombinedParserExitCodes(parsedTestCase);

  return new TestCaseDefinition({
    ...commonData,
    test_type: TestCaseType.COMBINED,
    expected_parser_exit_codes: combinedParserExitCodes,
    expected_interpreter_exit_codes: parsedTestCase.expected_interpreter_exit_codes,
  });
}

/**
 * @brief The final test case definition is created according to the resolved type.
 *
 * The parsed test case is classified first. Based on the resolved type,
 * the corresponding final TestCaseDefinition model is created.
 *
 * @param parsedTestCase Parsed SOLtest test case.
 * @returns Final TestCaseDefinition model.
 * @throws Error If the test case type cannot be determined or the parsed data are inconsistent.
 */
export function createTestCaseDefinition(parsedTestCase: ParsedTestCase): TestCaseDefinition {
  const testCaseType = classifyTestCase(parsedTestCase);

  if (testCaseType === TestCaseType.PARSE_ONLY) {
    return createParseOnlyDefinition(parsedTestCase);
  }

  if (testCaseType === TestCaseType.EXECUTE_ONLY) {
    return createExecuteOnlyDefinition(parsedTestCase);
  }

  return createCombinedDefinition(parsedTestCase);
}
