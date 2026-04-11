/**
 * @file compiler_runner.ts
 * @brief Running of the SOL26 compiler is implemented.
 * @author Hana Liškařová xliskah00
 *
 * DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
 *
 * A small wrapper over the shared low-level command runner is provided here.
 * Only compiler-specific request preparation is handled in this module.
 */

import { CommandResult, runCommand } from "./process_runner.js";

/**
 * @brief Input data needed to run the compiler are described.
 *
 * Compiler source code is passed through standard input.
 * Command-line arguments are provided explicitly.
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
 * @brief One compiler run is executed.
 *
 * The compiler is started through the shared command runner.
 * Source code is passed as standard input, and the collected result
 * is returned unchanged.
 *
 * @param request Input data for one compiler run.
 * @returns Promise resolving to the collected compiler command result.
 */
export function runCompiler(request: CompilerRequest): Promise<CommandResult> {
  const command = request.command;
  const args = request.args;
  const sourceCode = request.source_code;

  return runCommand({
    command,
    args,
    input: sourceCode,
  });
}
