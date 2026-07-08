# Mission Data Prioritization

## Topic Summary

### The Problem: Starved Downlinks

A Mars-to-Earth optical contact may last minutes and offer tens of Mbps,
while a single day's panorama is gigabytes. When bandwidth is intermittent
and dwarfed by demand, the question is not *how fast* to send data but
*what to send, in what order, over a finite window*. AETHERIX answers this
with a four-tier data classification, CCSDS-class compression, and a
deadline-aware QoS scheduler with preemption. All in
`src/routing/prioritization.py`.

---

### Four-Tier Mission Data Classification

Each `DataCategory` maps onto a BPv7 `BundlePriority` so the
classification flows through the existing bundle/forwarding machinery
unchanged. Rank 0 is most urgent.

| Tier | `DataCategory` | Examples | Maps to `BundlePriority` | Rank | Preemptive? |
|-----:|----------------|----------|--------------------------|-----:|:-----------:|
| 1 | EMERGENCY_SAFETY | Health telemetry, collision avoidance, faults | EMERGENCY (0) | 0 | **yes** |
| 2 | MISSION_CRITICAL | Command acks, time-sensitive science events | HIGH_SCIENCE (1) | 1 | no |
| 3 | HIGH_PRIORITY | Routine telemetry, scheduled observations | STANDARD (2) | 2 | no |
| 4 | LOW_PRIORITY | Housekeeping logs, bulk transfers, SW images | BULK (4) | 4 | no |

> **Priority space note**: BPv7 defines five `BundlePriority` levels
> (EMERGENCY=0 ... BULK=4). The four mission tiers use four of them;
> HOUSEKEEPING (3) is reserved for the underlying bundle layer.

Rank ordering is strict: an item with rank 0 is always attempted before
rank 1 regardless of arrival time, because the cost of a missed safety
alert is catastrophic while bulk data can wait a contact.

---

### Compression (CCSDS 121.0-B-3 / 122.0-B-2)

Every `TrafficItem` is compressed before it competes for the link, so the
scheduler plans against *transmitted* bytes, not raw bytes. Ratios are
representative figures from the CCSDS standards applied analytically.

| Data type | Standard | Method | Ratio | Lossless? | Reduction |
|-----------|----------|--------|------:|:---------:|----------:|
| telemetry | CCSDS 121.0-B-3 | Rice / adaptive | 3.0x | yes | 66.7% |
| housekeeping | ISO LZMA | LZMA | 4.0x | yes | 75.0% |
| text | RFC 8878 | zstd | 5.0x | yes | 80.0% |
| image_lossless | CCSDS 122.0-B-2 | Wavelet lossless | 2.0x | yes | 50.0% |
| image_lossy | CCSDS 122.0-B-2 | Wavelet lossy | 10.0x | no | 90.0% |
| video | ITU-T H.265 | HEVC-class | 50.0x | no | 98.0% |
| raw | - | none | 1.0x | yes | 0.0% |

```
reduction_percent = 100 * (1 - 1 / ratio)
compressed_bytes  = round(original_bytes / ratio)
tx_time           = (compressed_bytes * 8) / link_rate_bps
```

Lossless CCSDS 121.0-B-3 is mandatory for telemetry and command data where
a single flipped bit is a mission hazard; lossy CCSDS 122.0-B-2 wavelet
compression is reserved for imagery and video where a 10x-50x reduction is
worth the fidelity cost.

---

### Deadline-Aware QoS Scheduler

`QoSScheduler` plans a single finite contact window. It is strict-priority
and deadline-aware: an item is delivered only if it both fits in the
remaining contact time *and* completes before its own deadline.

| Parameter | Demo value | Meaning |
|-----------|-----------:|---------|
| `link_rate_bps` | 30e6 | 30 Mbps optical downlink |
| `contact_duration_s` | 900 | 15-minute contact window |

**Scheduling algorithm:**

