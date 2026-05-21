# Space Systems & Simulation References

AETHERIX targets compliance with CCSDS standards for interoperability, uses NASA's Deep Space Network as its ground segment model, and plans to validate its routing algorithms in ns-3 or OMNeT++ network simulators with GMAT for orbital dynamics. The references below cover the CCSDS standards suite, NASA technical documents, simulation tool documentation, and additional space communication surveys.

## Most Important

| Ref | Citation | Why Critical |
|-----|----------|--------------|
| [44] | CCSDS 734.2-B-1 | DTN architecture standard — AETHERIX must comply |
| [45] | CCSDS 735.1-B-1 | Bundle protocol standard — BPv7 specification |
| [52] | NASA DSN 810-005 | DSN link design handbook — ground station parameters |
| [57] | Henderson et al., 2008 | ns-3 overview — target simulation platform |
| [60] | GMAT R2022a | Orbital dynamics simulation for contact window validation |

---

## CCSDS Standards — DTN

[44] CCSDS, "Delay-Tolerant Networking (DTN) Architecture," CCSDS 734.2-B-1, Blue Book, Nov. 2015. [Online]. Available: https://public.ccsds.org/Pubs/734x2b1.pdf

> The CCSDS recommended standard for DTN architecture in space. Aligns with RFC 4838 but adds space-specific considerations (contact scheduling, security policy, convergence layer adapters). AETHERIX claims compliance with this standard; the 5-tier topology and store-and-forward design must conform to the architecture described here.

[45] CCSDS, "Bundle Protocol Specification," CCSDS 735.1-B-1, Blue Book, Sep. 2020. [Online]. Available: https://public.ccsds.org/Pubs/735x1b1.pdf

> The CCSDS profile of the Bundle Protocol, specifying which BPv7 features are mandatory for space missions and how bundles interact with space link protocols. AETHERIX's `Bundle` class must comply with this specification's block structure and processing rules for flight qualification.

[46] CCSDS, "Bundle Protocol Security (BPSec)," CCSDS 735.2-B-1, Blue Book, Oct. 2022.

> Defines security blocks for the Bundle Protocol: integrity (signature) and confidentiality (encryption) blocks that can be added to bundles. AETHERIX's QKD-derived keys would be used with BPSec's integrity and confidentiality blocks to secure bundles in transit across the interplanetary network.

[47] CCSDS, "Licklider Transmission Protocol (LTP)," CCSDS 734.1-B-1, Blue Book, May 2015.

> The CCSDS profile of LTP for space links. Specifies how LTP segments are encapsulated in CCSDS space data link protocol frames. AETHERIX references this standard for the convergence layer between BPv7 bundles and the physical deep-space link.

## CCSDS Standards — Space Link Protocols

[48] CCSDS, "Space Link Identification—Conventions and Protocols," CCSDS 142.0-B-2, Blue Book, Nov. 2021. (LNIS v5)

> Defines the Logical Node Identification Scheme (LNIS v5) for identifying entities in the space link infrastructure. AETHERIX's endpoint ID scheme must be compatible with CCSDS space link identifiers for proper integration with the DSN and relay satellites.

[49] CCSDS, "Optical Communications Physical Layer," CCSDS 141.0-B-1, Blue Book, Aug. 2019. [Online]. Available: https://public.ccsds.org/Pubs/141x0b1.pdf

> Specifies the physical layer for optical communications in space: modulation (PPM), coding (LDPC), acquisition sequences, and signal formats. AETHERIX's optical link budget parameters assume PPM modulation as specified in this standard.

[50] CCSDS, "TM Synchronization and Channel Coding," CCSDS 131.0-B-4, Blue Book, Sep. 2023.

> Defines channel coding for telemetry links including Reed-Solomon, convolutional, turbo, and LDPC codes. AETHERIX's link budget calculator uses coding gain values derived from the performance curves specified in this standard.

## CCSDS Standards — Cross Support

