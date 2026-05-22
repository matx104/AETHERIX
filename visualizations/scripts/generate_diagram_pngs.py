#!/usr/bin/env python3
"""Generate standalone SVG and PNG diagram files for sharing."""
import os
import re
import cairosvg

DIAGRAMS_DIR = os.path.join(os.path.dirname(__file__), '..', 'diagrams')
DIAGRAMS_DIR = os.path.abspath(DIAGRAMS_DIR)

SVG_WRAPPER = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="background:#050a14">
<rect width="{w}" height="{h}" fill="#050a14"/>
{content}
</svg>'''

def wrap_svg(content, w=920, h=440):
    return SVG_WRAPPER.format(w=w, h=h, content=content)

DIAGRAMS = {
    'system_architecture': {
        'title': 'System Architecture',
        'w': 920, 'h': 440,
        'svg': '''
<defs>
<linearGradient id="ga1" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#00d4ff" stop-opacity="0.2"/><stop offset="100%" stop-color="#7c5cf7" stop-opacity="0.1"/></linearGradient>
<linearGradient id="ga2" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#ff6b35" stop-opacity="0.15"/><stop offset="100%" stop-color="#f85149" stop-opacity="0.08"/></linearGradient>
<marker id="arrowW" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6" fill="none" stroke="#5a6578" stroke-width="1"/></marker>
</defs>
<text x="450" y="32" text-anchor="middle" fill="#00d4ff" font-size="16" font-weight="700" font-family="monospace">AETHERIX PLATFORM</text>
<rect x="20" y="45" width="860" height="4" rx="2" fill="url(#ga1)"/>

<rect x="20" y="60" width="200" height="130" rx="8" fill="rgba(0,212,255,0.06)" stroke="#00d4ff" stroke-opacity="0.25"/>
<text x="120" y="82" text-anchor="middle" fill="#00d4ff" font-size="12" font-weight="700" font-family="monospace">INFRASTRUCTURE</text>
<text x="120" y="100" text-anchor="middle" fill="#8892a4" font-size="10">link_budget.py</text>
<text x="120" y="116" text-anchor="middle" fill="#8892a4" font-size="10">rf_link_budget.py</text>
<text x="120" y="136" text-anchor="middle" fill="#5a6578" font-size="9">FSPL, EIRP, margin</text>
<text x="120" y="152" text-anchor="middle" fill="#5a6578" font-size="9">Ka/X/S/UHF bands</text>
<text x="120" y="168" text-anchor="middle" fill="#5a6578" font-size="9">CCSDS 141.0-B-1</text>

<rect x="240" y="60" width="200" height="130" rx="8" fill="rgba(124,92,247,0.06)" stroke="#7c5cf7" stroke-opacity="0.25"/>
<text x="340" y="82" text-anchor="middle" fill="#7c5cf7" font-size="12" font-weight="700" font-family="monospace">ROUTING</text>
<text x="340" y="100" text-anchor="middle" fill="#8892a4" font-size="10">rl_agent.py</text>
<text x="340" y="116" text-anchor="middle" fill="#8892a4" font-size="10">bundle.py / ltp.py</text>
<text x="340" y="136" text-anchor="middle" fill="#5a6578" font-size="9">Q-learning, federated</text>
<text x="340" y="152" text-anchor="middle" fill="#5a6578" font-size="9">BPv7, LTP, TCPCL, UDP-CL</text>
<text x="340" y="168" text-anchor="middle" fill="#5a6578" font-size="9">RFC 9171, RFC 5326</text>

<rect x="460" y="60" width="200" height="130" rx="8" fill="rgba(200,76,255,0.06)" stroke="#c84cff" stroke-opacity="0.25"/>
<text x="560" y="82" text-anchor="middle" fill="#c84cff" font-size="12" font-weight="700" font-family="monospace">SECURITY</text>
<text x="560" y="100" text-anchor="middle" fill="#8892a4" font-size="10">qkd.py</text>
<text x="560" y="116" text-anchor="middle" fill="#8892a4" font-size="10">repeater_chain.py</text>
<text x="560" y="136" text-anchor="middle" fill="#5a6578" font-size="9">BB84, E91 protocols</text>
<text x="560" y="152" text-anchor="middle" fill="#5a6578" font-size="9">CASCADE reconciliation</text>
<text x="560" y="168" text-anchor="middle" fill="#5a6578" font-size="9">NIST FIPS 203/204 (PQC)</text>

<rect x="680" y="60" width="200" height="130" rx="8" fill="rgba(255,107,53,0.06)" stroke="#ff6b35" stroke-opacity="0.25"/>
<text x="780" y="82" text-anchor="middle" fill="#ff6b35" font-size="12" font-weight="700" font-family="monospace">ORBITAL</text>
<text x="780" y="100" text-anchor="middle" fill="#8892a4" font-size="10">contact_windows.py</text>
<text x="780" y="116" text-anchor="middle" fill="#8892a4" font-size="10">topology.py / doppler.py</text>
<text x="780" y="136" text-anchor="middle" fill="#5a6578" font-size="9">5-tier, 241 nodes</text>
<text x="780" y="152" text-anchor="middle" fill="#5a6578" font-size="9">Synodic period modeling</text>
<text x="780" y="168" text-anchor="middle" fill="#5a6578" font-size="9">Doppler compensation</text>

