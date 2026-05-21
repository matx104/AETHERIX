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
| **Phase 2** | BPv7 + RL Routing | Bundle protocol, Q-learning agent, contact windows | ✅ Complete (demo) |
| **Phase 3** | QKD Integration | BB84/E91 simulation, quantum repeater model | ✅ Complete (demo) |
| **Phase 4** | Web Platform | Interactive demo site (GitHub Pages), Docker deployment | ✅ Complete |
| **Phase 5** | Simulation & Validation | ns-3/OMNeT++ integration, full scenario testing | 📅 Planned |
| **Phase 6** | Production Hardening | DQN replacement, ION-DTN integration, real ephemeris | 📅 Future |
| **Phase 7** | Deployment | Hardware-in-the-loop testing, mission integration | 📅 Future |

### Current Status (Phases 1-4 Complete)

- **5 Python modules** implemented and tested (`src/`)
- **6 interactive demos** (`demos/`)
- **Live web platform** with 7 simulation tabs (`docs/`)
- **64 academic references** in IEEE format (`references/`)
- **20 data visualization charts** (`visualizations/charts/`)
- **Full test suite** started (`tests/`)
