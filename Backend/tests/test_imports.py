"""
Quick test to verify all imports work correctly from tests/ folder
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("=" * 70)
print("Import Verification Test")
print("=" * 70)
print(f"\nProject root: {project_root}")
print(f"Python path includes project root: {project_root in sys.path}")

# Test all critical imports
imports_to_test = [
    ("Supervisor Agent", "from src.supervisor_agent import SupervisorAgent"),
    ("Supervisor A2A", "from src.supervisor_agent_a2a import SupervisorAgentA2A"),
    ("Supervisor HITL", "from src.supervisor_agent_hitl import SupervisorAgentHITL"),
    ("Product Agent", "from src.product_agent import ProductAgent"),
    ("Business Agent", "from src.business_agent import BusinessAgent"),
    ("A2A Broker", "from src.a2a_broker import get_broker"),
    ("HITL Manager", "from src.hitl_manager import get_hitl_manager"),
    ("RAG System", "from src.rag_system import get_rag_system"),
    ("LangGraph Agent", "from src.langgraph_agent import BeautySearchAgent"),
]

print("\nTesting imports:")
print("-" * 70)

passed = 0
failed = 0

for name, import_stmt in imports_to_test:
    try:
        exec(import_stmt)
        print(f"✓ {name:30s} - OK")
        passed += 1
    except Exception as e:
        print(f"✗ {name:30s} - FAILED: {str(e)}")
        failed += 1

print("-" * 70)
print(f"\nResults: {passed} passed, {failed} failed")

if failed == 0:
    print("\n✓ All imports successful! Tests can run from tests/ folder.")
else:
    print(f"\n✗ {failed} imports failed. Check the errors above.")

print("=" * 70)
