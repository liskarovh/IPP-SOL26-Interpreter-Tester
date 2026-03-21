/**
 * @file stdout_comparator.ts
 * @brief Comparison of program standard output against an expected output file is implemented.
 * @author Hana Liškařová xliskah00
 * DOXYGEN COMMENTS ARE AI GENERATED AND PROOF READ BY ME
 *
 * When an expected output file is available, the actual standard output is
 * written into a temporary file and compared against the expected output file
 * by using the diff command.
 *
 * When no expected output file is provided, the output is considered unchecked
 * and no comparison is performed.
 */

import { rmSync, writeFileSync } from "fs";
import { tmpdir } from "os";
import { join } from "path";

import { runCommand } from "../execution/process_runner.js";

/**
 * @brief Input data needed for one standard output comparison are described.
 */
export interface StdoutComparisonRequest {
  /** Path to the expected output file, or null when no expected output file exists. */
  expected_stdout_file: string | null;
  /** Actual standard output that is to be compared. */
  actual_stdout: string;
}

/**
 * @brief Result of one standard output comparison is described.
 */
export interface StdoutComparisonResult {
  /** Flag indicating whether output comparison was actually performed. */
  was_checked: boolean;
  /** Flag indicating whether the compared outputs match. */
  matches: boolean;
  /** Output of the diff command, or null when no difference output is available. */
  diff_output: string | null;
}

let temporaryOutputFileCounter = 0;

/**
 * @brief A temporary output file path is created.
 *
 * A simple unique file name is built from the current process identifier,
 * current time, and a local counter.
 *
 * @returns Path to a temporary output file.
 */
function createTemporaryOutputFilePath(): string {
  temporaryOutputFileCounter += 1;

  const processIdText = String(process.pid);
  const currentTimeText = String(Date.now());
  const counterText = String(temporaryOutputFileCounter);

  const fileName = `sol26-tester-output-${processIdText}-${currentTimeText}-${counterText}.txt`;

  return join(tmpdir(), fileName);
}

/**
 * @brief A temporary output file is created from actual standard output text.
 *
 * The file is created in the operating system temporary directory and is
 * intended to exist only for the duration of one diff comparison.
 *
 * @param actualStdout Actual standard output text written to the temporary file.
 * @returns Path to the created temporary output file.
 */
function createTemporaryOutputFile(actualStdout: string): string {
  const outputFilePath = createTemporaryOutputFilePath();

  writeFileSync(outputFilePath, actualStdout, "utf8");

  return outputFilePath;
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
 * @brief One standard output comparison is performed.
 *
 * When no expected output file is provided, comparison is skipped and the
 * result is reported as unchecked. Otherwise, the actual standard output is
 * compared against the expected output file by using the diff command.
 *
 * Exit code 0 means that the outputs match.
 * Exit code 1 means that the outputs differ.
 * Any other exit code is treated as a comparison failure.
 *
 * @param request Input data for one standard output comparison.
 * @returns Promise resolving to the comparison result.
 */
export async function compareStdout(
  request: StdoutComparisonRequest
): Promise<StdoutComparisonResult> {
  if (request.expected_stdout_file === null) {
    return {
      was_checked: false,
      matches: true,
      diff_output: null,
    };
  }

  const actualOutputFilePath = createTemporaryOutputFile(request.actual_stdout);

  try {
    const diffResult = await runCommand({
      command: "diff",
      args: [request.expected_stdout_file, actualOutputFilePath],
      input: null,
    });

    if (diffResult.exit_code === 0) {
      return {
        was_checked: true,
        matches: true,
        diff_output: null,
      };
    }

    if (diffResult.exit_code === 1) {
      return {
        was_checked: true,
        matches: false,
        diff_output: diffResult.stdout,
      };
    }

    throw new Error(`The diff command failed with exit code ${String(diffResult.exit_code)}.`);
  } finally {
    removeTemporaryFile(actualOutputFilePath);
  }
}
