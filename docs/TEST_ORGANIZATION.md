# Test Organization

## Overview

All test files have been organized into the `tests/` folder for better project structure and maintainability.

## Test Folder Structure

```
yelp_mcp/
├── tests/
│   ├── __init__.py                      # Makes tests a package
│   ├── test_path_setup.py               # Verify imports work
│   ├── test_a2a_simple.py               # A2A communication basics
│   ├── test_a2a_communication.py        # A2A comprehensive tests
│   ├── test_hitl_system.py              # HITL approval workflow
│   ├── test_supervisor.py               # Original supervisor tests
│   ├── test_beauty_search_agent.py      # Beauty search agent tests
│   ├── test_product_comparison.py       # Product comparison tests
│   ├── test_connection.py               # Yelp API connection test
│   ├── test_app.py                      # Flask app test
│   ├── test_agent.py                    # Unit tests (pytest)
│   ├── test_yelp_client.py              # Yelp client tests
│   ├── verify_setup.py                  # Complete setup verification
│   └── demo_comparison.py               # Botox vs Evolus demo
```

## Running Tests

### From Project Root

All tests can be run from the project root directory:

```bash
# Quick verification
python tests/test_path_setup.py

# A2A Tests
python tests/test_a2a_simple.py
python tests/test_a2a_communication.py

# HITL Tests
python tests/test_hitl_system.py

# Original System Tests
python tests/test_supervisor.py
python tests/test_beauty_search_agent.py

# Product Tests
python tests/test_product_comparison.py
python tests/demo_comparison.py

# API Tests
python tests/test_connection.py
python tests/test_app.py

# Full Verification
python tests/verify_setup.py
```

### From Tests Folder

You can also run tests from within the `tests/` folder:

```bash
cd tests
python test_a2a_simple.py
python test_hitl_system.py
python test_supervisor.py
```

## Import Path Configuration

All test files have been updated with the following import path setup to ensure they can find the `src/` module:

```python
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now imports work from both project root and tests/ folder
from src.supervisor_agent import SupervisorAgent
from src.rag_system import get_rag_system
```

This configuration allows tests to:
- ✅ Run from project root: `python tests/test_name.py`
- ✅ Run from tests folder: `cd tests && python test_name.py`
- ✅ Import all `src/` modules correctly
- ✅ Work in any IDE that runs tests from either location

## Test Categories

### 1. Path & Setup Tests
- **test_path_setup.py** - Verifies Python path configuration works
- **verify_setup.py** - Complete system verification (API keys, dependencies, etc.)

### 2. A2A Communication Tests
- **test_a2a_simple.py** - Basic A2A functionality (no Unicode issues)
- **test_a2a_communication.py** - Comprehensive A2A testing

### 3. HITL Approval Tests
- **test_hitl_system.py** - Human approval workflow tests

### 4. Agent Tests
- **test_supervisor.py** - Original supervisor agent
- **test_beauty_search_agent.py** - Enhanced beauty search agent
- **test_agent.py** - Unit tests (pytest-based)

### 5. Product & RAG Tests
- **test_product_comparison.py** - Botox vs Evolus comparison
- **demo_comparison.py** - Simple RAG-based demo

### 6. API & Connection Tests
- **test_connection.py** - Yelp API connectivity
- **test_app.py** - Flask app endpoints
- **test_yelp_client.py** - Yelp client functionality

## Migration Notes

### What Changed
- All test files moved from project root to `tests/` folder
- Added Python path configuration to all test files
- Updated README.md with new test instructions
- Created test_path_setup.py for quick verification

### What Stayed the Same
- All original test files preserved
- Test functionality unchanged
- No changes to src/ code
- All imports still work

### Files Updated
The following test files were updated with path configuration:

1. test_a2a_simple.py
2. test_a2a_communication.py
3. test_hitl_system.py
4. test_supervisor.py
5. test_beauty_search_agent.py
6. test_product_comparison.py
7. test_connection.py
8. verify_setup.py
9. demo_comparison.py

### Files Not Updated
The following files didn't need path updates (no src imports):
- test_app.py (simple Flask test)
- test_agent.py (pytest with different structure)
- test_yelp_client.py (already had correct imports)

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: No module named 'src'`:

1. **Check you're using updated test files** - All files should have path setup code
2. **Verify project structure** - Ensure `src/` folder exists in project root
3. **Run path test** - `python tests/test_path_setup.py` should show "Path setup successful!"

### Unicode Errors on Windows

If you see Unicode encoding errors:
- Use `test_a2a_simple.py` instead of `test_a2a_communication.py`
- Both files test A2A, but simple version avoids emoji characters

### Test Timeouts

Some tests may take time due to:
- API calls to Yelp, OpenAI, or Anthropic
- RAG indexing operations
- LangGraph initialization

This is normal. Tests with actual API calls may take 30-60 seconds.

## Best Practices

### Running Specific Tests

```bash
# Quick smoke test
python tests/test_path_setup.py

# Test one feature
python tests/test_a2a_simple.py

# Full system test
python tests/verify_setup.py
```

### Before Committing Code

Run these tests to verify everything works:

```bash
python tests/test_path_setup.py     # Imports work
python tests/test_supervisor.py     # Original system works
python tests/test_a2a_simple.py     # A2A works
python tests/test_hitl_system.py    # HITL works
```

### CI/CD Integration

For automated testing:

```bash
# Run all tests that don't require API calls
python tests/test_path_setup.py

# Run with API keys in environment
export YELP_API_KEY=xxx
export OPENAI_API_KEY=xxx
python tests/verify_setup.py
```

## Summary

✅ **All test files organized in tests/ folder**
✅ **Path configuration added to all test files**
✅ **Tests can run from project root or tests/ folder**
✅ **README.md updated with test instructions**
✅ **Backward compatible - all existing tests still work**

---

**Updated**: 2025-10-10
**Status**: ✅ Complete
