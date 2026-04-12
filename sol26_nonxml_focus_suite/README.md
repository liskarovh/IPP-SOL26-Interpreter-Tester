# Focused non-XML SOL26 suite

This package contains only non-XML tests, split into two groups:

- `corrected_tests/` — tests that were inconsistent with the SOL26 specification and were corrected.
- `valid_but_currently_failing/` — tests that appear valid against the SOL26 specification and were left unchanged; they failed in the supplied report and therefore are good candidates for interpreter fixes.

XML tests were intentionally omitted.

## Corrected tests
- `VALID_SELFSUP_001`–`012`: fixed method selectors so their arity matches the method block.
- `VALID_SELFSUP_014`, `016`, `018`, `020`, `022`: fixed expected output according to the `self` / `super` example from the specification.
- `VALID_SELFSUP_023`–`034`: removed duplicate `Main` definition by introducing `Child : Parent` and `Main : Child`.
- `VALID_SCOPE_027`, `028`: fixed expected closure output so captured `x` reflects the later `x := 9`.
- `VALID_COMPLEX_003`: fixed expected output according to the `self` / `super` specification example.
- `RT51_042_inheritance_miss_2`: corrected expected exit code from 51 to 54.
- `RT54_001_collision`: corrected expected outcome to a valid attribute write (`0`) because there is no colliding zero-argument method.
- `RT54_DEEP_007_collision_after_from_copy_then_method_call`: corrected expected outcome to valid (`0`) because the copied receiver is still `Object`, not `Main`.

## Valid but currently failing tests
These were copied unchanged from the original suite because they appear specification-valid:
- `RT51_009_object_keyword`
- `RT51_012_user_object_keyword`
- `RT51_BASIC_002_unknown_keyword_on_object`
- `RT54_008_collision`
- `RT54_009_collision`
- `RT54_013_collision`
- `VAL_ATTR_030_child_reads_parent_created_attr_via_super`
- `VAL_CTOR_010_subint_new_attr`
- `VAL_CTOR_012_substring_new_attr`
