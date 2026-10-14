"""
tests/conftest.py – Pytest Configuration & Fixtures
====================================================
Ensures backend directory is on sys.path for all test runs.
"""

import sys
from pathlib import Path

# Add backend root directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
