import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/cmd", tags=["cmd"])

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
VENV_PYTHON = str(PROJECT_ROOT / "venv" / "bin" / "python3")

CATEGORIES = {
    "scripts": {
        "label": "Shell Scripts",
        "commands": [
            {
                "id": "init",
                "label": "Initialize Environment",
                "description": "Set up virtual environment and install dependencies",
                "cmd": "./scripts/init.sh",
                "cwd": str(PROJECT_ROOT),
                "icon": "setup",
            },
            {
                "id": "init-dev",
                "label": "Initialize (Dev Mode)",
                "description": "Set up venv with dev tools (linting, formatting)",
                "cmd": "./scripts/init.sh --dev",
                "cwd": str(PROJECT_ROOT),
                "icon": "setup",
            },
            {
                "id": "test",
                "label": "Run Test Suite",
                "description": "Run all 189 tests",
                "cmd": "./scripts/run_tests.sh",
                "cwd": str(PROJECT_ROOT),
                "icon": "test",
            },
            {
                "id": "test-verbose",
                "label": "Run Tests (Verbose)",
                "description": "Run tests with verbose output",
                "cmd": "./scripts/run_tests.sh -v",
                "cwd": str(PROJECT_ROOT),
                "icon": "test",
            },
            {
                "id": "lint",
                "label": "Code Quality Check",
                "description": "Run ruff linter and style checks",
                "cmd": "./scripts/lint.sh",
                "cwd": str(PROJECT_ROOT),
                "icon": "lint",
            },
            {
                "id": "lint-fix",
                "label": "Auto-Fix Code Style",
                "description": "Auto-fix code style issues",
                "cmd": "./scripts/lint.sh --fix",
                "cwd": str(PROJECT_ROOT),
                "icon": "lint",
            },
            {
                "id": "clean",
                "label": "Clean Artifacts",
                "description": "Clean build artifacts and caches",
                "cmd": "./scripts/clean.sh",
                "cwd": str(PROJECT_ROOT),
                "icon": "clean",
            },
        ],
    },
    "modules": {
        "label": "Python Modules",
        "commands": [
            {
                "id": "mod-link-budget",
                "label": "Optical Link Budget",
                "description": "Optical link budget calculations",
                "cmd": f"{VENV_PYTHON} src/infrastructure/link_budget.py",
                "cwd": str(PROJECT_ROOT),
                "icon": "link",
            },
            {
                "id": "mod-rf-budget",
                "label": "RF Link Budget",
                "description": "RF link budget (Ka/X/S/UHF bands)",
                "cmd": f"{VENV_PYTHON} src/infrastructure/rf_link_budget.py",
                "cwd": str(PROJECT_ROOT),
                "icon": "link",
            },
            {
                "id": "mod-rl-agent",
                "label": "RL Routing Agent",
                "description": "Reinforcement learning routing demo",
                "cmd": f"{VENV_PYTHON} src/routing/rl_agent.py",
                "cwd": str(PROJECT_ROOT),
                "icon": "routing",
            },
            {
                "id": "mod-bundle",
                "label": "Bundle Protocol",
                "description": "BPv7 bundle protocol demo",
                "cmd": f"{VENV_PYTHON} src/routing/bundle.py",
                "cwd": str(PROJECT_ROOT),
                "icon": "bundle",
            },
            {
                "id": "mod-forwarding",
                "label": "Store-and-Forward Engine",
                "description": "DTN forwarding engine demo",
                "cmd": f"{VENV_PYTHON} src/routing/forwarding_engine.py",
                "cwd": str(PROJECT_ROOT),
                "icon": "routing",
            },
            {
                "id": "mod-prioritization",
                "label": "Priority Scheduler",
                "description": "Data prioritization scheduler demo",
                "cmd": f"{VENV_PYTHON} src/routing/prioritization.py",
                "cwd": str(PROJECT_ROOT),
                "icon": "routing",
            },
            {
                "id": "mod-training",
                "label": "RL Training Loop",
                "description": "Reinforcement learning training demo",
                "cmd": f"{VENV_PYTHON} src/routing/training.py",
                "cwd": str(PROJECT_ROOT),
                "icon": "routing",
            },
            {
                "id": "mod-qkd",
                "label": "QKD Protocol (BB84/E91)",
                "description": "Quantum key distribution simulation",
                "cmd": f"{VENV_PYTHON} src/security/qkd.py",
                "cwd": str(PROJECT_ROOT),
                "icon": "security",
            },
            {
                "id": "mod-repeater",
                "label": "Quantum Repeater Chain",
                "description": "Multi-hop quantum repeater demo",
                "cmd": f"{VENV_PYTHON} src/security/repeater_chain.py",
                "cwd": str(PROJECT_ROOT),
                "icon": "security",
            },
            {
                "id": "mod-privacy",
                "label": "Privacy Amplification",
                "description": "CASCADE reconciliation demo",
                "cmd": f"{VENV_PYTHON} src/security/privacy_amplification.py",
                "cwd": str(PROJECT_ROOT),
                "icon": "security",
            },
            {
                "id": "mod-contact",
                "label": "Contact Windows",
                "description": "Contact window prediction",
                "cmd": f"{VENV_PYTHON} src/orbital/contact_windows.py",
                "cwd": str(PROJECT_ROOT),
                "icon": "orbital",
            },
            {
                "id": "mod-doppler",
                "label": "Doppler Shift",
                "description": "Classical and relativistic Doppler calculations",
                "cmd": f"{VENV_PYTHON} src/orbital/doppler.py",
                "cwd": str(PROJECT_ROOT),
                "icon": "orbital",
            },
            {
                "id": "mod-topology",
                "label": "Network Topology",
                "description": "5-tier network topology (241 nodes)",
                "cmd": f"{VENV_PYTHON} src/orbital/topology.py",
                "cwd": str(PROJECT_ROOT),
                "icon": "orbital",
            },
            {
                "id": "mod-radiation",
                "label": "Radiation Hardening",
                "description": "Radiation tolerance simulation",
                "cmd": f"{VENV_PYTHON} src/computing/radiation.py",
                "cwd": str(PROJECT_ROOT),
                "icon": "sim",
            },
            {
                "id": "mod-simulator",
                "label": "Simulation Engine",
                "description": "Full simulation engine",
                "cmd": f"{VENV_PYTHON} src/simulation/simulator.py",
                "cwd": str(PROJECT_ROOT),
                "icon": "sim",
            },
            {
                "id": "mod-policy",
                "label": "Policy Engine",
                "description": "Policy-based routing engine",
                "cmd": f"{VENV_PYTHON} src/simulation/policy_engine.py",
                "cwd": str(PROJECT_ROOT),
                "icon": "sim",
            },
        ],
    },
}


