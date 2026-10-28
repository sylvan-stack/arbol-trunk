# Tests: arbol-trunk

Only the top-tier cases below are active. They may be selected when useful during implementation; running tests after every change is not required. Writing, restoring or running mid-tier tests requires a separate testing task explicitly requested by the owner. Do not write or restore low-tier tests.

[Complete inventory and tier justifications](docs/test-inventory.md) · [Machine-readable inventory](test-tiers.json)

Reviewed revision: `d067d7dd7fe72bd1f47c636df51bee53bd7aeb44` (28 October 2026), plus the preceding local pruning changes. No tests were run for this reset.

## Selection and limits

3 active Python definitions and 0 active standalone programs; 238 commented Python definitions. Also disabled: 0 named Node cases, 0 custom scenario functions and 0 standalone check programs. 2 broad entry points explicitly refuse. 7 low-tier cases remain removed from the prior review. These categories overlap in execution and must not be added into a runtime suite size.

Top-tier cases were individually read for the failure they observe. The remaining mid-tier labels are provisional execution decisions, not a claim that thousands of tests have passed a complete semantic review. Reassess value before restoring any of them. A browser program may contain many assertions; it is inventoried as one indivisible program, not as one asserted behavior.

## Active top tier

| Exact test selector | Why this case earns a place |
| --- | --- |
| [`test_events.Events.test_a_full_file_keeps_only_closures_of_written_starts_usage_finished_and_the_end`](trunks/trivial/tests/test_events.py#L87) | Crosses the event-file cap after recording starts. Requires gapless numbering and closure/usage/end records for admitted work, while rejecting new work and closures of omitted starts. |
| [`test_replacement.ReplacingAMessage.test_the_transaction_checks_the_target_again_after_the_preliminary_lookup`](trunks/trivial/tests/test_replacement.py#L82) | Changes the replacement target between preliminary lookup and transactional acceptance. Requires refusal with no new exchange, message deletion or folder leakage, detecting a time-of-check/time-of-use gap. |
| [`test_settle.SavingSettlement.test_two_settlers_both_return_the_stored_state_and_only_one_replays`](trunks/trivial/tests/test_settle.py#L258) | Schedules two overlapping settlers against the delayed database fixture. Requires identical replies, exactly one stored end, closed connections and one folder cleanup. |

## Running a selected top-tier case

Select the exact method, never a whole module as a substitute. Retain the original fixture prerequisites. A missing dependency, skipped case or unavailable database is not a pass. No live-provider check was promoted.

Use the repository interpreter and source/test import paths; for example, from `trunks/trivial/`:

```sh
PYTHONPATH=src:tests python -m unittest test_events.Events.test_a_full_file_keeps_only_closures_of_written_starts_usage_finished_and_the_end
```

## Restoring a mid-tier selection in an explicit testing task

1. Read the case and its helpers, reassess its information value, and identify the exact requested scope. Delete low-value cases instead of restoring them.
2. Uncomment only the selected `TEST-TIER-DISABLED-BEGIN` / `END` block by removing one leading `# ` (Python) or `// ` (JavaScript) from each original source line. Remove the marker lines. A bare `#` or `//` line inside a block represents an empty original line. Restore needed names from the complete `TEST-TIER-IMPORTS` statements at the file tail into their original scope and normal import section, rather than uncommenting them at the tail. Do not discard other local changes.
3. For standalone programs or custom scenario functions, remove only their adjacent `TEST-TIER-REFUSAL` stub or terminal refusal after restoring the actual implementation. Restore required shared helpers. The empty-suite `pass` is harmless and can be removed once a class has a real body.
4. Update both inventories to reflect the selection. Run only the requested scope, record actual results, then return mid-tier code to comments when the task finishes unless the owner asked to retain it active. Promotion to top tier needs a concrete, individually reviewed reason.

Broad build/qualification checks refuse while their implementation is commented. Preserve that refusal until the requested qualification has its necessary tests restored. A top-only run does not satisfy an old full-suite gate. Metadata verification, production validation, fixture helpers, Storybook examples and historical result records are not test passes and remain separate.
