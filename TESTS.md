# Tests: arbol-trunk

Only the top-tier cases below are active. They may be selected when useful during implementation; running tests after every change is not required. Writing, restoring or running mid-tier tests requires a separate testing task explicitly requested by the owner. Do not write or restore low-tier tests.

[Mid-tier descriptions and justifications](MID_TIER.md) · [Complete inventory and tier justifications](docs/test-inventory.md) · [Machine-readable inventory](test-tiers.json)

Reviewed revision: `d067d7dd7fe72bd1f47c636df51bee53bd7aeb44` (28 October 2026), plus the preceding local pruning changes. No tests were run for this reset.

## Selection and limits

3 active Python definitions and 0 active standalone programs; 238 commented Python definitions. Also disabled: 0 named Node cases, 0 custom scenario functions and 0 standalone check programs. 2 broad entry points explicitly refuse. 7 low-tier cases remain removed from the prior review. These categories overlap in execution and must not be added into a runtime suite size.

Top-tier cases were individually read for the failure they observe. The remaining mid-tier labels are provisional execution decisions, not a claim that thousands of tests have passed a complete semantic review. Reassess value before restoring any of them. A browser program may contain many assertions; it is inventoried as one indivisible program, not as one asserted behavior.

## Active top tier

| Exact selector or program | Why this case earns a place |
| --- | --- |
| [`test_top_events.Events.test_a_full_file_keeps_only_closures_of_written_starts_usage_finished_and_the_end`](trunks/trivial/tests/top/test_top_events.py#L14) | Crosses the event-file cap after recording starts. Requires gapless numbering and closure/usage/end records for admitted work, while rejecting new work and closures of omitted starts. |
| [`test_top_replacement.ReplacingAMessage.test_the_transaction_checks_the_target_again_after_the_preliminary_lookup`](trunks/trivial/tests/top/test_top_replacement.py#L17) | Changes the replacement target between preliminary lookup and transactional acceptance. Requires refusal with no new exchange, message deletion or folder leakage, detecting a time-of-check/time-of-use gap. |
| [`test_top_settle.SavingSettlement.test_two_settlers_both_return_the_stored_state_and_only_one_replays`](trunks/trivial/tests/top/test_top_settle.py#L15) | Schedules two overlapping settlers against the delayed database fixture. Requires identical replies, exactly one stored end, closed connections and one folder cleanup. |

## Layout and shared support

Case bodies are separated into [`trunks/trivial/tests/top/`](trunks/trivial/tests/top/) and [`trunks/trivial/tests/mid/`](trunks/trivial/tests/mid/). The former mixed test modules retain shared fixture classes, helper functions and imports at their established paths, with no inventoried test methods. This preserves existing subprocess paths, patch targets and fixture imports without copying helpers into both tiers. Original check entry points retain their refusals.

## Running a selected top-tier case

Select an exact method when it resolves a concrete uncertainty; no run is required after an edit. The new module names begin with test_top_ so they cannot shadow the shared fixture modules. Do not run whole folders or discovery as a substitute. Original prerequisites, skips and environment limitations still apply. A focused result is not full qualification.

From trunks/trivial, using the prepared repository interpreter:

```sh
PYTHONPATH=src:tests:tests/top python -m unittest test_top_events.Events.test_a_full_file_keeps_only_closures_of_written_starts_usage_finished_and_the_end
```

## Mid-tier review and restoration

[MID_TIER.md](MID_TIER.md) describes every retained mid-tier entry and its existing reason, identifies provisional classifications and explains restoration. Only a separately requested testing task may restore or run these sources. Keep the source in the mid folder; restore only the selected imports, class headers and bodies, update the inventories, and return the source to comments afterward unless the owner says otherwise. Broad entry points continue to refuse; repairing a qualification workflow requires its own explicit testing task.

Layout revision: `68f80423abcb20775f5594eabcd9b1194ea18ef0`. No tests were run for this reorganization. Previous identifiers and source lines are retained in test-tiers.json. Indexed Origin relocation and ingest remain deferred; moving files supplies no new runtime proof.
