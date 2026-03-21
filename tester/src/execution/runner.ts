/**
 * @file tool_runners.ts
 * @brief Running of the SOL26 compiler and interpreter is implemented.
 * @author Hana Liškařová xliskah00
 * DOXYGEN COMMENTS ARE AI GENERATED AND PROOF READ BY ME
 *
 * Small wrappers over the shared low-level command runner are provided here.
 * One wrapper is used for the SOL26 compiler, and one wrapper is used for
 * the interpreter.
 *
 * Only tool-specific request preparation is implemented here. Test execution
 * flow, output comparison, and reporting are intentionally left to later
 * layers.
 */

import { CommandResult, runCommand } from "./process_runner.js";

/**
 * @brief Input data needed to run the compiler are described.
 *
 * The compiler source code is passed through standard input. Command-line
 * arguments are kept explicit so that the caller can decide how the compiler
 * executable is started.
 */
export interface CompilerRequest {
  /** Command used to start the compiler. */
  command: string;
  /** Arguments passed to the compiler command. */
  args: string[];
  /** SOL26 source code passed to the compiler through standard input. */
  source_code: string;
}

/**
 * @brief Input data needed to run the interpreter are described.
 *
 * The interpreter command and its arguments are provided explicitly so that
 * the caller can decide how the XML source file and optional input file are
 * passed to the interpreter.
 */
export interface InterpreterRequest {
  /** Command used to start the interpreter. */
  command: string;
  /** Arguments passed to the interpreter command. */
  args: string[];
}

/**
 * @brief One compiler run is executed.
 *
 * The compiler is started through the shared command runner. The compiler
 * source code is passed as standard input, and the collected command result
 * is returned unchanged.
 *
 * @param request Input data for one compiler run.
 * @returns Promise resolving to the collected compiler command result.
 */
export function runCompiler(request: CompilerRequest): Promise<CommandResult> {
  return runCommand({
    command: request.command,
    args: request.args,
    input: request.source_code,
  });
}

/**
 * @brief One interpreter run is executed.
 *
 * The interpreter is started through the shared command runner. The provided
 * arguments are forwarded unchanged because the interpreter interface is
 * defined by the selected interpreter implementation.
 *
 * @param request Input data for one interpreter run.
 * @returns Promise resolving to the collected interpreter command result.
 */
export function runInterpreter(request: InterpreterRequest): Promise<CommandResult> {
  return runCommand({
    command: request.command,
    args: request.args,
    input: null,
  });
}