[51] CCSDS, "Cross Support Service Management—Service Specification," CCSDS 910.11-B-1, Blue Book, Aug. 2018.

> Defines how different space agencies coordinate to provide mutual ground station support. Relevant to AETHERIX's multi-DSN-station topology (Goldstone, Madrid, Canberra) which relies on cross-support agreements between NASA, ESA, and other agencies for continuous Earth coverage.

## NASA Technical Documents

[52] NASA/JPL, "DSN Telecommunications Link Design Handbook," DSN No. 810-005, Rev. E, Jet Propulsion Laboratory, 2023.

> The authoritative reference for DSN link design, covering antenna gain patterns, system noise temperature, atmospheric attenuation models, and supported modulation/coding schemes. AETHERIX's DSN ground station parameters (antenna diameter, G/T, EIRP) are sourced from this handbook.

[53] J. Taylor, D. K. Lee, and S. Shambayati, "Mars Reconnaissance Orbiter Telecommunications," in *The Deep Space Network*, 2006, Article 6.

> Describes MRO's X-band and Ka-band telecommunications system design and in-flight performance. Provides real link margin data for Mars-distance communications that AETHERIX uses to validate its link budget model against operational results.

[54] NASA, "LunaNet Interoperability Specification," NASA-SPEC-20200002, Version 5, 2023.

> NASA's interoperability specification for the LunaNet lunar communication and navigation network. While focused on the Moon, LunaNet's DTN-based architecture and interoperability requirements are directly applicable to AETHERIX's Mars network design. The specification defines how multiple providers interoperate via standard protocols — a model AETHERIX should follow.

[55] C. D. Edwards and R. DePaula, "Key Telecommunications Technologies for Increasing Data Return for Future Mars Exploration," *Acta Astronautica*, vol. 61, no. 1-6, pp. 131-138, Jun.-Aug. 2007.

> See also in *Orbital Mechanics* references. Analyzes technology options for Mars data return including optical, Ka-band, and relay strategies. AETHERIX's data rate projections and technology selection are grounded in Edwards's analysis.

[56] NASA, "Mars Communication Relay Mission Concept Study," JPL CL#18-2467, Jet Propulsion Laboratory, 2018.

> See also in *Orbital Mechanics* references. Concept study for a dedicated Mars relay satellite matching AETHERIX's Mars orbital tier design.

## Simulation Tools — ns-3

[57] T. R. Henderson, M. Lacage, G. F. Riley, C. Dowell, and J. B. Kopena, "Network Simulations with the ns-3 Simulator," in *Proc. ACM SIGCOMM Demo*, 2008, p. 527.

> Introduction to the ns-3 network simulator, which AETHERIX plans to use for validating RL routing policies. ns-3's discrete-event simulation model, modular network stack, and support for custom applications make it suitable for modeling DTN bundle exchange over long-delay links.

[58] ns-3 Consortium, "ns-3 Manual," Version 3.38, 2023. [Online]. Available: https://www.nsnam.org/documentation/

> The official ns-3 documentation. AETHERIX's planned `src/simulation/` module will use ns-3.38+ APIs for creating DTN network scenarios, implementing custom Bundle/LTP protocol models, and collecting routing performance metrics (delivery ratio, delay, hop count) for RL agent training and evaluation.

## Simulation Tools — OMNeT++

[59] A. Varga and R. Hornig, "An Overview of the OMNeT++ Simulation Environment," in *Proc. 1st Int. Conf. Simulation Tools and Techniques*, 2008, Article 60.

> OMNeT++ is the alternative network simulator AETHERIX considers. Its graphical IDE, INET framework for internet protocols, and modular architecture may offer advantages for visualizing the 5-tier topology. OMNeT++ 6.0+ is the target version.

## Simulation Tools — GMAT

[60] NASA Goddard Space Flight Center, "General Mission Analysis Tool (GMAT) User Guide," Version R2022a, 2022. [Online]. Available: https://documentation.help/GMAT/

