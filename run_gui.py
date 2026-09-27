#!/usr/bin/env python3
"""Launcher for the Voice Assistant Menu Bar App."""

import os
import sys

# Ensure project root is in sys.path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.gui.menu_bar import run_menu_app

if __name__ == "__main__":
    run_menu_app()
