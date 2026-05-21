# Learning Objective 5: Radiation-Hardened Computing

## Free Online Courses & Certificates

### University Courses (Free)
- **[Reliability Engineering — edX](https://www.edx.org/courses/reliability-engineering)** — Free audit
- **[Digital Systems Design — MIT OCW](https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/)** — Error detection/correction
- **[Error Correcting Codes — MIT OCW](https://ocw.mit.edu/courses/6-451-principles-of-digital-communication-ii-spring-2005/)** — Advanced ECC

### Official Documentation (Free)
- **[CCSDS 131.0-B-4 — TM Synchronization and Channel Coding](https://public.ccsds.org/Pubs/131x0b4e2.pdf)** — Error correction for space links
- **[CCSDS 231.0-B-4 — TC Synchronization and Channel Coding](https://public.ccsds.org/Pubs/231x0b4e1.pdf)** — Uplink coding
- **[NASA Radiation Effects](https://radhome.gsfc.nasa.gov/)** — NASA radiation effects analysis
- **[ESA Space Environment](https://www.esa.int/Safety_Security/Space_Debris/Space_environment)** — ESA resources

### YouTube Videos (Free)

| Video | Channel | Duration | Why Watch |
|-------|---------|----------|-----------|
| [Hamming Codes Explained](https://www.youtube.com/watch?v=X8jsijhllOU) | 3Blue1Brown | ~15 min | Best ECC visual explanation |
| [Reed-Solomon Error Correction](https://www.youtube.com/results?search_query=reed+solomon+code+explained) | Various | ~15 min | Used in CCSDS |
| [Radiation Effects on Electronics](https://www.youtube.com/results?search_query=radiation+effects+electronics+space) | Various | ~15 min | SEU, SEL, TID |
| [Triple Modular Redundancy](https://www.youtube.com/results?search_query=triple+modular+redundancy+explained) | Various | ~10 min | Fault tolerance technique |
| [How Spacecraft Survive Radiation](https://www.youtube.com/results?search_query=spacecraft+radiation+hardening) | Various | ~15 min | Practical measures |

### Key Concepts to Master

1. **Single-Event Upsets (SEU)** — Radiation flipping bits in memory/registers
2. **Error Detection & Correction** — Hamming codes, Reed-Solomon, LDPC (CCSDS 131.0-B-4)
3. **Triple Modular Redundancy (TMR)** — 3 copies, majority vote
4. **Total Ionizing Dose (TID)** — Cumulative radiation damage
5. **Shielding** — Physical protection, but adds mass
6. **Watchdog Timers** — Detect and recover from hangs
7. **CCSDS Channel Coding** — BCH, Reed-Solomon, Turbo codes, LDPC

### Practice Questions

1. What is a single-event upset? How does AETHERIX handle it? (30 seconds)
2. Compare Hamming codes and Reed-Solomon for space applications (1 minute)
3. Explain triple modular redundancy (30 seconds)
4. What error correction does CCSDS 131.0-B-4 specify? (30 seconds)
