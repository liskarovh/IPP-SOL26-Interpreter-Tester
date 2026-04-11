#!/usr/bin/env node
/**
 * @file tester.ts
 * @brief CLI entry point of the SOL26 integration tester is implemented.
 * @author Hana Liškařová xliskah00
 * @author Ondřej Ondryáš <iondryas@fit.vut.cz>
 *
 * DOXYGEN COMMENTS WERE AI GENERATED AND PROOFREAD BY ME
 *
 * Command-line arguments are parsed and validated here. Logging is configured,
 * the main tester workflow is invoked, and the final JSON report is written
 * either to the selected output file or to standard output.
 */

import { existsSync, lstatSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { parseArgs } from "node:util";

import { pino } from "pino";

import { TestReport } from "./models.js";
import { runTester, type ExecutionConfiguration } from "./run_tester.js";

const logger = pino({
  transport: {
    target: "pino-pretty",
    options: {
      colorize: true,
      destination: 2,
    },
  },
});

/**
 * @brief Parsed CLI arguments are described.
 */
interface CliArguments {
  /** Path to the directory with SOLtest files. */
  tests_dir: string;
  /** Indicates whether subdirectories should also be searched. */
  recursive: boolean;
  /** Output file path, or null when standard output is used. */
  output: string | null;
  /** Indicates whether dry-run mode is enabled. */
  dry_run: boolean;
  /** Include filters matching test case name or category. */
  include: string[] | null;
  /** Include filters matching only category. */
  include_category: string[] | null;
  /** Include filters matching only test case name. */
  include_test: string[] | null;
  /** Exclude filters matching test case name or category. */
  exclude: string[] | null;
  /** Exclude filters matching only category. */
  exclude_category: string[] | null;
  /** Exclude filters matching only test case name. */
  exclude_test: string[] | null;
  /** Number of verbose flags provided on the command line. */
  verbose: number;
  /** Indicates whether filters are interpreted as regular expressions. */
  regex_filters: boolean;
}

/**
 * @brief Final report is written to file or standard output.
 *
 * @param resultReport Final tester report.
 * @param outputFile Output file path, or null when standard output is used.
 */
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

/**
 * @brief Double-letter short options are normalized to their long form.
 *
 * This keeps CLI parsing compatible with parseArgs while preserving
 * the intended short-option syntax.
 */
const DOUBLE_LETTER_SHORT_OPTION_NORMALIZATION = new Map<string, string>([
  ["-ic", "--include-category"],
  ["-it", "--include-test"],
  ["-ec", "--exclude-category"],
  ["-et", "--exclude-test"],
]);

/**
 * @brief Help text shown for the tester CLI is stored.
 */
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
  "  -i, --include <value>     Include only test cases with the specified name or category. Can be used multiple times to specify multiple criteria. Can be combined with -ic and -it.",
  "  -ic, --include-category <value>",
  "                            Include only test cases with the specified category. Can be used multiple times to specify multiple accepted categories. Can be combined with -it and -i.",
  "  -it, --include-test <value>",
  "                            Include only test cases with the specified name. Can be used multiple times to specify multiple accepted names. Can be combined with -ic and -i.",
  "  -e, --exclude <value>     Exclude test cases with the specified name or category. Can be used multiple times to specify multiple criteria. Can be combined with -ec and -et.",
  "  -ec, --exclude-category <value>",
  "                            Exclude test cases with the specified category. Can be used multiple times to specify multiple accepted categories. Can be combined with -et and -e.",
  "  -et, --exclude-test <value>",
  "                            Exclude test cases with the specified name. Can be used multiple times to specify multiple accepted names. Can be combined with -ec and -e.",
  "  -g                        When used, the filters specified with -i[ct]/-e[ct] will be interpreted as regular expressions instead of literal strings.",
  "  -v, --verbose             Enable verbose logging output (using once = INFO level, using twice = DEBUG level).",
];

/**
 * @brief parseArgs option configuration is stored.
 */
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

/**
 * @brief Raw CLI arguments are normalized before parsing.
 *
 * Supported double-letter short options are replaced with their
 * corresponding long-form options.
 *
 * @param argv Raw CLI arguments.
 * @returns Normalized CLI arguments.
 */
function normalizeArgv(argv: string[]): string[] {
  const normalizedArguments: string[] = [];

  for (const argument of argv) {
    const normalizedArgument = DOUBLE_LETTER_SHORT_OPTION_NORMALIZATION.get(argument) ?? argument;

    normalizedArguments.push(normalizedArgument);
  }

  return normalizedArguments;
}

/**
 * @brief CLI help text is printed.
 */
function printHelp(): void {
  console.log(HELP_TEXT.join("\n"));
}

/**
 * @brief Optional repeated CLI values are normalized to list or null.
 *
 * Undefined and empty lists are converted to null.
 *
 * @param values Parsed repeated CLI values.
 * @returns List of values, or null when no values are present.
 */
function listOrNull(values: string[] | undefined): string[] | null {
  if (values === undefined || values.length === 0) {
    return null;
  }

  return values;
}

/**
 * @brief CLI filter values are normalized before validation.
 *
 * Null is converted to an empty array, values are trimmed,
 * and empty entries are removed.
 *
 * @param values Raw CLI filter values.
 * @returns Normalized filter values.
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
 * All configured include and exclude filters are normalized and compiled
 * as regular expressions. If one of them is invalid, a CLI validation error
 * is reported and the process terminates with exit code 2.
 *
 * @param args Parsed CLI arguments.
 */
