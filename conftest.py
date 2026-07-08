"""
Root conftest.py — adds src/ and backend/ to sys.path for all test discovery.

This eliminates the need for individual test files to do
``sys.path.insert(0, ...)`` and allows backend API tests to import
both the simulation core (``src/``) and the FastAPI app (``backend/``).
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _subdir in ("src", "backend"):
    _path = os.path.join(_HERE, _subdir)
    if _path not in sys.path:
        sys.path.insert(0, _path)
