"""Command catalog (read-only).

This router exposes a *reference* catalog of the project's scripts and module
demos: for each command it returns the exact shell command to copy/paste, a
description of what it does, and a summary of the expected output. It does NOT
execute anything server-side — commands are meant to be run by the user in
their own terminal. (An earlier version executed commands via an unauthenticated
SSE endpoint; that was removed to eliminate the remote-execution / CSRF surface.)
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/cmd", tags=["cmd"])

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

CATEGORIES = {
    "scripts": {
        "label": "Shell Scripts",
        "commands": [
            {
                "id": "init", "label": "Initialize Environment", "icon": "setup",
                "cmd": "./scripts/init.sh",
                "description": "Creates a Python virtual environment and installs runtime dependencies (pytest).",
                "expected": "Progress messages while the venv is created and pip installs packages, ending with a confirmation that the environment is ready.",
            },
            {
                "id": "init-dev", "label": "Initialize (Dev Mode)", "icon": "setup",
                "cmd": "./scripts/init.sh --dev",
                "description": "Same as init, plus developer tooling (ruff, black, isort, mypy, pytest-cov).",
                "expected": "Venv created and both runtime and dev dependencies installed; ends with a 'dev environment ready' style message.",
            },
            {
                "id": "test", "label": "Run Test Suite", "icon": "test",
                "cmd": "./scripts/run_tests.sh",
                "description": "Runs the full pytest suite across all 12 test files.",
                "expected": "A row of dots for passing tests, ending with '189 passed in <n>s'.",
            },
            {
                "id": "test-verbose", "label": "Run Tests (Verbose)", "icon": "test",
                "cmd": "./scripts/run_tests.sh -v",
                "description": "Runs the test suite with one line per test case.",
                "expected": "Each test id printed with PASSED, ending with '189 passed'.",
            },
            {
                "id": "lint", "label": "Code Quality Check", "icon": "lint",
                "cmd": "./scripts/lint.sh",
                "description": "Runs ruff and PEP 8 style checks (read-only, no changes).",
                "expected": "'All checks passed!' when clean, or a list of files/lines with style findings.",
            },
            {
                "id": "lint-fix", "label": "Auto-Fix Code Style", "icon": "lint",
                "cmd": "./scripts/lint.sh --fix",
                "description": "Auto-formats and fixes style issues in place (ruff/black/isort).",
                "expected": "A summary of files reformatted and issues fixed.",
            },
            {
                "id": "clean", "label": "Clean Artifacts", "icon": "clean",
                "cmd": "./scripts/clean.sh",
                "description": "Removes __pycache__, .pytest_cache, and build artifacts.",
                "expected": "A list of removed directories/files, ending with a 'cleaned' confirmation.",
            },
        ],
    },
    "modules": {
        "label": "Python Modules",
        "commands": [
            {
                "id": "mod-link-budget", "label": "Optical Link Budget", "icon": "link",
                "cmd": "python3 src/infrastructure/link_budget.py",
                "description": "Computes the 1550 nm optical link budget for Earth–Mars at min/avg/max distance.",
                "expected": "A table of EIRP, free-space path loss, received power and link margin (dB) for each distance scenario.",
            },
            {
                "id": "mod-rf-budget", "label": "RF Link Budget", "icon": "link",
                "cmd": "python3 src/infrastructure/rf_link_budget.py",
                "description": "Computes RF link budgets across the Ka, X, S and UHF bands.",
                "expected": "Per-band link-budget breakdown with gains, losses and resulting margin.",
            },
            {
                "id": "mod-rl-agent", "label": "RL Routing Agent", "icon": "routing",
                "cmd": "python3 src/routing/rl_agent.py",
                "description": "Q-learning routing agent making epsilon-greedy forwarding decisions.",
                "expected": "Observed network states, chosen actions and Q-values as the agent routes sample bundles.",
            },
            {
                "id": "mod-bundle", "label": "Bundle Protocol", "icon": "bundle",
                "cmd": "python3 src/routing/bundle.py",
                "description": "Creates a BPv7 bundle and prints its primary block and metadata.",
                "expected": "'Created: Bundle[…] mars.surface.rover-01 -> earth.control.moc …' followed by the serialized bundle fields.",
            },
            {
                "id": "mod-forwarding", "label": "Store-and-Forward Engine", "icon": "routing",
                "cmd": "python3 src/routing/forwarding_engine.py",
                "description": "DTN store-and-forward engine with a priority queue and custody tracking.",
                "expected": "Bundles enqueued by priority, custody-accept/forward events, and a final delivery summary.",
            },
            {
                "id": "mod-prioritization", "label": "Priority Scheduler", "icon": "routing",
                "cmd": "python3 src/routing/prioritization.py",
                "description": "Mission data prioritization: compression, deadline-aware QoS scheduling, emergency preemption.",
                "expected": "A compression-ratio table, a prioritized schedule (5/6 delivered, ~100% link use, bulk fragmented), and an emergency-preemption log.",
            },
            {
                "id": "mod-training", "label": "RL Training Loop", "icon": "routing",
                "cmd": "python3 src/routing/training.py",
                "description": "Trains the RL routing agent over many simulated episodes.",
                "expected": "Per-episode reward trending upward with a convergence message once the policy stabilizes.",
            },
            {
                "id": "mod-qkd", "label": "QKD Protocol (BB84/E91)", "icon": "security",
                "cmd": "python3 src/security/qkd.py",
                "description": "Runs the BB84 and E91 quantum key distribution protocols.",
                "expected": "Sifted key length and QBER, with a 'secure' verdict when QBER < 11% (and 'eavesdropper detected' above it).",
            },
            {
                "id": "mod-repeater", "label": "Quantum Repeater Chain", "icon": "security",
                "cmd": "python3 src/security/repeater_chain.py",
                "description": "Multi-hop quantum repeater chain using entanglement swapping.",
                "expected": "Per-hop entanglement swapping steps and the resulting end-to-end fidelity over the chain.",
            },
            {
                "id": "mod-privacy", "label": "Privacy Amplification", "icon": "security",
                "cmd": "python3 src/security/privacy_amplification.py",
                "description": "CASCADE reconciliation, universal hashing and the Csiszár–Körner bound.",
                "expected": "Reconciliation rounds, estimated leaked bits, and the final secure key length after amplification.",
            },
            {
                "id": "mod-contact", "label": "Contact Windows", "icon": "orbital",
                "cmd": "python3 src/orbital/contact_windows.py",
                "description": "Predicts Earth–Mars communication windows over the synodic period.",
                "expected": "Distance and one-way light time, a list of contact windows, and the solar-conjunction blackout period.",
            },
            {
                "id": "mod-doppler", "label": "Doppler Shift", "icon": "orbital",
                "cmd": "python3 src/orbital/doppler.py",
                "description": "Classical and relativistic Doppler shift for a given relative velocity.",
                "expected": "Classical and relativistic frequency-shift values and the difference between them.",
            },
            {
                "id": "mod-topology", "label": "Network Topology", "icon": "orbital",
                "cmd": "python3 src/orbital/topology.py",
                "description": "Builds the full 5-tier, 241-node interplanetary topology.",
                "expected": "A per-tier node count summary totaling 241 nodes across the five tiers.",
            },
            {
                "id": "mod-radiation", "label": "Radiation Hardening", "icon": "sim",
                "cmd": "python3 src/computing/radiation.py",
                "description": "Radiation effects and mitigation over an Earth–Mars transit (SEU/TID, TMR, ECC, scrubbing, FDIR).",
                "expected": "A transit summary (~37,000 raw upsets reduced to ~186 uncorrectable, ~200× protection), a TMR reliability table, and an FDIR watchdog walkthrough.",
            },
            {
                "id": "mod-simulator", "label": "Simulation Engine", "icon": "sim",
                "cmd": "python3 src/simulation/simulator.py",
                "description": "End-to-end mission simulation integrating topology, forwarding and bundles.",
                "expected": "A simulated Earth–Mars run with delivery metrics (delay, hops, delivery ratio).",
            },
            {
                "id": "mod-policy", "label": "Policy Engine", "icon": "sim",
                "cmd": "python3 src/simulation/policy_engine.py",
                "description": "Applies the 5 default routing policies (congestion control, emergency fast-path, etc.).",
                "expected": "Each policy listed with the routing decisions it produces for sample traffic.",
            },
        ],
    },
}


def _build_flat_index() -> dict:
    index = {}
    for cat_key, cat in CATEGORIES.items():
        for cmd in cat["commands"]:
            index[cmd["id"]] = {**cmd, "category": cat_key, "category_label": cat["label"]}
    return index


_FLAT = _build_flat_index()


@router.get("/catalog")
def get_catalog():
    """Return the full command reference catalog (read-only)."""
    return {
        "categories": {
            k: {"label": v["label"], "commands": v["commands"]}
            for k, v in CATEGORIES.items()
        },
        "total": len(_FLAT),
    }


@router.get("/catalog/{cmd_id}")
def get_command(cmd_id: str):
    """Return a single command's reference entry."""
    if cmd_id not in _FLAT:
        raise HTTPException(404, f"Command '{cmd_id}' not found")
    return _FLAT[cmd_id]
