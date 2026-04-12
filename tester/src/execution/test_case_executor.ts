/**
 * @file test_case_executor.ts
 * @brief Execution of one loaded test case is implemented.
 * @author Hana Liškařová xliskah00
 *
 * DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
 *
 * One already loaded test case is executed here according to its resolved
 * test case type.
 */

import { existsSync } from "fs";

import { LoadedTestCase } from "../discovery/load_test_case_definitions.js";
import { TestCaseType } from "../models.js";
import { CommandResult } from "./process_runner.js";
import { runCompiler } from "./compiler_runner.js";
import { runInterpreter } from "./interpreter_runner.js";
import { removeTemporaryFile, writeTemporaryFile } from "../temporary_file.js";

/**
 * @brief Input data needed to execute one loaded test case are described.
 */
export interface TestCaseExecutorRequest {
  /** Loaded test case that is to be executed. */
  loaded_test_case: LoadedTestCase;
  /** Command used to start the compiler. */
  compiler_command: string;
  /** Base arguments passed to the compiler command. */
  compiler_args: string[];
  /** Command used to start the interpreter. */
  interpreter_command: string;
  /** Base arguments passed to the interpreter command. */
  interpreter_args: string[];
}

/**
 * @brief Collected execution result of one test case is described.
 */
export interface TestCaseExecutionResult {
  /** Result of the parser/compiler stage, or null when no parser stage was executed. */
  parser_result: CommandResult | null;
  /** Result of the interpreter stage, or null when no interpreter stage was executed. */
  interpreter_result: CommandResult | null;
}

/**
 * @brief Interpreter input file path is resolved from the loaded test case.
 *
 * If no stdin file is defined for the current test case, null is returned.
 *
 * @param request Input data needed to execute one loaded test case.
 * @returns Path to the interpreter input file, or null when not defined.
 */
function getInterpreterInputFilePath(request: TestCaseExecutorRequest): string | null {
  return request.loaded_test_case.definition.stdin_file;
}

/**
 * @brief Interpreter arguments are built from base arguments and test case files.
 *
 * XML source is always passed through the -s option. If the loaded test case
 * defines an input file for the interpreted program, that file is passed
 * through the -i option as well.
 *
 * @param baseArgs Base interpreter arguments.
 * @param xmlFilePath Path to the XML source file.
 * @param inputFilePath Path to the interpreted program input file, or null.
 * @returns Final interpreter argument list.
 */
function buildInterpreterArgs(
  baseArgs: string[],
  xmlFilePath: string,
  inputFilePath: string | null
): string[] {
  const args = [...baseArgs, "-s", xmlFilePath];

  //program input file is passed through interpreter CLI
  if (inputFilePath !== null) {
    args.push("-i", inputFilePath);
  }

  return args;
}

/**
 * @brief One compiler step is executed.
 *
 * @param request Input data needed to execute one loaded test case.
 * @returns Promise resolving to the compiler command result.
 */
function runCompilerStep(request: TestCaseExecutorRequest): Promise<CommandResult> {
  validateCompilerScriptAvailability(request);

  return runCompiler({
    command: request.compiler_command,
    args: request.compiler_args,
    source_code: request.loaded_test_case.source_code,
  });
}

/**
 * @brief One interpreter step is executed over an XML file.
 *
 * XML input is passed through a temporary file. Interpreted program input is
 * passed through the interpreter CLI when a stdin file is defined for the test
 * case. No program input is written to the interpreter process standard input.
 *
 * @param request Input data needed to execute one loaded test case.
 * @param xmlFilePath Path to the XML file passed to the interpreter.
 * @returns Promise resolving to the interpreter command result.
 */
function runInterpreterStep(
  request: TestCaseExecutorRequest,
  xmlFilePath: string
): Promise<CommandResult> {
  const inputFilePath = getInterpreterInputFilePath(request);

  return runInterpreter({
    command: request.interpreter_command,
    args: buildInterpreterArgs(request.interpreter_args, xmlFilePath, inputFilePath),
    input: null,
  });
}

