/**
 * @file process_runner.ts
 * @brief Running of one external command is implemented.
 * @author Hana Liškařová xliskah00
 * DOXYGEN COMMENTS ARE AI GENERATED AND PROOF READ BY ME
 *
 * One external command is started, optional text input is written to its
 * standard input, and its standard output, standard error, exit code,
 * and termination signal are collected.
 *
 * Only low-level command running is implemented here. No SOL26-specific
 * logic is included in this module.
 */

import { execFile } from "child_process";

/**
 * @brief Input data needed to run one external command are described.
 */
export interface CommandRequest {
  /** Command that is to be started. */
  command: string;
  /** Arguments passed to the command. */
  args: string[];
  /** Optional text written to standard input. */
  input: string | null;
}

/**
 * @brief Result of one finished external command is described.
 */
export interface CommandResult {
  /** Exit code returned by the command, or null when the command ended by signal. */
  exit_code: number | null;
  /** Signal that terminated the command, or null when the command exited normally. */
  signal: NodeJS.Signals | null;
  /** Text collected from standard output. */
  stdout: string;
  /** Text collected from standard error. */
  stderr: string;
}

/**
 * @brief One unknown process error is converted into an Error instance.
 *
 * Native Error instances are returned unchanged. String values are converted
 * into Error instances directly. Objects with a string message field are
 * converted from that message. All remaining values are converted into
 * a generic process error.
 *
 * @param error Unknown process error value.
 * @returns Error instance created from the provided value.
 */
function createProcessError(error: unknown): Error {
  if (error instanceof Error) {
    return error;
  }

  if (typeof error === "string") {
    return new Error(error);
  }

  if (typeof error === "object" && error !== null) {
    const errorWithMessage = error as { message?: unknown };

    if (typeof errorWithMessage.message === "string") {
      return new Error(errorWithMessage.message);
    }
  }

  return new Error("An unknown process error occurred.");
}

/**
 * @brief One external command is run and its outputs are collected.
 *
 * The command is started directly without a shell. Standard output and
 * standard error are collected as UTF-8 text. When the command cannot be
 * started at all, the returned promise is rejected. When the command is
 * started successfully, the returned promise is resolved after the command
 * finishes, even when its exit code is non-zero.
 *
 * @param request Input data for one command run.
 * @returns Promise resolving to the collected command result.
 */
export function runCommand(request: CommandRequest): Promise<CommandResult> {
  return new Promise<CommandResult>((resolve, reject) => {
    const startedCommand = execFile(
      request.command,
      request.args,
      {
        encoding: "utf8",
      },
      (error, stdout, stderr) => {
        if (error !== null && typeof error.code === "string") {
          reject(createProcessError(error));
          return;
        }

        const result: CommandResult = {
          exit_code: startedCommand.exitCode ?? null,
          signal: startedCommand.signalCode ?? null,
          stdout,
          stderr,
        };

        resolve(result);
      }
    );

    if (request.input !== null && startedCommand.stdin !== null) {
      startedCommand.stdin.write(request.input);
    }

    if (startedCommand.stdin !== null) {
      startedCommand.stdin.end();
    }
  });
}
