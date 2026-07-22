# Day 33: Compression & QoS Scheduling — CCSDS 121/122 and Deadline-Aware Forwarding

## 📅 August 24, 2026

## 🎯 Learning Objective

Master how AETHERIX applies CCSDS-standardised compression (lossless 121.0-B-3 Rice coding and lossy 122.0-B-2 wavelet) to multiply effective bandwidth, and how the deadline-aware QoS scheduler plans a single finite contact window using strict priority, deadline checking, and BPv7 fragmentation.

---

## 📖 The Core Concept

### Compression: Multiplying Effective Bandwidth

On a bandwidth-starved interplanetary link, compression is not optional — it is the difference between delivering a day's science data and losing it. AETHERIX compresses every `TrafficItem` *before* it competes for the link, so the scheduler plans against *transmitted* bytes, not raw bytes.

The compression profiles are representative ratios from CCSDS standards and the data-compression literature:

| Data Type | Standard | Method | Ratio | Lossless? | Reduction |
|-----------|----------|--------|------:|:---------:|----------:|
| telemetry | **CCSDS 121.0-B-3** | Rice / adaptive | 3.0× | yes | 66.7% |
| housekeeping | ISO LZMA | LZMA | 4.0× | yes | 75.0% |
| text | RFC 8878 | zstd | 5.0× | yes | 80.0% |
| image_lossless | **CCSDS 122.0-B-2** | Wavelet lossless | 2.0× | yes | 50.0% |
| image_lossy | **CCSDS 122.0-B-2** | Wavelet lossy | 10.0× | no | 90.0% |
| video | ITU-T H.265 | HEVC-class | 50.0× | no | 98.0% |
| raw | — | none | 1.0× | yes | 0.0% |

Key formulas:
```
reduction_percent = 100 × (1 − 1/ratio)
compressed_bytes  = round(original_bytes / ratio)
tx_time           = (compressed_bytes × 8) / link_rate_bps
```

**Lossless CCSDS 121.0-B-3** (Rice/adaptive coding) is mandatory for telemetry and command data where a single flipped bit is a mission hazard. **Lossy CCSDS 122.0-B-2** (wavelet compression) is reserved for imagery and video where a 10× to 50× reduction is worth the fidelity cost. The distinction is not academic: a corrupted command byte could send a rover the wrong instruction, while a slightly degraded panorama is acceptable.

### CCSDS 121.0-B-3: Lossless Data Compression

The Rice coder (and its adaptive variant) exploits the fact that many instrument telemetry streams have a predictable low-entropy structure — successive samples are similar, so the residual after prediction is small. Rice coding maps small residuals to short codewords and large residuals to longer ones, achieving 2–4× compression on typical telemetry with *zero information loss*. The standard is specifically designed for space: low complexity, deterministic execution time, suitable for radiation-hardened processors with limited clock speed.

### CCSDS 122.0-B-2: Image Data Compression

The CCSDS wavelet image compressor uses a discrete wavelet transform (DWT) followed by bit-plane encoding. It offers both lossless (integer DWT, ~2× ratio) and lossy (floating-point DWT, up to 10×+ ratio) modes. For Mars imagery, the lossy mode is typically used for panoramas (10× reduction: an 8 GB raw image becomes 800 MB, fitting in a single contact), while lossless is reserved for scientific measurements where every pixel value matters.

### The Deadline-Aware QoS Scheduler

`QoSScheduler` plans a single finite contact window. It is **strict-priority** and **deadline-aware**: an item is delivered only if it both fits in the remaining contact time *and* completes before its own deadline.

The scheduling algorithm:

```
1. Sort items by (category.rank ASC, deadline_s ASC)
2. t = 0
3. For each item in order:
   remaining = contact_duration - t
   duration  = (item.effective_bytes × 8) / link_rate_bps
   finish    = t + duration

   if remaining ≤ 0:
       DEFER (contact ended)
   elif finish ≤ contact_duration AND finish ≤ item.deadline:
       DELIVER; t = finish
   elif finish > deadline AND duration ≤ remaining:
       DEFER (would miss deadline → let next item try)
   elif item.fragmentable:
       FRAGMENT: send partial, remainder next contact
   else:
       DEFER (NO_FRAGMENT, exceeds window)
```

### The Four Decision Branches

| Branch | Condition | Outcome |
|--------|-----------|---------|
| **Deliver** | fits window AND meets deadline | `delivered=True`, full bytes sent |
| **Defer (late)** | would fit but misses its own deadline | deferred to next contact |
| **Fragment** | does not fit, fragmentation allowed | partial send, remainder next contact |
| **Defer (full)** | NO_FRAGMENT and exceeds window | deferred to next contact |

### BPv7 Fragmentation: Why Partial Sends Are Safe

When an item is too large for the remaining contact, BPv7 fragmentation allows sending part of it now and the remainder on the next contact. The remainder carries the `IS_FRAGMENT` flag and is reassembled downstream using the offset and total-length fields in the primary block (RFC 9171 §4.5). This is what makes the scheduler aggressive about link utilization: it never wastes the last minutes of a contact window — if 60% of a large bundle fits, that 60% is sent.

The `TrafficItem` dataclass has a `fragmentable` flag (defaulting to `True`) that maps to the BPv7 `NO_FRAGMENT` processing control flag. Items with time-critical content (like emergency alerts) may set `fragmentable=False` to ensure they are sent complete or not at all.

