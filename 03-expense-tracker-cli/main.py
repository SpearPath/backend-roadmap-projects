#!/usr/bin/env python3
"""
Expense Tracker CLI Entry Point
Run directly with:
    python main.py <command> [options]
"""
import sys
from pathlib import Path

# Add project root to sys.path so src is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.cli import run_cli

if __name__ == "__main__":
    sys.exit(run_cli())
