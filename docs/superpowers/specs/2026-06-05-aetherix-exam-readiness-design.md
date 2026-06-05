# AETHERIX Exam-Readiness Hardening — Design Spec

**Date:** 2026-06-05
**Author:** Claude (Opus 4.8) + Muhammad Abdullah Tariq
**Exam:** EduQual Level 6, Diploma in AI Operations — Topic 59 (oral presentation + interview), within 24h
**Status:** Approved, in implementation

## Goal

Make every Topic 59 deliverable provably addressed across **all four surfaces** — Python code (`src/`), the presentation deck (`presentation/`), the web showcase site (`docs/`), and the interview question bank (`interview_prep/`) — with no fabricated facts, then polish UI/UX on the deck and site, and ship a powerful exam-revision question bank.

## Deliverables (from `AETHERIX.md`, Topic 59)

Learning objectives: **a.** DTN protocols · **b.** Quantum comms/crypto · **c.** Space infrastructure · **d.** Orbital mechanics/link prediction · **e.** Radiation-hardened computing · **f.** Mission-critical data prioritization · **g.** Industry application · **h.** Tools.
Presentation sections (graded): Network Architecture · Quantum Comms · Infrastructure · Scenario Analysis.
Interview: 7 topic areas. Weights: Technical Depth 40% / Presentation 30% / Problem-Solving 20% / Practical 10%.

## Confirmed gaps (evidence-based)

- 🔴 **e. Radiation-hardened computing** — 0 code files, 0 slides, ~0 mentions in `docs/index.html`. Absent everywhere.
- 🟠 **f. Data prioritization** — partial (`BundlePriority` in `bundle.py`); no compression, no emergency-protocol framework, no dedicated slide, thin in UI.
- Minor: **Doppler** exists in `src/orbital/doppler.py` but is nearly invisible in the web UI (1 mention) despite being an explicit interview question.

## Work breakdown (sequenced by grading weight — Approach A)

### Phase 1 — Code gaps (Technical Depth 40%)
- `src/computing/__init__.py`, `src/computing/radiation.py`: `RadiationEnvironment`, `RadiationEffect` enum (SEU/SEL/MBU/TID/DD), `TMRVoter`, `ECCMemory` (Hamming SECDED), `MemoryScrubber`, `FDIRController` (+watchdog), `simulate_transit()` demo. Cited, honest simplified model.
- `src/routing/prioritization.py`: `DataClass` (4 spec tiers) ↔ `BundlePriority`, `Compressor` (CCSDS-121 lossless + CCSDS-122/JPEG2000 lossy ratios, modeled), `QoSScheduler` (deadline-aware, preemptive), `EmergencyProtocol`. Builds on `bundle.py`.
- `tests/test_radiation.py`, `tests/test_prioritization.py`.

### Phase 2 — Fact-check pass (feeds 40%)
- Verify all quantitative claims across slides, `index.html`, `README`, `docs/` vs exam spec + code outputs + real physics/standards.
- Output `docs/FACT_CHECK_REPORT.md` (claim / source / verdict ✅⚠️❌ / fix). Fix errors in place.
- Known finding: standardize one-way light-time to physically-correct ~3–22 min (spec overview says "4–24").

### Phase 3 — Presentation deck (Presentation 30%)
- Insert 2 slides into `generate_pptx.py` + `generate_pdf.py` (Radiation; Data Prioritization), each with a stat card from the new sims. Renumber footers, bump `total` 25→27, update Agenda. Regenerate PPTX + PDF. Add `14_*.md`/`15_*.md`; note Python is canonical.

### Phase 4 — Web showcase site (ALL sections — per user)
Both new objectives + Doppler surfacing must appear in:
- **Learn** section (2 new educational pages, matching existing style)
- **Demos** section (interactive demo(s): SEU/TMR voter and/or priority scheduler+compression)
- **Resources / Study** section (study-resource entries + references)
- **Glossary** (new terms: SEU, SEL, TID, TMR, ECC, SECDED, FDIR, scrubbing, QoS, CCSDS-121/122, preemption, safe mode, etc.)
- **Presentation** section within the site (reflect the 2 new slides)
- Register all new pages in nav; ensure dark/light + responsive.

### Phase 5 — Master question bank (Problem-Solving 20%)
- `interview_prep/question_bank/master_exam_bank.md` — by objective a–f, tiered 🟢🟡🔴⚫, model answers + "if they push further".
- `rapid_recall_flashcards.md`, `mock_exam_simulation.md` (7 interview areas, timed).
- Fact-check + extend existing `challenging`/`design_decisions`/`technical` (add e & f). Add `question_bank/README.md` index.

### Phase 6 — UI/UX polish (deck + site)
- Deck: color/font consistency, projector contrast, no overflow, consistent footers, legible diagrams, 16:9.
- Site: nav completeness, mobile responsiveness, dark/light parity, contrast/alt-text/heading order, no broken links.

### Phase 7 — Traceability + verification
- `docs/DELIVERABLES_COVERAGE.md` — matrix: every objective a–h, 4 presentation sections, 7 interview areas, 14 success-checklist items → code module + slide # + UI section + question-bank section.
- Run `./scripts/run_tests.sh`; regenerate PPTX+PDF; spot-check site; confirm matrix fully green.

## Constraints / principles
- No fabricated physics or latency numbers; cite seed/config for any simulated result (sovereign contract).
- Match existing code patterns (dataclass + references docstring + `__main__` demo) and slide/site styles.
- Incremental commits on `main` (matches established workflow; site served from `docs/`).

## Cut-line (if time runs short)
Web interactive demos and deck animation polish are cut last; rubric-heavy items (facts, code depth, deck content, Q&A) land first.