```
schedule(items):
    ordered <- sort items by (category.rank ASC, deadline_s ASC)
    t <- 0
    for item in ordered:
        remaining <- contact_duration_s - t
        dur       <- (item.effective_bytes * 8) / link_rate_bps
        finish    <- t + dur
        if remaining <= 0:
            defer(item, "contact ended")
        elif finish <= contact_duration_s and finish <= item.deadline_s:
            deliver(item); t <- finish
        elif finish > item.deadline_s and dur <= remaining:
            defer(item, "would miss deadline")
        elif item.fragmentable:
            send partial (BPv7 fragmentation); t <- contact_duration_s
        else:
            defer(item, "NO_FRAGMENT, exceeds window")
```

| Decision branch | Condition | Outcome |
|-----------------|-----------|---------|
| Deliver | fits window AND meets deadline | `delivered=True`, full bytes sent |
| Defer (late) | would fit but misses its own deadline | deferred to next contact |
| Fragment | does not fit, BPv7 fragmentation clear | partial send, remainder next contact |
| Defer (full) | NO_FRAGMENT and exceeds window | deferred to next contact |

BPv7 fragmentation (RFC 9171) is what makes partial sends safe: the
remainder carries `IS_FRAGMENT` and is reassembled downstream.

---

### Emergency Protocol and Preemption

`EmergencyProtocol` handles the case where a safety-critical bundle
arrives mid-transfer. Emergency traffic is the only tier flagged
`preemptive=True`. An emergency preempts the in-progress item, transmits
via a low-rate direct-to-Earth backup link, then resumes normal scheduling.

| Step | Action | Rate / effect |
|------|--------|---------------|
| 1 | Compare ranks | if in_progress.rank <= emergency.rank, do not preempt |
| 2 | Preempt | suspend current transfer, log the swap |
| 3 | Send emergency | direct-to-Earth backup at 10 kbps |
| 4 | Resume | original item continues after the emergency clears |

```
preempt(in_progress, emergency):
    if in_progress.rank <= emergency.rank: return NO_PREEMPTION
    tx_s <- (emergency.effective_bytes * 8) / direct_to_earth_rate_bps
    emergency sent via 10 kbps backup in tx_s seconds
    resume in_progress after emergency clears
```

The 10 kbps backup (`direct_to_earth_rate_bps = 1.0e4`) is deliberately a
*thin but reliable* path — far below the 30 Mbps optical downlink, but it
closes even when the primary link is down. An emergency alert is small
(bytes, not megabytes), so the low rate still meets its seconds-level
deadline.

---

### Putting It Together: Constrained Mars Downlink

The demo scenario (`simulate_downlink`, seed 42) mixes all four tiers over
a single 900 s / 30 Mbps contact:

| Item | Category | Raw size | Compressed | Deadline |
|------|----------|---------:|-----------:|---------:|
| rover-health-telemetry | EMERGENCY_SAFETY | 2 MB | 0.7 MB | 60 s |
| command-acknowledgements | MISSION_CRITICAL | 5 MB | 1.7 MB | 120 s |
| seismic-event-capture | MISSION_CRITICAL | 40 MB | 13 MB | 300 s |
| daily-panorama-imagery | HIGH_PRIORITY | 8 GB | 0.8 GB | 900 s |
| housekeeping-logs | LOW_PRIORITY | 400 MB | 100 MB | 1200 s |
| software-update-archive | LOW_PRIORITY | 6 GB | 6 GB | 1800 s |

The scheduler delivers emergency and mission-critical items in full,
fragments the panorama across contacts, and defers the bulk software
update — exactly the behaviour a bandwidth-starved mission needs.

---

### Key Formulas Summary

| Formula | Equation | Used In |
|---------|----------|---------|
| Reduction % | `100 * (1 - 1/ratio)` | `CompressionProfile` |
| Compressed bytes | `round(original / ratio)` | `Compressor.compress` |
| Tx time | `(effective_bytes * 8) / link_rate_bps` | `QoSScheduler._tx_time` |
| Sort key | `(category.rank, deadline_s)` | `QoSScheduler.schedule` |
| Emergency tx time | `(bytes * 8) / 1.0e4` | `EmergencyProtocol.preempt` |
