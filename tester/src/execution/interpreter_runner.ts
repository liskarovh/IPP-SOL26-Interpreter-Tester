/**
 * @file interpreter_runner.ts
 * @brief Running of the SOL26 interpreter is implemented.
 * @author Hana Liškařová xliskah00
 *
 * DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
 *
 * A small wrapper over the shared low-level command runner is provided here.
 * Only interpreter-specific request preparation is handled in this module.
 */

import { CommandResult, runCommand } from "./process_runner.js";

/**
 * @brief Input data needed to run the interpreter are described.
 *
 * Interpreter command and arguments are provided explicitly.
 * Optional program input may be passed through standard input.
 */
export interface InterpreterRequest {
  /** Command used to start the interpreter. */
  command: string;
  /** Arguments passed to the interpreter command. */
  args: string[];
  /** Optional program input written to the interpreter standard input. */
  input: string | null;
}

/**
 * @brief One interpreter run is executed.
 *
 * The interpreter is started through the shared command runner.
 * Provided arguments are forwarded unchanged.
 *
 * @param request Input data for one interpreter run.
 * @returns Promise resolving to the collected interpreter command result.
 */
export function runInterpreter(request: InterpreterRequest): Promise<CommandResult> {
  const command = request.command;
  const args = request.args;
  const input = request.input;

  return runCommand({
    command,
    args,
    input,
  });
}
