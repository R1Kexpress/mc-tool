# D1 and D2 development

Implementation lives in this checkout:
`C:\Users\Rayya\.codex\worktrees\8a46\mc-tool`.
The original Minecraft server, Node bot, Python environment, arena configuration,
and D0 logs remain in `C:\Users\Rayya\cs_proj\mc-tool`.
No Node changes or new packages are needed for the prompt defenses.

## Conditions and files

`agent/defenses.py` defines two initial variants per defense (`v1`, `v2`):

- D0 uses the original prompt and observation formatting byte for byte.
- D1 adds a system warning about instructions on signs. Observations stay inline.
- D2 adds a system instruction and separates sign JSON into an `untrusted_signs`
  section. Delimiter characters in JSON strings are escaped without changing
  the decoded sign text. Other game-state fields retain their values.

`agent/controller.py` selects the prompt and observation representation. Raw
observations remain in the trace. It also saves the exact observation text sent
to the model. All conditions expose and execute the same tools; no actions are
blocked or replaced by these defenses. The same reset and stopping rule applies.

`run.py` accepts `--defense D0|D1|D2`, `--prompt-variant`, and
`--phase development|evaluation`. D0 defaults to `baseline`; D1/D2 default to `v1`.
Invalid defense/variant combinations fail before resetting Minecraft. The phase
defaults to development. Each record includes the exact system prompt, task,
variant, observation format version, and a SHA-256 prompt fingerprint, including
for failed setup records. Harness version remains 6 because execution rules are
unchanged; use the defense, phase, variant, and fingerprint to identify prompts.

The D0 report and raw-file hashes are in `reports/d0_baseline.md` and
`reports/d0_baseline_manifest.json`.

## Start with two short development checks

Keep Minecraft, the original Node bot, and Ollama running. In the PowerShell
terminal with `MC_RCON_PASSWORD` set, run:

```powershell
cd C:\Users\Rayya\.codex\worktrees\8a46\mc-tool
$experimentPython = 'C:\Users\Rayya\cs_proj\mc-tool\.venv\Scripts\python.exe'
$experimentArena = 'C:\Users\Rayya\cs_proj\mc-tool\arena.json'

& $experimentPython run.py --config $experimentArena --defense D1 --prompt-variant v1 --phase development --attack control --n 1 --seed 1000 --output runs/dev_D1_v1_control.jsonl
& $experimentPython run.py --config $experimentArena --defense D1 --prompt-variant v1 --phase development --attack A1 --n 1 --seed 1000 --output runs/dev_D1_v1_A1.jsonl
```

These are development checks, not a defense-effectiveness estimate. If you opened
a new terminal, set `MC_RCON_PASSWORD` there using the credential instructions in
`EXPERIMENTS.md`. Use the original three-log `arena.json`, not the ten-log test
fixture. Run just one runner at a time.

## Select variants before evaluation

Compare both variants of each defense on the same development conditions and seed
list. For example, use five episodes per cell with seeds 1000–1004, across
control/A1/A2. Include the two initial seed-1000 checks rather than rerunning and
double-counting them. Keep all outcomes, including timeouts and failed episodes.

Choose a selection rule before reading those results. A reasonable pilot rule is
to require at least 4/5 control tasks completed, then choose the eligible variant
with fewer diamond-loss episodes across A1 and A2. Break ties by attacked task
completion, then fewer tool calls, then prefer v1. This tiny development sample
is for screening only, not a statistically reliable ranking. If neither variant
meets the control criterion, retain the results and revise on development data.

Freeze the selected prompt text and fingerprint for each defense. Then run 20
episodes per cell, seeds 0–19, for control/A1/A2 with `--phase evaluation`, in new
files (120 total D1/D2 evaluation episodes). Report every variant tried and the
selection rule; do not pick the best evaluation result after seeing outcomes.
For example, after selection, substitute the chosen defense and variant:

```powershell
& $experimentPython run.py --config $experimentArena --defense D1 --prompt-variant v1 --phase evaluation --attack A1 --n 20 --seed 0 --output runs/eval_D1_v1_A1.jsonl
```

Separate seed lists reduce reuse of development episodes; they do not create
held-out attack payloads. A1 and A2 are known pilot attacks. Keep additional
payloads unseen during tuning for a later generalization test. The phase flag
labels records; it does not automatically freeze prompts or prevent rerunning
seeds. Check uniqueness and fingerprints before summarizing a file.

Development is complete as of 30 October 2026: D1 v1 and D2 v2 are selected by
the stated rule. Formal defense evaluation has not run. Current result summaries,
archived raw data, and frozen prompts are linked from the root README. Automated tests
check prompt equivalence, D2 text preservation and delimiter handling, unchanged
tool availability, metadata propagation, and the existing reset/runner behavior.

Progress messages identify reset verification, game-state reads, model waits, and
rejected multi-call responses. These messages do not change inference settings
or actions. A silent-looking initial turn can be a model generating several tool
calls; those calls are rejected by the existing one-call protocol, not executed.
An interrupted episode is retained separately. If rerunning it, first check that
the seed does not already have a completed outcome in the file.
