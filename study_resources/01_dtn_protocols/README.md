# Learning Objective 1: Delay-Tolerant Networking & Bundle Protocol

## Free Online Courses & Certificates

### University Courses (Free)
- **[Delay-Tolerant Networking — NASA/JPL](https://www.youtube.com/results?search_query=delay+tolerant+networking+JPL)** — Search for JPL DTN seminars on YouTube
- **[Computer Networking — Stanford (Coursera)](https://www.coursera.org/course/comnetwork)** — Foundation in networking concepts; free to audit
- **[Introduction to Computer Networking — Stanford (CS144)](https://cs144.github.io/)** — Full course materials, free
- **[Computer Communications — University of Colorado (Coursera)](https://www.coursera.org/specializations/computer-communications)** — Free audit mode

### Official Documentation (Free)
- **[RFC 9171 — Bundle Protocol Version 7](https://www.rfc-editor.org/rfc/rfc9171)** — THE primary document. Read sections 3-5 in full.
- **[RFC 4838 — DTN Architecture](https://www.rfc-editor.org/rfc/rfc4838)** — The foundational architecture RFC
- **[RFC 5326 — Licklider Transmission Protocol](https://www.rfc-editor.org/rfc/rfc5326)** — LTP specification
- **[RFC 9172 — Bundle Protocol Security](https://www.rfc-editor.org/rfc/rfc9172)** — BPSec specification
- **[CCSDS 734.2-B-1 — DTN Architecture](https://public.ccsds.org/Pubs/734x2b1.pdf)** — CCSDS Blue Book (free download)
- **[CCSDS 735.1-B-1 — Bundle Protocol](https://public.ccsds.org/Pubs/735x1b1.pdf)** — CCSDS specification
- **[CCSDS 734.1-B-1 — LTP](https://public.ccsds.org/Pubs/734x1b1e2.pdf)** — LTP over CCSDS

### YouTube Videos (Free)

#### Must-Watch (DTN Specific)
| Video | Channel | Duration | Why Watch |
|-------|---------|----------|-----------|
| [Delay Tolerant Networking: An Introduction](https://www.youtube.com/watch?v=W2PC3LIg7WI) | Various | ~30 min | Good overview of DTN concepts |
| [NASA DTN Overview](https://www.youtube.com/results?search_query=nasa+delay+tolerant+networking) | NASA | ~20 min | Official NASA perspective |
| [InterPlanetary File System (IPFS) concepts](https://www.youtube.com/watch?v=5Uj6uR3fp-U) | Various | ~15 min | Content-addressed storage concepts |
| [ION-DTN Tutorial](https://www.youtube.com/results?search_query=ION-DTN+tutorial) | Various | ~45 min | Practical DTN implementation |
| [Bundle Protocol v7 Explained](https://www.youtube.com/results?search_query=bundle+protocol+v7+rfc+9171) | Various | ~20 min | RFC walkthrough |

#### Networking Foundations
| Video | Channel | Duration | Why Watch |
|-------|---------|----------|-----------|
| [How TCP/IP Works](https://www.youtube.com/watch?v=3b_TAYtzuho) | NetworkChuck | ~15 min | Contrast with DTN |
| [OSI Model Explained](https://www.youtube.com/watch?v=LANW3QgAO5Y) | PowerCert | ~15 min | Layer understanding |
| [Store and Forward Networking](https://www.youtube.com/results?search_query=store+and+forward+networking+explained) | Various | ~10 min | Core DTN concept |

### Academic Papers (Free / Open Access)

| Paper | Authors | Year | Link | Priority |
|-------|---------|------|------|:--------:|
| "A Delay-Tolerant Network Architecture for Challenged Internets" | K. Fall | 2003 | [ACM DL](https://dl.acm.org/doi/10.1145/863955.863960) | MUST READ |
| "Delay-Tolerant Networking: An Approach to Interplanetary Internet" | S. Burleigh et al. | 2003 | [IEEE](https://doi.org/10.1109/MCOM.2003.1204759) | MUST READ |
| "Contact Graph Routing in DTN Space Networks" | G. Araniti et al. | 2015 | [IEEE](https://doi.org/10.1109/MCOM.2015.7060488) | HIGH |
| "Routing in the Space Internet: A Contact Graph Routing Tutorial" | J. Fraire et al. | 2021 | [ScienceDirect](https://doi.org/10.1016/j.jnca.2020.102884) | HIGH |
| "Epidemic Routing for Partially-Connected Ad Hoc Networks" | A. Vahdat, D. Becker | 2000 | [ Duke TR](https://www.cs.duke.edu/~vahdat/CR/epidemic.pdf) | MEDIUM |

### Blogs & Articles (Free)

- **[DTNRG — Delay Tolerant Networking Research Group](https://irtf.org/dtnrg)** — IRTF research group (historic but foundational)
- **[ION-DTN Documentation](https://sourceforge.net/projects/ion-dtn/)** — Reference implementation docs
- **[NASA DTN Page](https://www.nasa.gov/mission_pages/station/research/experiments/explorer/Investigation.html)** — DTN experiments on ISS
- **[InterPlanetary Networking Special Interest Group (IPNSIG)](https://ipnsig.org/)** — Community & resources
- **[Bundle Protocol Wikipedia](https://en.wikipedia.org/wiki/Bundle_Protocol)** — Quick reference overview
- **[Vint Cerf — Interplanetary Internet](https://www.google.com/search?q=vint+cerf+interplanetary+internet+talk)** — Cerf's vision for IPN

### Software to Practice With

| Software | Type | Link | Purpose |
|----------|------|------|---------|
| **ION-DTN** | DTN Implementation | [SourceForge](https://sourceforge.net/projects/ion-dtn/) | Reference BPv7 implementation |
| **dtln2** | DTN Implementation | [GitHub](https://github.com/dtn7/dtn7) | Modern Go-based BPv7 |
| **IBR-DTN** | DTN Implementation | [GitHub](https://github.com/ibrdtn/ibrdtn) | C++ DTN daemon |
| **Postman** | API Testing | [postman.com](https://www.postman.com/) | Test REST APIs |
| **Wireshark** | Packet Analyzer | [wireshark.org](https://www.wireshark.org/) | Analyze BPv7 bundles |

### Key Concepts to Master

1. **Store-and-Forward** — How bundles persist at intermediate nodes
2. **Custody Transfer** — Responsibility chain for delivery guarantee
3. **Convergence Layers** — LTP, TCPCL, UDP-CL and when to use each
4. **Priority Classes** — P0 (Emergency) through P4 (Bulk)
5. **Why TCP/IP fails** — Be able to explain in 30 seconds with specific numbers
6. **Contact Graph Routing** — Know what it is, know why AETHERIX replaces it

### Practice Questions

1. Explain store-and-forward in your own words (1 minute)
2. What happens to a bundle when a link drops mid-transfer? (30 seconds)
3. Compare LTP and TCP convergence layers (1 minute)
4. Walk through a custody transfer sequence (1 minute)
5. Why is BPv7 better than BPv6? (RFC 9171 vs older specs)
