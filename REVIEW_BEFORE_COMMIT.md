# Review before committing

Prepared 30 October 2026. No files have been staged or committed by the agent.
The checkout is currently at a detached HEAD; create a branch before committing.

## Changes to review

- `README.md`: current project status, working startup commands, actual file
  layout, recorded dependency versions, completed milestones, D0 results with
  confidence intervals, all D1/D2 development counts, and a new 30 October log
  entry. Formal defense evaluation is explicitly pending.
- `results/`: 15 exact raw JSONL copies plus a source/hash manifest and scoring
  notes. 128 raw records preserve 120 selected measured outcomes and eight
  duplicate/interrupted/infrastructure records. Original live logs are unchanged.
- `reports/`: baseline/selection analyses, D2 selection notes, and the exact frozen
  D1 v1 and D2 v2 prompt metadata. The chosen variants follow the prior screening
  rule; the reports disclose development-data limitations and utility costs.
- `.gitignore` and `tests/arena.json`: keep only the root arena config private;
  include the deterministic test fixture that the previous ignore rule omitted.
- `DEFENSES.md`: current development status. Other accumulated, previously
  uncommitted files contain the runner, RCON reset/checkers, prompt conditions,
  Node tools, tests, and setup notes from the earlier sessions.

Verification: 31 Python tests and 5 Node tests passed. All 15 archived files match
their recorded SHA-256 hashes. Intended source/docs/results files were checked
for the configured RCON password without exposing its value; no matches found.

## Commit yourself

Run these in a VS Code PowerShell terminal, **not** the active experiment terminal
if a trial is running:

```powershell
cd C:\Users\Rayya\.codex\worktrees\f029\mc-tool

# Review tracked edits. New files are also visible in VS Code Source Control.
git diff -- README.md .gitignore
git status --short

# Once satisfied, create a branch and stage only the intended files.
git switch -c codex/d0-baseline-prompt-defenses
git add .gitignore README.md REVIEW_BEFORE_COMMIT.md DEFENSES.md EXPERIMENTS.md TEAMS_UPDATE_2026-10-23.md agent bot prompts reports results requirements.txt run.py arena.example.json tests

# Review the staged file list and changes before the final command.
git diff --cached --stat
git diff --cached --name-only
git diff --cached -- README.md .gitignore

git commit -m "Add reproducible injection harness and archive D0 and prompt development results"
git status --short
```

The explicit staging command excludes the existing local changes to
`mc_server/server.properties` (which contains the RCON credential) and
`mc_server/ops.json` (local operator identities). Those remain modified after the
commit. It also excludes live `runs/`, `.venv`, the root `arena.json`, server/world
runtime data, and installed dependencies. Existing server libraries already in
repository history are untouched. This does not push anything to a remote.
