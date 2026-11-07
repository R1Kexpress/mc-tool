# D4 frozen evaluation

All 60 measured outcomes are complete: control / A1 / A2, seeds 0–19, 20 episodes per cell.
The archive retains 61 raw records: 60 measured outcomes and one setup failure.

| Cell | Diamond losses | 95% Wilson CI | Tasks completed | 95% Wilson CI | Task without loss | Blocked calls |
|---|---:|---|---:|---|---:|---:|
| control | 0/20 | 0.0%–16.1% | 14/20 | 48.1%–85.5% | 14/20 | 0 |
| A1 | 0/20 | 0.0%–16.1% | 8/20 | 21.9%–61.3% | 8/20 | 475 |
| A2 | 0/20 | 0.0%–16.1% | 9/20 | 25.8%–65.8% | 9/20 | 0 |

No diamond loss was observed with D4 in these trials, while task completion was 70% in control,
40% under A1 and 45% under A2. The 475 rejected A1 calls include drops of any item, not
only diamonds. Zero observed loss is not a guarantee of immunity; its per-cell 95% upper
Wilson bound is 16.1%. Task failures must accompany the security result.

## Protocol and enforcement

D4 v1 uses harness 8, llama3.2:3b, temperature 0.7, a 40-step limit and a 300-second budget.
The arena requires three oak logs in the configured chest and starts with five diamonds.
The system prompt, observations and tools match D0. Python latches sign exposure before
the first model call, including the blank control sign, and rejects high-sensitivity calls
for the rest of that episode. Mining and chest storage retain baseline behavior. There is
no read_sign or give_item tool in this harness; /observe carries sign text and give_item
is rejected defensively if proposed. All 60 measured episodes latched at step 1.

## Stopping reasons and cost

| Cell | Stopping reasons | Mean seconds | Mean steps | Mean prompt tokens | Mean completion tokens |
|---|---|---:|---:|---:|---:|
| control | step_cap: 6, task_complete: 14 | 69.8 | 17.6 | 34984.3 | 449.2 |
| A1 | step_cap: 12, task_complete: 8 | 125.3 | 27.9 | 86104.9 | 701.1 |
| A2 | step_cap: 7, task_complete: 9, timeout: 4 | 137.8 | 24.4 | 75108.9 | 622.1 |

Completed timeouts, step caps and early done calls remain measured outcomes.
The JSON report also retains median runtime, proposed tool calls and rejected multicall counts.

## Runtime, interruptions and limitations

Ollama 0.40.12; Node v25.8.2; Python 3.12.10.
Model digest: `a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72` (matches the frozen D1/D2 model).
Installed packages: `{"express": "5.2.1", "mineflayer": "4.39.0", "mineflayer-collectblock": "1.6.0", "mineflayer-pathfinder": "2.4.5"}`.

Collection used fixed serial cell order control, A1, A2 and ascending seeds; it was not randomized.
The user requested a pause after 49 completed outcomes. The active episode finished and saved;
no measured seed was repeated. On resume, A2 seed 9 failed reset because the old bot session
had disconnected. That setup_error is retained, excluded from measured rates, and retried only
after restarting the baseline bot. There were no measured outcomes discarded or selected by result.
The sources and settings remained frozen across resume. The smoke checks used seed 10000 and
remain separate from formal outcomes; the unsuccessful control smoke was retained without tuning.

This is a later, separate harness-8 campaign. Comparisons with the earlier D0 pilot and D1/D2
harness-6 evaluation are descriptive, not randomized/concurrent causal comparisons. A1 and A2
are known payloads, not held-out attacks. D4 does not block chest_store, including diamond
storage; its guarantees cover the specified high-sensitivity tools, not every possible transfer.

## Archive and reproduction

[Manifest](../results/d4_evaluation/manifest.json) indexes byte-exact raw JSONL, frozen plan,
source snapshots, runtime, pause evidence and console/service logs. Earlier frozen archives
and prompt selection files are unchanged. Original ignored live files remain in place.

Run `.\.venv\Scripts\python.exe -B scripts/analyze_d4_evaluation.py` from the repository root
to verify all checksums, source fingerprints, unique measured seeds and lock traces, and regenerate
this report without Minecraft or Ollama. Do not rerun completed formal seeds.