---

## 🔬 In AETHERIX

The compression and scheduling implementation lives entirely in `src/routing/prioritization.py`:

**`CompressionProfile`** (line 77): A frozen dataclass with `name`, `standard`, `ratio`, `lossless`, and a `reduction_percent` property.

**`COMPRESSION_PROFILES`** (line 91): A dictionary keyed by data type, containing seven profiles.

**`Compressor`** (line 121): A simple class that looks up the profile for a data type and computes `compressed_bytes = int(round(size_bytes / profile.ratio))`.

**`QoSScheduler`** (line 207): The main scheduling class, initialised with `link_rate_bps` and `contact_duration_s`. The `schedule(items)` method sorts by `(category.rank, deadline_s)` and iterates, applying the four-branch decision logic. The `_tx_time(item)` helper computes `(effective_bytes × 8) / link_rate_bps`.

The demo `simulate_downlink()` (line 317) runs over a **30 Mbps optical downlink** with a **15-minute (900 s) contact window**. The capacity is `30e6 / 8 × 900 = 3,375 MB ≈ 3.3 GB`. With compression, the daily panorama (8 GB raw → 800 MB lossy) fits alongside all emergency and mission-critical data, while the 6 GB software update is deferred — link utilization approaches 100%.

---

## 📐 Key Numbers & Formulas

| Number | Value | Context |
|--------|-------|---------|
| Telemetry compression | **3.0×** (CCSDS 121.0-B-3) | Rice / adaptive, lossless |
| Lossy image compression | **10.0×** (CCSDS 122.0-B-2) | Wavelet, lossy |
| Video compression | **50.0×** (H.265) | HEVC-class, lossy |
| Demo link rate | **30 Mbps** | Optical downlink |
| Demo contact window | **900 seconds** (15 min) | Single finite contact |
| Demo link capacity | **~3.3 GB** | 30e6/8 × 900 |
| Reduction formula | `100 × (1 − 1/ratio)` | CompressionProfile |
| Tx time formula | `(bytes × 8) / link_rate_bps` | QoSScheduler._tx_time |
| Sort key | `(rank ASC, deadline ASC)` | Strict priority then deadline |

---

## 🔗 Standards & References

- [CCSDS 121.0-B-3](https://public.ccsds.org/Pubs/121x0b3.pdf) — Lossless Data Compression
- [CCSDS 122.0-B-2](https://public.ccsds.org/Pubs/122x0b2.pdf) — Image Data Compression
- [RFC 9171 §4.5](https://www.rfc-editor.org/rfc/rfc9171#section-4.5) — Bundle fragmentation
- [RFC 8878](https://www.rfc-editor.org/rfc/rfc8878) — zstd compression
- **Repo:** `src/routing/prioritization.py` — `CompressionProfile`, `QoSScheduler`
- **Repo:** `interview_prep/topic_summaries/data_prioritization.md`

---

## 💡 How the Examiner Will Probe This

**Q: "Why use CCSDS compression standards instead of general-purpose algorithms like gzip?"**

> CCSDS 121.0-B-3 and 122.0-B-2 are specifically designed for the space environment. They have deterministic execution time (critical for real-time flight software on rad-hard processors), low computational complexity (the RAD750 runs at ~200 MHz), and are heritage-proven on actual missions. Gzip/zlib would work but lacks the deterministic guarantees needed for a hard real-time scheduling system, and their variable compression time is undesirable when every millisecond of contact window matters.

**Q: "How does the scheduler decide between delivering, deferring, and fragmenting?"**

> Three conditions are checked per item. First, does it fit in the remaining window AND meet its deadline? If yes, deliver. Second, if it would fit but misses its own deadline, defer (don't waste window time on data that will be stale). Third, if it doesn't fit but is fragmentable, send a partial via BPv7 fragmentation — the remainder carries IS_FRAGMENT and is reassembled downstream. Only NO_FRAGMENT bundles that exceed the window are fully deferred.

**Q: "What's the link utilization on a typical contact?"**

> The scheduler pushes utilization toward 100% by fragmenting the last item that doesn't fully fit. In the demo scenario, emergency and mission-critical data are delivered in full, the daily panorama is fragmented (60-100% sent depending on remaining time), and only the bulk software update is fully deferred. The key insight is that fragmentation prevents wasted capacity at the end of the window.

---

## ✅ Self-Check Questions

1. Calculate the compressed size of a 40 MB telemetry bundle using CCSDS 121.0-B-3.
2. What is the reduction percentage for a 10× lossy wavelet compression?
3. Why is lossless compression mandatory for command and telemetry data?
4. Explain the four decision branches in the QoS scheduler. When is an item fragmented vs deferred?
5. How does BPv7 ensure that fragmented bundles are correctly reassembled downstream?

---

## 📂 Deep Dive Resources

- **Source code:** `src/routing/prioritization.py` — `COMPRESSION_PROFILES`, `Compressor`, `QoSScheduler`
- **Topic summary:** `interview_prep/topic_summaries/data_prioritization.md`
- **Demo:** Run `python src/routing/prioritization.py` for the constrained downlink demo
- **Standards:** CCSDS 121.0-B-3 (lossless) and 122.0-B-2 (image) Blue Books
- **Presentation script:** Slide 19 (Data Prioritization) in `docs/downloads/AETHERIX_Presentation_Script.md`
