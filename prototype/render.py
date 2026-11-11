#!/usr/bin/env python3
"""Backward-compatible entry point. The renderer now lives at compose/render.py."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent.parent / "compose" / "render.py"), run_name="__main__")
