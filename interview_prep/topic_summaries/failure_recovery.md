# Failure and Recovery

## Topic Summary

### Failure Mode Catalogue

A deep-space link is never "up" like a terrestrial link. AETHERIX treats
failure as the *expected* regime: every failure mode has a detected
fallback, and store-and-forward means a "down" link is rarely a "lost"
bundle. The five canonical modes:

| # | Failure | Trigger | Detection | First response |
|---:|---------|---------|-----------|----------------|
| 1 | Solar conjunction blackout | Sun-Earth-Mars angle < 10 deg | orbital geometry | store at Lagrange relays |
| 2 | Optical link failure | clouds / pointing loss | link quality drop | fall back to Ka-band RF |
| 3 | Ka-band degradation | solar plasma scintillation | Eb/N0 margin loss | reroute via X-band + Lagrange relays |
| 4 | Node failure (radiation SEU) | single-event upset | node status -> OFFLINE | isolate node, reroute around it |
| 5 | Buffer overflow | sustained ingress > egress | buffer_utilization > 0.9 | priority-based eviction |

---

### 1. Solar Conjunction Blackout

Approximately every **26 months** (the Earth-Mars synodic period) the two
planets pass near solar conjunction and the Sun's corona raises the noise
floor until no reliable link exists. Modeled in `predict_contact_windows()`
as a hard exclusion at `contact_windows.py:253`:

```
if phase_angle < 10 degrees: skip window
```

| Property | Value |
|----------|-------|
| Recurrence | ~26 months (synodic period) |
| Exclusion half-angle | 10 degrees (phase angle) |
| Typical blackout duration | ~2 weeks |
| Surviving path | store-and-forward via ES-L4 / ES-L5 relays |

The Lagrange relays (tier 3) sit ~60 degrees off the Sun-Earth line, so
they keep line-of-sight to both planets when the direct path is occulted.

---

### 2. Optical -> Ka-band RF Fallback

Optical (1550 nm) is the high-rate primary but is weather- and
pointing-sensitive (blocked by clouds, needs < 10 urad pointing). On
failure the contact is retried over Ka-band RF (26.5 GHz), which trades
rate (2-10 Mbps vs 50-200 Mbps) for robustness — rain fades only, no
pointing budget, degraded-but-usable through conjunction. The switch is
automatic: the forwarding engine sees optical link quality fall and the RL
agent reroutes to any neighbor with `link_quality >= MIN_LINK_QUALITY`
(0.3). See `rl_agent.py:83`.

---

### 3. Ka-band -> X-band via Lagrange Relays

During conjunction even Ka-band degrades under solar-plasma
scintillation. The next fallback is **X-band** (8.4 GHz), the deep-space
standard, routed through the Lagrange relays which support both Ka and
optical and stay reachable.

| Band | Frequency | Use in failure chain |
|------|----------:|----------------------|
| Ka | 26.5 GHz | primary RF (optical failed) |
| X | 8.4 GHz | conjunction fallback (Ka degraded) |
| S | 2.3 GHz | TT&C / emergency beacon |

X-band is far lower rate but tolerates the corona: a thin but reliable
connection is preserved while bulk traffic waits in store-and-forward.

---

### 4. Node Failure and Isolation (Radiation SEU)

A single-event upset can corrupt memory or latch a relay. Each `DTNNode`
exposes a `NodeStatus`: ACTIVE (nominal), DEGRADED (partial failure), or
OFFLINE (failed / isolated). Only ACTIVE and DEGRADED nodes are routed
through:

```
is_operational(node) = node.status in (ACTIVE, DEGRADED)
```

A node going OFFLINE is dropped from the adjacency set, so BFS and the RL
agent route around it. Custody transfer (RFC 9171 section 4.5) guarantees
a bundle held by a failing node is not lost: the preceding custodian
retransmits once a new next-hop is found (`forwarding_engine.py:306`/`:323`).

---

### 5. Buffer Overflow and Priority-Based Eviction

