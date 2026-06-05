# AETHERIX Fact-Check Report

**Date:** 2026-06-05 · **Scope:** standards references, physics/quantitative claims, repo metrics across slides, `docs/index.html`, `README.md`, `references/`, agent-config files, and code.

Verdict legend: ✅ correct · ⚠️ imprecise/standardized · ❌ wrong (fixed) · 📌 noted

---

## 1. Standards references (HIGH IMPACT)

The repository carried a **systematically mislabeled CCSDS standards table**, repeated 100+ times. Titles were verified against the official **public.ccsds.org** PDFs and **rfc-editor.org**.

| Reference | Claimed (wrong) | Verified correct title | Verdict |
|-----------|-----------------|------------------------|---------|
| CCSDS 734.2-B-1 | "DTN Architecture" | **CCSDS Bundle Protocol Specification** | ❌→fixed |
| CCSDS 735.1-B-1 | "Bundle Protocol" | **Asynchronous Message Service (AMS)** — *not* BP | ❌→removed |
| CCSDS 735.2-B-1 | "BPSec" | **does not exist**; BPSec is IETF **RFC 9172** | ❌→fixed |
| CCSDS 142.0-B-2 | "Space Link IDs / LNIS v5" | **142.0-B-1 = Optical Comms Coding & Sync**; doc as titled does not exist | ❌→fixed |
| CCSDS 734.3-B-1 | "LTP Convergence-Layer Adapter" | **Schedule-Aware Bundle Routing (SABR)** | ❌→fixed |
| CCSDS 141.0-B-1 | "Optical Communications" | Optical Communications Physical Layer | ✅ |
| CCSDS 734.1-B-1 | "LTP for CCSDS" | Licklider Transmission Protocol (LTP) for CCSDS | ✅ |
| CCSDS 401.0-B-30 | "RF & Modulation" | Radio Frequency and Modulation Systems | ✅ |
| CCSDS 121.0-B-3 | "Lossless Compression" | Lossless Data Compression | ✅ |
| CCSDS 122.0-B-2 | "Image Compression" | Image Data Compression | ✅ |
| RFC 9171 | "BPv7" | Bundle Protocol Version 7 | ✅ |
| RFC 4838 | (under-used) | Delay-Tolerant Networking Architecture | ✅ |
| RFC 5326 | "LTP" | Licklider Transmission Protocol — Specification | ✅ |
| RFC 9172 / 9173 | — | BPSec / Default Security Contexts for BPSec | ✅ |
| RFC 7242 / 9174 | "TCPCL" | DTN TCP Convergence-Layer (v3 / v4) | ✅ |
| RFC 7122 | "UDPCL" | Datagram Convergence Layers for DTN BP & LTP | ✅ |

**Corrected standards mapping now used everywhere:**
- **DTN Architecture** → RFC 4838 (IETF) + CCSDS 734.0-G-1 (Green Book rationale)
- **Bundle Protocol** → RFC 9171 (BPv7) + CCSDS 734.2-B-1 (CCSDS profile)
- **BPSec (security)** → RFC 9172 (+ RFC 9173 contexts)
- **Contact-graph routing baseline** → CCSDS 734.3-B-1 (SABR) — the static router AETHERIX's RL agent replaces
- **Optical** → CCSDS 141.0-B-1 (physical) + 142.0-B-1 (coding & sync)
- **LTP** → RFC 5326 + CCSDS 734.1-B-1

**Files fixed:** `references/standards/ccsds_standards.md` (canonical, rewritten), `presentation/generate_pptx.py`, `presentation/generate_pdf.py`, `README.md`, `CLAUDE.md` (+ mirrors `GEMINI.md`, `.cursorrules`, `.windsurfrules`), `AGENTS.md`, `.github/copilot-instructions.md`, `docs/index.html` (badges, prose, protocol-stack table).

