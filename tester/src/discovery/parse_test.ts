/**
 * @file parse_test.ts
 * @brief Parsing of one SOLtest test case file is implemented.
 * @author Hana Liškařová xliskah00
 *
 * DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
 *
 * One discovered ".test" file is read, split into header and source code,
 * and parsed into an internal test case representation.
 */

import { readFileSync } from "node:fs";

import { TestCaseDefinitionFile } from "../models.js";
import { parseTestHeader } from "./parse_test_header.js";

/**
 * @brief One parsed SOLtest test case is described.
 *
 * This internal structure is used after textual parsing and before the final
 * template model is created.
 */
export interface ParsedTestCase {
  /** Test case name derived from the discovered file metadata. */
  name: string;
  /** Path to the ".test" source file. */
  test_source_path: string;
  /** Optional path to the ".in" file. */
  stdin_file: string | null;
  /** Optional path to the ".out" file. */
  expected_stdout_file: string | null;
  /** Optional test case description. */
  description: string | null;
  /** Required category of the test case. */
  category: string;
  /** Required point value of the test case. */
  points: number;
  /** Parser exit codes collected from "!C!" directives. */
  expected_parser_exit_codes: number[];
  /** Interpreter exit codes collected from "!I!" directives. */
  expected_interpreter_exit_codes: number[];
  /** Source code part of the test case. */
  source_code: string;
}

/**
 * @brief Split SOLtest file content is described.
 *
 * Header lines and source code are stored separately so they can be processed
 * by different helpers.
 */
interface SplitTestFileContent {
  /** Header lines stored before the required blank separator line. */
  header_lines: string[];
  /** Source code stored after the required blank separator line. */
  source_code: string;
}

/**
 * @brief File content is normalized to Unix newlines.
 *
 * @param fileContents Raw file content.
 * @returns File content with normalized newline characters.
 */
function normalizeNewlines(fileContents: string): string {
  return fileContents.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
}

/**
 * @brief The first blank separator line is found.
 *
 * @param allLines All normalized file lines.
 * @returns Index of the first blank separator line, or -1 if none exists.
 */
function findHeaderSeparatorIndex(allLines: string[]): number {
  let currentIndex = 0;

  for (const currentLine of allLines) {
    //first blank line ends header
    if (currentLine.trim() === "") {
      return currentIndex;
    }

    currentIndex += 1;
  }

  return -1;
}

/**
 * @brief The required blank separator is validated.
 *
 * @param separatorIndex Index of the detected separator.
 * @param testSourcePath Path to the parsed ".test" file.
 * @throws Error If the required blank separator is missing.
 */
function validateHeaderSeparator(separatorIndex: number, testSourcePath: string): void {
  //header and source separation
  if (separatorIndex === -1) {
    throw new Error(`SOLtest file "${testSourcePath}" does not contain blank line separator.`);
  }
}

/**
 * @brief Presence of source code is validated.
 *
 * @param sourceCode Parsed source code section.
 * @param testSourcePath Path to the parsed ".test" file.
 * @throws Error If no source code is present.
 */
function validateSourceCode(sourceCode: string, testSourcePath: string): void {
  if (sourceCode.trim() === "") {
    throw new Error(`SOLtest file "${testSourcePath}" does not contain source code.`);
  }
}

/**
 * @brief File content is split into header lines and source code.
 *
 * The first blank line is treated as the separator between the SOLtest header
 * and the source code. Missing separator or missing source code is rejected.
 *
 * @param fileContents Full content of the SOLtest file.
 * @param testSourcePath Path to the parsed ".test" file.
 * @returns Split header lines and source code.
 * @throws Error If the required separator or source code is missing.
 */
function splitTestFileContent(fileContents: string, testSourcePath: string): SplitTestFileContent {
  const normalizedContents = normalizeNewlines(fileContents);
  const allLines = normalizedContents.split("\n");
  const separatorIndex = findHeaderSeparatorIndex(allLines);

  validateHeaderSeparator(separatorIndex, testSourcePath);

  //split file into header and source
  const headerLines = allLines.slice(0, separatorIndex);
  const sourceLines = allLines.slice(separatorIndex + 1);
  const sourceCode = sourceLines.join("\n");

  validateSourceCode(sourceCode, testSourcePath);

  return {
    header_lines: headerLines,
    source_code: sourceCode,
  };
}

/**
 * @brief One parsed test case is assembled from discovered file data.
 *
 * @param discoveredFile Discovered test case file metadata.
 * @param splitContent Split header and source-code data.
 * @returns Parsed SOLtest test case.
 */
function buildParsedTestCase(
  discoveredFile: TestCaseDefinitionFile,
  splitContent: SplitTestFileContent
): ParsedTestCase {
  const parsedHeader = parseTestHeader(splitContent.header_lines, discoveredFile.test_source_path);

  return {
    name: discoveredFile.name,
    test_source_path: discoveredFile.test_source_path,
    stdin_file: discoveredFile.stdin_file,
    expected_stdout_file: discoveredFile.expected_stdout_file,
    description: parsedHeader.description,
    category: parsedHeader.category as string,
    points: parsedHeader.points as number,
    expected_parser_exit_codes: parsedHeader.expected_parser_exit_codes,
    expected_interpreter_exit_codes: parsedHeader.expected_interpreter_exit_codes,
    source_code: splitContent.source_code,
  };
}

/**
 * @brief One discovered SOLtest file is parsed into an internal representation.
 *
 * The file is read, split into header and source code, and converted into
 * a parsed test case structure.
 *
 * @param discoveredFile Discovered test case file metadata.
 * @returns Parsed SOLtest test case.
 * @throws Error If the SOLtest file is malformed.
 */
export function parseTestCaseFile(discoveredFile: TestCaseDefinitionFile): ParsedTestCase {
  const fileContents = readFileSync(discoveredFile.test_source_path, "utf-8");
  const splitContent = splitTestFileContent(fileContents, discoveredFile.test_source_path);

  return buildParsedTestCase(discoveredFile, splitContent);
}