function validateRegexFilters(args: CliArguments): void {
  if (!args.regex_filters) {
    return;
  }

  const filterValues: string[] = [];

  //collect all filter values
  for (const value of normalizeCliFilterValues(args.include)) {
    filterValues.push(value);
  }

  for (const value of normalizeCliFilterValues(args.include_category)) {
    filterValues.push(value);
  }

  for (const value of normalizeCliFilterValues(args.include_test)) {
    filterValues.push(value);
  }

  for (const value of normalizeCliFilterValues(args.exclude)) {
    filterValues.push(value);
  }

  for (const value of normalizeCliFilterValues(args.exclude_category)) {
    filterValues.push(value);
  }

  for (const value of normalizeCliFilterValues(args.exclude_test)) {
    filterValues.push(value);
  }

  for (const filterValue of filterValues) {
    try {
      void new RegExp(filterValue);
    } catch (error: unknown) {
      let errorMessage = "Unknown regular expression error";

      if (error instanceof Error) {
        errorMessage = error.message;
      }

      console.error(`Invalid regular expression filter "${filterValue}": ${errorMessage}`);
      process.exit(2);
    }
  }
}

/**
 * @brief Raw CLI argument parsing is performed.
 *
 * @param argv Raw CLI arguments.
 * @returns Result returned by parseArgs.
 */
function parseCliArgumentsRaw(argv: string[]) {
  return parseArgs({
    args: normalizeArgv(argv),
    options: PARSE_OPTIONS,
    allowPositionals: true,
    strict: true,
  } as const);
}

/**
 * @brief Command-line arguments are parsed and validated.
 *
 * Help handling, positional argument validation, path validation,
 * output validation, and regex-filter validation are all performed here.
 *
 * @returns Parsed and validated CLI arguments.
 */
function parseArguments(): CliArguments {
  /**
   * Parses the command-line arguments and performs basic validation and sanitization.
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
  const positionalArguments = parsed.positionals;

  if (parsedValues.help) {
    printHelp();
    process.exit(0);
  }

  //only one test dir exactly
  if (positionalArguments.length !== 1 || positionalArguments[0] === undefined) {
    console.error("Exactly one positional argument (tests_dir) is required.");
    process.exit(2);
  }

  const testsDir = resolve(positionalArguments[0]);

  const args: CliArguments = {
    tests_dir: testsDir,
    recursive: parsedValues.recursive,
    output: parsedValues.output ?? null,
    dry_run: parsedValues["dry-run"],
    include: listOrNull(parsedValues.include),
    include_category: listOrNull(parsedValues["include-category"]),
    include_test: listOrNull(parsedValues["include-test"]),
    exclude: listOrNull(parsedValues.exclude),
    exclude_category: listOrNull(parsedValues["exclude-category"]),
    exclude_test: listOrNull(parsedValues["exclude-test"]),
    verbose: parsedValues.verbose?.length ?? 0,
    regex_filters: parsedValues["regex-filters"],
  };

  //tests_dir must point to an existing directory
  if (!existsSync(args.tests_dir) || !lstatSync(args.tests_dir).isDirectory()) {
    console.error("The provided path is not a directory.");
    process.exit(1);
  }

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
 * Default logging level is warn. One verbose flag enables info logging.
 * Two or more verbose flags enable debug logging.
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
 * @brief Execution configuration is created in the CLI layer.
 *
 * Environment variables are optional. When they are not set,
 * simple fallback values are used.
 *
 * @returns Execution configuration used by the tester workflow.
 */
function getExecutionConfiguration(): ExecutionConfiguration {
  let compilerCommand = "/opt/runtime-python/bin/python";
  let compilerArgs: string[] = ["/app/tester/tools/sol2xml/sol_to_xml.py"];
  let interpreterCommand = "/usr/local/bin/solint";
  const interpreterArgs: string[] = [];

  const configuredCompilerCommand = process.env["SOL26_COMPILER_PYTHON"];
  const configuredCompilerScript = process.env["SOL26_COMPILER_SCRIPT"];
  const configuredInterpreterCommand = process.env["SOL26_INTERPRETER"];

  if (configuredCompilerCommand !== undefined) {
    compilerCommand = configuredCompilerCommand;
  }

  if (configuredCompilerScript !== undefined) {
    compilerArgs = [configuredCompilerScript];
  }

  if (configuredInterpreterCommand !== undefined) {
    interpreterCommand = configuredInterpreterCommand;
  }

  return {
    compiler_command: compilerCommand,
    compiler_args: compilerArgs,
    interpreter_command: interpreterCommand,
    interpreter_args: interpreterArgs,
  };
}

/**
 * @brief Main CLI workflow is performed.
 *
 * CLI arguments are parsed, logging is configured, the tester workflow
 * is executed, and the final report is written. Fatal errors are reported
 * to standard error and terminate the process with exit code 1.
 *
 * @returns Promise resolving when CLI processing finishes.
 */
async function main(): Promise<void> {
  try {
    const args = parseArguments();

    configureLogging(args);

    const execution = getExecutionConfiguration();

    //any uncaught workflow error is fatal cli failure
    const report = await runTester({
      tests_dir: args.tests_dir,
      recursive: args.recursive,
      dry_run: args.dry_run,
      include: args.include,
      include_category: args.include_category,
      include_test: args.include_test,
      exclude: args.exclude,
      exclude_category: args.exclude_category,
      exclude_test: args.exclude_test,
      regex_filters: args.regex_filters,
      execution,
    });

    writeResult(report, args.output);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(message);
    process.exit(1);
  }
}

await main();