> GMAT provides high-fidelity orbital propagation for mission analysis. AETHERIX can use GMAT to generate realistic contact windows (considering J2 perturbations, third-body gravity, solar radiation pressure) that feed into the network simulator. The combination of GMAT for orbital dynamics and ns-3 for network simulation would create a complete Earth–Mars DTN simulation environment.

## CCSDS DTN Architecture (Extended)

[65] CCSDS, "Delay/Disruption-Tolerant Networking Bundle Protocol Licklider Transmission Protocol (LTP) Convergence-Layer Adapter," CCSDS 734.3-B-1, Blue Book, Apr. 2022. [Online]. Available: https://public.ccsds.org/Pubs/734x3b1.pdf

> Specifies how DTN bundles are transported over LTP in CCSDS-compliant systems, defining the mapping between BPv7 administrative records and LTP session segments. AETHERIX's LTP convergence layer follows this standard for bundling red-part (reliable) and green-part (best-effort) data into LTP blocks, with priority-aware segmentation that maps BPv7 priority classes to LTP quality-of-service markers.

## Policy-Based Routing in Space Networks

[66] G. Araniti, A. Iera, S. Pizzi, and F. Vatalaro, "QoS-Oriented Traffic Management in DTN-based Space Communication Systems," *IEEE Wireless Communications*, vol. 26, no. 2, pp. 46-53, Apr. 2019.

> Proposes policy-based traffic management for space DTN networks, where routing and scheduling decisions are governed by declarative policies that consider bundle priority, deadline, source type, and current link conditions. AETHERIX's policy engine implements a similar policy-based routing framework: rules are defined as priority-tier constraints (e.g., "P0 bundles must use lowest-latency path regardless of energy cost") and enforced at each custodian node during forwarding decisions.

[67] S. Burleigh, "Interplanetary Overlay Network (ION): An Implementation of the DTN Architecture," in *Proc. IEEE Aerospace Conf.*, 2019, pp. 1-8.

> Updated description of ION-DTN's architecture including its policy-based routing extensions, which allow mission operators to inject routing constraints (preferred paths, excluded nodes, time-window restrictions) alongside contact plans. AETHERIX's policy engine design draws on ION's approach but adds RL-learned policies that automatically adapt the policy parameters based on observed network performance.

## Additional Space Communication Surveys

[61] I. F. Akyildiz, O. B. Akan, C. Chen, J. Fang, and W. Su, "InterPlaNetary Internet: State-of-the-Art and Research Challenges," *Computer Networks*, vol. 43, no. 2, pp. 75-112, Oct. 2003.

> Comprehensive survey of the InterPlaNetary Internet vision, covering the protocol stack, routing challenges, transport issues, and security requirements. Identifies the same research gaps (adaptive routing, QoS, security) that AETHERIX addresses with RL routing and QKD.

[62] J. Wyatt, S. Burleigh, R. Jones, L. Torgerson, and S. Wissler, "Disruption Tolerant Networking Flight Validation Experiment on NASA's EPOXI Mission," in *Proc. 1st Int. Conf. Advances in Satellite and Space Communications*, 2009, pp. 187-196.

> Flight validation of DTN on the EPOXI (Deep Impact extended) mission. Demonstrates that BPv7 works in real space conditions with intermittent contacts and long delays — operational evidence that AETHERIX's architecture is practical.

[63] S. Wehner, D. Elkouss, and R. Hanson, "Quantum Internet: A Vision for the Road Ahead," *Science*, vol. 362, no. 6412, p. eaam9288, Oct. 2018. doi: 10.1126/science.aam9288

> See also in *Quantum Communication* references. Provides the quantum internet roadmap that contextualizes AETHERIX's QKD security layer.

[64] J. Caleffi, A. S. Cacciapuoti, and L. Hanzo, "Quantum Internet: From Communication to Distributed Computing!" in *Proc. 5th ACM Int. Conf. Nanoscale Computing and Communication*, 2018, Article 3.

> See also in *Quantum Communication* references. Long-term vision for quantum networking beyond key distribution.
