#!/usr/bin/env node
/**
 * An integration testing script for the SOL26 interpreter.
 *
 * IPP: You can implement the entire tool in this file if you wish, but it is recommended to split
 *      the code into multiple files and modules as you see fit.
 *
 *      Below, you have some code to get you started with the CLI argument parsing and logging setup,
 *      but you are **free to modify it** in whatever way you like.
 *
 * Author: Ondřej Ondryáš <iondryas@fit.vut.cz>
 *
 * AI usage notice: The author used OpenAI Codex to create the implementation of this
 *                  module based on its Python counterpart.
 */

import { existsSync, lstatSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { parseArgs } from "node:util";

import { pino } from "pino";

import { TestReport, UnexecutedReason, UnexecutedReasonCode } from "./models.js";
import {
  loadTestCaseDefinitions,
  type LoadedTestCase,
} from "./discovery/load_test_case_definitions.js";
import { matchesConfiguredFilters } from "./discovery/filter_matcher.js";
import { executeTestCase } from "./execution/test_case_executor.js";
import { resolveTestCase } from "./evaluation/test_resolver.js";
import { buildReport, buildUnexecuted, type ResolvedTestCase } from "./report/report_builder.js";
import { buildDryRunReport } from "./report/build_dry_run_report.js";

const logger = pino({
  transport: {
    target: "pino-pretty",
    options: {
      colorize: true,
      destination: 2,
    },
  },
});

interface CliArguments {
  tests_dir: string;
  recursive: boolean;
  output: string | null;
  dry_run: boolean;
  include: string[] | null;
  include_category: string[] | null;
  include_test: string[] | null;
  exclude: string[] | null;
  exclude_category: string[] | null;
  exclude_test: string[] | null;
  verbose: number;
  regex_filters: boolean;
}

function writeResult(resultReport: TestReport, outputFile: string | null): void {
  /**
   * Writes the final report to the specified output file or standard output if no file is provided.
   */
  const resultJson = JSON.stringify(resultReport, null, 2);
  if (outputFile !== null) {
    writeFileSync(outputFile, resultJson, "utf8");
    return;
  }

  console.log(resultJson);
}

const DOUBLE_LETTER_SHORT_OPTION_NORMALIZATION = new Map<string, string>([
  ["-ic", "--include-category"],
  ["-it", "--include-test"],
  ["-ec", "--exclude-category"],
  ["-et", "--exclude-test"],
]);

const HELP_TEXT = [
  "Usage:",
  "  tester [options] tests_dir",
  "",
  "Positional arguments:",
  "  tests_dir                 Path to a directory with the test cases in the SOLtest format.",
  "",
  "Options:",
  "  -h, --help                Show this help message and exit.",
  "  -r, --recursive           Recursively search for test cases in subdirectories of the provided directory.",
  "  -o, --output <path>       The output file to write the test results to. If not provided, results will be printed to standard output.",
  "  --dry-run                 Perform a dry run: discover the test cases but don't actually execute them.",
  "  -i, --include <value>     Include only test cases with the specified name or category. Can be used multiple times to specify multiple criteria.Can be combined with -ic and -it.",
  "  -ic, --include-category <value>",
  "                            Include only test cases with the specified category. Can be used multiple times to specify multiple accepted categories. Can be combined with -it and -i.",
  "  -it, --include-test <value>",
  "                            Include only test cases with the specified name. Can be used multiple times to specify multiple accepted names. Can be combined with -ic and -i.",
  "  -e, --exclude <value>     Exclude test cases with the specified name or category. Can be used multiple times to specify multiple criteria.Can be combined with -ic and -it.",
  "  -ec, --exclude-category <value>",
  "                            Exclude test cases with the specified category. Can be used multiple times to specify multiple accepted categories. Can be combined with -it and -i.",
  "  -et, --exclude-test <value>",
  "                            Exclude test cases with the specified name. Can be used multiple times to specify multiple accepted names. Can be combined with -ic and -i.",
  "  -g                        When used, the filters specified with -i[ct]/-e[ct] will be interpreted as regular expressions instead of literal strings.",
  "  -v, --verbose             Enable verbose logging output (using once = INFO level, using twice = DEBUG level).",
];

const PARSE_OPTIONS = {
  help: { type: "boolean", short: "h", default: false },
  recursive: { type: "boolean", short: "r", default: false },
  output: { type: "string", short: "o" },
  "dry-run": { type: "boolean", default: false },
  include: { type: "string", short: "i", multiple: true },
  "include-category": { type: "string", multiple: true },
  "include-test": { type: "string", multiple: true },
  exclude: { type: "string", short: "e", multiple: true },
  "exclude-category": { type: "string", multiple: true },
  "exclude-test": { type: "string", multiple: true },
  "regex-filters": { type: "boolean", short: "g", default: false },
  verbose: { type: "boolean", short: "v", multiple: true },
} as const;

function normalizeArgv(argv: string[]): string[] {
  return argv.map((arg) => DOUBLE_LETTER_SHORT_OPTION_NORMALIZATION.get(arg) ?? arg);
}

function printHelp(): void {
  console.log(HELP_TEXT.join("\n"));
}

function listOrNull(values: string[] | undefined): string[] | null {
  if (values === undefined || values.length === 0) {
    return null;
  }

  return values;
}

/**
 * @brief CLI filter values are normalized before validation is performed.
 *
 * Null is converted into an empty array. Individual values are trimmed, and
 * empty values are removed so that validation is performed over the same
 * effective values that are later used by filter matching.
 *
 * @param values Raw CLI filter values.
 * @returns Normalized non-empty filter values.
 */
function normalizeCliFilterValues(values: string[] | null): string[] {
  if (values === null) {
    return [];
  }

  const normalizedValues: string[] = [];

  for (const value of values) {
    const trimmedValue = value.trim();

    if (trimmedValue === "") {
      continue;
    }

    normalizedValues.push(trimmedValue);
  }

  return normalizedValues;
}

/**
 * @brief Regex filter syntax is validated when regex matching is enabled.
 *
 * All configured include and exclude filters are normalized and then compiled
 * as regular expressions. When one of them is invalid, a CLI validation error
 * is reported and the process is terminated with exit code 2.
 *
 * @param args Parsed CLI arguments.
 */
function validateRegexFilters(args: CliArguments): void {
  if (!args.regex_filters) {
    return;
  }

  const filterGroups = [
    ...normalizeCliFilterValues(args.include),
    ...normalizeCliFilterValues(args.include_category),
    ...normalizeCliFilterValues(args.include_test),
    ...normalizeCliFilterValues(args.exclude),
    ...normalizeCliFilterValues(args.exclude_category),
    ...normalizeCliFilterValues(args.exclude_test),
  ];

  for (const filterValue of filterGroups) {
    try {
      void new RegExp(filterValue);
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown regular expression error";

      console.error(`Invalid regular expression filter "${filterValue}": ${errorMessage}`);
      process.exit(2);
    }
  }
}

function parseCliArgumentsRaw(argv: string[]) {
  return parseArgs({
    args: normalizeArgv(argv),
    options: PARSE_OPTIONS,
    allowPositionals: true,
    strict: true,
  } as const);
}

function parseArguments(): CliArguments {
  /**
   * Parses the command-line arguments and performs basic validation a sanitization.
   */
  let parsed: ReturnType<typeof parseCliArgumentsRaw>;

  try {
    parsed = parseCliArgumentsRaw(process.argv.slice(2));
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(message);
    process.exit(2);
  }

  const parsedValues = parsed.values;

  if (parsedValues["help"]) {
    printHelp();
    process.exit(0);
  }

  if (parsed.positionals.length !== 1 || parsed.positionals[0] === undefined) {
    console.error("Exactly one positional argument (tests_dir) is required.");
    process.exit(2);
  }

  const args: CliArguments = {
    tests_dir: resolve(parsed.positionals[0]),
    recursive: parsedValues["recursive"],
    output: parsedValues["output"] ?? null,
    dry_run: parsedValues["dry-run"],
    include: listOrNull(parsedValues["include"]),
    include_category: listOrNull(parsedValues["include-category"]),
    include_test: listOrNull(parsedValues["include-test"]),
    exclude: listOrNull(parsedValues["exclude"]),
    exclude_category: listOrNull(parsedValues["exclude-category"]),
    exclude_test: listOrNull(parsedValues["exclude-test"]),
    verbose: parsedValues["verbose"]?.length ?? 0,
    regex_filters: parsedValues["regex-filters"],
  };

  // Check source directory
  if (!existsSync(args.tests_dir) || !lstatSync(args.tests_dir).isDirectory()) {
    console.error("The provided path is not a directory.");
    process.exit(1);
  }

  // Warn if the output file already exists
  if (args.output !== null) {
    const outputParent = dirname(args.output);
    if (!existsSync(outputParent)) {
      console.error("The parent directory of the output file does not exist.");
      process.exit(1);
    }

    if (existsSync(args.output)) {
      logger.warn("The output file will be overwritten: %s", args.output);
    }
  }

  validateRegexFilters(args);
  return args;
}

/**
 * @brief Logging level is configured from parsed CLI arguments.
 *
 * The default logging level is set to warn. When one verbose flag is provided,
 * info logging is enabled. When two or more verbose flags are provided, debug
 * logging is enabled.
 *
 * @param args Parsed CLI arguments.
 */
function configureLogging(args: CliArguments): void {
  logger.level = "warn";

  if (args.verbose >= 2) {
    logger.level = "debug";
    return;
  }

  if (args.verbose === 1) {
    logger.level = "info";
  }
}

/**
 * @brief Execution failure type is derived from the error message.
 *
 * Errors caused by missing commands, failed process spawning, or missing
 * execution permissions are treated as cannot-execute failures. All other
 * errors are treated as generic execution failures.
 *
 * @param errorMessage Human-readable execution error message.
 * @returns Matching unexecuted reason code.
 */
function getExecutionFailureReasonCode(errorMessage: string): UnexecutedReasonCode {
  const normalizedMessage = errorMessage.toLowerCase();

  if (normalizedMessage.includes("enoent")) {
    return UnexecutedReasonCode.CANNOT_EXECUTE;
  }

  if (normalizedMessage.includes("eacces")) {
    return UnexecutedReasonCode.CANNOT_EXECUTE;
  }

  if (normalizedMessage.includes("spawn")) {
    return UnexecutedReasonCode.CANNOT_EXECUTE;
  }

  return UnexecutedReasonCode.OTHER;
}

/**
 * @brief Full tester execution pipeline is performed.
 *
 * Test cases are loaded first. In dry-run mode, only discovery and filtering
 * results are reported. Otherwise, selected test cases are executed and
 * resolved into the final report.
 *
 * @param args Parsed CLI arguments.
 * @returns Final tester report.
 */
async function runTester(args: CliArguments): Promise<TestReport> {
  const loadedTestCases = loadTestCaseDefinitions(args.tests_dir, args.recursive);

  logger.info(
    {
      loaded_test_case_count: loadedTestCases.loaded_test_cases.length,
      failed_test_case_count: loadedTestCases.failed_test_cases.length,
    },
    "Test case definitions were loaded."
  );

  if (args.dry_run) {
    return buildDryRunReport(loadedTestCases, args);
  }

  const selectedTestCases: LoadedTestCase[] = [];

  for (const loadedTestCase of loadedTestCases.loaded_test_cases) {
    if (!matchesConfiguredFilters(loadedTestCase.definition, args)) {
      continue;
    }

    selectedTestCases.push(loadedTestCase);
  }

  logger.info(
    {
      selected_test_case_count: selectedTestCases.length,
    },
    "Test cases were selected for execution."
  );

  const environment = process.env;

  let compilerCommand = "/opt/runtime-python/bin/python";
  const configuredCompilerCommand = environment["SOL26_COMPILER_PYTHON"];
  if (configuredCompilerCommand !== undefined) {
    compilerCommand = configuredCompilerCommand;
  }

  let compilerScript = "/app/tester/tools/sol2xml/sol_to_xml.py";
  const configuredCompilerScript = environment["SOL26_COMPILER_SCRIPT"];
  if (configuredCompilerScript !== undefined) {
    compilerScript = configuredCompilerScript;
  }

  let interpreterCommand = "/usr/local/bin/solint";
  const configuredInterpreterCommand = environment["SOL26_INTERPRETER"];
  if (configuredInterpreterCommand !== undefined) {
    interpreterCommand = configuredInterpreterCommand;
  }

  const resolvedTestCases: ResolvedTestCase[] = [];
  const executionFailures: Record<string, UnexecutedReason> = {};

  for (const selectedTestCase of selectedTestCases) {
    const testCaseName = selectedTestCase.definition.name;

    logger.info({ test_case_name: testCaseName }, "Test case execution started.");

    try {
      const executionResult = await executeTestCase({
        loaded_test_case: selectedTestCase,
        compiler_command: compilerCommand,
        compiler_args: [compilerScript],
        interpreter_command: interpreterCommand,
        interpreter_args: [],
      });

      const resolvedReport = await resolveTestCase(selectedTestCase.definition, executionResult);

      resolvedTestCases.push({
        definition: selectedTestCase.definition,
        report: resolvedReport,
      });

      logger.info({ test_case_name: testCaseName }, "Test case execution finished.");
    } catch (error: unknown) {
      let errorMessage = "An unknown error occurred.";

      if (error instanceof Error) {
        errorMessage = error.message;
      } else if (typeof error === "string") {
        errorMessage = error;
      }

      const reasonCode = getExecutionFailureReasonCode(errorMessage);

      executionFailures[testCaseName] = new UnexecutedReason(reasonCode, errorMessage);

      logger.warn(
        {
          test_case_name: testCaseName,
          reason_code: reasonCode,
          reason_message: errorMessage,
        },
        "Test case execution failed."
      );
    }
  }

  const unexecuted = buildUnexecuted(loadedTestCases, args);

  for (const [testCaseName, reason] of Object.entries(executionFailures)) {
    unexecuted[testCaseName] = reason;
  }

  return buildReport({
    discovered_test_cases: loadedTestCases.loaded_test_cases.map(
      (loadedTestCase) => loadedTestCase.definition
    ),
    unexecuted,
    resolved_test_cases: resolvedTestCases,
  });
}

/**
 * @brief The tester entry point is executed.
 *
 * CLI arguments are parsed, logging is configured, the tester pipeline is run,
 * and the final report is written. Fatal errors are reported to stderr and
 * terminate the process with exit code 1.
 */
async function main(): Promise<void> {
  try {
    const args = parseArguments();
    configureLogging(args);

    const report = await runTester(args);
    writeResult(report, args.output);
  } catch (error: unknown) {
    let errorMessage = "An unknown error occurred.";

    if (error instanceof Error) {
      errorMessage = error.message;
    } else if (typeof error === "string") {
      errorMessage = error;
    }

    console.error(errorMessage);
    process.exit(1);
  }
}

await main();
