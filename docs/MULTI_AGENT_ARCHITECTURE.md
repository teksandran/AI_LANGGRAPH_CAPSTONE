# Multi-Agent Architecture

## Overview

The project now supports **two agent architectures**:

1. **Single Agent Architecture** (Original) - `BeautySearchAgent`
2. **Multi-Agent Architecture** (New) - `SupervisorAgent` with specialized workers

---

## Architecture Comparison

### 1. Single Agent (Original)

```
┌─────────────────────────────────┐
│     BeautySearchAgent           │
│  (LangGraph Agent)              │
│                                 │
│  ┌──────────────────────────┐  │
│  │    7 Tools:              │  │
│  │  • Yelp Tools (4)        │  │
│  │  • RAG Tools (3)         │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
```

**Pros:**
- Simpler architecture
- Single LLM call per query
- All tools available at once

**Cons:**
- Tool selection can be ambiguous
- Harder to maintain as tools grow
- Less specialized behavior

---

### 2. Multi-Agent (New)

```
┌───────────────────────────────────────┐
│         SupervisorAgent               │
│    (Coordinator/Router)               │
└──────────┬────────────────────────────┘
           │
      ┌────┴─────┐
      │          │
      ▼          ▼
┌──────────┐  ┌────────────┐
│ Product  │  │ Business   │
│  Agent   │  │   Agent    │
└────┬─────┘  └─────┬──────┘
     │              │
     ▼              ▼
┌─────────┐   ┌──────────┐
│   RAG   │   │   Yelp   │
│ System  │   │   API    │
└─────────┘   └──────────┘
```

**Pros:**
- Specialized agents per domain
- Cleaner separation of concerns
- Easier to maintain and extend
- Better error handling per domain
- Can run agents in parallel (future)

**Cons:**
- More complex architecture
- Multiple LLM calls (supervisor + worker)
- Slightly higher latency

---

## Agent Details

### SupervisorAgent
**Location:** [src/supervisor_agent.py](src/supervisor_agent.py)

**Responsibilities:**
- Routes queries to appropriate worker agent
- Coordinates between specialized agents
- Synthesizes final responses

**Decision Logic:**
```python
Product keywords → ProductAgent
  - "What is Botox?"
  - "Compare X and Y"
  - "Tell me about Evolus"

Location keywords → BusinessAgent
  - "Find X in Y"
  - "Salons near me"
  - "Providers in location"
```

---

### ProductAgent
**Location:** [src/product_agent.py](src/product_agent.py)

**Responsibilities:**
- Handle product information queries
- Search RAG system for Botox/Evolus data
- Format product information responses
- Compare products

**Capabilities:**
- Product descriptions
- FDA-approved uses
- Treatment areas
- Benefits and results
- Side-by-side comparisons

---

### BusinessAgent
**Location:** [src/business_agent.py](src/business_agent.py)

**Responsibilities:**
- Handle business/location queries
- Search Yelp for salons, spas, providers
- Extract location and service type from queries
- Format business results

**Capabilities:**
- Location-based search
- Business ratings and reviews
- Contact information
- Service type filtering

---

## Workflow Example

### Query: "What are the differences between Botox and Evolus?"

```
1. User Query
   ↓
2. SupervisorAgent receives query
   ↓
3. Supervisor analyzes: "This is about product comparison"
   ↓
4. Routes to: ProductAgent
   ↓
5. ProductAgent:
   - Searches RAG for Botox info
   - Searches RAG for Evolus info
   - Compares results
   ↓
6. Returns formatted comparison
   ↓
7. SupervisorAgent receives response
   ↓
8. Supervisor decides: FINISH (task complete)
   ↓
9. Returns final response to user
```

### Query: "Find Botox providers in New York"

```
1. User Query
   ↓
2. SupervisorAgent receives query
   ↓
3. Supervisor analyzes: "This is about finding businesses"
   ↓
4. Routes to: BusinessAgent
   ↓
5. BusinessAgent:
   - Extracts location: "New York"
   - Extracts service: "Botox providers"
   - Searches Yelp API
   ↓
6. Returns formatted business results
   ↓
7. SupervisorAgent receives response
   ↓
8. Supervisor decides: FINISH (task complete)
   ↓
9. Returns final response to user
```

---

## Usage

### Using Single Agent (Original)

```python
from src.langgraph_agent import BeautySearchAgent

agent = BeautySearchAgent(
    yelp_api_key="your-key",
    llm_provider="openai"
)

response = await agent.run("What is Botox?")
```