<line x1="120" y1="190" x2="120" y2="215" stroke="#5a6578" stroke-width="1.5" marker-end="url(#arrowW)"/>
<line x1="340" y1="190" x2="340" y2="215" stroke="#5a6578" stroke-width="1.5" marker-end="url(#arrowW)"/>
<line x1="560" y1="190" x2="560" y2="215" stroke="#5a6578" stroke-width="1.5" marker-end="url(#arrowW)"/>
<line x1="780" y1="190" x2="780" y2="215" stroke="#5a6578" stroke-width="1.5" marker-end="url(#arrowW)"/>

<rect x="20" y="220" width="860" height="50" rx="8" fill="url(#ga2)" stroke="#ff6b35" stroke-opacity="0.25"/>
<text x="450" y="242" text-anchor="middle" fill="#ff6b35" font-size="12" font-weight="700" font-family="monospace">SIMULATION ENGINE</text>
<text x="450" y="260" text-anchor="middle" fill="#8892a4" font-size="10">simulator.py · policy_engine.py · training.py · multi_agent.py · forwarding_engine.py</text>

<line x1="450" y1="270" x2="450" y2="290" stroke="#5a6578" stroke-width="1.5" marker-end="url(#arrowW)"/>

<rect x="130" y="295" width="640" height="45" rx="8" fill="rgba(63,185,80,0.06)" stroke="#3fb950" stroke-opacity="0.25"/>
<text x="450" y="316" text-anchor="middle" fill="#3fb950" font-size="12" font-weight="700" font-family="monospace">WEB SHOWCASE — 10 Interactive Demos</text>
<text x="450" y="332" text-anchor="middle" fill="#8892a4" font-size="10">matx104.github.io/AETHERIX · 149 tests · 27 Python modules</text>

<rect x="20" y="360" width="410" height="24" rx="4" fill="rgba(0,212,255,0.04)" stroke="#00d4ff" stroke-opacity="0.15"/>
<text x="225" y="376" text-anchor="middle" fill="#5a6578" font-size="9">CCSDS 734.2-B-1 · CCSDS 735.1-B-1 · CCSDS 141.0-B-1</text>
<rect x="470" y="360" width="410" height="24" rx="4" fill="rgba(124,92,247,0.04)" stroke="#7c5cf7" stroke-opacity="0.15"/>
<text x="675" y="376" text-anchor="middle" fill="#5a6578" font-size="9">RFC 9171 · RFC 5326 · RFC 7242 · NIST FIPS 203/204</text>
'''
    },
    'dtn_store_and_forward': {
        'title': 'DTN Store-and-Forward',
        'w': 920, 'h': 400,
        'svg': '''
<defs>
<marker id="dtA" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6" fill="none" stroke="#00d4ff" stroke-width="1.2"/></marker>
<marker id="dtR" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6" fill="none" stroke="#f85149" stroke-width="1"/></marker>
</defs>
<text x="460" y="24" text-anchor="middle" fill="#8892a4" font-size="11" font-weight="600" letter-spacing="2">TCP/IP: END-TO-END CONNECTION (FAILS IN SPACE)</text>
<rect x="60" y="36" width="120" height="40" rx="6" fill="rgba(0,212,255,0.1)" stroke="#00d4ff" stroke-opacity="0.4"/>
<text x="120" y="60" text-anchor="middle" fill="#00d4ff" font-size="11" font-weight="600">Source</text>
<line x1="180" y1="56" x2="250" y2="56" stroke="#00d4ff" stroke-width="1.5" stroke-dasharray="4,3"/>
<rect x="250" y="36" width="120" height="40" rx="6" fill="rgba(0,212,255,0.1)" stroke="#00d4ff" stroke-opacity="0.4"/>
<text x="310" y="60" text-anchor="middle" fill="#00d4ff" font-size="11" font-weight="600">Router</text>
<line x1="370" y1="56" x2="440" y2="56" stroke="#00d4ff" stroke-width="1.5" stroke-dasharray="4,3"/>
<rect x="440" y="36" width="120" height="40" rx="6" fill="rgba(0,212,255,0.1)" stroke="#00d4ff" stroke-opacity="0.4"/>
<text x="500" y="60" text-anchor="middle" fill="#00d4ff" font-size="11" font-weight="600">Router</text>
<line x1="560" y1="56" x2="630" y2="56" stroke="#f85149" stroke-width="1.5" stroke-dasharray="4,3"/>
<rect x="630" y="36" width="120" height="40" rx="6" fill="rgba(248,81,73,0.1)" stroke="#f85149" stroke-opacity="0.4" stroke-dasharray="3,3"/>
<text x="690" y="60" text-anchor="middle" fill="#f85149" font-size="11" font-weight="600">Dest</text>
<text x="810" y="60" text-anchor="middle" fill="#f85149" font-size="22">✗</text>

<text x="460" y="108" text-anchor="middle" fill="#8892a4" font-size="11" font-weight="600" letter-spacing="2">DTN: STORE-AND-FORWARD (WORKS IN SPACE)</text>

<rect x="20" y="120" width="160" height="95" rx="8" fill="rgba(63,185,80,0.08)" stroke="#3fb950" stroke-opacity="0.3"/>
<text x="100" y="142" text-anchor="middle" fill="#3fb950" font-size="11" font-weight="700">SOURCE</text>
<text x="100" y="158" text-anchor="middle" fill="#8892a4" font-size="9">Create Bundle</text>
<text x="100" y="172" text-anchor="middle" fill="#8892a4" font-size="9">Priority: P2</text>
<text x="100" y="190" text-anchor="middle" fill="#5a6578" font-size="8">CUSTODY: Source</text>

