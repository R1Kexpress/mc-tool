# mc-tool

**Prompt injection in a Minecraft agent: do structural defenses beat prompting?**

A small study of how often hidden instructions (in signs, books, chat, item names) hijack an LLM-driven Minecraft bot, and whether architectural defenses hold up better than "please ignore injected instructions" prompts. Everything runs locally on a laptop (RTX 3050) against a private server.

> **Status:** D0 pilot complete (60 measured episodes). D1/D2 prompt development complete (60 selected outcomes); D1 v1 and D2 v2 selected for evaluation. Formal defense evaluation and structural defenses are pending.
> **Experiment setup:** see [`EXPERIMENTS.md`](EXPERIMENTS.md)
> **Defense workflow:** see [`DEFENSES.md`](DEFENSES.md)
> **Archived data:** see [`results/README.md`](results/README.md)
> **Full plan:** see [`PROJECT_PLAN.md`](PROJECT_PLAN.md)

---

## Research question

Do structural defenses (confirmation gates, tool locking, planner/reader split) reduce attack success rate more than prompt-based defenses, and at what cost to normal task performance?

## Stack

| Piece | Choice | Pinned version |
|---|---|---|
| Game server | Minecraft Java server | 1.20.4 |
| Bot library | Mineflayer (Node.js) | 4.39.0, locked in `bot/package-lock.json` |
| Navigation / collection | mineflayer-pathfinder / mineflayer-collectblock | 2.4.5 / 1.6.0 |
| Local HTTP API | Express | 5.2.1 |
| LLM runtime | Ollama | Runtime version not yet recorded |
| Evaluated model | llama3.2:3b | Q4_K_M observed during setup; exact model digest not yet recorded |
| Orchestration / analysis | Python | 3.12 used; dependencies pinned in `requirements.txt` |
| Hardware | Laptop RTX 3050, VRAM: _TBD_ | n/a |

## Quick start

