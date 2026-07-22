# Day 7: Reward Function & Hyperparameters

## 📅 July 29, 2026

## 🎯 Learning Objective
Master the reward function `R = α·delivery − β·delay − γ·hops − δ·drops − ε·energy` and the rationale for every hyperparameter value. The examiner will probe *why* each weight takes the value it does — this lesson prepares you to justify each knob. This maps to **LO2**.

## 📖 The Core Concept

### The Reward Function: A Multi-Objective Balancing Act

The reward function is the *compass* that guides the RL agent's learning. Every value the agent receives tells it "do more of this" or "do less of that." Designing the reward function is the single most consequential engineering decision in the entire RL system — a poorly designed reward produces an agent that optimises the wrong thing.

AETHERIX uses a **linear weighted sum** of five objectives:

```
R = α·delivery − β·delay − γ·hops − δ·drops − ε·energy
```

| Term | Weight | Value | Rationale |
|------|--------|-------|-----------|
| delivery | α (alpha) | **1.0** | Successful delivery is the baseline positive signal |
| delay | β (beta) | **0.1** | Penalise excessive delay — low weight because some delay is unavoidable in DTN |
| hops | γ (gamma) | **0.05** | Penalise unnecessary hops — very low because sometimes more hops = better routing |
| drops | δ (delta) | **10.0** | Heavy penalty for dropping bundles — drops are the worst outcome |
| energy | ε (epsilon) | **0.01** | Mild energy penalty — important but secondary to delivery |

### Why These Exact Values?

**α = 1.0 (delivery):** This is the normalisation anchor. Every other weight is calibrated relative to delivery. A successful delivery yields +1.0 reward — the reference unit. This keeps the reward scale interpretable: "a drop costs as much as 10 successful deliveries."

**δ = 10.0 (drops):** This is the **dominant penalty** — 10× the delivery reward. Why? Because in a deep-space mission, a dropped bundle means lost science data that may be impossible to recollect (the instrument has moved on, the orbital geometry has changed). The 10:1 ratio ensures the agent treats drops as existential threats. The agent will store a bundle indefinitely rather than risk a drop, even if that means higher delay.

**β = 0.1 (delay):** Delay matters but is not the primary concern. In interplanetary DTN, some delay is inherent — a bundle from Mars to Earth takes 4–22 minutes regardless of routing. The 0.1 weight creates a *mild* pressure toward faster paths without overwhelming the delivery signal. A bundle delivered in 10 minutes scores `1.0 − 0.1×10 = 0.0` (net zero — barely worth forwarding); delivered in 1 minute scores `1.0 − 0.1×1 = 0.90` (strong positive).

**γ = 0.05 (hops):** Each extra hop adds complexity, energy, and drop risk. But sometimes more hops are *better* (e.g., routing through a stable relay rather than a marginal direct link). The very low 0.05 weight provides a gentle nudge toward fewer hops without forcing the agent into bad direct-link decisions.

**ε = 0.01 (energy):** Energy conservation matters for battery-powered rovers and relays, but it's secondary to data delivery. The 0.01 weight ensures the agent *prefers* energy-efficient paths when all else is equal, but will spend energy freely to avoid drops or ensure delivery.

### Epsilon Decay: The Exploration Schedule

The exploration rate ε starts at **1.0** (pure exploration) and decays by a factor of **0.995 per episode**:

```
ε(ep) = max(0.01, 1.0 × 0.995^ep)
```

This is **geometric decay** — the agent explores aggressively early, then gradually shifts to exploitation. The half-life of exploration is `ln(0.5)/ln(0.995) ≈ 138 episodes`. By episode ~500, ε ≈ 0.08. By episode ~920, ε hits the floor of 0.01.

Why geometric rather than linear? Because early exploration needs to cover the entire state space, but as the Q-table fills in, the marginal value of exploration drops rapidly. Geometric decay matches this curve.

### Convergence Detection

The agent has converged when its policy stabilises — when it stops changing its decisions for a given state. AETHERIX tracks two convergence indicators:

1. **Q-table stability:** The average absolute change in Q-values per episode falls below a threshold (typically 0.001) for 50 consecutive episodes.
2. **Policy stability:** The action selected for the 10 most-visited states has not changed for 100 consecutive episodes.

The training loop in `training.py` checks these after each episode and halts early when both conditions are met — typically around episode 600–800 in the 15-node training topology.

### The Danger of Reward Hacking

A reward function can be "gamed." If the drop penalty were too low (say δ=0.5), the agent would learn to *drop every bundle immediately* — instant low delay, zero energy cost, small drop penalty, net positive reward. The δ=10.0 weight prevents this. Similarly, if α were too high relative to β, the agent would take any path regardless of delay. The 10:1 δ:α ratio is the key safety margin.

## 🔬 In AETHERIX

The reward function is in `src/routing/rl_agent.py`, method `RLRoutingAgent.calculate_reward()`:

```python
REWARD_WEIGHTS = {
    "delivery": 1.0,     # α
    "delay": 0.1,        # β
    "hops": 0.05,        # γ
    "drop": 10.0,        # δ
    "energy": 0.01,      # ε
}
```

The method signature:
```python
def calculate_reward(self, bundle, delivered=False, dropped=False,
                     delay_hours=0, hop_count=0, energy_consumed=0.0):
```