def _build_flat_index() -> dict[str, dict]:
    index = {}
    for cat_key, cat in CATEGORIES.items():
        for cmd in cat["commands"]:
            index[cmd["id"]] = {**cmd, "category": cat_key, "category_label": cat["label"]}
    return index


_FLAT = _build_flat_index()


@router.get("/catalog")
def get_catalog():
    return {
        "categories": {
            k: {"label": v["label"], "commands": v["commands"]}
            for k, v in CATEGORIES.items()
        },
        "total": len(_FLAT),
    }


@router.get("/catalog/{cmd_id}")
def get_command(cmd_id: str):
    if cmd_id not in _FLAT:
        from fastapi import HTTPException
        raise HTTPException(404, f"Command '{cmd_id}' not found")
    return _FLAT[cmd_id]


@router.get("/run/{cmd_id}")
async def run_command(cmd_id: str, args: Optional[str] = Query(default=None)):
    if cmd_id not in _FLAT:
        from fastapi import HTTPException
        raise HTTPException(404, f"Command '{cmd_id}' not found")

    entry = _FLAT[cmd_id]
    cmd_str = entry["cmd"]
    if args:
        cmd_str = f"{cmd_str} {args}"

    async def stream():
        yield f"data: {json.dumps({'type': 'meta', 'cmd': cmd_str, 'id': cmd_id, 'label': entry['label']})}\n\n"

        shell = True if cmd_str.startswith("./") else False
        cmd_list = cmd_str if shell else cmd_str.split()

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd_list,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=entry["cwd"],
                env={**os.environ, "PYTHONUNBUFFERED": "1", "TERM": "dumb"},
            )
        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'text': str(exc)})}\n\n"
            return

        buf = b""
        try:
            while True:
                chunk = await proc.stdout.read(512)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    text = line.decode("utf-8", errors="replace")
                    yield f"data: {json.dumps({'type': 'stdout', 'text': text})}\n\n"
            if buf:
                text = buf.decode("utf-8", errors="replace")
                yield f"data: {json.dumps({'type': 'stdout', 'text': text})}\n\n"
        except asyncio.CancelledError:
            proc.kill()
            return

        rc = await proc.wait()
        yield f"data: {json.dumps({'type': 'done', 'exit_code': rc})}\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
