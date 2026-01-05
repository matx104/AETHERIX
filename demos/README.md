# AETHERIX Demonstration Suite

Interactive demos for the EduQual Level 6 oral presentation on interplanetary communication networks.

## Quick Start

```bash
# Run all demos sequentially
python demos/06_integrated_demo/presentation_demo.py

# Run individual demos
python demos/01_link_budget_demo/run_demo.py
python demos/02_dtn_routing_demo/run_demo.py
python demos/03_orbital_mechanics_demo/run_demo.py
python demos/04_quantum_key_demo/run_demo.py
python demos/05_mars_mission_scenario/run_demo.py
python demos/06_integrated_demo/presentation_demo.py
```

## Demo Overview

| Demo | Duration | Purpose | Live Demo? |
|------|----------|---------|------------|
| 01_link_budget | 10s | Optical link calculations | Yes |
| 02_dtn_routing | 30s | Bundle forwarding visualization | Yes |
| 03_orbital_mechanics | 20s | Earth-Mars distance | Yes |
| 04_quantum_key | 15s | BB84 QKD simulation | Optional |
| 05_mars_mission | 45s | End-to-end scenario | Yes |
| 06_integrated | 2 min | Full presentation demo | **PRIMARY** |

## Requirements

```bash
pip install matplotlib numpy
```

## Demo Descriptions

### 1. Link Budget Demo
Calculates optical link budget for Mars-Earth communications at different distances.
- Shows FSPL, antenna gains, link margin
- Compares perihelion, average, aphelion scenarios
- **Exam relevance**: Learning objective 2d (link budget calculations)

### 2. DTN Routing Demo
Simulates bundle forwarding through the 5-tier network.
- Visualizes store-and-forward mechanism
- Shows bundle progress through network
- **Exam relevance**: Learning objective 2a (DTN protocols)

### 3. Orbital Mechanics Demo
Calculates Earth-Mars distance over the synodic period.
- One-way light time calculation
- Contact window prediction
- **Exam relevance**: Learning objective 2d (orbital propagation)

### 4. Quantum Key Demo
Simulates BB84 quantum key distribution protocol.
- Basis selection and measurement
- Key sifting and error checking
- **Exam relevance**: Learning objective 2b (QKD)

### 5. Mars Mission Scenario
Complete end-to-end communication scenario.
- Data generation at rover
- Bundle routing through network
- Delivery confirmation at MOC
- **Exam relevance**: Learning objective 2f (mission-critical data)

### 6. Integrated Demo
Combines all demos for presentation with timing.
- Runs automatically with pauses
- Professional output formatting
- **Use this for the exam presentation**

## Output Examples

Demo outputs are saved to `demos/output/` directory:
- `link_budget_report.txt`
- `routing_trace.txt`
- `orbital_plot.png`
- `qkd_results.txt`
- `mission_timeline.txt`
