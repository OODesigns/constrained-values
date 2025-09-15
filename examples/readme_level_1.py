"""
Level 1: Simple Range Validation

The most basic use case is ensuring a value falls within a specific range. 
Instead of passing an integer around and checking its bounds everywhere, 
we create an `Age` type by defining a class.
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))