When sustained ingress exceeds egress (a long conjunction approach),
buffers fill and the policy engine evicts the lowest-value bundles first
(`policy_engine.py:174`):

```
congestion_control (policy priority 90, match_all):
    if buffer_occupancy > 0.9 AND bundle.priority >= 3:
        drop
```

| Buffer state | Threshold | Action |
|--------------|----------:|--------|
| Normal | < 0.5 | accept all |
| Loaded | 0.5 - 0.9 | defer BULK (rank 4) |
| Critical | > 0.9 | drop housekeeping / bulk; protect EMERGENCY + HIGH_SCIENCE |

Eviction is strictly priority-ordered: the `BundleQueue` sorts by
`(priority, deadline)`, so the first bundles dropped are always lowest
priority. EMERGENCY (rank 0) and HIGH_SCIENCE (rank 1) are never evicted
while a lower-priority bundle occupies space.

---

### The RL Agent as Failure Detector

The routing agent is the real-time sensor of link health. Rather than a
binary up/down flag, it consumes a normalised `link_quality` (0.0-1.0)
with one decisive threshold (`MIN_LINK_QUALITY = 0.3`, `rl_agent.py:83`):

| Link quality | Agent action | Rationale |
|------------:|--------------|-----------|
| >= 0.3 | FORWARD | link closes with margin |
| < 0.3 | STORE | wait for next contact, avoid a lossy forward |

```
if quality < MIN_LINK_QUALITY:
    store(bundle)
```

This threshold corresponds roughly to the -3 dB margin boundary (see
`link_budget.md`): below it the link is "intermittent" and store-and-
forward is correct. The same 0.3 cutoff is the `deep_space_store` policy
(`policy_engine.py:174`), so the deterministic layer and the learned
agent agree on when to stop forwarding.

---

### Recovery Ramp After Conjunction

Links do not snap back to full rate once the angle passes 10 degrees —
the corona is still hot. AETHERIX ramps capacity back gradually:

| Phase | Sun angle | Optical | Ka-band | Behaviour |
|-------|----------:|:-------:|:-------:|-----------|
| Blackout | < 10 deg | down | down | store-only via Lagrange relays |
| Early recovery | 10-15 deg | down | degraded | X-band trickle; drain emergency backlog |
| Partial | 15-25 deg | marginal | up | Ka restores; agent forwards rank <= 1 |
| Nominal | > 25 deg | up | up | full optical + Ka; resume bulk transfers |

The drained backlog order is fixed by the QoS scheduler: EMERGENCY first,
then MISSION_CRITICAL, HIGH_PRIORITY, BULK last. Buffer occupancy returns
below 0.9 and `congestion_control` stands down.

---

### Availability Math

Reliability comes from *layered* fallback, not any single perfect link.
If the optical path (site-diversity availability 95.7%) fails, Ka-band RF
(99.0%) covers most of the remainder:

```
A_combined = 1 - (1 - A_optical)(1 - A_rf)
           = 1 - (1 - 0.957)(1 - 0.99)
           = 1 - 0.043 * 0.01   =   0.9996  ->  99.96%
```

| Layer | Availability | Residual outage |
|-------|-------------:|---------------:|
| Optical (3-site diversity) | 0.957 | 0.043 |
| Ka-band RF | 0.990 | 0.010 |
| Combined | 0.9996 | 0.0004 |

The 99.96% combined figure exceeds the 99.9% target. The residual 0.04%
is absorbed by store-and-forward — a bundle that cannot move this contact
waits for the next — so delivery availability is higher still than any
instantaneous link.

---

### Key Formulas Summary

| Formula | Equation | Used In |
|---------|----------|---------|
| Conjunction exclusion | `phase_angle < 10 deg` | `contact_windows.py:253` |
| Node operational | `status in (ACTIVE, DEGRADED)` | `node.py:69` |
| Store threshold | `link_quality < 0.3` | `rl_agent.py:83` |
| Buffer eviction | `occupancy > 0.9 AND priority >= 3` | `policy_engine.py:174` |
| Combined availability | `1 - prod(1 - A_i)` | `link_budget.md` |