/**
 * @brief Interpreter execution over temporary XML source is performed.
 *
 * XML text is written to a temporary file, the interpreter is run over that
 * file, and the file is removed afterwards.
 *
 * @param request Input data needed to execute one loaded test case.
 * @param xmlSourceCode XML source code written to the temporary file.
 * @param parserResult Parser result associated with this execution, or null.
 * @returns Promise resolving to the collected test case execution result.
 */
async function executeInterpreterFromXmlSource(
  request: TestCaseExecutorRequest,
  xmlSourceCode: string,
  parserResult: CommandResult | null
): Promise<TestCaseExecutionResult> {
  const xmlFilePath = writeTemporaryFile({
    file_name_prefix: "sol26-tester",
    file_extension: "xml",
    content: xmlSourceCode,
  });

  try {
    const interpreterResult = await runInterpreterStep(request, xmlFilePath);

    return {
      parser_result: parserResult,
      interpreter_result: interpreterResult,
    };
    //remove temp file
  } finally {
    removeTemporaryFile(xmlFilePath);
  }
}

/**
 * @brief One parse-only test case is executed.
 *
 * @param request Input data needed to execute one loaded test case.
 * @returns Promise resolving to the collected test case execution result.
 */
async function executeParseOnlyTestCase(
  request: TestCaseExecutorRequest
): Promise<TestCaseExecutionResult> {
  const parserResult = await runCompilerStep(request);

  return {
    parser_result: parserResult,
    interpreter_result: null,
  };
}

/**
 * @brief One execute-only test case is executed.
 *
 * @param request Input data needed to execute one loaded test case.
 * @returns Promise resolving to the collected test case execution result.
 */
function executeExecuteOnlyTestCase(
  request: TestCaseExecutorRequest
): Promise<TestCaseExecutionResult> {
  return executeInterpreterFromXmlSource(request, request.loaded_test_case.source_code, null);
}

/**
 * @brief One combined test case is executed.
 *
 * @param request Input data needed to execute one loaded test case.
 * @returns Promise resolving to the collected test case execution result.
 */
async function executeCombinedTestCase(
  request: TestCaseExecutorRequest
): Promise<TestCaseExecutionResult> {
  const parserResult = await runCompilerStep(request);

  //parser failed, no interpreter execution
  if (parserResult.exit_code !== 0) {
    return {
      parser_result: parserResult,
      interpreter_result: null,
    };
  }

  return executeInterpreterFromXmlSource(request, parserResult.stdout, parserResult);
}

/**
 * @brief One loaded test case is executed according to its test case type.
 *
 * @param request Input data needed to execute one loaded test case.
 * @returns Promise resolving to the collected test case execution result.
 */
export async function executeTestCase(
  request: TestCaseExecutorRequest
): Promise<TestCaseExecutionResult> {
  const testCaseType = request.loaded_test_case.definition.test_type;

  if (testCaseType === TestCaseType.PARSE_ONLY) {
    return executeParseOnlyTestCase(request);
  }

  if (testCaseType === TestCaseType.EXECUTE_ONLY) {
    return executeExecuteOnlyTestCase(request);
  }

  return executeCombinedTestCase(request);
}

/**
 * @brief Availability of the configured compiler script is validated.
 *
 * The first compiler argument is treated as the compiler script path.
 * If that file does not exist, execution of the current test case fails
 * immediately.
 *
 * @param request Input data needed to execute one loaded test case.
 * @throws Error If the configured compiler script does not exist.
 */
function validateCompilerScriptAvailability(request: TestCaseExecutorRequest): void {
  const compilerScriptPath = request.compiler_args[0];

  if (compilerScriptPath === undefined) {
    return;
  }

  //missing compiler script - execution failure
  if (!existsSync(compilerScriptPath)) {
    throw new Error(`ENOENT: compiler script was not found: ${compilerScriptPath}`);
  }
}
