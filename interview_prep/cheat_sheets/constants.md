# AETHERIX Constants Cheat Sheet

## Physical Constants

| Constant | Symbol | Value |
|----------|--------|-------|
| Speed of light | c | 299,792,458 m/s |
| Boltzmann constant | k | 1.381×10⁻²³ J/K |
| Planck constant | h | 6.626×10⁻³⁴ J·s |
| Astronomical Unit | AU | 149,597,870.7 km |

---

## Earth Parameters

| Parameter | Value |
|-----------|-------|
| Orbital radius | 1.0 AU |
| Orbital period | 365.25 days |
| Eccentricity | 0.0167 |
| Rotation period | 23.934 hours |
| GEO altitude | 35,786 km |

---

## Mars Parameters

| Parameter | Value |
|-----------|-------|
| Orbital radius | 1.524 AU |
| Orbital period | 686.98 days |
| Eccentricity | 0.0934 |
| Rotation period | 24.623 hours |
| Areostationary altitude | 17,032 km |
| Surface gravity | 3.72 m/s² |

---

## Earth-Mars Distances

| Scenario | Distance | Light Time |
|----------|----------|------------|
| Perihelion opposition | 54.6M km (0.365 AU) | 3.0 min |
| Average | 225M km (1.5 AU) | 12.5 min |
| Aphelion conjunction | 401M km (2.68 AU) | 22.3 min |
| **Synodic period** | 779.94 days | - |

---

## AETHERIX Network Parameters

| Parameter | Value |
|-----------|-------|
| Total nodes | 232 |
| Earth ground | 6 nodes |
| Earth orbital | 51 nodes |
| Deep space | 4 nodes |
| Mars orbital | 4 nodes |
| Mars surface | 167 nodes |

---

## Communication Parameters

| Parameter | Value |
|-----------|-------|
| Optical wavelength | 1550 nm |
| Optical frequency | 193.4 THz |
| Mars TX aperture | 22 cm (0.22 m) |
| Earth RX aperture | 1.0 m |
| Laser power | 5 W (36.99 dBm) |

---

## Data Rates

| Link | Minimum | Typical | Maximum |
|------|---------|---------|---------|
| Earth-Mars optical | 2 Mbps | 10-20 Mbps | 200 Mbps |
| Earth-Mars RF | 125 kbps | 2 Mbps | 6 Mbps |
| Mars ISL | 1 Gbps | 1-2 Gbps | 10 Gbps |
| Surface-orbital | 256 kbps | 2 Mbps | 100 Mbps |

---

## QKD Parameters

| Parameter | Earth-LEO | Earth-GEO | Earth-Mars |
|-----------|-----------|-----------|------------|
| Key rate | 1-10 kbps | 100-1000 bps | 1-10 bps |
| Distance | <2,000 km | ~36,000 km | 54-401M km |
| Protocol | BB84 | BB84/E91 | E91+Repeaters |
| QBER threshold | <11% | <11% | <11% |

---

## Priority Levels

| Level | Name | Max Delay | Example |
|-------|------|-----------|---------|
| P0 | Emergency | <1 min | Anomaly alerts |
| P1 | High Science | <30 min | Solar events |
| P2 | Standard | <24 hours | Daily science |
| P3 | Housekeeping | <7 days | Logs |
| P4 | Bulk | <30 days | Archives |

---

## CCSDS Standards (Know These!)

| Standard | Title |
|----------|-------|
| CCSDS 734.2-B-1 | DTN Architecture |
| CCSDS 735.1-B-1 | Bundle Protocol |
| CCSDS 142.0-B-2 | LNIS v5 (Space Link IDs) |
| CCSDS 141.0-B-1 | Optical Communications |
| RFC 9171 | Bundle Protocol Version 7 |
| RFC 5326 | Licklider Transmission Protocol |