<line x1="180" y1="168" x2="220" y2="168" stroke="#00d4ff" stroke-width="1.5" marker-end="url(#dtA)"/>
<text x="200" y="160" text-anchor="middle" fill="#5a6578" font-size="8">link up</text>

<rect x="220" y="120" width="160" height="95" rx="8" fill="rgba(0,212,255,0.08)" stroke="#00d4ff" stroke-opacity="0.3"/>
<text x="300" y="142" text-anchor="middle" fill="#00d4ff" font-size="11" font-weight="700">NODE A</text>
<text x="300" y="158" text-anchor="middle" fill="#8892a4" font-size="9">Forward bundle</text>
<text x="300" y="172" text-anchor="middle" fill="#3fb950" font-size="9">Custody accepted ✓</text>
<text x="300" y="195" text-anchor="middle" fill="#d29922" font-size="8">📁 STORE: 2 bundles</text>

<line x1="380" y1="168" x2="420" y2="168" stroke="#d29922" stroke-width="1.5" stroke-dasharray="4,2"/>
<text x="400" y="160" text-anchor="middle" fill="#d29922" font-size="8">no link</text>

<rect x="420" y="120" width="160" height="95" rx="8" fill="rgba(210,153,34,0.08)" stroke="#d29922" stroke-opacity="0.3"/>
<text x="500" y="142" text-anchor="middle" fill="#d29922" font-size="11" font-weight="700">NODE B</text>
<text x="500" y="158" text-anchor="middle" fill="#8892a4" font-size="9">📁 Storing bundle</text>
<text x="500" y="172" text-anchor="middle" fill="#8892a4" font-size="9">Waiting for link...</text>
<text x="500" y="195" text-anchor="middle" fill="#d29922" font-size="8">⏳ WAIT 14 min</text>

<line x1="580" y1="168" x2="620" y2="168" stroke="#00d4ff" stroke-width="1.5" marker-end="url(#dtA)"/>
<text x="600" y="160" text-anchor="middle" fill="#00d4ff" font-size="8">link up</text>

<rect x="620" y="120" width="160" height="95" rx="8" fill="rgba(0,212,255,0.08)" stroke="#00d4ff" stroke-opacity="0.3"/>
<text x="700" y="142" text-anchor="middle" fill="#00d4ff" font-size="11" font-weight="700">NODE C</text>
<text x="700" y="158" text-anchor="middle" fill="#8892a4" font-size="9">Forward bundle</text>
<text x="700" y="172" text-anchor="middle" fill="#3fb950" font-size="9">Custody accepted ✓</text>
<text x="700" y="190" text-anchor="middle" fill="#5a6578" font-size="8">CUSTODY: Node C</text>

<line x1="780" y1="168" x2="820" y2="168" stroke="#3fb950" stroke-width="1.5" marker-end="url(#dtA)"/>

<rect x="820" y="130" width="80" height="75" rx="8" fill="rgba(63,185,80,0.08)" stroke="#3fb950" stroke-opacity="0.3"/>
<text x="860" y="158" text-anchor="middle" fill="#3fb950" font-size="11" font-weight="700">DEST</text>
<text x="860" y="178" text-anchor="middle" fill="#3fb950" font-size="18">✓</text>
<text x="860" y="196" text-anchor="middle" fill="#8892a4" font-size="9">Delivered</text>

<rect x="20" y="240" width="280" height="50" rx="6" fill="rgba(0,212,255,0.04)" stroke="#00d4ff" stroke-opacity="0.15"/>
<text x="160" y="260" text-anchor="middle" fill="#00d4ff" font-size="10" font-weight="600">Key: Custody Transfer</text>
<text x="160" y="278" text-anchor="middle" fill="#8892a4" font-size="9">Each node takes responsibility for the bundle</text>

<rect x="320" y="240" width="280" height="50" rx="6" fill="rgba(63,185,80,0.04)" stroke="#3fb950" stroke-opacity="0.15"/>
<text x="460" y="260" text-anchor="middle" fill="#3fb950" font-size="10" font-weight="600">Data Never Lost</text>
<text x="460" y="278" text-anchor="middle" fill="#8892a4" font-size="9">Bundle stored until next hop confirms</text>

<rect x="620" y="240" width="280" height="50" rx="6" fill="rgba(124,92,247,0.04)" stroke="#7c5cf7" stroke-opacity="0.15"/>
<text x="760" y="260" text-anchor="middle" fill="#7c5cf7" font-size="10" font-weight="600">No End-to-End Needed</text>
<text x="760" y="278" text-anchor="middle" fill="#8892a4" font-size="9">Hop-by-hop, works with 22-min delays</text>

<rect x="20" y="310" width="880" height="45" rx="6" fill="rgba(255,107,53,0.04)" stroke="#ff6b35" stroke-opacity="0.15"/>
<text x="460" y="332" text-anchor="middle" fill="#ff6b35" font-size="10" font-weight="600">Three Convergence Layers</text>
<text x="200" y="348" text-anchor="middle" fill="#8892a4" font-size="9">LTP (RFC 5326) — Deep space</text>
<text x="560" y="348" text-anchor="middle" fill="#8892a4" font-size="9">TCPCL (RFC 7242) — Earth segment</text>
<text x="820" y="348" text-anchor="middle" fill="#8892a4" font-size="9">UDP-CL — Optical ISL</text>
'''
    },
    '5tier_network': {
        'title': '5-Tier Network',
        'w': 920, 'h': 480,
        'svg': '''
