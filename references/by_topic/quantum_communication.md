# Quantum Communication & Cryptography References

AETHERIX uses Quantum Key Distribution (QKD) to establish information-theoretically secure keys between Earth and Mars nodes, protecting bundle payload integrity against adversaries with quantum computers. The references below cover the foundational QKD protocols (BB84, E91), satellite-based demonstrations, quantum repeaters for deep-space ranges, and post-quantum cryptographic alternatives.

## Most Important

| Ref | Citation | Why Critical |
|-----|----------|--------------|
| [12] | Bennett & Brassard, 1984 | Original BB84 protocol — basis for AETHERIX's QKD implementation |
| [13] | Ekert, 1991 | E91 entanglement-based protocol — implemented in `src/security/qkd.py` |
| [15] | Liao et al., 2017 | First satellite-to-ground QKD — proves space QKD is feasible |
| [19] | Briegel et al., 1998 | Quantum repeater concept — needed for Earth–Mars distances |
| [22] | NIST PQC, 2024 | Post-quantum standards — fallback/complement to QKD |

---

## Foundational QKD Papers

[12] C. H. Bennett and G. Brassard, "Quantum Cryptography: Public Key Distribution and Coin Tossing," in *Proc. IEEE Int. Conf. Computers, Systems and Signal Processing*, Bangalore, India, 1984, pp. 175-179.

> The original BB84 quantum key distribution protocol. Uses two conjugate bases (rectilinear and diagonal) for encoding single photons, with eavesdropping detected via the quantum bit error rate (QBER). AETHERIX's `BB84Protocol` class in `src/security/qkd.py` implements this protocol with QBER < 11% as the security threshold.

[13] A. K. Ekert, "Quantum Cryptography Based on Bell's Theorem," *Physical Review Letters*, vol. 67, no. 6, pp. 661-663, Aug. 1991. doi: 10.1103/PhysRevLett.67.661

> Entanglement-based QKD using Einstein-Podolsky-Rosen (EPR) pairs. Security is verified through Bell inequality violations rather than basis comparison. AETHERIX's `E91Protocol` class implements this approach, which is more naturally suited to satellite-relayed quantum links where entangled photon sources are already on orbit.

[14] N. Gisin, G. Ribordy, W. Tittel, and H. Zbinden, "Quantum Cryptography," *Reviews of Modern Physics*, vol. 74, no. 1, pp. 145-195, Mar. 2002. doi: 10.1103/RevModPhys.74.145

> Comprehensive review of quantum cryptography theory and experiment as of 2002. Covers BB84, E91, B92, and continuous-variable protocols, plus practical implementation challenges (detector efficiency, dark counts, photon source imperfections). Essential background for AETHERIX's QKD module design.

## Satellite QKD

[15] S.-K. Liao et al., "Satellite-to-Ground Quantum Key Distribution," *Nature*, vol. 549, no. 7670, pp. 43-47, Sep. 2017. doi: 10.1038/nature23655

> Reports the first satellite-to-ground QKD demonstration using China's Micius satellite, achieving kilohertz-rate key generation over 1,200 km. This result directly validates AETHERIX's assumption that satellite-based QKD can support an interplanetary security layer. The link budget analysis (photon loss, detector performance) informs AETHERIX's optical link model.

[16] J. Yin et al., "Satellite-Based Entanglement Distribution Over 1200 Kilometers," *Science*, vol. 356, no. 6343, pp. 1140-1144, Jun. 2017. doi: 10.1126/science.aan3211

> Demonstrates entanglement distribution from the Micius satellite to two ground stations separated by 1,200 km. Proves that the E91-style entanglement protocol AETHERIX implements can operate through the atmosphere. The measured Bell parameter violation confirms security against eavesdropping at satellite scales.

[17] R. Bedington, J. M. Arrazola, and A. Ling, "Progress in Satellite Quantum Key Distribution," *npj Quantum Information*, vol. 3, no. 1, p. 30, Aug. 2017. doi: 10.1038/s41534-017-0031-5

> Survey of satellite QKD approaches: downlink, uplink, and entanglement-based configurations. Analyzes the trade-offs that inform AETHERIX's design choice of a downlink configuration (source on satellite, detectors on ground) for the Earth orbital tier.

[18] S.-K. Liao et al., "Satellite-Relayed Intercontinental Quantum Network," *Physical Review Letters*, vol. 120, no. 3, p. 030501, Jan. 2018. doi: 10.1103/PhysRevLett.120.030501

> Extends the Micius results to a satellite-relayed network connecting three ground stations across continents via trusted-node QKD. Demonstrates the multi-hop quantum key relay architecture that AETHERIX's `QuantumRepeater` class models for extending QKD beyond single-link ranges.

## Quantum Repeaters

[19] H.-J. Briegel, W. Dür, J. I. Cirac, and P. Zoller, "Quantum Repeaters: The Role of Imperfect Local Operations in Quantum Communication," *Physical Review Letters*, vol. 81, no. 26, pp. 5932-5935, Dec. 1998.

> Introduces the quantum repeater concept: purifying entanglement at intermediate nodes to extend quantum communication range. For Earth–Mars distances (54.6M–401M km), direct photon transmission is infeasible — AETHERIX's `QuantumRepeater` with entanglement swapping is the theoretical path to deep-space QKD.

[20] L.-M. Duan, M. D. Lukin, J. I. Cirac, and P. Zoller, "Long-Distance Quantum Communication with Atomic Ensembles and Linear Optics," *Nature*, vol. 414, no. 6862, pp. 413-418, Nov. 2001.

> Proposes a practical quantum repeater using atomic ensembles and linear optics (DLCZ protocol). AETHERIX's quantum repeater simulation draws on this architecture for modeling entanglement purification and swapping operations at relay nodes positioned at Lagrange points (ES-L4, ES-L5).

## Post-Quantum Cryptography

[21] D. J. Bernstein and T. Lange, "Post-Quantum Cryptography," *Nature*, vol. 549, no. 7671, pp. 188-194, Sep. 2017. doi: 10.1038/nature23461

> Overview of cryptographic algorithms believed to be secure against quantum computers (lattice-based, code-based, multivariate, hash-based). AETHERIX uses PQC as a complement to QKD: PQC provides computational security during conjunction blackouts when QKD links are unavailable.

[22] NIST, "Post-Quantum Cryptography Standardization," National Institute of Standards and Technology, 2024. [Online]. Available: https://csrc.nist.gov/projects/post-quantum-cryptography

> NIST's official PQC standardization process, selecting CRYSTALS-Kyber (ML-KEM) for key encapsulation and CRYSTALS-Dilithium (ML-DSA) for digital signatures. AETHERIX should adopt these NIST-selected algorithms for hybrid classical-quantum security in production deployments.

## Quantum Networking

[63] S. Wehner, D. Elkouss, and R. Hanson, "Quantum Internet: A Vision for the Road Ahead," *Science*, vol. 362, no. 6412, p. eaam9288, Oct. 2018. doi: 10.1126/science.aam9288

> Roadmap for the quantum internet from near-term (QKD) to long-term (quantum computing networks). Places AETHERIX's QKD work at the first stage of quantum network maturity, with quantum repeaters representing the second stage.

[64] J. Caleffi, A. S. Cacciapuoti, and L. Hanzo, "Quantum Internet: From Communication to Distributed Computing!" in *Proc. 5th ACM Int. Conf. Nanoscale Computing and Communication*, 2018, Article 3.

> Surveys quantum networking protocols beyond QKD, including quantum teleportation and distributed quantum computation. Provides the longer-term vision for AETHERIX's security layer: moving from key distribution to quantum-authenticated bundle custody transfer.
