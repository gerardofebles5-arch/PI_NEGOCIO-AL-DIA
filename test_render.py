#!/usr/bin/env python3
"""
Archivo de prueba para verificar que el entorno de Render funciona correctamente
"""
import sys
import os

print("Python version:", sys.version)
print("Working directory:", os.getcwd())
print("Python executable:", sys.executable)

# Test basic imports
try:
    import flask
    print("Flask: OK")
except ImportError as e:
    print(f"Flask: ERROR - {e}")

try:
    import numpy
    print("NumPy: OK")
except ImportError as e:
    print(f"NumPy: ERROR - {e}")

try:
    import PIL
    print("Pillow: OK")
except ImportError as e:
    print(f"Pillow: ERROR - {e}")

print("Test completed successfully!")
