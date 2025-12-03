# setup.py - Python version enforcer
import sys

# Force Python 3.11
required_python = (3, 11, 0)
current_python = sys.version_info[:3]

if current_python < required_python:
    print(f"❌ Python {current_python[0]}.{current_python[1]}.{current_python[2]} not supported")
    print(f"✅ Required: Python {required_python[0]}.{required_python[1]}.{required_python[2]}+")
    sys.exit(1)

print(f"✅ Python {current_python[0]}.{current_python[1]}.{current_python[2]} is supported")