# Multi-Agent Beauty Search System with A2A & HITL

A production-ready multi-agent system for beauty and aesthetic product search with **Agent-to-Agent (A2A) communication** and **Human-in-the-Loop (HITL) approval** capabilities.

## 🎯 What This System Does

- **Product Information**: Search for Botox, Evolus, and other aesthetic products
- **Business Search**: Find beauty salons, spas, and providers via Yelp API
- **Agent Collaboration**: Agents communicate directly to solve complex queries
- **Human Oversight**: Human approval workflow for safety and compliance
- **RAG System**: Retrieval-Augmented Generation for product knowledge
- **RESTful API**: Easy integration with web and mobile apps

## 🚀 Quick Start

### Prerequisites

```bash
# Required API keys in .env file
YELP_API_KEY=your_yelp_key
OPENAI_API_KEY=your_openai_key
# OR
ANTHROPIC_API_KEY=your_anthropic_key
```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Run the API Server

```bash
# Start server on http://localhost:5000
python api_server.py
```

### Test the System

```bash
# All tests are now in tests/ folder
python tests/test_path_setup.py      # Verify setup
python tests/test_a2a_simple.py      # Test A2A
python tests/test_hitl_system.py     # Test HITL

# Or run from tests/ folder
cd tests
python test_a2a_simple.py
```

## 📚 Documentation

All documentation is in the [`docs/`](docs/) folder:

### 🌟 Start Here
- **[Executive Summary](docs/EXECUTIVE_SUMMARY.md)** 🎯 **NEW** - Problem, solution, use cases & ROI
- **[High-Level Overview](docs/HIGH_LEVEL_OVERVIEW.md)** - Architecture, implementation & workflows
- **[Quick Start](docs/QUICK_START.md)** - Get running in 5 minutes
- **[Documentation Index](docs/INDEX.md)** - Complete documentation map (19 docs)

### Getting Started
- **[How to Run](docs/HOW_TO_RUN.md)** - Detailed setup
- **[Sample Queries](docs/SAMPLE_QUERIES.md)** - Example queries

### Architecture
- **[System Overview](docs/COMPLETE_SYSTEM_SUMMARY.md)** - Complete system guide
- **[Integration Architecture](docs/INTEGRATION_ARCHITECTURE.md)** - How components connect

### Features
- **[A2A Communication](docs/A2A_DOCUMENTATION.md)** - Agent collaboration
- **[HITL Approval](docs/HITL_DOCUMENTATION.md)** - Human oversight
- **[Product Search](docs/PRODUCT_SEARCH_GUIDE.md)** - RAG system
- **[LangSmith Tracing](docs/LANGSMITH_GUIDE.md)** - Monitoring

### Integration
- **[React/Frontend](docs/REACT_API_GUIDE.md)** - UI integration
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues

## 🌟 Key Features

### Agent-to-Agent Communication

```python
from src.supervisor_agent_a2a import SupervisorAgentA2A

supervisor = SupervisorAgentA2A(yelp_api_key=key, enable_a2a=True)
result = await supervisor.run_with_a2a("What is Botox and where in NYC?")
```

### Human-in-the-Loop Approval

```python
from src.supervisor_agent_hitl import SupervisorAgentHITL

supervisor = SupervisorAgentHITL(
    yelp_api_key=key,
    enable_a2a=True,
    enable_hitl=True
)
result = await supervisor.run_with_hitl("What is Botox?")
```

### 100% Backward Compatible

```python
from src.supervisor_agent import SupervisorAgent

supervisor = SupervisorAgent(yelp_api_key=key)
response = await supervisor.run("What is Botox?")
```

## 📊 API Endpoints

- `GET /api/health` - Health check
- `POST /api/query` - Main query endpoint
- `GET /api/hitl/pending` - Get pending approvals
- `POST /api/hitl/approve/<id>` - Approve request

See [React API Guide](docs/REACT_API_GUIDE.md) for complete API documentation.

## 🧪 Testing

All test files are in the `tests/` folder:

```bash
# Run from project root
python tests/test_path_setup.py          # Verify imports work
python tests/test_a2a_simple.py          # Test A2A communication
python tests/test_hitl_system.py         # Test HITL approval
python tests/test_supervisor.py          # Test original supervisor
python tests/verify_setup.py             # Full system verification

# Or change to tests/ folder
cd tests
python test_a2a_simple.py
```

### Available Tests

- `test_path_setup.py` - Verify Python path configuration
- `test_a2a_simple.py` - A2A communication basics
- `test_a2a_communication.py` - A2A comprehensive tests
- `test_hitl_system.py` - HITL approval workflow
- `test_supervisor.py` - Original supervisor agent
- `test_beauty_search_agent.py` - Beauty search agent
- `test_product_comparison.py` - Product comparison
- `test_connection.py` - Yelp API connection
- `verify_setup.py` - Complete system check
- `demo_comparison.py` - Botox vs Evolus demo

## 📦 Project Structure

```
yelp_mcp/
├── src/                 # Source code
├── docs/                # Documentation
├── examples/            # Examples
├── tests/              # Tests
├── api_server.py       # API server
└── README.md           # This file
```

## 🔧 Configuration

```python
# All features
supervisor = SupervisorAgentHITL(
    yelp_api_key=key,
    enable_a2a=True,
    enable_hitl=True
)

# A2A only
supervisor = SupervisorAgentA2A(yelp_api_key=key, enable_a2a=True)

# Original
supervisor = SupervisorAgent(yelp_api_key=key)
```

---

**Version**: 2.0 | **Status**: ✅ Production Ready | **Updated**: 2025-10-09

For detailed documentation, see the [`docs/`](docs/) folder.
