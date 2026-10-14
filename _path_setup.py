# foodwise-ai/_path_setup.py
# Ensures the project root is on sys.path so `src.*` imports work
# when pages are run directly by Streamlit (without `pip install -e .`).
# Every page imports this module before importing from src.
import sys
import os

_root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)
