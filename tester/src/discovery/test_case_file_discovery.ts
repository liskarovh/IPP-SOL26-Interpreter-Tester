/**
 * @file test_case_file_discovery.ts
 * @brief Discovery of test case files in the SOLtest directory structure is implemented.
 * @author Hana Liškařová xliskah00
 *
 * DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
 *
 * Test case source files with the ".test" extension are searched for here.
 * Matching sibling ".in" and ".out" files are resolved as well.
 */

import { Dirent, existsSync, readdirSync } from "node:fs";
import { basename, join } from "node:path";

import { TestCaseDefinitionFile } from "../models.js";

/**
 * @brief Directory entries are loaded and sorted by name.
 *
 * @param directoryPath Path to the directory whose entries are read.
 * @returns Sorted directory entries.
 */
function getSortedDirectoryEntries(directoryPath: string): Dirent[] {
  const entries = readdirSync(directoryPath, { withFileTypes: true });
  entries.sort((left, right) => left.name.localeCompare(right.name));
  return entries;
}

/**
 * @brief A sibling input or output file path is returned when the file exists.
 *
 * A path with the requested extension is constructed next to the test case file.
 * If the file does not exist, null is returned.
 *
 * @param directoryPath Path to the directory where the sibling file is expected.
 * @param testCaseName Test case name without the ".test" extension.
 * @param extension Expected sibling file extension.
 * @returns Path to the sibling file, or null if the file does not exist.
 */
function getSiblingFilePathIfExists(
  directoryPath: string,
  testCaseName: string,
  extension: ".in" | ".out"
): string | null {
  const siblingFilePath = join(directoryPath, `${testCaseName}${extension}`);

  //missing sibling file
  if (!existsSync(siblingFilePath)) {
    return null;
  }

  return siblingFilePath;
}

/**
 * @brief A discovered test case file model is created from one ".test" file.
 *
 * The base test case name is derived from the file name.
 * Matching ".in" and ".out" files are resolved when present.
 *
 * @param directoryPath Path to the directory containing the test file.
 * @param testFileName Name of the ".test" file.
 * @returns Created discovered test case file model.
 */
function createDiscoveredTestCaseFile(
  directoryPath: string,
  testFileName: string
): TestCaseDefinitionFile {
  const testCaseName = basename(testFileName, ".test");
  const testSourcePath = join(directoryPath, testFileName);
  const stdinFilePath = getSiblingFilePathIfExists(directoryPath, testCaseName, ".in");
  const expectedStdoutFilePath = getSiblingFilePathIfExists(directoryPath, testCaseName, ".out");

  return new TestCaseDefinitionFile({
    name: testCaseName,
    test_source_path: testSourcePath,
    stdin_file: stdinFilePath,
    expected_stdout_file: expectedStdoutFilePath,
  });
}

/**
 * @brief Test case files are discovered in one directory and optionally in subdirectories.
 *
 * All ".test" files in the current directory are collected first.
 * If recursive traversal is enabled, subdirectories are processed afterwards.
 *
 * @param directoryPath Path to the directory being searched.
 * @param recursive Indicates whether subdirectories are also searched.
 * @returns Discovered test case file models from the processed directory tree.
 */
function discoverTestCaseFilesInDirectory(
  directoryPath: string,
  recursive: boolean
): TestCaseDefinitionFile[] {
  const discoveredFiles: TestCaseDefinitionFile[] = [];
  const entries = getSortedDirectoryEntries(directoryPath);

  for (const entry of entries) {
    if (!entry.isFile()) {
      continue;
    }

    //only .test files for test cases
    if (!entry.name.endsWith(".test")) {
      continue;
    }

    const discoveredFile = createDiscoveredTestCaseFile(directoryPath, entry.name);
    discoveredFiles.push(discoveredFile);
  }

  //stop if recursive traversal is not enabled
  if (!recursive) {
    return discoveredFiles;
  }

  for (const entry of entries) {
    if (!entry.isDirectory()) {
      continue;
    }

    const subdirectoryPath = join(directoryPath, entry.name);
    const discoveredFilesInSubdirectory = discoverTestCaseFilesInDirectory(subdirectoryPath, true);

    for (const discoveredFile of discoveredFilesInSubdirectory) {
      discoveredFiles.push(discoveredFile);
    }
  }

  return discoveredFiles;
}

/**
 * @brief Test case files are discovered in the provided test directory.
 *
 * Discovery is delegated to the internal directory traversal helper.
 * The final result is sorted by full test source path.
 *
 * @param testsDir Path to the root directory with test cases.
 * @param recursive Indicates whether subdirectories are also searched.
 * @returns Discovered test case file models.
 */
export function discoverTestCaseFiles(
  testsDir: string,
  recursive: boolean
): TestCaseDefinitionFile[] {
  const discoveredFiles = discoverTestCaseFilesInDirectory(testsDir, recursive);

  discoveredFiles.sort((left, right) =>
    left.test_source_path.localeCompare(right.test_source_path)
  );

  return discoveredFiles;
}
