# Tests: arbol-trunk

All test work, including top-tier cases, requires a separate task explicitly requested by the owner. Implement and polish code first; only the owner decides when it is ready for tests. Do not write, edit, maintain or run tests during implementation. Keep existing source in its documented state and low-tier examples commented at file ends.

[Mid-tier descriptions and justifications](MID_TIER.md) · [Complete inventory and tier justifications](docs/test-inventory.md) · [Machine-readable inventory](test-tiers.json)

Reviewed revision: `d05362c865f8aea86b162c1f7a275c552f48ed43` under SYL-327 (29 October 2026). No tests were run.

## Selection and limits

The SYL-327 review retained 3 Trivial top-tier entries and 19 mid-tier entries. It removed 222 low-tier entries. AFL-13 adds two Steady top-tier cases. Definitions, scenarios, programs and entry points overlap, so these inventory totals are distinct from runtime suite counts. Retained mid-tier sources remain uncommented.

## Active top tier

| Exact selector or program | Why this case earns a place |
| --- | --- |
| [`test_top_events.Events.test_a_full_file_keeps_only_closures_of_written_starts_usage_finished_and_the_end`](trunks/trivial/tests/top/test_top_events.py#L14) | Crosses the event-file cap after recording starts. Requires gapless numbering and closure/usage/end records for admitted work, while rejecting new work and closures of omitted starts. |
| [`test_top_replacement.ReplacingAMessage.test_the_transaction_checks_the_target_again_after_the_preliminary_lookup`](trunks/trivial/tests/top/test_top_replacement.py#L17) | Changes the replacement target between preliminary lookup and transactional acceptance. Requires refusal with no new exchange, message deletion or folder leakage, detecting a time-of-check/time-of-use gap. |
| [`test_top_settle.SavingSettlement.test_two_settlers_both_return_the_stored_state_and_only_one_replays`](trunks/trivial/tests/top/test_top_settle.py#L15) | Schedules two overlapping settlers against the delayed database fixture. Requires identical replies, exactly one stored end, closed connections and one folder cleanup. |
| [`test_top_qualification.WriterAdmission.test_steady_refuses_exclusive_writer_lock_and_old_layout_marker`](trunks/steady/tests/top/test_top_qualification.py#L18) | Exercises Steady's independent writer reader against a real exclusive lock and then an incompatible marker with the lock free. This catches a fence bypass that the Backend reader's tests cannot detect. |
| [`test_top_qualification.PhaseReplay.test_phase_replay_preserves_exact_complete_records_before_a_torn_append`](trunks/steady/tests/top/test_top_qualification.py#L58) | Reads an actual torn journal. It preserves exact escaped text and a wide integer in complete records and rejects the uncommitted tail, a crash boundary untouched by ordinary completion. |

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

Steady's numbered Build runs `package.integrity` and `unit`. The unit gate runs the packaged top-tier cases with the packaged interpreter and refuses an empty selection. The shared installation lifecycle and real Claude message are recorded separately against the same numbered Build for STE-0.13.

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

## Real existing profiles for live qualification · 12 November 2026

Live gates use a real existing provider profile and Subscription ID directly. The default Claude selection is the existing `anthropic` record. Trivial reads it from `~/.arbol/drivers/claude` by default. `ARBOL_BUILD_LIVE_SUBSCRIPTION` selects an existing real ID, and `ARBOL_BUILD_TEST_STATE_DIR` can point to an existing real Driver state directory, including before the layout move. Missing, signed-out, non-vendor-login and test-* selections refuse before inference. Trivial stages just the selected account record in its disposable home. The native Claude tool uses the existing OS account sign-in.

The real profile retains its native credential binding and normal vendor behavior. Application databases, runtime and Build registry remain disposable. Full Build gates, real inference and actual completion and usage observations remain required. Earlier test-profile records keep their historical scope.

ASD-14 adds one mid-tier identity journey: `PYTHONPATH=src:tests:tests/mid uv run --no-sync python -m unittest test_mid_chat_identity.ChatIdentity.test_accepted_chat_survives_continuation_replacement_and_driver_selection` from `trunks/trivial`. It uses disposable installation/database fixtures and recording Driver stand-ins, with no provider profile provisioning or inference. Its accepted UUID is compared at the actual launch boundary.