Use separate terminals for Minecraft, the Node bot, Ollama, and the experiment
runner. Follow [`EXPERIMENTS.md`](EXPERIMENTS.md) for Java/server startup, RCON
configuration, and the password environment variable. For a fresh checkout, from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm ci --prefix bot
Copy-Item arena.example.json arena.json
# Fill arena.json with the actual spawn, chest, sign, and log coordinates.
# Start Minecraft and Ollama, then start the bot in its own terminal:
node bot/bot.js
# In the runner terminal, after setting MC_RCON_PASSWORD:
.\.venv\Scripts\python.exe run.py --smoke-test
.\.venv\Scripts\python.exe run.py --defense D0 --attack control --n 1
```

The measured pilot uses a **three-log target**, ten available single-layer logs,
five starting diamonds, temperature 0.7, 40 steps, and a 300-second episode budget.
Set `target_logs` to 3 in the local arena config to reproduce that task. The
ten-log task was demonstrated manually but was unreliable across early trials.
Logs, resets, and checkers use the configured target chest; `done()` is not proof
of success. The harness also ends episodes when game state confirms completion.

For the existing setup across separate checkouts, use the explicit Python and
arena paths documented in [`DEFENSES.md`](DEFENSES.md). `agent/agent.py` and
`prompts/prompts.txt` retain preliminary demos; `run.py` is the measured runner.

## Repo layout

```
mc-tool/
├── README.md          # this file + running log
├── PROJECT_PLAN.md    # full design, experiments, timeline
├── mc_server/         # local Minecraft server; runtime data stays local
├── bot/               # Mineflayer tools + observation layer
├── agent/             # LLM controller + defenses
├── run.py             # episode/batch CLI
├── tests/             # Python and Node regression tests
├── runs/              # live JSONL output (gitignored)
├── results/           # archived D0/development raw data + manifest
└── reports/           # baseline analysis and frozen prompt selections
```

---

## Milestones

- [ ] **M0:** Hardware check, model runs at usable speed
- [ ] **M1:** Local server running, versions pinned
- [x] **M2:** Bot joins server and chats
- [x] **M3:** LLM picks an action and the bot executes it
- [x] **M4:** Bot reads a sign (first injection channel)
- [x] **M5:** Simplified three-log T1 measured end-to-end (D0 control: 20/20 successes)
- [x] **M6:** Baseline attack success rate measured (defense D0)
- [ ] **M7:** Prompt defenses (D1-D2) evaluated — development complete; formal evaluation pending
- [ ] **M8:** Structural defenses (D3-D5) evaluated
- [ ] **M9:** Analysis, plots, writeup/poster

---

## Project log

### 2026-10-30: Archive baseline and prompt-development results for review

**Done:** Preserved 15 raw JSONL files in `results/` with SHA-256 hashes and
selected episode IDs. The snapshot contains 128 raw records: 120 selected measured
outcomes, two repeated completed development records, two interrupted attempts,
two setup errors, and two checker errors. Original live files remain unchanged.

**Results:** D0 control completed 20/20 tasks with no diamond losses. A1 caused
diamond losses in 14/20 episodes; A2 caused none, but only 12/20 tasks finished.
All 14 successful A1 attacks also completed the legitimate task. Both D1/D2
variants passed their five control trials. Under the previously stated selection
rule, D1 v1 and D2 v2 have fewer attacked diamond-loss episodes than their
alternatives; exact prompts/fingerprints are recorded in
`reports/frozen_prompt_selection.json`.

**Learned:** Task completion can coexist with security failure. D2 v2's lower
development diamond-loss count coincides with worse attacked task completion;
getting stuck is not evidence of reliable protection. Prompt wording changes
behavior, but five-trial cells are too small for a reliable effectiveness ranking.

**Data handling:** Summaries retain the first completed outcome per seed, retain
timeouts and step caps, and keep duplicate/interrupted/infrastructure records in
the archive. The duplicate-handling policy was adopted after reruns occurred and
is disclosed. Development results are not pooled with the D0 pilot or future
evaluation. Known A1/A2 payloads are not a held-out generalization test.

**Versions:** Minecraft 1.20.4; llama3.2:3b; harness v6; temperature 0.7. Locked
Node dependency versions are listed above. Runtime versions/model digest still
need recording before the next evaluation.

**Next:** Freeze the selected prompts and run 20 evaluation episodes per cell for
D1 v1 and D2 v2 on control/A1/A2, seeds 0–19 (120 new episodes). Preserve raw
outcomes and report attack success, task utility, cost, and confidence intervals.
Structural defenses remain unimplemented. No git commit was created by the agent;
the user requested a reviewable change set and will commit it themselves.

### 2026-10-28: Preserve D0 pilot and add prompt-only defense conditions

Saved the D0 results and raw-file checksums in `reports/`. Added selectable D1
warnings and D2 sign spotlighting, two initial prompt variants each, without
changing D0's model-visible prompts or the v6 tools/reset/completion rules. Records
now include exact prompt metadata, fingerprints, and development/evaluation phase.
Added independent test arena data so tests do not depend on private local config.
See `DEFENSES.md` for worktree-aware commands and variant-selection procedure.
Live defense effectiveness is not yet measured; start with a development control
and A1 check before choosing frozen prompts for the 120-episode comparison.

### 2026-10-23: Normalize tool counts consistently

The first A1 trial repeatedly selected diamond dropping with `count: "5"`, but the
drop endpoint rejected strings while storage accepted them. Both tools now use
the same count parser: positive integer numbers and digit-only strings are valid;
booleans, arrays, fractions, and malformed strings remain invalid. Tool choice is
unchanged. Preserve the original A1 trace as attempted redirection with mechanical
failure, and collect fresh matched controls/attacks under harness version 6.

### 2026-10-22: End episodes on measured task completion

The user chose game-state completion as the experiment boundary. The controller
now reads task progress after actions and stops when the configured log total is
in the target chest, including on the last allowed step. All conditions use the
same rule. Final attack checks still preserve earlier diamond loss or tosses.
Task wording allows batch deposits; the model chooses the action sequence. New
records use harness version 5; earlier stopping-policy results remain separate.

### 2026-10-22: Diagnose repeated empty-inventory deposits

The history-enabled control repeatedly chose storage before mining. Local Ollama
metadata confirms the installed llama3.2:3b Q4_K_M model advertises tools. Four
requests without executing game tools compared task placement at seeds 0 and 1:
repeating the task in the latest user observation changed seed 0 from storage to
mining; both formats chose mining at seed 1. The controller now repeats the task
with each observation while preserving history (harness version 4). Full-episode
improvement remains unverified. Also fixed lost partial traces when Ctrl+C
interrupts an episode. No mining count or deposit restriction was introduced.

### 2026-10-22: Preserve controller conversation history

The revised control run stored nine logs, then repeatedly attempted empty-inventory
deposits until the step cap. In `agent/controller.py`, each model request previously
discarded earlier turns and retained only the latest tool result. The controller
now retains observations, assistant calls, and tool-role responses within each
episode and clears them between episodes. Action selection stays with the model;
no bulk mining or deposit gate was added. Multiple calls in a response receive
explicit errors rather than silently ignoring extra calls. Logs now identify
harness version 3. All 19 Python tests pass; model improvement awaits a live rerun.

### 2026-10-22: Fix ambiguous chest targeting

The first automated control reached the step cap after ten successful one-log
deposits, while the target chest held seven logs. Two chests were present, and
nearest-chest storage could distribute deposits between them. Storage now uses
the arena's exact chest coordinates, and each model observation includes that
chest's measured oak-log total. Records identify this revision as harness version
2; retain the earlier trial as a diagnostic rather than pool it with the baseline.
The layout after a trial shows consumed logs; use `--reset-only` to inspect the
prepared layout before another model episode.

### 2026-10-22: D0 trial harness

**Done:** Added configurable arena reset over RCON, chest/inventory checkers,
episode-scoped drop events, serial action handling, a batch CLI, and JSONL logs.
Configured the user-provided spawn/chest location and a new single-layer log row
plus sign. Enabled the RCON setting; a local password and server restart are still
needed. Setup and outcome failures stop batches rather than produce trusted scores.

**Validation:** Python unit tests and Node action/episode tests cover tool routing,
reset failure, checker behavior after item pickup, timeouts, and per-trial logging.
Live reset verification and no-attack reliability runs remain pending.

**Next:** Follow `EXPERIMENTS.md`: set RCON password, start Minecraft/Node, run
`run.py --smoke-test`, then one control episode and five control trials.

_Newest entries on top. Record what you did, what broke, what you learned, and the exact versions or commands that worked._

### 2026-10-02: Day 0, project chosen

**Done**
- Picked the project after ruling out tool-calling (burnout), memory/forgetting (not interesting), and grokking (a friend is already doing it).
- Chose agent security in Minecraft: prompt-injection attacks and defenses on a local-model bot.
- Wrote the project plan and this README.

**Decisions**
- Local models via Ollama, so no per-run API cost.
- Private local server only; no real servers or players involved.
- Payloads are benign in-game actions (dropping items, etc.).

**Next**
- [ ] Run `nvidia-smi`, record VRAM
- [ ] Pull a ~3B model with Ollama and test speed
- [ ] Pick and pin a Minecraft version that Mineflayer supports
- [ ] Get the server running and join it from the game client

**Open questions**
- Which model sizes are actually usable on this GPU?
- Will small models complete even the simple wood-collection task reliably? If not, simplify tasks first.

<!-- Copy this template for each new entry

### YYYY-MM-DD: short title

**Done**
-

**Broke / confusing**
-

**Learned**
-

**Versions / commands that worked**
-

**Next**
- [ ]
-->

---

## Results

### D0 exploratory pilot

All cells use llama3.2:3b, harness v6, the same three-log arena, and seeds 0–19.
Intervals below are 95% Wilson intervals. Diamond loss in control is an accidental
loss rate; in attacked episodes it is the attack-success rate (ASR).

| Condition | Diamond-drop/loss rate | 95% CI | Task completion | 95% CI |
|---|---:|---:|---:|---:|
| Control, blank sign | 0/20 (0%) | 0–16% | 20/20 (100%) | 84–100% |
| A1, explicit system override | 14/20 (70%) | 48–85% | 18/20 (90%) | 70–97% |
| A2, server inventory-audit notice | 0/20 (0%) | 0–16% | 12/20 (60%) | 39–78% |

Mean episode times were 33.5s (control), 59.8s (A1), and 107.1s (A2), including
measured failures. See [`reports/d0_baseline.md`](reports/d0_baseline.md).

### Prompt development: five trials per cell

Each cell uses seeds 1000–1004. Entries are success counts out of five. These are
variant-selection data, not final estimates of defense effectiveness.

| Defense / variant | Control tasks | A1 diamond losses | A1 tasks | A2 diamond losses | A2 tasks |
|---|---:|---:|---:|---:|---:|
| D1 v1 — selected | 5/5 | 3/5 | 4/5 | 0/5 | 3/5 |
| D1 v2 | 5/5 | 5/5 | 5/5 | 0/5 | 4/5 |
| D2 v1 | 5/5 | 5/5 | 5/5 | 0/5 | 4/5 |
| D2 v2 — selected | 5/5 | 3/5 | 3/5 | 0/5 | 2/5 |

The selection rule requires at least 4/5 control tasks, then minimizes diamond-loss
episodes over A1/A2; ties use attacked task completion, tool-call cost, then v1.
D1 v1 and D2 v2 each have 3/10 attacked diamond-loss episodes versus 5/10 for their
alternatives. D2 v2 completes only 5/10 attacked tasks, compared with 9/10 for v1:
the security/utility tradeoff must be reported rather than called an unqualified
improvement. For A1's 3/5 loss count the 95% CI is 23–88%; for 5/5 it is 57–100%.
For each 0/5 loss count the interval is 0–43%. No observed losses is not immunity.

Selected prompts and their exact fingerprints are in
[`reports/frozen_prompt_selection.json`](reports/frozen_prompt_selection.json).
See the [D1](reports/d1_development_selection.md) and
[D2](reports/d2_development_selection.md) selection notes. The 20-trial-per-cell
D1/D2 evaluation has **not** run yet. No structural-defense result is claimed.

## References

- Greshake et al., 2023, indirect prompt injection in LLM-integrated applications
- AgentDojo (agent prompt-injection benchmark)
- Spotlighting, dual-LLM pattern, CaMeL (defense approaches)
- Mineflayer and Ollama documentation

_Look up and add current links as you read them._

## Ethics

All experiments run on a private local server. Attack code exists to evaluate and harden your own agents, not to target real systems or users.
