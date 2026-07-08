# AETHERIX — Comprehensive Usage Guide & Design Rationale

> **What this document is:** a single reference that tells you (1) exactly how
> to run every part of AETHERIX and (2) *why every major design choice was
> made* — the reasoning, selection criteria, and trade-offs an examiner or new
> contributor needs. If you read one document end-to-end, read this one.

---

## Table of Contents

1. [Quick Start — 30 seconds to running](#1-quick-start--30-seconds-to-running)
2. [Which Interface Should I Use? (decision matrix)](#2-which-interface-should-i-use-decision-matrix)
3. [Basic Usage — the 5 essential commands](#3-basic-usage--the-5-essential-commands)
4. [Detailed Usage](#4-detailed-usage)
   - [4.1 End-to-end simulation driver (`run_simulation.py`)](#41-end-to-end-simulation-driver-run_simulationpy)
   - [4.2 Individual Python module demos](#42-individual-python-module-demos)
   - [4.3 Shell utility scripts](#43-shell-utility-scripts)
   - [4.4 The test suite](#44-the-test-suite)
   - [4.5 Full-stack web dashboard (PM2)](#45-full-stack-web-dashboard-pm2)
   - [4.6 Docker Compose deployment](#46-docker-compose-deployment)
   - [4.7 Static showcase site (GitHub Pages)](#47-static-showcase-site-github-pages)
   - [4.8 Presentation deck generation](#48-presentation-deck-generation)
5. [Configuration Reference (` .env`)](#5-configuration-reference-env)
6. [Architecture & Design Decisions (full rationale)](#6-architecture--design-decisions-full-rationale)
   - [6.1 Why a zero-dependency core](#61-why-a-zero-dependency-core)
   - [6.2 Network topology — why 5 tiers, 241 nodes](#62-network-topology--why-5-tiers-241-nodes)
   - [6.3 Hybrid optical/RF — why 1550 nm + Ka-band](#63-hybrid-opticalrf--why-1550-nm--ka-band)
   - [6.4 Why RL routing over Contact Graph Routing](#64-why-rl-routing-over-contact-graph-routing)
   - [6.5 Why Q-tables before Deep Q-Networks](#65-why-q-tables-before-deep-q-networks)
   - [6.6 The reward function — weight-by-weight justification](#66-the-reward-function--weight-by-weight-justification)
   - [6.7 ε-greedy — why decay = 0.995](#67-ε-greedy--why-decay--0995)
   - [6.8 Why Lagrange relays at ES-L4 / ES-L5](#68-why-lagrange-relays-at-es-l4--es-l5)
   - [6.9 Convergence layers — why LTP / TCPCL / UDP-CL](#69-convergence-layers--why-ltp--tcpcl--udp-cl)
   - [6.10 Security — why QKD + post-quantum cryptography](#610-security--why-qkd--post-quantum-cryptography)
   - [6.11 Radiation hardening — the mitigation stack](#611-radiation-hardening--the-mitigation-stack)
   - [6.12 Data prioritization — the 4-tier QoS rationale](#612-data-prioritization--the-4-tier-qos-rationale)
   - [6.13 Failure & recovery scenario (full walkthrough)](#613-failure--recovery-scenario-full-walkthrough)
   - [6.14 Standards compliance rationale](#614-standards-compliance-rationale)
7. [Reproducibility — seeds, configs, citing results](#7-reproducibility--seeds-configs-citing-results)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Quick Start — 30 seconds to running

```bash
git clone https://github.com/matx104/AETHERIX.git
cd AETHERIX
python run_simulation.py        # runs all 6 modules, zero pip installs
```

That's it. The simulation core (`src/`) and the driver (`run_simulation.py`)
depend **only on the Python standard library**. Python 3.9+ is the sole
prerequisite. You will see output for six modules ending with
`All modules complete.`

To run just one module (e.g. the failure & recovery scenario):

```bash
python run_simulation.py --module 4
```

---

## 2. Which Interface Should I Use? (decision matrix)

AETHERIX exposes five interfaces. Pick by goal:

| Your goal | Use this | Install needed |
|-----------|----------|----------------|
| Evaluate the simulation logic / reproduce results | **CLI** — `python run_simulation.py` | Python only |
| Browse interactive browser demos without a backend | **Showcase site** — `docs/` static SPA | Python only (`http.server`) |
| Click-driven dashboard with live API calculations | **Web app** — PM2 full-stack | Python + Node.js |
| Isolated / production-like environment | **Docker Compose** | Docker |
| Review or regenerate the slide deck | **Presentation** generators | Python + `python-pptx`/`reportlab` |

**Selection criteria:**
- **Lowest friction / examiner clone-and-run** → CLI (`run_simulation.py`).
- **Visual exploration** → Showcase site (no backend, instant).
- **Full feature set (simulations with persistence, command reference)** → Web app.
- **Reproducible isolated environment** → Docker.

---

## 3. Basic Usage — the 5 essential commands

| # | Command | What it does | When to use |
|---|---------|--------------|-------------|
| 1 | `python run_simulation.py` | Runs all 6 end-to-end modules | The default — first thing to run |
| 2 | `python run_simulation.py -m 4` | Runs only the failure & recovery module | Demoing the conjunction scenario |
| 3 | `python -m pytest tests/ -q` | Runs the 202-test suite | Verifying correctness after changes |
| 4 | `./scripts/init.sh` | Creates venv + installs dev tools | Before linting / first setup |
| 5 | `./scripts/dev.sh docker-up` | Launches full-stack web app | Want the dashboard |

**Read this if nothing else:**

```bash
# The whole architecture in one command — no installs required:
python run_simulation.py

# Need to prove correctness?
python -m pytest tests/ -q          # 480 passed

# Want a specific slice? Modules are numbered 1-6:
python run_simulation.py --module 4
python run_simulation.py --module 5
```

---

## 4. Detailed Usage

### 4.1 End-to-end simulation driver (`run_simulation.py`)

This is the primary entry point. It lives at the repository root and is
self-contained.

**Full flag reference:**

| Flag | Short | Default | Purpose |
|------|-------|---------|---------|
| `--module N` | `-m N` | *(all)* | Run a single module (1–6) |
| `--seed N` | | `42` | RNG seed for reproducibility |
| `--quiet` | `-q` | off | Suppress formatted output (for scripting) |
| `--help` | `-h` | | Show help + module list |

**The six modules and what each demonstrates:**

| Module | Name | What you see | Key source |
|:------:|------|--------------|------------|
| 1 | Baseline DTN simulation | Bundle generation, store-and-forward delivery ratio over the 241-node topology | `src/simulation/simulator.py` |
| 2 | Optical vs RF link budget | 1550 nm optical and Ka-band RF margins at opposition / average / conjunction distances | `src/infrastructure/link_budget.py`, `rf_link_budget.py` |
| 3 | RL routing convergence | ε-greedy training: epsilon 1.0 → 0.018 over 800 episodes, forward-decision ratio | `src/routing/rl_agent.py`, `training.py` |
| 4 | **Failure & recovery** | Solar-conjunction optical blackout → RL agent reroutes P0 bundles via Ka-band RF through ES-L4 | `rl_agent.py`, `policy_engine.py` |
| 5 | QKD security | BB84 key exchange: clean channel (QBER ~0%) vs eavesdropped (QBER ~25% > 11% threshold) | `src/security/qkd.py` |
| 6 | Radiation hardening | Raw SEU count vs TMR+ECC+scrubbing residual, TMR reliability gain, RAD750 TID margin, FDIR watchdog | `src/computing/radiation.py` |

**How to read Module 4 output (the centerpiece):**

```
Path evaluation (conjunction degraded):
 x  Direct Mars -> Earth (1550 nm optical)   conjunction reward = -1.438  [CLOSED]
 ok Mars -> ES-L4 relay -> Earth (Ka-band)   conjunction reward = -0.201  [OPEN]

RL agent decision (P0 bundle)   forward -> transit.esl4.relay
Policy engine (P0 EMERGENCY)    forward via best_link   [emergency_fast_path]
Policy engine (P4 BULK)         store                   [deep_space_store]
```

- `CLOSED` = link quality (0.05) is below the agent's 0.3 forward threshold.
- `OPEN` = the Ka-band relay path (quality 0.65) clears the threshold.
- The **reward** is computed from the real weights
  `R = +1.0·delivery − 0.001·delay − 0.1·hops`. The optical path has no
  delivery (quality too low) so its reward collapses.
- The policy engine simultaneously forces P0 forward and defers P4 bulk —
  mission-critical data is never blocked by non-urgent traffic.

> **Why this matters:** this is the exact resilience scenario the architecture
> must guarantee — see [§6.13](#613-failure--recovery-scenario-full-walkthrough).

---

### 4.2 Individual Python module demos

Each source module has a `if __name__ == "__main__"` demo. Run any directly:

```bash
python src/infrastructure/link_budget.py     # Optical link budget (1550 nm)
python src/infrastructure/rf_link_budget.py  # RF link budget (Ka/X/S/UHF)
python src/routing/rl_agent.py               # RL routing agent demo
python src/routing/bundle.py                 # BPv7 bundle protocol
python src/routing/forwarding_engine.py      # Store-and-forward engine
python src/routing/training.py               # RL training loop
python src/routing/prioritization.py         # Mission data prioritization
python src/security/qkd.py                   # QKD (BB84 / E91)
python src/security/repeater_chain.py        # Quantum repeater chain
python src/security/privacy_amplification.py # CASCADE reconciliation
python src/orbital/contact_windows.py        # Contact window prediction
python src/orbital/doppler.py                # Doppler shift calculations
python src/orbital/topology.py               # 5-tier network topology
python src/computing/radiation.py            # Radiation hardening sim
python src/simulation/simulator.py           # Full simulation engine
python src/simulation/policy_engine.py       # Policy-based routing
```

**Selection criteria — which to run:**
- Want physics numbers? → `link_budget.py`, `rf_link_budget.py`, `contact_windows.py`.
- Want the AI/routing story? → `rl_agent.py`, `training.py`, `forwarding_engine.py`.
- Want security? → `qkd.py`, `repeater_chain.py`, `privacy_amplification.py`.
- Want resilience? → `radiation.py`.

---

### 4.3 Shell utility scripts

| Script | What it does | Decision: when to run |
|--------|--------------|----------------------|
| `./scripts/init.sh` | Create venv, install deps from `requirements.txt` | First setup, or after pulling new deps |
| `./scripts/init.sh --dev` | Above + linting/formatting tools | If you will edit code |
| `./scripts/run_tests.sh` | Run the 202-test suite | After any code change |
| `./scripts/run_tests.sh -v` | Verbose test output | Debugging a specific test |
| `./scripts/run_demos.sh` | Interactive menu of 6 demos | Exploring without memorizing commands |
| `./scripts/lint.sh` | Code quality checks | Before committing |
| `./scripts/lint.sh --fix` | Auto-fix style issues | Quick cleanup |
| `./scripts/clean.sh` | Remove build artifacts / caches | Free disk space / reset |
| `./scripts/dev.sh start` | Start backend + frontend (PM2) | Running the web app |
| `./scripts/dev.sh docker-up` | Build + start Docker stack | Containerized deployment |

---

### 4.4 The test suite

```bash
python -m pytest tests/ -q           # 480 tests, ~9s
python -m pytest tests/ -v           # verbose, one line per test
python -m pytest tests/test_run_simulation.py -q   # just the driver tests
python -m pytest tests/ -k failure   # tests matching "failure"
```

**13 test files, what each covers:**

| File | Covers |
|------|--------|
| `test_link_budget.py` | Optical + RF link budgets |
| `test_bundle.py` | BPv7 bundle data structures |
| `test_rl_agent.py` | RL routing agent decisions + reward |
| `test_training.py` | RL training loop, ε-decay, convergence |
| `test_forwarding.py` | Store-and-forward, LTP, TCPCL, UDPCL |
| `test_topology.py` | 5-tier topology + contact graph |
| `test_qkd.py` | BB84 + E91 protocols |
| `test_quantum_extended.py` | Repeater chains + privacy amplification |
| `test_orbital.py` | Orbital mechanics, Doppler, celestial bodies |
| `test_policy_engine.py` | Routing policy engine |
| `test_radiation.py` | Radiation effects, TMR, ECC, scrubbing, FDIR |
| `test_prioritization.py` | Data prioritization, compression, QoS |
| `test_run_simulation.py` | End-to-end driver + failure-recovery decision |

**Decision criterion:** every public function has test coverage. The suite
runs in <10s so it should be run before every commit.

---

### 4.5 Full-stack web dashboard (PM2)

A React + FastAPI dashboard with real-time visualizations.

```bash
./scripts/dev.sh setup    # install Python + Node.js deps (first time)
./scripts/dev.sh start    # start backend (8000) + frontend (3000) via PM2
```

| URL | Service |
|-----|---------|
| http://localhost:3000 | Frontend dashboard |
| http://localhost:8000 | Backend API |
| http://localhost:8000/docs | Swagger / OpenAPI docs |

**PM2 management:**

| Command | Purpose |
|---------|---------|
| `./scripts/dev.sh status` | Show process status |
| `./scripts/dev.sh logs backend` | Tail backend logs |
| `./scripts/dev.sh restart` | Restart all processes |
| `./scripts/dev.sh stop` | Stop all processes |

> **Selection note:** local PM2 uses SQLite; Docker (next) uses PostgreSQL.
> Use PM2 for fast iteration, Docker for production parity.

---

### 4.6 Docker Compose deployment

```bash
./scripts/dev.sh docker-up     # postgres + backend + frontend
```

| URL / port | Service |
|------------|---------|
| http://localhost:3000 | Frontend (nginx) |
| http://localhost:8000 | Backend API (FastAPI) |
| localhost:5432 | PostgreSQL |

| Command | Purpose |
|---------|---------|
| `./scripts/dev.sh docker-down` | Stop + remove containers |
| `./scripts/dev.sh docker-logs` | Tail container logs |
| `./scripts/dev.sh docker-ps` | Show container status |

**Decision criterion for Docker vs PM2:** Docker gives environment isolation
and the production database (PostgreSQL); PM2 is faster to iterate with. The
backend code is identical — only the database driver differs, selected by
`DATABASE_URL` in `.env`.

---

### 4.7 Static showcase site (GitHub Pages)

The showcase is a fully client-side SPA — no backend required.

```bash
# Option A: Python's built-in server
python -m http.server 8080 --directory docs/
# Open http://localhost:8080

# Option B: Docker (nginx)
docker compose up --build
# Open http://localhost:8080
```

Live at **[matx104.github.io/AETHERIX](https://matx104.github.io/AETHERIX/)**.

Includes **12 interactive browser demos** (all simulations ported to
JavaScript) and **12 learn pages**. The demos run entirely in the browser.

---

### 4.8 Presentation deck generation

The deck is authored as Markdown in `presentation/slides/` and compiled:

```bash
cd presentation
pip install python-pptx reportlab     # one-time, for generation only
python generate_pptx.py               # -> output/AETHERIX_Presentation.pptx
python generate_pdf.py                # -> output/AETHERIX_Presentation.pdf
```

> **Selection note:** the committed outputs already exist in
> `presentation/output/`, so regeneration is optional. The two new
> gap-analysis slides are `slides/16_trade_off_analysis.md` and
> `slides/17_failure_recovery.md`.

---

## 5. Configuration Reference (` .env`)

Copy `.env.example` to `.env` and adjust. All values have safe defaults.

| Variable | Default | Decision criteria for changing |
|----------|---------|--------------------------------|
| `DATABASE_URL` | `sqlite:///./aetherix.db` | Keep SQLite for local dev; Docker auto-sets to PostgreSQL |
| `DEBUG` | `true` | Set `false` in production |
| `LOG_LEVEL` | `INFO` | Use `DEBUG` when diagnosing |
| `BACKEND_PORT` | `8000` | Change if port is in use |
| `FRONTEND_PORT` | `3000` | Change if port is in use |
| `POSTGRES_DB` | `aetherix` | Docker database name |
| `POSTGRES_USER` | `aetherix` | Docker database user |
| `POSTGRES_PASSWORD` | `aetherix_dev` | **Change in any non-local deploy** |
| `CORS_ORIGINS` | `["http://localhost:3000",...]` | Add origins if frontend served elsewhere |

---

## 6. Architecture & Design Decisions (full rationale)

> This section defends every major choice with **reasoning, selection
> criteria, and trade-offs** — the material an oral examiner will probe.

### 6.1 Why a zero-dependency core

**Decision:** `src/` and `run_simulation.py` use only the Python standard
library (`math`, `random`, `dataclasses`, `enum`, `typing`, `collections`,
`uuid`, `time`, `bisect`, `statistics`).

**Selection criteria:**
- **Reproducibility** — an examiner can `git clone && python run_simulation.py`
  with no install step. Nothing can break from a dependency conflict.
- **Auditability** — every algorithm is readable in-place; no opaque library
  call hides the physics or the ML.
- **Educational value** — a Q-table, a BB84 sifting step, and an ECC Hamming
  encoder are more instructive hand-rolled than imported.

**Trade-off / honesty:** production would use `numpy`, `torch` (DQN), `qiskit`
(photon-level QKD), `astropy`/`jplephem` (precise ephemeris), and `ns-3`
(network simulation). These are documented as the Phase-6 upgrade path. The
demo is explicit that it does *not* use them — the numbers are produced by the
bundled models, not fabricated from a library.

---

### 6.2 Network topology — why 5 tiers, 241 nodes

**Decision:** a 5-tier hierarchy, 241 nodes:

| Tier | Segment | Count | Rationale |
|:----:|---------|------:|-----------|
| 1 | Earth Ground (DSN + control) | 5 | Geographic diversity (Goldstone/Madrid/Canberra) + ops centres |
| 2 | Earth Orbital | 51 | 3 GEO relays + 48-satellite LEO laser mesh (6 planes × 8) |
| 3 | Deep Space Transit | 4 | 2 primary + 2 backup Lagrange relays (ES-L4/ES-L5) |
| 4 | Mars Orbital | 4 | 2 areostationary + 2 polar orbiters (minimum for global coverage) |
| 5 | Mars Surface | 177 | Bases, rovers, fixed stations, drones, sensor mesh |

**Selection criteria — why each tier exists and cannot be merged:**
- **Tier 2** handles atmospheric bypass + inter-DSN routing in <20 ms/hop via
  optical ISL. Without it, Canberra→Goldstone data would traverse terrestrial
  fibre (100–300 ms) outside AETHERIX's control.
- **Tier 3** provides conjunction coverage + the quantum repeater hop. Nothing
  else maintains Earth–Mars connectivity when the Sun is between them
  (see [§6.8](#68-why-lagrange-relays-at-es-l4--es-l5)).
- **Tier 4/5** are the data source/sink.

**Trade-off:** 241 nodes is a large state space for the RL agent. Mitigated by
state discretisation (Q-table). Removing any tier breaks a unique capability —
the tiered design *localises* failures (a Tier-5 rover failure does not affect
Tier 1–3).

---

### 6.3 Hybrid optical/RF — why 1550 nm + Ka-band

**Decision:** 1550 nm optical for throughput; Ka-band RF for reliability.

**Selection criteria:**

| Factor | 1550 nm optical | Ka-band RF | Winner |
|--------|-----------------|------------|--------|
| Throughput | 2–200 Mbps (DSOC-class) | 0.125–6 Mbps | Optical (10–100×) |
| Weather | Blocked by clouds (60–70% clear/site) | Penetrates clouds (99%+) | RF |
| Solar corona (conjunction) | Severely degraded | Robust at wide elongation | RF |
| Beam divergence | Narrow (needs precise pointing) | Wider (forgiving) | RF |
| Eye safety | Safe at cornea | N/A | Optical |
| Component maturity | Telecom C-band heritage | Deep-space heritage | Tie |

**Reasoning:** optical and RF are *complementary*, not competitive. Optical
carries the bulk science downlink; RF is the guaranteed-reliability fallback
for emergency traffic and conjunction periods. This mirrors NASA's DSOC
co-flying with the RF system on Psyche. The RL agent routes P0/P1 via RF for
guaranteed delivery and bulk via optical for speed.

**Why 1550 nm specifically** (not 800/1064 nm): telecom heritage (cheap, mature
components), atmospheric absorption window, corneal eye safety, and both APD
and SNSPD detectors available.

---

### 6.4 Why RL routing over Contact Graph Routing

**Decision:** replace static Contact Graph Routing (CGR) with Q-learning.

**Selection criteria:**

| Criterion | CGR (static schedule) | AETHERIX RL agent |
|-----------|----------------------|-------------------|
| Real-time adaptivity | No — re-plans on schedule refresh (12+ min stale) | Yes — reacts to live link/buffer state |
| Multi-objective optimisation | One metric (usually delay) | 5 (delivery, delay, hops, drops, energy) |
| Learns from experience | No | Yes — policy improves over the synodic period |
| Distance-phase awareness | Requires manual schedule per phase | Learned automatically |

**Reasoning:** CGR computes optimal routes over a pre-planned contact graph,
but it cannot adapt to unplanned events (solar flare, buffer filling). The RL
reward function `R = α(delivery) − β(delay) − γ(hops) − δ(drops) − ε(energy)`
captures the five competing objectives simultaneously. The policy develops
*distance-phase-aware* routing that no pre-planned schedule encodes.

**Trade-off / safety net:** RL has no optimality guarantee and needs training
time. If agent confidence drops below 0.3, AETHERIX falls back to CGR.
Production replaces Q-tables with DQN + experience replay.

---

### 6.5 Why Q-tables before Deep Q-Networks

**Selection criteria:**
- **Interpretability** — every Q-value is inspectable: "from node X, the best
  action when buffer is 80% full and link quality is 0.6 is STORE." A neural
  network is a black box. *Essential for a defence.*
- **Rapid iteration** — a Q-table trains in seconds; reward weights tune fast.
- **Right-sized state space** — 241 nodes with discretised variables fit a
  Q-table.

**Upgrade path (Phase 6):** replace the table with a neural network, add
experience replay (1M transitions), target networks for stability, and
prioritised replay + curriculum learning to cut training time.

---

### 6.6 The reward function — weight-by-weight justification

`R = α(delivery) − β(delay) − γ(hops) − δ(drops) − ε(energy)`
(source: `rl_agent.py:70-74`)

| Symbol | Value | Selection criteria / reasoning |
|--------|------|--------------------------------|
| α delivery | **1.0** | The baseline unit of success — a delivered bundle. |
| β delay | **0.001/s** | A 12-hour delay = 43.2 penalty. Significant enough to prefer faster routes, not so large the agent gambles on risky shortcuts. |
| γ hops | **0.1** | Each hop adds custody overhead + failure risk. Discourages needless relay stops. |
| δ drops | **10.0** | **10× the delivery reward.** A drop is *total* failure (data lost), not merely "no success." |
| ε energy | **0.01/Wh** | A 5 W laser for 1 hour = 0.05 penalty. Keeps power in check without dominating. |

**Tuning method:** empirical, over the 780-day synodic simulation. The weights
encode operational priority: **delivery >> avoiding-drops > delay > hops >
energy**. Dynamic adjustment (raise ε in a dust storm, lower β during
conjunction) is a planned production enhancement.

---

### 6.7 ε-greedy — why decay = 0.995

(source: `training.py:50`, `epsilon_start=1.0`, `epsilon_end=0.01`)

**The math:**
```
episodes to ε=0.30:  log(0.30)/log(0.995) ≈ 240
episodes to ε=0.01:  log(0.01)/log(0.995) ≈ 920
```

**Selection criteria:**
- **Why not faster (0.99)?** Reaches ε=0.01 in ~460 episodes — the agent stops
  exploring before it has seen the full distance variation (7.3× range). An
  agent trained too fast on "easy" opposition learns to always forward
  immediately — catastrophic during conjunction.
- **Why not slower (0.999)?** ~4600 episodes to converge — wasted compute.
- **0.995** gives ~240 episodes of substantial exploration (enough to sample
  rare high-consequence states: conjunction blackout, buffer overflow, dust
  storm) then a long exploitation tail.

**The principle:** exploration must persist long enough to visit the *rare,
high-consequence states* at least a few times. Verify live:
`python run_simulation.py -m 3` shows ε dropping 1.0 → 0.018 over 800 episodes.

---

### 6.8 Why Lagrange relays at ES-L4 / ES-L5

**Selection criteria — three unique properties:**
1. **Gravitational stability** — L4/L5 are stable Trojan points requiring
   near-zero station-keeping fuel. L1/L2 are unstable (continuous correction).
2. **Conjunction coverage** — at 60° ahead/behind Earth in its orbit, L4/L5
   relays have line-of-sight to Mars *around the solar limb* even at true
   conjunction: **50–70% availability vs 0% for direct links.**
3. **Intermediate distance** — at ~1 AU from Earth, they split the deep-space
   link into two shorter hops with better budgets.

**Reasoning:** no Mars-orbit relay can solve the conjunction problem because
the Sun-blocked geometry is on the Earth side. L4/L5 are co-located with the
classical relay satellites — avoids dedicated quantum spacecraft launches.

---

### 6.9 Convergence layers — why LTP / TCPCL / UDP-CL

| Layer | Protocol | Selection criteria |
|-------|----------|--------------------|
| Deep-space hops | **LTP** (RFC 5326) | Link-local reliability (each hop ACKs independently); red/green differentiation in one session; timers default to minutes/hours, not ms |
| Earth segment | **TCPCL** (RFC 7242) | Session management where RTT is short |
| Optical ISL | **UDP-CL** | Fragmentation + loss simulation for inter-satellite laser links |

**Why LTP over TCP for deep space:** TCP's reliability needs end-to-end ACKs
with sender state sized to RTT. At 6–44 min RTT, a TCP sender would buffer
millions of segments and every timeout triggers backoff calibrated for ms
networks. LTP makes reliability *link-local*: retransmission happens only on
the failed hop, not end-to-end.

---

### 6.10 Security — why QKD + post-quantum cryptography

**Decision:** defence-in-depth with two layers addressing different threats.

| Layer | Threat addressed | Property |
|-------|------------------|----------|
| **QKD** (BB84/E91) | Eavesdropping on the key exchange | Information-theoretic security (laws of physics) |
| **PQC** (ML-KEM/ML-DSA, NIST FIPS 203/204) | "Store-now-decrypt-later" quantum attacks | Computational security on classical hardware; handles authentication |

**Reasoning:** QKD guarantees the *key exchange* is secure by physics but needs
line-of-sight hardware and has low key rates at interplanetary distance
(1–10 bps). PQC works on any channel and provides authentication (which QKD
alone cannot). If the quantum channel is down, ML-KEM handles key exchange; if
lattice crypto is ever broken, QKD keys are unaffected.

**Security threshold:** BB84 QBER < 11% indicates no eavesdropper. The demo
shows a clean channel at ~0% and an intercepted channel at ~25% (detected,
key discarded). See `run_simulation.py -m 5`.

---

### 6.11 Radiation hardening — the mitigation stack

**Selection criteria — defence-in-depth, each layer addresses a failure mode:**

| Effect | What it does | Mitigation | Reasoning |
|--------|--------------|------------|-----------|
| SEU | Single bit flip | SECDED ECC (Hamming) | Corrects 1 bit, detects 2 (21.9% overhead) |
| MBU | ≥2 adjacent bits | Bit interleaving | Spreads a strike across words |
| SEL | Parasitic short (destructive) | Current limiting + power-cycle | Hardware protection |
| TID | Cumulative dose (krad) | Rad-hard parts (RAD750 ~200 krad) | >2000× margin on Mars surface |
| — | Processor hang | FDIR + watchdog timer | Detect → isolate → reset → SAFE_MODE |

**Headline numbers (AETHERIX model, `run_simulation.py -m 6`):**
- ~37,000 raw bit upsets over a 210-day, 512 Mbit cruise → ~186 residual
  after mitigation → **~200× protection**.
- TMR reliability gain at p=1e-4: **3,334×** (system error ≈ 3p² vs p).
- RAD750 TID margin over a 687-day Mars surface mission: **2,127×**.

**Heritage:** NASA RAD750 (Curiosity, Perseverance C&DH), ESA LEON3FT/GR712RC.

---

### 6.12 Data prioritization — the 4-tier QoS rationale

**Decision:** 4 mission data categories with deadline-aware preemption.

| Class | Examples | Latency target | Routing |
|-------|----------|---------------|---------|
| P0 Emergency | Safety alerts, commands | <1 min | RF + LTP red + custody (most reliable) |
| P1 High Science | High-value observations | <30 min | Optical + LTP green (fastest) |
| P2/P3 Standard/Housekeeping | Telemetry | <7 days | Best-effort |
| P4 Bulk | Software updates, archives | <30 days | Opportunistic, first evicted |

**Selection criteria:** RFC 9171 defines only 3 classes (bulk/normal/expedited)
— too coarse. Splitting P0 from P1 lets the RL agent make finer decisions: P0
pre-empts everything and uses the most reliable path; P4 is evicted first under
buffer pressure. The policy engine **never** drops P0/P1.

---

### 6.13 Failure & recovery scenario (full walkthrough)

> This is the resilience guarantee the architecture must prove. Run it live:
> `python run_simulation.py -m 4`.

**The threat:** during Earth–Sun–Mars conjunction, the direct 1550 nm
line-of-sight passes through the Sun's corona. Solar-plasma scintillation
collapses optical link quality below the agent's **0.3 forward threshold**.

**Recovery sequence (autonomous, no Earth intervention — which is impossible
anyway at 22-min one-way light time):**

1. **Detect** — the RL agent's Q-value for the optical path collapses. Link
   quality 0.05 < 0.3 threshold → no delivery reward → conjunction reward
   = −1.44 (vs −0.20 for the relay path).
2. **Re-route** — the agent, in exploit mode, selects the highest-Q neighbour:
   **ES-L4 (Ka-band RF)**, which sits at 60° solar elongation, avoiding the
   corona (quality 0.65, OPEN).
3. **Prioritise** — the policy engine fires simultaneously:
   - P0 EMERGENCY → `emergency_fast_path` → **forward** on best available link.
   - P4 BULK → `deep_space_store` → **store** and defer until conjunction passes.
4. **Outcome** — mission-critical bundles reach Earth via
   Mars → ES-L4 → Earth (Ka-band); no bandwidth wasted on non-urgent data;
   **zero mission-critical data lost.**

```
Mars areo-relay ──optical CLOSED──✗──► Earth (direct)
     │
     └──Ka-band OPEN──► ES-L4 relay ──Ka-band──► Earth  ✓ P0 delivered
```

**Design lesson:** the RL agent adapts in real time; the policy engine
guarantees deterministic P0 pre-emption regardless of agent confidence. This
is defence-in-depth at the routing layer.

---

### 6.14 Standards compliance rationale

AETHERIX follows, not reinvents, the standards:

| Standard | Why followed |
|----------|--------------|
| RFC 9171 (BPv7) | The DTN bundle format — interoperability with ION-DTN |
| RFC 5326 (LTP) | Deep-space convergence layer — solves the ACK-timer problem |
| RFC 7242 (TCPCL) | Earth-segment convergence |
| RFC 4838 | DTN architecture |
| CCSDS 734.2-B-1 / 735.1-B-1 | Bundle protocol + schedule-aware routing |
| CCSDS 141.0-B-1 / 131.0-B-4 | Optical + TM data link |
| CCSDS 121.0-B-3 / 122.0-B-2 | Lossless + image compression |
| NIST FIPS 203/204 | Post-quantum KEM + signatures |

**Selection criterion:** follow the standard rather than invent a custom
format. CBOR encoding (RFC 8949) was chosen *by the IETF*, not by AETHERIX —
compact, deterministic, self-describing.

---

## 7. Reproducibility — seeds, configs, citing results

> Per the project operating contract: **no mocked physics, no fabricated
> numbers.** Every result cites its seed and config.

- **RNG seed:** all simulations accept `--seed` (default 42). Same seed →
  identical output. `python run_simulation.py --seed 7`.
- **Config:** `SimulationConfig` (`src/simulation/simulator.py`) records
  duration, time-step, distance, data rates, and generation rate.
- **Citing a result:** state the module, seed, and config. Example:
  *"Baseline DTN, seed=42, 24h/300s steps, 225 M km, 20 bundles/hr → 34.7%
  delivery ratio."*
- **Link budgets:** computed at runtime by the bundled calculators — not
  hardcoded. Verify: `python src/infrastructure/link_budget.py`.

---

## 8. Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `ModuleNotFoundError` running a module | CWD is not repo root, or venv not active | Run from repo root; `source venv/bin/activate` |
| `run_simulation.py` output differs | Different seed | Use `--seed 42` for the documented numbers |
| `ImportError` in tests | pytest not installed | `pip install pytest` or `./scripts/init.sh` |
| `pm2 not found` | PM2 not installed globally | `npm install -g pm2` |
| Docker DB connection refused | PostgreSQL still starting | Wait for healthcheck; `docker compose ps` |
| Showcase site blank | Opened via `file://` | Serve `docs/` over HTTP: `python -m http.server 8080 --directory docs/` |
| PPTX generation fails | `python-pptx` not installed | `pip install python-pptx` (optional, outputs already committed) |
| Frontend build errors | Stale node_modules | Delete `frontend/node_modules`, run `npm install` |
| Port 3000/8000 in use | Another process | Change `FRONTEND_PORT`/`BACKEND_PORT` in `.env` |

---

*For the per-slide speaker notes and deeper Q&A, see
[`interview_prep/question_bank/`](../interview_prep/question_bank/) (design
decisions, RL hyperparameters, challenging questions).*
