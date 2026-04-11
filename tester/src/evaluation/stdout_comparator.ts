/**
 * @file stdout_comparator.ts
 * @brief Comparison of program standard output against an expected output file is implemented.
 * @author Hana Liškařová xliskah00
 *
 * DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
 *
 * When an expected output file is available, actual standard output is written
 * to a temporary file and compared with the expected file by using diff.
 *
 * When no expected output file is provided, output is left unchecked.
 */

import { removeTemporaryFile, writeTemporaryFile } from "../temporary_file.js";
import { CommandResult, runCommand } from "../execution/process_runner.js";

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

/**
 * @brief The diff command is executed for two output files.
 *
 * @param expectedOutputFile Path to the expected output file.
 * @param actualOutputFile Path to the temporary file with actual output.
 * @returns Promise resolving to the collected diff command result.
 */
async function runDiffCommand(
  expectedOutputFile: string,
  actualOutputFile: string
): Promise<CommandResult> {
  return runCommand({
    command: "diff",
    args: [expectedOutputFile, actualOutputFile],
    input: null,
  });
}

/**
 * @brief An unchecked comparison result is created.
 *
 * @returns Comparison result indicating that no output comparison was performed.
 */
function createUncheckedComparisonResult(): StdoutComparisonResult {
  return {
    was_checked: false,
    matches: true,
    diff_output: null,
  };
}

/**
 * @brief A successful comparison result is created.
 *
 * @returns Comparison result indicating that outputs match.
 */
function createMatchingComparisonResult(): StdoutComparisonResult {
  return {
    was_checked: true,
    matches: true,
    diff_output: null,
  };
}

/**
 * @brief A differing comparison result is created.
 *
 * @param diffOutput Output produced by diff.
 * @returns Comparison result indicating that outputs differ.
 */
function createDifferingComparisonResult(diffOutput: string): StdoutComparisonResult {
  return {
    was_checked: true,
    matches: false,
    diff_output: diffOutput,
  };
}

/**
 * @brief One diff command result is resolved into a comparison result.
 *
 * Exit code 0 means outputs match.
 * Exit code 1 means outputs differ.
 * Any other exit code is treated as a comparison failure.
 *
 * @param diffResult Result of the diff command.
 * @returns Final standard-output comparison result.
 * @throws Error If the diff command fails unexpectedly.
 */
function resolveDiffResult(diffResult: CommandResult): StdoutComparisonResult {
  //passed
  if (diffResult.exit_code === 0) {
    return createMatchingComparisonResult();
  }

  //failed
  if (diffResult.exit_code === 1) {
    return createDifferingComparisonResult(diffResult.stdout);
  }

  throw new Error(`Diff command failed with exit code ${String(diffResult.exit_code)}.`);
}

/**
 * @brief One standard output comparison is performed.
 *
 * If no expected output file is provided, comparison is skipped and the
 * result is reported as unchecked. Otherwise, actual standard output is
 * compared with the expected output file by using diff.
 *
 * @param request Input data for one standard output comparison.
 * @returns Promise resolving to the comparison result.
 */
export async function compareStdout(
  request: StdoutComparisonRequest
): Promise<StdoutComparisonResult> {
  const expectedOutputFile = request.expected_stdout_file;

  //skip comparison when no expected output exists
  if (expectedOutputFile === null) {
    return createUncheckedComparisonResult();
  }

  const actualOutputFile = writeTemporaryFile({
    file_name_prefix: "sol26-tester-output",
    file_extension: "txt",
    content: request.actual_stdout,
  });

  try {
    const diffResult = await runDiffCommand(expectedOutputFile, actualOutputFile);

    return resolveDiffResult(diffResult);
    //always remove temp output file
  } finally {
    removeTemporaryFile(actualOutputFile);
  }
}
