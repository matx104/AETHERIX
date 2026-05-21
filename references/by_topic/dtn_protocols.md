# DTN & Bundle Protocol References

Delay-tolerant networking is the backbone of AETHERIX. Earth–Mars links suffer 3–22 minute one-way light delays and frequent blackouts from solar conjunction, making TCP-style protocols unusable. The references below define the store-and-forward architecture (BPv7, LTP, Contact Graph Routing) that AETHERIX builds upon, and the RL-enhanced routing that replaces static contact plans.

## Most Important

| Ref | Citation | Why Critical |
|-----|----------|--------------|
| [4] | Burleigh et al., RFC 9171 (2022) | Current BPv7 standard — AETHERIX bundle format follows this |
| [2] | Burleigh et al., 2003 | Foundational DTN architecture paper |
| [3] | Cerf et al., RFC 4838 (2007) | DTN architecture RFC — defines the bundle layer |
| [8] | Fraire et al., 2021 | Contact Graph Routing tutorial — baseline AETHERIX improves on |
| [5] | Ramadas et al., RFC 5326 (2008) | LTP specification — convergence layer for deep-space links |

---

## Foundational Papers

[1] K. Fall, "A Delay-Tolerant Network Architecture for Challenged Internets," in *Proc. ACM SIGCOMM*, 2003, pp. 27-34. doi: 10.1145/863955.863960

> Introduces the DTN concept as an overlay architecture for networks with intermittent connectivity. Fall's seminal work defines the bundle layer that sits between transport and application — the exact layer AETHERIX implements for interplanetary routing.

[2] S. Burleigh, A. Hooke, L. Torgerson, K. Fall, V. Cerf, B. Durst, K. Scott, and H. Weiss, "Delay-Tolerant Networking: An Approach to Interplanetary Internet," *IEEE Communications Magazine*, vol. 41, no. 6, pp. 128-136, Jun. 2003. doi: 10.1109/MCOM.2003.1204759

> The first comprehensive description of DTN applied to the Interplanetary Internet. Co-authored by Vint Cerf and the JPL DTN team, this paper motivates the store-and-forward approach and outlines the custody-transfer mechanism that AETHERIX's bundle implementation uses.

[3] V. Cerf, S. Burleigh, A. Hooke, L. Torgerson, R. Durst, K. Scott, K. Fall, and H. Weiss, "Delay-Tolerant Networking Architecture," RFC 4838, Apr. 2007. [Online]. Available: https://www.rfc-editor.org/rfc/rfc4838

> The IETF's official DTN architecture specification. Defines the bundle layer, endpoint IDs, and the security-in-depth model. AETHERIX's endpoint ID format (`dtn://node/service`) derives from this RFC.

## Bundle Protocol & Convergence Layers

[4] S. Burleigh, K. Fall, and E. J. Birrane III, "Bundle Protocol Version 7," RFC 9171, Jan. 2022. [Online]. Available: https://www.rfc-editor.org/rfc/rfc9171

> The definitive BPv7 specification. AETHERIX's `Bundle` class (in `src/routing/bundle.py`) implements this standard: primary block structure, CRC integrity, lifetime management, and custody tracking. Any production deployment must conform to this RFC.

[5] M. Ramadas, S. Burleigh, and S. Farrell, "Licklider Transmission Protocol - Specification," RFC 5326, Sep. 2008. [Online]. Available: https://www.rfc-editor.org/rfc/rfc5326

> LTP provides reliable, session-based transmission over long-delay links — the convergence layer beneath BPv7 for deep-space links. AETHERIX references LTP as the transport mechanism for Earth–Mars hops where retransmission timers would otherwise be impractical.

## ION-DTN & Contact Graph Routing

[6] S. Burleigh, "Interplanetary Overlay Network (ION) Design and Operation," Jet Propulsion Laboratory, California Institute of Technology, Pasadena, CA, Tech. Rep. D-48259, 2007.

> The ION-DTN implementation reference. ION is the flight-proven DTN stack that AETHERIX plans to integrate with via `scripts/setup-ion-dtn.sh`. Understanding ION's contact-plan format is essential for the RL agent's state representation.

[7] G. Araniti, N. Bezirgiannidis, E. Birrane, I. Bisio, S. Burleigh, et al., "Contact Graph Routing in DTN Space Networks: Overview, Enhancements and Performance," *IEEE Communications Magazine*, vol. 53, no. 3, pp. 38-46, Mar. 2015.

> Comprehensive overview of Contact Graph Routing (CGR), the current state-of-the-art for DTN routing in space. AETHERIX's RL agent is positioned as an enhancement over CGR, learning dynamic routing policies that adapt to link quality variations that static contact plans cannot capture.

[8] J. A. Fraire, O. De Jonckère, and S. C. Burleigh, "Routing in the Space Internet: A Contact Graph Routing Tutorial," *Journal of Network and Computer Applications*, vol. 174, p. 102884, 2021.

> An accessible CGR tutorial with worked examples. Essential reading for understanding the baseline routing algorithm that AETHERIX's RL approach seeks to improve upon. Fraire's formal model of contact graphs maps directly to AETHERIX's network topology.