<defs>
<marker id="ntA" markerWidth="7" markerHeight="5" refX="7" refY="2.5" orient="auto"><path d="M0,0 L7,2.5 L0,5" fill="none" stroke="#5a6578" stroke-width="1"/></marker>
<linearGradient id="ntE" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#0d47a1"/><stop offset="100%" stop-color="#1e88e5"/></linearGradient>
<linearGradient id="ntM" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#d84315"/><stop offset="100%" stop-color="#ff7043"/></linearGradient>
</defs>
<ellipse cx="220" cy="80" rx="170" ry="60" fill="none" stroke="#1e88e5" stroke-width="1" stroke-opacity="0.3" stroke-dasharray="4,3"/>
<text x="220" y="18" text-anchor="middle" fill="#1e88e5" font-size="10" font-weight="600" letter-spacing="1">EARTH</text>
<rect x="80" y="46" width="90" height="30" rx="4" fill="url(#ntE)" fill-opacity="0.7"/><text x="125" y="66" text-anchor="middle" fill="white" font-size="9" font-weight="600">Goldstone</text>
<rect x="185" y="38" width="70" height="30" rx="4" fill="url(#ntE)" fill-opacity="0.7"/><text x="220" y="58" text-anchor="middle" fill="white" font-size="9" font-weight="600">Madrid</text>
<rect x="270" y="46" width="90" height="30" rx="4" fill="url(#ntE)" fill-opacity="0.7"/><text x="315" y="66" text-anchor="middle" fill="white" font-size="9" font-weight="600">Canberra</text>
<text x="220" y="95" text-anchor="middle" fill="#5a6578" font-size="8">T1: Earth Ground (6 nodes)</text>

<ellipse cx="220" cy="150" rx="200" ry="30" fill="none" stroke="#42a5f5" stroke-width="1" stroke-opacity="0.3" stroke-dasharray="4,3"/>
<rect x="60" y="133" width="60" height="24" rx="4" fill="#42a5f5" fill-opacity="0.5"/><text x="90" y="150" text-anchor="middle" fill="white" font-size="8" font-weight="600">GEO-1</text>
<rect x="130" y="133" width="60" height="24" rx="4" fill="#42a5f5" fill-opacity="0.5"/><text x="160" y="150" text-anchor="middle" fill="white" font-size="8" font-weight="600">GEO-2</text>
<rect x="200" y="133" width="60" height="24" rx="4" fill="#42a5f5" fill-opacity="0.5"/><text x="230" y="150" text-anchor="middle" fill="white" font-size="8" font-weight="600">GEO-3</text>
<text x="330" y="145" text-anchor="middle" fill="#42a5f5" font-size="9" font-weight="600">+ 48 LEO laser mesh</text>
<text x="220" y="175" text-anchor="middle" fill="#5a6578" font-size="8">T2: Earth Orbital (51 nodes)</text>

<line x1="220" y1="100" x2="220" y2="120" stroke="#5a6578" stroke-width="1" marker-end="url(#ntA)"/>
<line x1="220" y1="180" x2="220" y2="200" stroke="#5a6578" stroke-width="1" marker-end="url(#ntA)"/>
<text x="240" y="195" fill="#7c5cf7" font-size="8">1550nm optical</text>

<rect x="140" y="205" width="160" height="50" rx="6" fill="rgba(124,92,247,0.1)" stroke="#7c5cf7" stroke-opacity="0.3"/>
<text x="220" y="222" text-anchor="middle" fill="#7c5cf7" font-size="10" font-weight="700">DEEP SPACE TRANSIT</text>
<text x="220" y="238" text-anchor="middle" fill="#8892a4" font-size="9">ES-L4 · ES-L5 Lagrange relays</text>
<text x="220" y="250" text-anchor="middle" fill="#5a6578" font-size="8">T3: 4 nodes</text>

<text x="460" y="305" text-anchor="middle" fill="#5a6578" font-size="9" font-style="italic">~225 million km average</text>
<line x1="310" y1="235" x2="580" y2="235" stroke="#5a6578" stroke-width="1" stroke-dasharray="3,3" marker-end="url(#ntA)"/>
<text x="445" y="230" text-anchor="middle" fill="#00d4ff" font-size="8">interplanetary optical link</text>
<text x="445" y="248" text-anchor="middle" fill="#5a6578" font-size="8">12.5 min one-way light time</text>

<ellipse cx="700" cy="80" rx="170" ry="60" fill="none" stroke="#ff7043" stroke-width="1" stroke-opacity="0.3" stroke-dasharray="4,3"/>
<text x="700" y="18" text-anchor="middle" fill="#ff7043" font-size="10" font-weight="600" letter-spacing="1">MARS</text>
<rect x="560" y="46" width="80" height="30" rx="4" fill="url(#ntM)" fill-opacity="0.7"/><text x="600" y="66" text-anchor="middle" fill="white" font-size="9" font-weight="600">MRS-Alpha</text>
<rect x="655" y="46" width="80" height="30" rx="4" fill="url(#ntM)" fill-opacity="0.7"/><text x="695" y="66" text-anchor="middle" fill="white" font-size="9" font-weight="600">MRS-Beta</text>
<rect x="750" y="46" width="80" height="30" rx="4" fill="url(#ntM)" fill-opacity="0.7"/><text x="790" y="66" text-anchor="middle" fill="white" font-size="9" font-weight="600">MRS-Polar</text>
<text x="700" y="95" text-anchor="middle" fill="#5a6578" font-size="8">T4: Mars Orbital (13 nodes)</text>