### Using Multi-Agent (New)

```python
from src.supervisor_agent import SupervisorAgent

supervisor = SupervisorAgent(
    yelp_api_key="your-key",
    llm_provider="openai"
)

response = await supervisor.run("What is Botox?")
```

---

## Testing

### Test Single Agent
```bash
.venv\Scripts\python test_agent.py
```

### Test Multi-Agent
```bash
.venv\Scripts\python test_supervisor.py
```

### Test Product Agent Directly
```python
from src.product_agent import ProductAgent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
agent = ProductAgent(llm=llm)

response = agent.run("What is Botox?")
print(response)
```

### Test Business Agent Directly
```python
from src.business_agent import BusinessAgent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
agent = BusinessAgent(yelp_api_key="your-key", llm=llm)

response = await agent.run("Find salons in NYC")
print(response)
```

---

## When to Use Which?

### Use Single Agent When:
- Simple deployments
- Minimizing LLM calls
- Cost is primary concern
- Quick prototyping

### Use Multi-Agent When:
- Complex applications
- Need specialized behaviors
- Better maintainability required
- Planning to add more agents
- Want parallel agent execution (future)

---

## Architecture Evolution

```
Version 1.0: Single Agent
├── BeautySearchAgent
└── 7 Tools

Version 2.0: Multi-Agent (Current)
├── BeautySearchAgent (still available)
└── SupervisorAgent
    ├── ProductAgent
    │   └── RAG System
    └── BusinessAgent
        └── Yelp API

Future: Multi-Agent + Parallel
├── SupervisorAgent
├── ProductAgent (parallel)
├── BusinessAgent (parallel)
├── ReviewAgent (new)
└── RecommendationAgent (new)
```

---

## Files Summary

### New Files Created:
1. **[src/supervisor_agent.py](src/supervisor_agent.py)** - Supervisor coordinator
2. **[src/product_agent.py](src/product_agent.py)** - Product specialist
3. **[src/business_agent.py](src/business_agent.py)** - Business specialist
4. **[test_supervisor.py](test_supervisor.py)** - Test script

### Existing Files (Unchanged):
- **[src/langgraph_agent.py](src/langgraph_agent.py)** - Original single agent
- **[src/rag_system.py](src/rag_system.py)** - RAG system
- **[src/tools.py](src/tools.py)** - Tool definitions
- **[src/yelp_client.py](src/yelp_client.py)** - Yelp API client

---

## Performance Comparison

| Metric | Single Agent | Multi-Agent |
|--------|--------------|-------------|
| LLM Calls | 1-2 | 2-4 |
| Latency | ~2-3s | ~4-6s |
| Accuracy | Good | Better |
| Maintainability | Medium | High |
| Extensibility | Medium | High |
| Cost per query | Lower | Higher |

---

## Benefits of Multi-Agent

### 1. Separation of Concerns
- Each agent focuses on one domain
- Clearer responsibilities
- Easier debugging

### 2. Specialized Prompts
- Product agent optimized for RAG
- Business agent optimized for location
- Better results per domain

### 3. Independent Development
- Modify agents independently
- Add new agents without affecting others
- Version agents separately

### 4. Better Error Handling
- Agent-specific error handling
- Graceful degradation per domain
- Clearer error messages

### 5. Scalability
- Can distribute agents across services
- Parallel agent execution (future)
- Load balancing per agent type

---

## Migration Guide

### From Single to Multi-Agent

```python
# Before (Single Agent)
from src.langgraph_agent import BeautySearchAgent

agent = BeautySearchAgent(
    yelp_api_key=api_key,
    llm_provider="openai"
)

response = await agent.run(query)

# After (Multi-Agent)
from src.supervisor_agent import SupervisorAgent

supervisor = SupervisorAgent(
    yelp_api_key=api_key,
    llm_provider="openai"
)

response = await supervisor.run(query)
```

**Note:** Both APIs are identical! Just swap the class name.

---

## Future Enhancements

### Planned Agents:
1. **ReviewAgent** - Specialized in analyzing reviews
2. **RecommendationAgent** - Personalized recommendations
3. **PricingAgent** - Price comparison and optimization
4. **SchedulingAgent** - Appointment booking

### Planned Features:
- Parallel agent execution
- Agent memory/state sharing
- Dynamic agent selection
- Agent voting/consensus
- Self-healing agents

---

**Last Updated:** 2025-10-09
**Version:** 2.0 - Multi-Agent Architecture
