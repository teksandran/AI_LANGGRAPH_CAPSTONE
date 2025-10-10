"""
Simple path setup verification
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("Path Setup Test")
print("=" * 60)
print(f"Current file: {__file__}")
print(f"Project root: {project_root}")
print(f"Project root in sys.path: {project_root in sys.path}")

# Check if src directory exists
src_path = os.path.join(project_root, 'src')
print(f"\nSrc directory exists: {os.path.exists(src_path)}")
print(f"Src path: {src_path}")

# List src contents
if os.path.exists(src_path):
    src_files = [f for f in os.listdir(src_path) if f.endswith('.py')]
    print(f"\nPython files in src/: {len(src_files)}")
    for f in sorted(src_files)[:10]:  # Show first 10
        print(f"  - {f}")

print("\n[OK] Path setup successful!")
print("=" * 60)