<ellipse cx="700" cy="150" rx="170" ry="30" fill="none" stroke="#d29922" stroke-width="1" stroke-opacity="0.3" stroke-dasharray="4,3"/>
<rect x="560" y="137" width="55" height="22" rx="4" fill="#d29922" fill-opacity="0.5"/><text x="587" y="152" text-anchor="middle" fill="white" font-size="8">Base-1</text>
<rect x="625" y="137" width="55" height="22" rx="4" fill="#d29922" fill-opacity="0.5"/><text x="652" y="152" text-anchor="middle" fill="white" font-size="8">Base-2</text>
<rect x="690" y="137" width="55" height="22" rx="4" fill="#d29922" fill-opacity="0.5"/><text x="717" y="152" text-anchor="middle" fill="white" font-size="8">Rover</text>
<text x="800" y="148" text-anchor="middle" fill="#d29922" font-size="9" font-weight="600">+ 164 more</text>
<text x="700" y="175" text-anchor="middle" fill="#5a6578" font-size="8">T5: Mars Surface (167 nodes)</text>

<line x1="700" y1="100" x2="700" y2="120" stroke="#5a6578" stroke-width="1" marker-end="url(#ntA)"/>

<text x="460" y="370" text-anchor="middle" fill="#00d4ff" font-size="11" font-weight="600">241 Nodes · 5 Tiers · 3 Redundant Paths · No Single Point of Failure</text>
<rect x="60" y="385" width="800" height="4" rx="2" fill="url(#ga1)" opacity="0.3"/>
'''
    },
    'earth_mars_journey': {
        'title': 'Earth-Mars Journey',
        'w': 920, 'h': 440,
        'svg': '''
<defs>
<marker id="jmA" markerWidth="7" markerHeight="5" refX="7" refY="2.5" orient="auto"><path d="M0,0 L7,2.5 L0,5" fill="none" stroke="#ff6b35" stroke-width="1.2"/></marker>
<linearGradient id="jmG" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#d84315" stop-opacity="0.3"/><stop offset="50%" stop-color="#7c5cf7" stop-opacity="0.15"/><stop offset="100%" stop-color="#1e88e5" stop-opacity="0.3"/></linearGradient>
</defs>
<circle cx="80" cy="80" r="45" fill="#d84315" fill-opacity="0.2" stroke="#ff6b35" stroke-width="1.5"/>
<text x="80" y="76" text-anchor="middle" fill="#ff6b35" font-size="12" font-weight="700">MARS</text>
<text x="80" y="92" text-anchor="middle" fill="#8892a4" font-size="8">Surface</text>
<circle cx="840" cy="80" r="55" fill="#1e88e5" fill-opacity="0.2" stroke="#00d4ff" stroke-width="1.5"/>
<text x="840" y="76" text-anchor="middle" fill="#00d4ff" font-size="12" font-weight="700">EARTH</text>
<text x="840" y="92" text-anchor="middle" fill="#8892a4" font-size="8">Ground</text>
<line x1="125" y1="80" x2="795" y2="80" stroke="#5a6578" stroke-width="0.5" stroke-dasharray="4,4"/>
<text x="460" y="50" text-anchor="middle" fill="#5a6578" font-size="9" font-style="italic">~225 million km · 12.5 min one-way light time</text>

<rect x="150" y="68" width="72" height="34" rx="6" fill="rgba(255,112,67,0.15)" stroke="#ff7043" stroke-opacity="0.4"/>
<text x="186" y="84" text-anchor="middle" fill="#ff7043" font-size="8" font-weight="600">Areostat</text>
<text x="186" y="96" text-anchor="middle" fill="#5a6578" font-size="7">17,032 km</text>
<line x1="105" y1="80" x2="150" y2="80" stroke="#ff6b35" stroke-width="1.5" marker-end="url(#jmA)"/>

<rect x="270" y="68" width="72" height="34" rx="6" fill="rgba(255,112,67,0.15)" stroke="#ff7043" stroke-opacity="0.4"/>
<text x="306" y="84" text-anchor="middle" fill="#ff7043" font-size="8" font-weight="600">Polar Orbiter</text>
<text x="306" y="96" text-anchor="middle" fill="#5a6578" font-size="7">Optical ISL</text>
<line x1="222" y1="80" x2="270" y2="80" stroke="#ff6b35" stroke-width="1.5" marker-end="url(#jmA)"/>

<rect x="400" y="58" width="100" height="44" rx="6" fill="rgba(124,92,247,0.15)" stroke="#7c5cf7" stroke-opacity="0.4"/>
<text x="450" y="76" text-anchor="middle" fill="#7c5cf7" font-size="8" font-weight="600">ES-L4 Relay</text>
<text x="450" y="90" text-anchor="middle" fill="#5a6578" font-size="7">Lagrange Point</text>
<text x="450" y="100" text-anchor="middle" fill="#5a6578" font-size="7">150M km</text>
<line x1="342" y1="80" x2="400" y2="80" stroke="#7c5cf7" stroke-width="1.5" marker-end="url(#jmA)"/>

<rect x="550" y="68" width="80" height="34" rx="6" fill="rgba(66,165,245,0.15)" stroke="#42a5f5" stroke-opacity="0.4"/>
<text x="590" y="84" text-anchor="middle" fill="#42a5f5" font-size="8" font-weight="600">LEO Mesh</text>
<text x="590" y="96" text-anchor="middle" fill="#5a6578" font-size="7">48 satellites</text>
<line x1="500" y1="80" x2="550" y2="80" stroke="#42a5f5" stroke-width="1.5" marker-end="url(#jmA)"/>

