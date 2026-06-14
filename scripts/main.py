"""
Application entry point.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.gui import main_gui

if __name__ == "__main__":
    main_gui()