# Tests: arbol-trunk

All test work, including top-tier cases, requires a separate task explicitly requested by the owner. Implement and polish code first; only the owner decides when it is ready for tests. Do not write, edit, maintain or run tests during implementation. Keep existing source in its documented state and low-tier examples commented at file ends.

[Mid-tier descriptions and justifications](MID_TIER.md) · [Complete inventory and tier justifications](docs/test-inventory.md) · [Machine-readable inventory](test-tiers.json)

Reviewed revision: `d05362c865f8aea86b162c1f7a275c552f48ed43` under SYL-327 (29 October 2026). No tests were run.

## Selection and limits

3 top-tier inventory entries and 18 mid-tier entries are available after the higher-bar review. 222 low-tier entries were removed under SYL-327. Definitions, scenarios, programs and entry points overlap; this is not a runtime suite count. Top-tier bodies are unchanged. Retained mid-tier sources remain uncommented.

## Active top tier

| Exact selector or program | Why this case earns a place |
| --- | --- |
| [`test_top_events.Events.test_a_full_file_keeps_only_closures_of_written_starts_usage_finished_and_the_end`](trunks/trivial/tests/top/test_top_events.py#L14) | Crosses the event-file cap after recording starts. Requires gapless numbering and closure/usage/end records for admitted work, while rejecting new work and closures of omitted starts. |
| [`test_top_replacement.ReplacingAMessage.test_the_transaction_checks_the_target_again_after_the_preliminary_lookup`](trunks/trivial/tests/top/test_top_replacement.py#L17) | Changes the replacement target between preliminary lookup and transactional acceptance. Requires refusal with no new exchange, message deletion or folder leakage, detecting a time-of-check/time-of-use gap. |
| [`test_top_settle.SavingSettlement.test_two_settlers_both_return_the_stored_state_and_only_one_replays`](trunks/trivial/tests/top/test_top_settle.py#L15) | Schedules two overlapping settlers against the delayed database fixture. Requires identical replies, exactly one stored end, closed connections and one folder cleanup. |

## Layout and shared support

Case bodies are separated into [`trunks/trivial/tests/top/`](trunks/trivial/tests/top/) and [`trunks/trivial/tests/mid/`](trunks/trivial/tests/mid/). The former mixed test modules retain shared fixture classes, helper functions and imports at their established paths, with no inventoried test methods. This preserves existing subprocess paths, patch targets and fixture imports without copying helpers into both tiers. Compatibility entries preserve original package and resource paths while loading the mid-tier implementation. Product-side test APIs load it only when invoked and refuse if the test source is absent.

## Running a selected top-tier case in an owner-requested testing task

Select an exact method when it resolves a concrete uncertainty; no run is required after an edit. The new module names begin with test_top_ so they cannot shadow the shared fixture modules. Do not run whole folders or discovery as a substitute. Original prerequisites, skips and environment limitations still apply. A focused result is not full qualification.

From trunks/trivial, using the prepared repository interpreter:

```sh
PYTHONPATH=src:tests:tests/top python -m unittest test_top_events.Events.test_a_full_file_keeps_only_closures_of_written_starts_usage_finished_and_the_end
```

## Mid-tier execution

[MID_TIER.md](MID_TIER.md) lists the descriptions, tier reasons and review status. The source is now uncommented and stays that way. Writing or running it still requires a separately requested testing task. Do not run tests automatically after edits or merges. Inspect prerequisites and indirect calls before invoking a program or qualification entry point. A focused result is not full qualification.

For a Python method, use the same fixture setup as the top tier, put the mid folder on PYTHONPATH, and select `test_mid_<module>.Class.test_method`. Mycel's fixture-aware runner accepts `--tests tests/mid --select test_mid_<module>.Class.test_method`; store cases require explicit disposable-store settings. Archived scenarios and programs retain their original compatibility entry paths.

Restoration under SYL-326 used static checks only. No tests, Builds, provider calls, Origin migrations or corpus ingest were performed. Original prerequisites and environment limits still apply.

## Qualification after SYL-327

The packaged unit gate no longer stands for the former complete Build qualification: since SYL-329 it runs the top tier only, as Builds below says. Individual top and mid selections remain governed by the policy above; their results cannot stand in for the former complete Build qualification.

## Builds

Since SYL-329 (29 October 2026) a Build runs the top tier only. Its `unit` check runs every case under `trunks/trivial/tests/top/`. The Root Contract suite (`contract-1`) is mid tier, so `trunks/trivial/arbol-build.json` no longer lists it; run `rct-conformance.py --trunk <entry> --root-contract 1` from `arbol-root` when the owner asks. The `live` check, one real message through the installed Claude Driver, is unchanged. The mid tier runs only when the owner asks for a mid-tier run.

## Owner-controlled testing and archived examples — SYL-330

All test work is separate from implementation, including top-tier regressions,
fixtures, snapshots, classification, archival maintenance and runner changes.
Only the owner decides readiness and requests the testing task; do not create
one autonomously or widen implementation into testing. A test-running Build
also belongs to a separately requested testing/Build task; its gate stays intact.
A test review, writing or archival task does not itself authorize execution.

Read the retained cases and the `LOW TIER — DO NOT ENABLE OR RECREATE` footers
before adding related tests. They preserve rejected historical source, reasons
and revisions, so obvious or redundant checks are not generated again. All
archived lines are comments, including imports and registrations. They add no
runnable coverage. Re-admission needs distinct new evidence and owner-requested
test work; a testing request alone does not make low-tier cases useful.