<rect x="680" y="68" width="80" height="34" rx="6" fill="rgba(0,212,255,0.15)" stroke="#00d4ff" stroke-opacity="0.4"/>
<text x="720" y="84" text-anchor="middle" fill="#00d4ff" font-size="8" font-weight="600">DSN</text>
<text x="720" y="96" text-anchor="middle" fill="#5a6578" font-size="7">Goldstone</text>
<line x1="630" y1="80" x2="680" y2="80" stroke="#00d4ff" stroke-width="1.5" marker-end="url(#jmA)"/>
<line x1="760" y1="80" x2="795" y2="80" stroke="#00d4ff" stroke-width="1.5" marker-end="url(#jmA)"/>

<text x="20" y="200" fill="#8892a4" font-size="11" font-weight="600" letter-spacing="1.5">HOP DETAIL</text>
<rect x="20" y="215" width="125" height="80" rx="6" fill="rgba(255,112,67,0.08)" stroke="#ff7043" stroke-opacity="0.25"/>
<text x="82" y="232" text-anchor="middle" fill="#ff7043" font-size="9" font-weight="700">HOP 1</text><text x="82" y="246" text-anchor="middle" fill="#8892a4" font-size="8">Rover→UHF</text><text x="82" y="260" text-anchor="middle" fill="#5a6578" font-size="7">UHF 400 MHz</text><text x="82" y="274" text-anchor="middle" fill="#5a6578" font-size="7">~400 km · 2 Mbps</text>
<line x1="145" y1="255" x2="160" y2="255" stroke="#5a6578" stroke-width="1" marker-end="url(#jmA)"/>
<rect x="160" y="215" width="125" height="80" rx="6" fill="rgba(255,112,67,0.08)" stroke="#ff7043" stroke-opacity="0.25"/>
<text x="222" y="232" text-anchor="middle" fill="#ff7043" font-size="9" font-weight="700">HOP 2</text><text x="222" y="246" text-anchor="middle" fill="#8892a4" font-size="8">UHF→Areostat</text><text x="222" y="260" text-anchor="middle" fill="#5a6578" font-size="7">17,032 km alt</text><text x="222" y="274" text-anchor="middle" fill="#5a6578" font-size="7">256 kbps</text>
<line x1="285" y1="255" x2="300" y2="255" stroke="#5a6578" stroke-width="1" marker-end="url(#jmA)"/>
<rect x="300" y="215" width="125" height="80" rx="6" fill="rgba(255,112,67,0.08)" stroke="#ff7043" stroke-opacity="0.25"/>
<text x="362" y="232" text-anchor="middle" fill="#ff7043" font-size="9" font-weight="700">HOP 3</text><text x="362" y="246" text-anchor="middle" fill="#8892a4" font-size="8">Areostat→Polar</text><text x="362" y="260" text-anchor="middle" fill="#5a6578" font-size="7">Optical ISL</text><text x="362" y="274" text-anchor="middle" fill="#5a6578" font-size="7">10 Gbps</text>
<line x1="425" y1="255" x2="440" y2="255" stroke="#5a6578" stroke-width="1" marker-end="url(#jmA)"/>
<rect x="440" y="215" width="125" height="80" rx="6" fill="rgba(124,92,247,0.08)" stroke="#7c5cf7" stroke-opacity="0.25"/>
<text x="502" y="232" text-anchor="middle" fill="#7c5cf7" font-size="9" font-weight="700">HOP 4-5</text><text x="502" y="246" text-anchor="middle" fill="#8892a4" font-size="8">Deep Space</text><text x="502" y="260" text-anchor="middle" fill="#5a6578" font-size="7">1550nm laser</text><text x="502" y="274" text-anchor="middle" fill="#5a6578" font-size="7">225M km · 10-20 Mbps</text>
<line x1="565" y1="255" x2="580" y2="255" stroke="#5a6578" stroke-width="1" marker-end="url(#jmA)"/>
<rect x="580" y="215" width="125" height="80" rx="6" fill="rgba(66,165,245,0.08)" stroke="#42a5f5" stroke-opacity="0.25"/>
<text x="642" y="232" text-anchor="middle" fill="#42a5f5" font-size="9" font-weight="700">HOP 6</text><text x="642" y="246" text-anchor="middle" fill="#8892a4" font-size="8">LEO Mesh</text><text x="642" y="260" text-anchor="middle" fill="#5a6578" font-size="7">Optical ISL</text><text x="642" y="274" text-anchor="middle" fill="#5a6578" font-size="7">10 Gbps</text>
<line x1="705" y1="255" x2="720" y2="255" stroke="#5a6578" stroke-width="1" marker-end="url(#jmA)"/>
<rect x="720" y="215" width="125" height="80" rx="6" fill="rgba(63,185,80,0.08)" stroke="#3fb950" stroke-opacity="0.25"/>
<text x="782" y="232" text-anchor="middle" fill="#3fb950" font-size="9" font-weight="700">HOP 7</text><text x="782" y="246" text-anchor="middle" fill="#8892a4" font-size="8">DSN→JPL</text><text x="782" y="260" text-anchor="middle" fill="#5a6578" font-size="7">Ka-band</text><text x="782" y="274" text-anchor="middle" fill="#3fb950" font-size="8" font-weight="600">DELIVERED ✓</text>

