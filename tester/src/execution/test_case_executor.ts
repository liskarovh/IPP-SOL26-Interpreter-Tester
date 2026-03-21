/**
 * @file test_case_executor.ts
 * @brief Execution of one loaded test case is implemented.
 * @author Hana Liškařová xliskah00
 * DOXYGEN COMMENTS ARE AI GENERATED AND PROOF READ BY ME
 *
 * One already loaded test case is executed according to its resolved test case
 * type. Parse-only, execute-only, and combined execution flows are handled here.
 *
 * Source code is taken directly from the loaded test case, so the original
 * SOLtest file does not have to be parsed again. Temporary XML files are
 * created only when they are needed by the interpreter interface.
 */

import { rmSync, writeFileSync } from "fs";
import { tmpdir } from "os";
import { join } from "path";

import { TestCaseType } from "../models.js";
import { LoadedTestCase } from "../discovery/load_test_case_definitions.js";
import { CommandResult } from "./process_runner.js";
import { runCompiler, runInterpreter } from "./runner.js";

/**
 * @brief Input data needed to execute one loaded test case are described.
 *
 * Compiler and interpreter commands are provided explicitly together with their
 * base argument lists. Interpreter arguments are constructed by appending the
 * XML file path and then the optional input file path.
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
 *
 * Parser result is present for parse-only and combined test cases.
 * Interpreter result is present for execute-only test cases and for combined
 * test cases whose parser stage finished successfully.
 */
export interface TestCaseExecutionResult {
  /** Result of the parser/compiler stage, or null when no parser stage was executed. */
  parser_result: CommandResult | null;
  /** Result of the interpreter stage, or null when no interpreter stage was executed. */
  interpreter_result: CommandResult | null;
}

let temporaryXmlFileCounter = 0;

/**
 * @brief A temporary XML file path is created.
 *
 * A simple unique file name is built from the current process identifier,
 * current time, and a local counter.
 *
 * @returns Path to a temporary XML file.
 */
function createTemporaryXmlFilePath(): string {
  temporaryXmlFileCounter += 1;

  const processIdText = String(process.pid);
  const currentTimeText = String(Date.now());
  const counterText = String(temporaryXmlFileCounter);

  const fileName = `sol26-tester-${processIdText}-${currentTimeText}-${counterText}.xml`;

  return join(tmpdir(), fileName);
}

/**
 * @brief A temporary XML file is created from XML text.
 *
 * The file is created in the operating system temporary directory and is
 * intended to exist only for the duration of one interpreter run.
 *
 * @param xmlSourceCode XML source code written to the temporary file.
 * @returns Path to the created temporary XML file.
 */
function createTemporaryXmlFile(xmlSourceCode: string): string {
  const xmlFilePath = createTemporaryXmlFilePath();

  writeFileSync(xmlFilePath, xmlSourceCode, "utf8");

  return xmlFilePath;
}

/**
 * @brief A temporary file is removed when it exists.
 *
 * Forced removal is used so that cleanup does not fail when the file was
 * already removed or was never created successfully.
 *
 * @param filePath Path to the temporary file.
 */
function removeTemporaryFile(filePath: string): void {
  rmSync(filePath, { force: true });
}

/**
 * @brief Interpreter arguments are built from base arguments and file paths.
 *
 * The XML file path is appended after the configured base interpreter
 * arguments. When an input file path is present, it is appended after the XML
 * file path.
 *
 * @param baseArgs Base interpreter arguments.
 * @param xmlFilePath Path to the XML source file.
 * @param inputFilePath Optional path to the input file.
 * @returns Final interpreter argument list.
 */
function buildInterpreterArgs(
  baseArgs: string[],
  xmlFilePath: string,
  inputFilePath: string | null
): string[] {
  const finalArgs = [...baseArgs, "-s", xmlFilePath];

  if (inputFilePath !== null) {
    finalArgs.push("-i");
    finalArgs.push(inputFilePath);
  }

  return finalArgs;
}

/**
 * @brief One parse-only test case is executed.
 *
 * Only the compiler stage is run here. No interpreter stage is executed for
 * parse-only test cases.
 *
 * @param request Input data needed to execute one loaded test case.
 * @returns Promise resolving to the collected test case execution result.
 */
async function executeParseOnlyTestCase(
  request: TestCaseExecutorRequest
): Promise<TestCaseExecutionResult> {
  const parserResult = await runCompiler({
    command: request.compiler_command,
    args: request.compiler_args,
    source_code: request.loaded_test_case.source_code,
  });

  return {
    parser_result: parserResult,
    interpreter_result: null,
  };
}

/**
 * @brief One execute-only test case is executed.
 *
 * XML source code is written to a temporary file and the interpreter is then
 * started over that file. The temporary file is removed afterwards.
 *
 * @param request Input data needed to execute one loaded test case.
 * @returns Promise resolving to the collected test case execution result.
 */
async function executeExecuteOnlyTestCase(
  request: TestCaseExecutorRequest
): Promise<TestCaseExecutionResult> {
  const xmlFilePath = createTemporaryXmlFile(request.loaded_test_case.source_code);

  try {
    const interpreterResult = await runInterpreter({
      command: request.interpreter_command,
      args: buildInterpreterArgs(
        request.interpreter_args,
        xmlFilePath,
        request.loaded_test_case.definition.stdin_file
      ),
    });

    return {
      parser_result: null,
      interpreter_result: interpreterResult,
    };
  } finally {
    removeTemporaryFile(xmlFilePath);
  }
}

/**
 * @brief One combined test case is executed.
 *
 * The compiler is run first. When the compiler does not finish with exit code
 * zero, the interpreter is not started. Otherwise, the produced XML output is
 * written to a temporary file and the interpreter is run over that file.
 *
 * @param request Input data needed to execute one loaded test case.
 * @returns Promise resolving to the collected test case execution result.
 */
async function executeCombinedTestCase(
  request: TestCaseExecutorRequest
): Promise<TestCaseExecutionResult> {
  const parserResult = await runCompiler({
    command: request.compiler_command,
    args: request.compiler_args,
    source_code: request.loaded_test_case.source_code,
  });

  if (parserResult.exit_code !== 0) {
    return {
      parser_result: parserResult,
      interpreter_result: null,
    };
  }

  const xmlFilePath = createTemporaryXmlFile(parserResult.stdout);

  try {
    const interpreterResult = await runInterpreter({
      command: request.interpreter_command,
      args: buildInterpreterArgs(
        request.interpreter_args,
        xmlFilePath,
        request.loaded_test_case.definition.stdin_file
      ),
    });

    return {
      parser_result: parserResult,
      interpreter_result: interpreterResult,
    };
  } finally {
    removeTemporaryFile(xmlFilePath);
  }
}

/**
 * @brief One loaded test case is executed according to its test case type.
 *
 * The execution flow is selected from the resolved test case type stored in
 * the final test case definition.
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
