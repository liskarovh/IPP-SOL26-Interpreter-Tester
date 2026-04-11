/**
 * @file temporary_file.ts
 * @brief Shared helper functions for temporary file handling are implemented.
 * @author Hana Liškařová xliskah00
 *
 * DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
 *
 * Temporary file paths are created inside the operating-system temporary
 * directory. File names are made unique enough for the tester workflow by
 * using process identifier, current time, and a local counter.
 */

import { rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

/**
 * @brief Input data needed to create one temporary file are described.
 */
export interface WriteTemporaryFileRequest {
  /** Prefix used at the beginning of the generated file name. */
  file_name_prefix: string;
  /** File extension used at the end of the generated file name. */
  file_extension: string;
  /** File content written into the temporary file. */
  content: string;
}

/**
 * @brief Temporary file counter is stored.
 *
 * A local counter is combined with process information and current
 * time to keep generated temporary file names unique enough for the
 * tester workflow.
 */
let temporaryFileCounter = 0;

/**
 * @brief A temporary file path is created.
 *
 * A simple file name is built from process identifier, current time,
 * local counter, requested prefix, and requested extension.
 *
 * @param fileNamePrefix Prefix used at the beginning of the generated file name.
 * @param fileExtension File extension used at the end of the generated file name.
 * @returns Path to a temporary file.
 */
function createTemporaryFilePath(fileNamePrefix: string, fileExtension: string): string {
  temporaryFileCounter += 1;

  const processIdText = String(process.pid);
  const currentTimeText = String(Date.now());
  const counterText = String(temporaryFileCounter);

  const fileName =
    `${fileNamePrefix}-${processIdText}-${currentTimeText}-${counterText}.` + fileExtension;

  return join(tmpdir(), fileName);
}

/**
 * @brief A temporary file is created from text content.
 *
 * @param request Input data needed to create one temporary file.
 * @returns Path to the created temporary file.
 */
export function writeTemporaryFile(request: WriteTemporaryFileRequest): string {
  const filePath = createTemporaryFilePath(request.file_name_prefix, request.file_extension);

  writeFileSync(filePath, request.content, "utf8");

  return filePath;
}

/**
 * @brief A temporary file is removed when it exists.
 *
 * Forced removal is used so that cleanup does not fail when the file was
 * already removed or was never created successfully.
 *
 * @param filePath Path to the temporary file.
 */
export function removeTemporaryFile(filePath: string): void {
  rmSync(filePath, { force: true });
}
