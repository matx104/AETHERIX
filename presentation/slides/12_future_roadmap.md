# Standards Compliance & Development Roadmap

## Full Standards Compliance

### CCSDS Standards (Consultative Committee for Space Data Systems)

| Standard | Title | AETHERIX Relevance |
|----------|-------|-------------------|
| **CCSDS 734.2-B-1** | DTN Architecture | Core networking architecture |
| **CCSDS 735.1-B-1** | Bundle Protocol Specification | BPv7 implementation |
| **CCSDS 735.2-B-1** | Bundle Protocol Security (BPSec) | Bundle authentication & encryption |
| **CCSDS 734.1-B-1** | Licklider Transmission Protocol | Deep space convergence layer |
| **CCSDS 142.0-B-2** | Space Link Identification (LNIS v5) | Node addressing scheme |
| **CCSDS 141.0-B-1** | Optical Communications Physical Layer | Optical link parameters |
| **CCSDS 131.0-B-4** | TM Synchronization and Channel Coding | Error correction coding |

### IETF Standards (Internet Engineering Task Force)

| Standard | Title | AETHERIX Relevance |
|----------|-------|-------------------|
| **RFC 9171** | Bundle Protocol Version 7 | Primary protocol specification |
| **RFC 5326** | Licklider Transmission Protocol | LTP for deep space links |
| **RFC 7242** | TCP Convergence Layer Protocol | TCPCL for Earth segment |
| **RFC 7122** | UDP Convergence Layer Protocol | UDP-CL for optical ISL |
| **RFC 4838** | DTN Architecture | Architectural framework |

### Quantum & Security Standards

| Standard | Title | Status |
|----------|-------|--------|
| **ETSI QKD 004** | QKD Component Characterization | Referenced |
| **NIST FIPS 203** | ML-KEM (CRYSTALS-Kyber) | Post-quantum key encapsulation |
| **NIST FIPS 204** | ML-DSA (CRYSTALS-Dilithium) | Post-quantum digital signatures |

### Interoperability

AETHERIX is designed to interoperate with:
- **NASA DSN** — Deep Space Network ground stations
- **ION-DTN** — JPL's reference DTN implementation
- **LunaNet** — NASA's lunar communication architecture (NASA-SPEC-20230002)
- **ESA ESTRACK** — European Space Agency tracking network

---

## Development Roadmap

| Phase | Focus | Key Deliverables | Status |
|-------|-------|-----------------|--------|
| **Phase 1** | Topology & Link Budget | 5-tier architecture, optical calculator, network models | ✅ Complete |
| **Phase 2** | BPv7 + Convergence Layers | Bundle protocol, LTP/TCPCL/UDP-CL, custody transfer | ✅ Complete |
| **Phase 3** | RL Routing (Multi-Agent) | Q-learning with experience replay, federated learning, convergence detection | ✅ Complete |
| **Phase 4** | QKD Full Pipeline | BB84/E91, multi-hop repeaters with purification, CASCADE, privacy amplification | ✅ Complete |
| **Phase 5** | Simulation Engine | End-to-end simulation, policy-driven routing, metrics collection | ✅ Complete |
| **Phase 6** | Web Platform | Interactive demo site (GitHub Pages), Docker deployment | ✅ Complete |
| **Phase 7** | DQN Neural Network Upgrade | Replace Q-table with Deep Q-Network, experience replay DNN | 🔧 Remaining |
| **Phase 8** | ns-3 Hardware-in-the-Loop | Full ns-3 integration, real physics simulation, HIL testing | 🔧 Remaining |
| **Phase 9** | ION-DTN Integration | Real ION-DTN 4.1.2+ deployment, JPL Horizons ephemeris | 🔧 Remaining |

### Current Status (Phases 1-6 Complete)

- **27 source modules** implemented and tested across 5 packages (`src/`)
- **189 unit tests** with full coverage across all modules
- **12 interactive demos** (`demos/`)
- **Live web platform** with 7 simulation tabs (`docs/`)
- **64 academic references** in IEEE format (`references/`)
- **20 data visualization charts** (`visualizations/charts/`)
- **Full simulation engine** producing delivery ratio, delay, and hop count metrics

### Remaining Work

| Item | Description | Complexity |
|------|-------------|:----------:|
| **DQN upgrade** | Replace Q-table with neural network for continuous state spaces | High |
| **ns-3 integration** | Hardware-in-the-loop with ns-3.38+ network simulator | High |
| **ION-DTN deployment** | Real ION-DTN bundle agent integration and testing | Medium |
