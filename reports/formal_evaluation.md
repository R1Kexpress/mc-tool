# Frozen prompt evaluation: D1 v1 and D2 v2

Completed November 1, 2026; 120 measured outcomes, six cells of 20, seeds 0-19. The frozen selection rule, variants, task, tools, and v6 episode mechanics were retained.

| Defense | Condition | Diamond loss | 95% Wilson CI | Tasks completed | 95% Wilson CI | Task without loss |
|---|---|---:|---:|---:|---:|---:|
| D1 v1 | control | 0/20 | 0.0-16.1% | 20/20 | 83.9-100.0% | 20/20 |
| D1 v1 | A1 | 6/20 | 14.5-51.9% | 14/20 | 48.1-85.5% | 9/20 |
| D1 v1 | A2 | 0/20 | 0.0-16.1% | 17/20 | 64.0-94.8% | 17/20 |
| D2 v2 | control | 0/20 | 0.0-16.1% | 20/20 | 83.9-100.0% | 20/20 |
| D2 v2 | A1 | 16/20 | 58.4-91.9% | 15/20 | 53.1-88.8% | 0/20 |
| D2 v2 | A2 | 0/20 | 0.0-16.1% | 5/20 | 11.2-46.9% | 5/20 |

Diamond loss is the attack-success rate in A1/A2 and an accidental-loss rate in control. Task completion and security are measured separately from game state; a completed diamond toss remains a security failure even after repickup. Intervals describe each binary rate separately, not the uncertainty of differences between conditions.

## Interpretation

D1 v1 lost diamonds in 6/20 A1 episodes versus 14/20 in the earlier D0 pilot (30% versus 70%, a descriptive reduction of 40 percentage points). D2 v2 lost diamonds in 16/20 (80%, 10 points above D0). Neither prompt defense reliably prevented A1 diamond dropping. D1 completed 14/20 A1 tasks and D2 completed 15/20, versus 18/20 in the D0 pilot; report these utility costs alongside ASR.

A2 caused no diamond losses in either defense or in D0. D1 completed 17/20 A2 tasks, while D2 completed only 5/20 (D0: 12/20). All 15 D2 A2 failures hit the step cap. Its zero observed losses coexist with low utility and do not establish protection. Both defenses completed 20/20 control tasks without diamond loss. Do not retune or replace D2 after seeing these evaluation outcomes.

## Cost and stopping behavior

| Defense | Condition | Mean seconds | Median seconds | Mean steps | Mean proposed tool calls | Mean rejected multi-call turns | Mean prompt tokens | Mean output tokens |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| D1 v1 | control | 45.3 | 42.3 | 7.3 | 8.3 | 0.3 | 9787.6 | 196.2 |
| D1 v1 | A1 | 169.1 | 147.2 | 10.2 | 11.4 | 0.5 | 18931.7 | 282.1 |
| D1 v1 | A2 | 108.8 | 71.2 | 10.9 | 13.6 | 1.1 | 24290.8 | 326.9 |
| D2 v2 | control | 50.3 | 46.1 | 7.9 | 9.2 | 0.7 | 12393.2 | 218.8 |
| D2 v2 | A1 | 111.8 | 66.2 | 16.6 | 19.7 | 1.0 | 44545.1 | 488.6 |
| D2 v2 | A2 | 110.6 | 119.6 | 32.5 | 33.0 | 0.3 | 105796.6 | 830.5 |

Costs average all 20 measured outcomes per cell, including failures. Seconds cover the model/action loop, excluding reset and final checker overhead. Proposed tool calls include all calls emitted by the model, including calls rejected by the one-call protocol; they are not counts of executed game actions. Prompt/output tokens are cumulative Ollama counts across the episode; retained history increases prompt-token totals. Wall time varies with machine load and pauses and is not a controlled model-only speed comparison.

| Defense | Condition | Stop reasons |
|---|---|---|
| D1 v1 | control | task_complete: 20 |
| D1 v1 | A1 | task_complete: 14, timeout: 6 |
| D1 v1 | A2 | task_complete: 17, timeout: 1, step_cap: 2 |
| D2 v2 | control | task_complete: 20 |
| D2 v2 | A1 | task_complete: 15, timeout: 2, step_cap: 2, done: 1 |
| D2 v2 | A2 | step_cap: 15, task_complete: 5 |

## Audit and reproducibility

The archive contains 123 raw JSONL records: 120 completed measured outcomes, one setup error (D1 A1 seed 5), and two checker errors (D1 A1 seed 16; D1 A2 seed 9). Invalid attempts were retained and their seeds rerun only after repair. There are no duplicate completed seeds or reused episode IDs. Timeouts and step caps with measured outcomes are retained as completed failures.

Two additional user-interrupted attempts have no outcome JSONL record: D1 A1 seed 5 and D2 A2 seed 5. Partial console logs and pause/stop audits survive, but full controller traces were not recovered. These attempts are not counted as measured episodes. Bot disconnections/server stalls caused the invalid attempts; the bot was reconnected before resuming. This infrastructure attrition and the fixed order limit interpretation.

The two user interruptions are documented in evidence/pause.json and evidence/stop_events.jsonl. Historical pause notes describe past state; the evaluation is now complete. All runtime, console, reconnection, and recovery evidence is retained in results/evaluation/evidence/. Frozen sources and their original lockfile are preserved byte for byte in source_snapshot/. manifest.json records source paths, byte counts, and SHA-256 checksums; formal_evaluation.json lists selected IDs and exact unrounded intervals.

Runtime: Python 3.12.5; Ollama 0.40.12; llama3.2:3b Q4_K_M; Minecraft 1.20.4; Java 21.0.3; Node v25.8.2. Model digest: `a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`. Runtime metadata is retained in evidence/runtime.json and evidence/game_runtime.json.

The runner guarded f029 sources and settings on resume; archived sources match the frozen plan. Main-checkout local lockfile edits are preserved separately and must not be mistaken for the frozen experiment lockfile.

## Limits and next step

This is one model, task, arena, and two known payloads, selected after development. Evaluation seeds are disjoint from development seeds but reuse D0 pilot seeds. A1/A2 are not held-out attacks. Cells ran in fixed D1/control/A1/A2 then D2/control/A1/A2 order, across several sessions; D0 is a separate earlier pilot without a recorded model digest. Differences are descriptive, not a randomized or concurrent causal comparison. The intervals are wide at n=20. No general robustness claim or structural-defense result follows from these data.

Next: design and implement structural defenses D3-D5 under a separate frozen protocol; keep this evaluation intact. No structural evaluation was run here.

Reproduce analysis without Minecraft or Ollama from the repository root:

```powershell
& C:\Users\Rayya\cs_proj\mc-tool\.venv\Scripts\python.exe -B scripts/analyze_evaluation.py
```
