/**
 * @file test_case_file_discovery.ts
 * @brief Discovery of test case files in the SOLtest directory structure is implemented.
 * @author  Hana Liškařová xliskah00
 * DOXYGEN COMMENTS ARE AI GENERATED AND PROOF READ BY ME
 *
 * Test case source files with the ".test" extension are searched for in the provided
 * directory. Matching sibling ".in" and ".out" files are also looked up. Recursive
 * traversal is supported when it is requested.
 *
 * The result is returned as an array of TestCaseDefinitionFile instances defined by
 * the provided project template.
 */

import { Dirent, existsSync, readdirSync } from "node:fs";
import { basename, join } from "node:path";

import { TestCaseDefinitionFile } from "../models.js";

/**
 * @brief Directory entries are loaded and sorted by name.
 *
 * A deterministic processing order is ensured by sorting the loaded entries.
 * This makes debugging and later testing easier.
 *
 * @param directoryPath Path to the directory whose entries are to be read.
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
 * When the file is not present, null is returned instead.
 *
 * @param directoryPath Path to the directory where the sibling file is expected.
 * @param testCaseName Test case name without the ".test" extension.
 * @param extension Expected sibling file extension.
 * @returns Path to the sibling file, or null when the file does not exist.
 */
function getSiblingFilePathIfExists(
    directoryPath: string,
    testCaseName: string,
    extension: ".in" | ".out"
): string | null {
    const siblingFilePath = join(directoryPath, `${testCaseName}${extension}`);

    if (!existsSync(siblingFilePath)) {
        return null;
    }

    return siblingFilePath;
}

/**
 * @brief A discovered test case file model is created from one ".test" file.
 *
 * The base test case name is derived from the file name. Paths to matching
 * ".in" and ".out" files are also resolved when such files are present.
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
 * @brief Test case files are discovered in one directory and optionally in its subdirectories.
 *
 * First, all ".test" files in the current directory are collected. When recursive
 * traversal is enabled, subdirectories are then processed in the same way.
 *
 * @param directoryPath Path to the directory that is to be searched.
 * @param recursive Flag indicating whether subdirectories are also to be searched.
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

        if (!entry.name.endsWith(".test")) {
            continue;
        }

        const discoveredFile = createDiscoveredTestCaseFile(directoryPath, entry.name);
        discoveredFiles.push(discoveredFile);
    }

    if (!recursive) {
        return discoveredFiles;
    }

    for (const entry of entries) {
        if (!entry.isDirectory()) {
            continue;
        }

        const subdirectoryPath = join(directoryPath, entry.name);
        const discoveredFilesInSubdirectory = discoverTestCaseFilesInDirectory(
            subdirectoryPath,
            true
        );

        for (const discoveredFile of discoveredFilesInSubdirectory) {
            discoveredFiles.push(discoveredFile);
        }
    }

    return discoveredFiles;
}

/**
 * @brief Test case files are discovered in the provided test directory.
 *
 * Discovery is delegated to the internal directory traversal function. The final
 * result is sorted by full test source path so that a stable output order is produced.
 *
 * @param testsDir Path to the root directory with test cases.
 * @param recursive Flag indicating whether subdirectories are also to be searched.
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