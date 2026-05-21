# AETHERIX Study Resources — Master Index

## How to Use This Directory

Each subdirectory maps to one of the **6 learning objectives** from your EduQual Level 6 oral presentation, plus two additional directories for courses/certificates and tools/software.

**Study order (recommended):**
1. Start with `01_dtn_protocols/` — this is the foundation, the most examinable topic
2. Then `02_quantum_communication/` — BB84 is guaranteed to come up
3. Then `04_orbital_mechanics/` — they'll ask you to calculate light-time
4. Then `03_space_infrastructure/` — DSN, Lagrange points, tiers
5. Then `06_data_prioritization/` — routing algorithms, priority classes
6. Then `05_radiation_computing/` — shortest topic, but know error correction basics
7. Finally `certificates_and_courses/` — do these alongside the topics

---

## Directory Structure

```
study_resources/
├── 01_dtn_protocols/          # LO1: Delay-Tolerant Networking
│   ├── README.md              # Curated resource list
│   └── deep_dive_notes.md     # Study notes for exam
├── 02_quantum_communication/  # LO2: Quantum Communication
│   ├── README.md
│   └── deep_dive_notes.md
├── 03_space_infrastructure/   # LO3: Space-Based Infrastructure
│   ├── README.md
│   └── deep_dive_notes.md
├── 04_orbital_mechanics/      # LO4: Orbital Mechanics
│   ├── README.md
│   └── deep_dive_notes.md
├── 05_radiation_computing/    # LO5: Radiation-Hardened Computing
│   ├── README.md
│   └── deep_dive_notes.md
├── 06_data_prioritization/    # LO6: Mission-Critical Data Prioritization
│   ├── README.md
│   └── deep_dive_notes.md
├── certificates_and_courses/  # Free courses, certs, MOOCs
│   └── README.md
└── tools_and_software/        # Software to install and practice with
    └── README.md
```

---

## Quick-Start Study Plan (2-Week Schedule)

### Week 1: Core Technical Depth

| Day | Focus | Activity |
|:---:|-------|----------|
| 1 | DTN Fundamentals | Read RFC 9171, watch "Delay Tolerant Networking" by JPL |
| 2 | Bundle Protocol | Read CCSDS 735.1-B-1, study store-and-forward diagrams |
| 3 | QKD Basics | Watch "Quantum Cryptography in 20 minutes", study BB84 steps |
| 4 | QKD Deep Dive | Read Bennett-Brassard 1984 paper, understand QBER threshold |
| 5 | Orbital Mechanics | Watch orbital mechanics playlist, practice light-time calculations |
| 6 | Space Infrastructure | Study DSN architecture, Lagrange point physics |
| 7 | Review + Practice | Run through all 50 technical questions in interview_prep/ |

### Week 2: Integration & Presentation

| Day | Focus | Activity |
|:---:|-------|----------|
| 8 | RL Routing | Watch Sutton & Barto lecture series (RL basics), study reward function |
| 9 | Data Prioritization | Study BPv7 priority classes, routing algorithms |
| 10 | Radiation & Error Correction | Study Hamming codes, Reed-Solomon, CCSDS coding |
| 11 | Standards Deep Dive | Read CCSDS Blue Books, understand compliance |
| 12 | Presentation Practice | Full 18-min run-through with speaker notes |
| 13 | Mock Interview | Practice with question bank, time your answers |
| 14 | Final Review | Review cheat sheets, key numbers, demo rehearsal |

---

## Exam Day Quick Reference

**The 10 numbers you MUST know:**

| # | Value | Context |
|---|-------|---------|
| 1 | 299,792 km/s | Speed of light (c) |
| 2 | 54.6 M km | Mars minimum distance (3 min light-time) |
| 3 | 401 M km | Mars maximum distance (22 min light-time) |
| 4 | 780 days | Earth-Mars synodic period |
| 5 | 1550 nm | Optical wavelength |
| 6 | 11% | QBER security threshold |
| 7 | 17,032 km | Areostationary orbit altitude |
| 8 | 232 | Total network nodes |
| 9 | 5 W | Typical laser power |
| 10 | 0.5-6 Mbps | Current Mars data rates |

**The 5 standards you MUST cite:**

| # | Standard | Context |
|---|----------|---------|
| 1 | RFC 9171 | Bundle Protocol Version 7 |
| 2 | CCSDS 734.2-B-1 | DTN Architecture |
| 3 | CCSDS 735.1-B-1 | Bundle Protocol Specification |
| 4 | CCSDS 141.0-B-1 | Optical Communications |
| 5 | RFC 5326 | Licklider Transmission Protocol |