<rect x="20" y="320" width="280" height="45" rx="6" fill="rgba(0,212,255,0.04)" stroke="#00d4ff" stroke-opacity="0.15"/>
<text x="160" y="340" text-anchor="middle" fill="#00d4ff" font-size="10" font-weight="600">Total Transit: ~13 min</text>
<text x="160" y="356" text-anchor="middle" fill="#8892a4" font-size="8">vs 12.5 min light-time!</text>
<rect x="320" y="320" width="280" height="45" rx="6" fill="rgba(63,185,80,0.04)" stroke="#3fb950" stroke-opacity="0.15"/>
<text x="460" y="340" text-anchor="middle" fill="#3fb950" font-size="10" font-weight="600">DTN Overhead: &lt;5%</text>
<text x="460" y="356" text-anchor="middle" fill="#8892a4" font-size="8">Store-and-forward adds minimal latency</text>
<rect x="620" y="320" width="280" height="45" rx="6" fill="rgba(124,92,247,0.04)" stroke="#7c5cf7" stroke-opacity="0.15"/>
<text x="760" y="340" text-anchor="middle" fill="#7c5cf7" font-size="10" font-weight="600">QKD Secured</text>
<text x="760" y="356" text-anchor="middle" fill="#8892a4" font-size="8">End-to-end quantum encryption</text>

<rect x="20" y="385" width="880" height="30" rx="6" fill="rgba(248,81,73,0.04)" stroke="#f85149" stroke-opacity="0.15"/>
<text x="460" y="405" text-anchor="middle" fill="#f85149" font-size="10" font-weight="600">⚡ If any link drops mid-transfer, the bundle is stored safely — zero data loss</text>
'''
    },
    'data_flow': {
        'title': 'Data Flow Diagram',
        'w': 920, 'h': 440,
        'svg': '''
<defs>
<marker id="dfA" markerWidth="7" markerHeight="5" refX="7" refY="2.5" orient="auto"><path d="M0,0 L7,2.5 L0,5" fill="none" stroke="#00d4ff" stroke-width="1.2"/></marker>
<marker id="dfG" markerWidth="7" markerHeight="5" refX="7" refY="2.5" orient="auto"><path d="M0,0 L7,2.5 L0,5" fill="none" stroke="#3fb950" stroke-width="1.2"/></marker>
</defs>
<text x="460" y="22" text-anchor="middle" fill="#8892a4" font-size="11" font-weight="600" letter-spacing="2">APPLICATION LAYER</text>
<rect x="20" y="32" width="200" height="50" rx="6" fill="rgba(0,212,255,0.08)" stroke="#00d4ff" stroke-opacity="0.3"/>
<text x="120" y="52" text-anchor="middle" fill="#00d4ff" font-size="10" font-weight="700">SOURCE NODE</text><text x="120" y="68" text-anchor="middle" fill="#8892a4" font-size="8">Science data (500 MB)</text>
<line x1="220" y1="57" x2="260" y2="57" stroke="#00d4ff" stroke-width="1.5" marker-end="url(#dfA)"/>
<rect x="260" y="32" width="200" height="50" rx="6" fill="rgba(124,92,247,0.08)" stroke="#7c5cf7" stroke-opacity="0.3"/>
<text x="360" y="52" text-anchor="middle" fill="#7c5cf7" font-size="10" font-weight="700">BUNDLE PROTOCOL</text><text x="360" y="68" text-anchor="middle" fill="#8892a4" font-size="8">BPv7 wraps data + metadata</text>
<line x1="460" y1="57" x2="500" y2="57" stroke="#7c5cf7" stroke-width="1.5" marker-end="url(#dfA)"/>
<rect x="500" y="32" width="200" height="50" rx="6" fill="rgba(63,185,80,0.08)" stroke="#3fb950" stroke-opacity="0.3"/>
<text x="600" y="52" text-anchor="middle" fill="#3fb950" font-size="10" font-weight="700">RL ROUTING</text><text x="600" y="68" text-anchor="middle" fill="#8892a4" font-size="8">Agent selects next hop</text>
<line x1="700" y1="57" x2="740" y2="57" stroke="#3fb950" stroke-width="1.5" marker-end="url(#dfG)"/>
<rect x="740" y="32" width="160" height="50" rx="6" fill="rgba(200,76,255,0.08)" stroke="#c84cff" stroke-opacity="0.3"/>
<text x="820" y="52" text-anchor="middle" fill="#c84cff" font-size="10" font-weight="700">QKD ENCRYPT</text><text x="820" y="68" text-anchor="middle" fill="#8892a4" font-size="8">BB84 key (256-bit)</text>

<text x="460" y="114" text-anchor="middle" fill="#8892a4" font-size="11" font-weight="600" letter-spacing="2">CONVERGENCE LAYER</text>
<rect x="100" y="124" width="250" height="45" rx="6" fill="rgba(255,107,53,0.08)" stroke="#ff6b35" stroke-opacity="0.3"/>
<text x="225" y="142" text-anchor="middle" fill="#ff6b35" font-size="10" font-weight="700">LTP SEGMENTATION</text><text x="225" y="158" text-anchor="middle" fill="#8892a4" font-size="8">RS encoding · retransmission</text>
<line x1="350" y1="147" x2="400" y2="147" stroke="#5a6578" stroke-width="1" marker-end="url(#dfA)"/>
<rect x="400" y="124" width="200" height="45" rx="6" fill="rgba(0,212,255,0.08)" stroke="#00d4ff" stroke-opacity="0.3"/>
<text x="500" y="142" text-anchor="middle" fill="#00d4ff" font-size="10" font-weight="700">STORE &amp; WAIT</text><text x="500" y="158" text-anchor="middle" fill="#8892a4" font-size="8">Buffer until link available</text>
<line x1="600" y1="147" x2="650" y2="147" stroke="#5a6578" stroke-width="1" marker-end="url(#dfG)"/>
<rect x="650" y="124" width="220" height="45" rx="6" fill="rgba(63,185,80,0.08)" stroke="#3fb950" stroke-opacity="0.3"/>
<text x="760" y="142" text-anchor="middle" fill="#3fb950" font-size="10" font-weight="700">FORWARD &amp; CUSTODY</text><text x="760" y="158" text-anchor="middle" fill="#8892a4" font-size="8">Transmit + custody transfer</text>

