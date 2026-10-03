# mc-tool

**Prompt injection in a Minecraft agent: do structural defenses beat prompting?**

A small study of how often hidden instructions (in signs, books, chat, item names) hijack an LLM-driven Minecraft bot, and whether architectural defenses hold up better than "please ignore injected instructions" prompts. Everything runs locally on a laptop (RTX 3050) against a private server.

> **Status:** Setup phase (nothing runs yet)
> **Full plan:** see [`PROJECT_PLAN.md`](PROJECT_PLAN.md)

---

## Research question

Do structural defenses (confirmation gates, tool locking, planner/reader split) reduce attack success rate more than prompt-based defenses, and at what cost to normal task performance?

## Stack

| Piece | Choice | Pinned version |
|---|---|---|
| Game server | Minecraft Java server | _TBD_ |
| Bot library | Mineflayer (Node.js) | _TBD_ |
| LLM runtime | Ollama (local models) | _TBD_ |
| Model(s) | ~3B and ~7-8B, quantized | _TBD_ |
| Orchestration / analysis | Python 3.10+ | _TBD_ |
| Hardware | Laptop RTX 3050, VRAM: _TBD_ | n/a |

## Quick start

> Fill this in once the setup works. Planned flow:

```bash
# 1. start the local Minecraft server (online-mode=false)
# 2. install bot dependencies
npm install
# 3. run the bot
node bot.js
```

## Repo layout (planned)

```
mc-tool/
├── README.md          # this file + running log
├── PROJECT_PLAN.md    # full design, experiments, timeline
├── server/            # server config, world seed
├── bot/               # Mineflayer tools + observation layer
├── agent/             # LLM controller + defenses
├── attacks/           # injection payloads
├── tasks/             # benign tasks + success checkers
├── runs/              # raw episode logs (JSONL)
└── analysis/          # stats and plots
```

---

## Milestones

- [ ] **M0:** Hardware check, model runs at usable speed
- [ ] **M1:** Local server running, versions pinned
- [ ] **M2:** Bot joins server and chats
- [ ] **M3:** LLM picks an action and the bot executes it
- [ ] **M4:** Bot reads a sign (first injection channel)
- [ ] **M5:** Benign task T1 completes end-to-end
- [ ] **M6:** Baseline attack success rate measured (defense D0)
- [ ] **M7:** Prompt defenses (D1-D2) evaluated
- [ ] **M8:** Structural defenses (D3-D5) evaluated
- [ ] **M9:** Analysis, plots, writeup/poster

---

## Project log

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

_Nothing yet. Results tables (ASR, utility, cost with confidence intervals) go here once experiments run._

| Model | Defense | Attack | Trials | ASR | Utility | Notes |
|---|---|---|---|---|---|---|
| | | | | | | |

## References

- Greshake et al., 2023, indirect prompt injection in LLM-integrated applications
- AgentDojo (agent prompt-injection benchmark)
- Spotlighting, dual-LLM pattern, CaMeL (defense approaches)
- Mineflayer and Ollama documentation

_Look up and add current links as you read them._

## Ethics

All experiments run on a private local server. Attack code exists to evaluate and harden your own agents, not to target real systems or users.
