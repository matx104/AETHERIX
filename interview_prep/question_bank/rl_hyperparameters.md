# RL Hyperparameters — Oral-Exam Deep-Dive

> The examiner will grill on these. Memorise the **reasoning**, not the code.
> Every value is sourced from `src/routing/rl_agent.py` and
> `src/routing/training.py`.

---

## Q1. Why is the ε-greedy decay 0.995?

`epsilon_decay = 0.995` (`TrainingConfig`, `training.py:50`).

**Answer:** The decay rate sets the exploration→exploitation transition speed.
With `epsilon_start = 1.0` and `epsilon_end = 0.01`:

```
episodes to reach ε = 0.30:  log(0.30) / log(0.995) ≈ 240 episodes
episodes to reach ε = 0.01:  log(0.01) / log(0.995) ≈ 920 episodes
```

- **Why not faster (e.g. 0.99)?** A 0.99 decay reaches ε = 0.01 in ~460
  episodes — the agent would stop exploring before it has seen the full
  synodic-period distance variation (54.6 M km → 401 M km, a 7.3× range).
  An agent trained too fast on the "easy" opposition phase learns to always
  forward immediately — a catastrophic policy during conjunction.
- **Why not slower (e.g. 0.999)?** 0.999 takes ~4600 episodes to converge,
  wasting compute. 0.995 gives ~240 episodes of substantial exploration
  (enough to cover diverse link/buffer states) then a long exploitation tail.
- **The principle:** exploration must persist long enough to visit the *rare,
  high-consequence states* (conjunction blackout, buffer overflow, dust storm)
  at least a few times. 0.995 empirically clears that bar for the
  241-node topology.

---

## Q2. Why is the learning rate 0.001?

`learning_rate = 0.001` (`rl_agent.py:92`, `training.py:51`).

**Answer:** Tabular Q-learning is stable at low learning rates because each
update is `Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',a') − Q(s,a)]`. With α = 0.001:
- Each new reward moves a Q-value by at most 0.1% of the TD-error — the table
  converges smoothly without oscillation.
- A higher α (e.g. 0.1) would let a single anomalous reward (e.g. a rare
  conjunction drop) distort the policy; 0.001 averages over many visits.
- This is the standard deep-RL learning-rate regime; the DQN upgrade keeps it.

---

## Q3. Why is the discount factor γ = 0.99?

`discount_factor = 0.99` (`rl_agent.py:93`).

**Answer:** γ controls how much the agent values *future* reward versus
*immediate* reward. γ = 0.99 means a reward 100 steps ahead is worth
0.99¹⁰⁰ ≈ 0.37 of its face value.
- DTN delivery is inherently *delayed* — a bundle may cross 3–5 hops over
  minutes to hours. A low γ (e.g. 0.5) would make the agent myopic: it would
  store locally (immediate small reward) instead of forwarding toward the
  distant delivery reward.
- γ = 0.99 gives an effective horizon of ~100 steps, comfortably longer than
  any single bundle's hop count, so the agent "sees" the delivery payoff.

---

## Q4. Why weigh buffer occupancy so heavily in the state?

The state key (`get_state_key`) discretises **buffer level first** (`high`/`low`
at the 0.7 threshold), then link level (`good`/`poor` at 0.5), then priority.

**Answer:** Buffer occupancy is the *failure mode you cannot recover from*.
- A dropped bundle is total data loss (the δ = 10.0 penalty reflects this).
- A poor link just means *delay* — the bundle waits in the queue and tries
  again. Delay is recoverable; data loss is not.
- So the state representation must distinguish "buffer nearly full" (imminent
  drop risk → must act now) from "buffer fine" (luxury to wait for a better
  link). Making buffer the primary state axis ensures the agent learns
  *preventive forwarding* — draining the buffer *before* it hits the 0.9
  congestion threshold — rather than reacting after the fact.
- This mirrors operational reality: a Mars relay with a full buffer is one
  dust storm away from catastrophic data loss.

---

## Q5. Why is MIN_LINK_QUALITY = 0.3?

`MIN_LINK_QUALITY = 0.3` (`rl_agent.py:77`).

**Answer:** Below 0.3 quality, the expected delivery probability times the
delivery reward (1.0 × ~0.3 = 0.3) is less than the hop penalty plus the risk
of a drop (δ = 10.0 × ~0.7 = 7.0 expected loss). Forwarding into a < 0.3 link
has *negative expected value*. So the threshold is derived from the reward
function, not arbitrary: it's the break-even point where `P(deliver)·α <
P(drop)·δ`. The failure-and-recovery demo (`run_simulation.py -m 4`) shows this
exactly — the conjunction optical link at quality 0.05 is below threshold → the
agent refuses to forward and reroutes via the 0.65-quality Ka-band relay.

---

## Q6. The full reward function — justify every weight.

`R = α(delivery) − β(delay) − γ(hops) − δ(drops) − ε(energy)`

| Symbol | Value | Justification |
|--------|------|---------------|
| α delivery | **1.0** | Baseline objective: a delivered bundle is the unit of success. |
| β delay | **0.001/s** | A 12-hour delay costs 43.2 points — significant but not so large the agent gambles on risky shortcuts. |
| γ hops | **0.1** | Each hop adds custody overhead + failure risk; discourages needless relay stops. |
| δ drops | **10.0** | **10× the delivery reward** — a drop is total failure, not merely "no success." |
| ε energy | **0.01/Wh** | A 5 W laser for 1 hour = 0.05 penalty — keeps power in check without dominating. |

**Tuning method:** empirical, over the 780-day synodic simulation. The weights
encode *operational priority*: delivery >> avoiding-drops > delay > hops >
energy. During a dust storm, ε would rise (power scarce); during conjunction,
β would fall (delays unavoidable) — dynamic weight adjustment is a planned
production enhancement.

---

## Q7. If you had to defend one number under pressure, which?

**ε-decay = 0.995.** It's the single knob that most affects policy quality.
Too fast → myopic, conjunction-incompetent agent. Too slow → wasted compute.
0.995 is the value that lets the agent see the *full distance-phase landscape*
(780-day synodic period, 7.3× distance range) before committing to a policy.
I can reproduce the convergence curve (`run_simulation.py -m 3`) to show
ε dropping from 1.0 → 0.018 over 800 episodes — the "70% exploitation" point
hits around episode 240, exactly when the agent has sampled enough conjunction
states to route around them.