<text x="460" y="204" text-anchor="middle" fill="#8892a4" font-size="11" font-weight="600" letter-spacing="2">PHYSICAL LAYER</text>
<rect x="20" y="214" width="215" height="45" rx="6" fill="rgba(210,153,34,0.08)" stroke="#d29922" stroke-opacity="0.3"/>
<text x="127" y="234" text-anchor="middle" fill="#d29922" font-size="10" font-weight="700">MARS UHF</text><text x="127" y="250" text-anchor="middle" fill="#8892a4" font-size="8">400 MHz · 2 Mbps</text>
<line x1="235" y1="237" x2="275" y2="237" stroke="#5a6578" stroke-width="1" marker-end="url(#dfA)"/>
<rect x="275" y="214" width="215" height="45" rx="6" fill="rgba(255,107,53,0.08)" stroke="#ff6b35" stroke-opacity="0.3"/>
<text x="382" y="234" text-anchor="middle" fill="#ff6b35" font-size="10" font-weight="700">DEEP SPACE 1550nm</text><text x="382" y="250" text-anchor="middle" fill="#8892a4" font-size="8">10-200 Mbps · 225M km</text>
<line x1="490" y1="237" x2="530" y2="237" stroke="#5a6578" stroke-width="1" marker-end="url(#dfA)"/>
<rect x="530" y="214" width="215" height="45" rx="6" fill="rgba(0,212,255,0.08)" stroke="#00d4ff" stroke-opacity="0.3"/>
<text x="637" y="234" text-anchor="middle" fill="#00d4ff" font-size="10" font-weight="700">EARTH ISL</text><text x="637" y="250" text-anchor="middle" fill="#8892a4" font-size="8">Laser mesh · 10 Gbps</text>
<line x1="745" y1="237" x2="785" y2="237" stroke="#5a6578" stroke-width="1" marker-end="url(#dfG)"/>
<rect x="785" y="214" width="115" height="45" rx="6" fill="rgba(63,185,80,0.08)" stroke="#3fb950" stroke-opacity="0.3"/>
<text x="842" y="234" text-anchor="middle" fill="#3fb950" font-size="10" font-weight="700">DSN</text><text x="842" y="250" text-anchor="middle" fill="#8892a4" font-size="8">Ka-band</text>

<text x="460" y="294" text-anchor="middle" fill="#8892a4" font-size="11" font-weight="600" letter-spacing="2">DELIVERY</text>
<rect x="100" y="304" width="200" height="40" rx="6" fill="rgba(63,185,80,0.08)" stroke="#3fb950" stroke-opacity="0.3"/>
<text x="200" y="328" text-anchor="middle" fill="#3fb950" font-size="10" font-weight="700">LTP REASSEMBLY</text>
<line x1="300" y1="324" x2="360" y2="324" stroke="#5a6578" stroke-width="1" marker-end="url(#dfA)"/>
<rect x="360" y="304" width="200" height="40" rx="6" fill="rgba(200,76,255,0.08)" stroke="#c84cff" stroke-opacity="0.3"/>
<text x="460" y="328" text-anchor="middle" fill="#c84cff" font-size="10" font-weight="700">QKD DECRYPT</text>
<line x1="560" y1="324" x2="620" y2="324" stroke="#5a6578" stroke-width="1" marker-end="url(#dfG)"/>
<rect x="620" y="304" width="200" height="40" rx="6" fill="rgba(0,212,255,0.08)" stroke="#00d4ff" stroke-opacity="0.3"/>
<text x="720" y="328" text-anchor="middle" fill="#00d4ff" font-size="10" font-weight="700">APPLICATION ✓</text>

<rect x="20" y="370" width="880" height="35" rx="6" fill="rgba(0,212,255,0.04)" stroke="#00d4ff" stroke-opacity="0.15"/>
<text x="460" y="392" text-anchor="middle" fill="#8892a4" font-size="9">Each hop: <tspan fill="#00d4ff" font-weight="600">BPv7</tspan> → <tspan fill="#7c5cf7" font-weight="600">LTP</tspan> → <tspan fill="#ff6b35" font-weight="600">Physical</tspan> → <tspan fill="#3fb950" font-weight="600">Store/Forward</tspan> → <tspan fill="#c84cff" font-weight="600">Custody</tspan></text>
'''
    },
}


def main():
    os.makedirs(DIAGRAMS_DIR, exist_ok=True)
    for name, info in DIAGRAMS.items():
        svg_content = wrap_svg(info['svg'], info['w'], info['h'])
        svg_path = os.path.join(DIAGRAMS_DIR, f'{name}.svg')
        png_path = os.path.join(DIAGRAMS_DIR, f'{name}.png')
        with open(svg_path, 'w') as f:
            f.write(svg_content)
        print(f'  SVG: {svg_path}')
        cairosvg.svg2png(bytestring=svg_content.encode(), write_to=png_path, output_width=info['w'] * 2, output_height=info['h'] * 2)
        print(f'  PNG: {png_path}')

    print(f'\nDone! {len(DIAGRAMS)} diagrams generated in {DIAGRAMS_DIR}')


if __name__ == '__main__':
    main()
