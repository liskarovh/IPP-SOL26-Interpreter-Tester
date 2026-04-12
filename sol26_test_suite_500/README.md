# SOL26 interpreter test suite draft
This archive contains a generated draft test suite for a SOL26 interpreter.
The suite was generated strictly around the constructs described in the SOL26 specification and the SOLtest format from the project assignment.

## Counts
- Total test cases: **500**
- CLI shell cases: **12**
- XML + static semantic cases: **88**
- Runtime error cases: **72**
- Valid program cases: **328**

## Important note
This is a **generated draft suite**. It was not executed against your concrete `SOL2XML` compiler and your concrete interpreter in this environment, so you should run at least a smoke subset first and then the full suite in your Docker/container setup.
The `00_cli_cases` directory contains shell-based CLI checks because invalid interpreter CLI invocation cannot be expressed naturally through SOLtest.

## Directory map
- `00_cli_cases`
- `10_xml_wellformed`
- `11_xml_structure`
- `20_static_semantics`
- `30_runtime_errors`
- `40_valid_programs`

## Usage hint
The SOLtest cases are organized by folders and categories so they can be filtered by your tester with `-ic`, `-ec`, `-it`, `-et`, and recursive discovery.

Parser-fail fixes applied in this bundle:
- repaired malformed SOL tests caused by helper methods outside class bodies
- added missing parentheses around nested `from: X new` sends
- removed stale internal report file from the bundle