Returns a float. The logic:
- If `delivered`: `+1.0` (delivery) `− 0.1 × delay_hours` (delay) `− 0.05 × hop_count` (hops) `− 0.01 × energy_consumed` (energy).
- If `dropped`: `−10.0` (drop penalty) `− 0.01 × energy_consumed` (energy already spent).
- Otherwise (stored, forwarded): `− 0.05 × hop_count − 0.01 × energy_consumed` (interim cost).

The epsilon decay is in `RLRoutingAgent.decay_epsilon()`:
```python
self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
```

With defaults `epsilon=1.0`, `epsilon_min=0.01`, `epsilon_decay=0.995`.

The Q-learning update uses `learning_rate=0.001` and `discount_factor=0.99`:
```python
def update(self, state, action, reward, next_state):
    key = self.get_state_key(state)
    next_key = self.get_state_key(next_state)
    current_q = self.q_table[key][action]
    max_next_q = max(self.q_table[next_key].values())
    td_target = reward + self.discount_factor * max_next_q
    self.q_table[key][action] += self.learning_rate * (td_target - current_q)
```

The training loop in `src/routing/training.py` (`Trainer` class) runs 1000 episodes over the `TrainingEnvironment` (15-node topology, 5-tier). Convergence is detected when policy entropy drops below a threshold for sustained episodes.

## 📐 Key Numbers & Formulas
- **Reward function:** `R = 1.0·delivery − 0.1·delay − 0.05·hops − 10.0·drops − 0.01·energy`
- **α (delivery):** 1.0 — normalisation anchor
- **β (delay):** 0.1 — delay_units = hours
- **γ (hops):** 0.05 — hop_units = count
- **δ (drops):** 10.0 — **dominant penalty, 10× delivery reward**
- **ε (energy):** 0.01 — energy_units = normalised 0–1
- **Epsilon start:** 1.0
- **Epsilon decay:** 0.995 per episode (geometric)
- **Epsilon floor:** 0.01
- **Learning rate:** 0.001
- **Discount factor:** 0.99
- **Exploration half-life:** ~138 episodes
- **Convergence:** typically episode 600–800 in 15-node topology
- **Training episodes:** 1000

## 🔗 Standards & References
- [Sutton & Barto — Reinforcement Learning Ch. 17 (Reward Shaping)](http://incompleteideas.net/book/RLbook2020.pdf)
- [OpenAI Spinning Up — Key Concepts in RL](https://spinningup.openai.com/en/latest/spinningup/rl_intro.html)
- [Ng et al. (1999) — "Policy Invariance Under Reward Transformations"](https://www.cs.brandeis.edu/~cs141b/CS141B_Spring2014/additional_readings/award_invariance.pdf)
- `interview_prep/question_bank/rl_hyperparameters.md` — per-knob justification
- `interview_prep/cheat_sheets/formulas.md` — all formulas in one place

## 💡 How the Examiner Will Probe This

**Q: "Why is the drop penalty 10 times the delivery reward?"**
→ In deep-space missions, a dropped bundle may represent irreplaceable science data — the instrument has moved on, the orbital geometry has changed. A 1:1 ratio would let the agent treat drops as acceptable. The 10:1 ratio ensures the agent stores bundles indefinitely rather than risk a drop. The net reward for a drop is −10, versus +1 for delivery — the agent learns that avoiding drops is 10× more important than achieving fast delivery.

**Q: "How did you prevent the agent from gaming the reward function?"**
→ Two mechanisms. First, the δ=10.0 drop penalty prevents the "drop everything" strategy — a dropped bundle costs 10× a delivered one. Second, I validated the learned policy on held-out scenarios (solar flares, node failures) that were not in training, confirming the agent generalises rather than exploiting a specific training artifact.

**Q: "What does your epsilon decay schedule look like and why?"**
→ Geometric decay at 0.995 per episode, starting from 1.0, flooring at 0.01. Geometric because early exploration needs to cover the full state space but marginal value of exploration drops rapidly as the Q-table fills. The floor at 0.01 ensures the agent never fully stops exploring — critical because the interplanetary environment is non-stationary (orbital phases, solar activity change link characteristics over time).

## ✅ What You Should Be Able to Answer After This Lesson
1. What are the five terms in the reward function and what is each weight?
2. Why is δ (drop penalty) set to 10.0 rather than 1.0 or 5.0?
3. What is the epsilon decay formula, and what is the exploration half-life?
4. What two convergence indicators does AETHERIX track?
5. What would happen if the drop penalty were too low (e.g., δ=0.5)?

## 📂 Deep Dive Resources
- `src/routing/rl_agent.py` — `REWARD_WEIGHTS`, `calculate_reward()`, `decay_epsilon()`, `update()`
- `src/routing/training.py` — `Trainer`, convergence detection
- `interview_prep/cheat_sheets/formulas.md` — reward function and all constants
- `interview_prep/question_bank/rl_hyperparameters.md` — detailed Q&A on each hyperparameter
- `docs/DESIGN_RATIONALE.md` — reward weight derivation
- Live demo: [https://matx104.github.io/AETHERIX/](https://matx104.github.io/AETHERIX/)