## DTN Routing Algorithms

[9] A. Vahdat and D. Becker, "Epidemic Routing for Partially-Connected Ad Hoc Networks," Duke University, Tech. Rep. CS-2000-06, 2000.

> Epidemic routing floods bundles through all encounters — the simplest DTN routing strategy. AETHERIX uses epidemic-style flooding as a comparison baseline when evaluating RL routing performance in simulations.

[10] T. Spyropoulos, K. Psounis, and C. S. Raghavendra, "Spray and Wait: An Efficient Routing Scheme for Intermittently Connected Mobile Networks," in *Proc. ACM SIGCOMM Workshop on Delay-Tolerant Networking*, 2005, pp. 252-259.

> Introduces controlled-copy flooding (Spray and Wait) as a resource-efficient alternative to epidemic routing. The spray count concept informed AETHERIX's `RoutingAction.SPLIT` action, which replicates bundles to multiple next hops.

[11] A. Lindgren, A. Doria, and O. Schelén, "Probabilistic Routing in Intermittently Connected Networks," *ACM SIGMOBILE Mobile Computing and Communications Review*, vol. 7, no. 3, pp. 19-20, Jul. 2003.

> PROPHET routing uses delivery probability estimates based on encounter history. AETHERIX's RL agent can be seen as a generalization: instead of heuristic probability updates, it learns optimal forwarding decisions via reward signals.

## Convergence Layers

[65] M. Demmer, J. Ott, and S. Perreault, "Delay-Tolerant Networking TCP Convergence Layer Protocol," RFC 7242, Aug. 2014. [Online]. Available: https://www.rfc-editor.org/rfc/rfc7242

> Defines the TCP convergence layer (TCPCL) for BPv7, providing reliable, session-based transport over TCP connections. AETHERIX uses TCPCL for Earth-segment links (DSN stations to Mission Operations Centers) where reliable, ordered delivery is required and round-trip times are terrestrial-scale. TCPCL's length-prefixed segment framing and session management complement LTP's deep-space role.

[66] S. Burleigh, "Delay-Tolerant Networking Licklider Transmission Protocol (LTP) Convergence-Layer Adapter," RFC 9174, Jan. 2023. [Online]. Available: https://www.rfc-editor.org/rfc/rfc9174

> Updates the LTP convergence-layer adapter specification for BPv7, defining how bundles are encapsulated into LTP blocks (red-part for reliable, green-part for best-effort delivery). AETHERIX's LTP implementation uses red-part segments for high-priority bundles (P0-P2) and green-part for bulk data (P3-P4), optimizing retransmission overhead on bandwidth-limited deep-space links.

## Store-and-Forward Theory

[67] K. Fall and S. Farrell, "DTN: An Architectural Retrospective," *IEEE Journal on Selected Areas in Communications*, vol. 26, no. 5, pp. 828-836, Jun. 2008. doi: 10.1109/JSAC.2008.080608

> Retrospective on the DTN architecture five years after its introduction, analyzing which design decisions stood the test of time and which evolved. Discusses the store-and-forward paradigm's robustness in the face of partitioned networks, the role of custody transfer in providing delivery guarantees, and the importance of late-binding for heterogeneous link environments — all principles embedded in AETHERIX's forwarding engine.

## Priority Queuing in DTN

[68] N. Bezirgiannidis, S. Burleigh, and V. Tsaoussidis, "Delivery Time Estimation for Space Bundle Protocols," in *Proc. 7th ACM Workshop on Performance Monitoring and Measurement of Heterogeneous Wireless and Wired Networks*, 2012, pp. 47-54.

> Presents delivery time estimation techniques for DTN bundles with different priority classes. Demonstrates that priority-aware scheduling at custodian nodes significantly improves on-time delivery for expedited traffic without starving bulk transfers. AETHERIX's policy engine implements priority-based queuing derived from this work, ensuring P0 (emergency) bundles always preempt lower-priority traffic in bounded-size buffers.

## Additional DTN References

[61] I. F. Akyildiz, O. B. Akan, C. Chen, J. Fang, and W. Su, "InterPlaNetary Internet: State-of-the-Art and Research Challenges," *Computer Networks*, vol. 43, no. 2, pp. 75-112, Oct. 2003.

> Broad survey of the InterPlaNetary Internet vision. Maps the protocol stack (application → bundle → transport → link) and identifies open research challenges in routing, security, and transport — all areas AETHERIX addresses.

[62] J. Wyatt, S. Burleigh, R. Jones, L. Torgerson, and S. Wissler, "Disruption Tolerant Networking Flight Validation Experiment on NASA's EPOXI Mission," in *Proc. 1st Int. Conf. Advances in Satellite and Space Communications*, 2009, pp. 187-196.

> Reports on the first in-space DTN experiment (EPOXI/Deep Impact flyby). Validates that BPv7 works in real orbital conditions — evidence that AETHERIX's architecture is grounded in flight-proven technology, not just theory.