**Sources:** [CCSDS 734.2-B-1 Bundle Protocol](https://ccsds.org/Pubs/734x2b1.pdf) · [CCSDS 734.3-B-1 SABR](https://ccsds.org/Pubs/734x3b1.pdf) · [CCSDS 735.1-B-1 AMS](https://ccsds.org/Pubs/735x1b1.pdf) · [CCSDS 734.0-G-1 DTN Rationale](https://ccsds.org/Pubs/734x0g1e1.pdf) · [CCSDS 141.0-B-1 Optical PHY](https://ccsds.org/Pubs/141x0b1.pdf) · [CCSDS 142.0-B-1 Optical Coding](https://ccsds.org/Pubs/142x0b1.pdf) · [RFC 9172 BPSec](https://www.rfc-editor.org/rfc/rfc9172) · [RFC 4838 DTN Arch](https://www.rfc-editor.org/rfc/rfc4838)

---

## 2. Physics & quantitative claims

| Claim | Repo value | Verified | Verdict |
|-------|-----------|----------|---------|
| Earth–Mars min distance | 54.6M km | 54.6M km (closest possible) | ✅ |
| Earth–Mars avg distance | ~225M km | ~225M km (≈1.5 AU mean separation) | ✅ |
| Earth–Mars max distance | 401M km **and** 390M km | ~401M km (aphelion, opposite sides) | ⚠️📌 |
| One-way light time | mostly 3–22 min; stray "4–24" | 54.6M/c=3.0 min, 401M/c=22.3 min → **3–22 min** | ⚠️→standardized |
| Round-trip light time | 6–44 min | 2×(3–22) = 6–44.6 min | ✅ |
| Synodic period | ~780 d / 779 d / 26 months | 779.9 days ≈ 25.6 months | ✅ |
| QBER security threshold | 11% | BB84 ≈ 11% one-way | ✅ |
| Optical wavelength | 1550 nm | telecom/deep-space optical standard | ✅ |
| Optical data rate | 2–200 Mbps | defensible vs NASA DSOC (267 Mbps @ ~0.3 AU, 2023–24) | ✅ |
| LEO laser constellation | 48 satellites | internal design choice, used consistently | ✅ |
| DSN complexes | Goldstone, Madrid, Canberra | correct | ✅ |

**Actions:**
- ⚠️ **Light time** standardized to **3–22 min one-way** in the student's materials (`README.md`, `docs/topology/`, `docs/QUICK_REFERENCE.md`, `presentation/slides/05`). The exam brief `AETHERIX.md` retains its given "4–24 min" wording (it is the examiner's source document, left untouched) — the physically-correct one-way range is 3.0–22.3 min.
- 📌 **Max distance 390 vs 401M km:** both appear. ~401M km is the true maximum (both planets at aphelion, opposite sides of the Sun, ≈2.68 AU). The link-budget code conservatively uses 390M km as its "maximum" preset. Left as-is to keep computed link-budget figures self-consistent; cite **~401M km** as the headline maximum in the presentation.

---

## 3. Repository metrics

| Metric | Stale value | Corrected |
|--------|-------------|-----------|
| Unit tests | 149 | **189** (149 + 40 new for radiation & prioritization) |
| Test files | 10 | **12** |
| Python modules | 27 | **30** |

Updated in `README.md` badges + tables and `docs/index.html` info bubble. Module/test tables now include `src/computing/radiation.py`, `src/routing/prioritization.py`, `tests/test_radiation.py`, `tests/test_prioritization.py`.

---

## 4. New-module modelling honesty (objectives e & f)

Both new modules use **transparent analytic models with cited order-of-magnitude figures**, not fabricated device qualifications (per the project's sovereign contract — no mocked physics):
- `radiation.py`: SEU rate = flux × per-bit cross-section; residual error budget includes **MBU + bit-interleaving** (the realistic dominant term), giving ~200× protection rather than an indefensible "millions×". TMR gain quoted at a fixed, documented p=1e-4/op. Stochastic demo seeded (42).
- `prioritization.py`: compression ratios are representative CCSDS-121/122-class figures applied analytically (no bytes actually compressed); scheduler is deterministic; BPv7 fragmentation modelled.

---

## 5. Residual / not changed (noted, low risk)

- 📌 Decorative duplicate standards badges may remain adjacent in `index.html` after the 735.1→734.2 sweep; cosmetic only, addressed in UI polish.
- 📌 "Grade A+" self-assessment removed from the index info-bubble (unverifiable claim).
- 📌 Exam brief `AETHERIX.md` left verbatim as the authoritative source document.
