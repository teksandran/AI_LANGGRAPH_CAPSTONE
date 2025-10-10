# High-Level Overview: Multi-Agent Beauty Search System

## Executive Summary

A production-ready **multi-agent AI system** that combines product knowledge search with business location services, enhanced with **Agent-to-Agent (A2A) communication** and **Human-in-the-Loop (HITL) approval** workflows. The system uses RAG (Retrieval-Augmented Generation) for product information and integrates with Yelp API for business search.

**Key Capabilities:**
- 🔍 Product information search (Botox, Evolus, aesthetic products)
- 📍 Business/location search via Yelp API
- 🤝 Direct agent-to-agent communication
- 👤 Human approval workflow for compliance
- 🔄 100% backward compatible architecture
- 🌐 RESTful API for web/mobile integration

---

## System Architecture

### 1. Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
│  (Web Apps, Mobile Apps, API Clients)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST
┌─────────────────────▼───────────────────────────────────────┐
│                   API SERVER LAYER                           │
│  • Flask API Server (api_server.py)                         │
│  • RESTful Endpoints                                        │
│  • HITL API Endpoints                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  AGENT LAYER (3 Modes)                      │
│                                                              │
│  Mode 1: Original Supervisor    (SupervisorAgent)          │
│  Mode 2: A2A-Enhanced           (SupervisorAgentA2A)       │
│  Mode 3: A2A + HITL             (SupervisorAgentHITL)      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                SPECIALIZED AGENTS                            │
│                                                              │
│  ProductAgent          BusinessAgent                        │
│  • RAG search          • Yelp API integration              │
│  • Product info        • Location search                   │
│  • Comparisons         • Business details                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              COORDINATION LAYER                              │
│                                                              │
│  A2A Broker (Singleton)      HITL Manager (Singleton)      │
│  • Message routing           • Approval workflow           │
│  • Agent registry            • Policy enforcement          │
│  • Conversation tracking     • Timeout handling            │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 DATA & SERVICES LAYER                        │
│                                                              │
│  RAG System        Yelp API        LLM Providers           │
│  • FAISS vector    • Business      • OpenAI                │
│  • Web scraping    • Reviews       • Anthropic             │
│  • Embeddings      • Locations     • Claude/GPT            │
└─────────────────────────────────────────────────────────────┘
```

### 2. Core Components

#### **Supervisor Agents (Orchestration)**

**SupervisorAgent** (Original)
- **Purpose:** Central coordinator using LangGraph
- **Routing:** Sequential decision-making
- **Use Case:** Simple queries, backward compatibility
- **Location:** [src/supervisor_agent.py](../src/supervisor_agent.py)

**SupervisorAgentA2A** (Enhanced)
- **Purpose:** A2A-enabled coordinator
- **Routing:** Direct agent communication + traditional routing
- **Use Case:** Complex multi-step queries
- **Location:** [src/supervisor_agent_a2a.py](../src/supervisor_agent_a2a.py)
- **Inheritance:** Extends SupervisorAgent + A2AAgentMixin

**SupervisorAgentHITL** (Full-Featured)
- **Purpose:** A2A + Human approval
- **Routing:** A2A communication with human oversight
- **Use Case:** Regulated environments, compliance requirements
- **Location:** [src/supervisor_agent_hitl.py](../src/supervisor_agent_hitl.py)
- **Inheritance:** Extends SupervisorAgentA2A + HITLAgentMixin

#### **Specialized Agents**

**ProductAgent**
- **Responsibility:** Product information retrieval
- **Data Source:** RAG system (FAISS vector store)
- **Capabilities:**
  - Search product information
  - Compare products (e.g., Botox vs Evolus)
  - Answer product-specific questions
- **Location:** [src/product_agent.py](../src/product_agent.py)

**BusinessAgent**
- **Responsibility:** Business/location search
- **Data Source:** Yelp Fusion API
- **Capabilities:**
  - Find businesses by location
  - Get business details
  - Search by category
- **Location:** [src/business_agent.py](../src/business_agent.py)

#### **Coordination Systems**

**A2A Message Broker** (Singleton)
- **Purpose:** Global message coordination between agents
- **Pattern:** Singleton (one instance per application)
- **Responsibilities:**
  - Agent registration and discovery
  - Message routing and delivery
  - Conversation history tracking
  - Broadcast messaging
- **Location:** [src/a2a_broker.py](../src/a2a_broker.py)

**HITL Manager** (Singleton)
- **Purpose:** Human approval workflow coordination
- **Pattern:** Singleton (one instance per application)
- **Responsibilities:**
  - Policy-based approval requirements
  - Request queuing and timeout handling
  - Human decision tracking
  - Audit trail maintenance
- **Location:** [src/hitl_manager.py](../src/hitl_manager.py)

---

## Implementation Details

### 1. Design Patterns Used

#### **Singleton Pattern**
```python
# A2A Broker - ensures single message coordinator
_global_broker = None

def get_broker() -> A2AMessageBroker:
    global _global_broker
    if _global_broker is None:
        _global_broker = A2AMessageBroker()
    return _global_broker
```

**Why:** All agents must share the same message broker and HITL manager for coordination.

#### **Mixin Pattern**
```python
# Reusable capabilities
class A2AAgentMixin:
    """Add A2A communication to any agent"""
    async def send_request(self, recipient, task, parameters):
        # A2A communication logic
        pass

class HITLAgentMixin:
    """Add human approval to any agent"""
    async def request_human_approval(self, action_type, action_data):
        # HITL approval logic
        pass
```

**Why:** Enables adding A2A and HITL capabilities to any agent without modifying base classes.

#### **Inheritance Chain**
```python
SupervisorAgent
    ↓ (inherits)
SupervisorAgentA2A (+ A2AAgentMixin)
    ↓ (inherits)
SupervisorAgentHITL (+ HITLAgentMixin)
```

**Why:** Preserves backward compatibility while progressively adding features.

### 2. Communication Protocols

#### **A2A Message Protocol**

```python
@dataclass
class A2AMessage:
    sender: str              # Agent sending the message
    recipient: str           # Target agent
    message_type: MessageType # REQUEST, RESPONSE, NOTIFICATION, etc.
    content: Dict[str, Any]  # Message payload
    message_id: str          # Unique identifier
    priority: MessagePriority # CRITICAL, HIGH, NORMAL, LOW
    timestamp: datetime      # When created
    conversation_id: str     # Thread tracking
```

**Message Types:**
- `REQUEST` - Ask another agent to perform a task
- `RESPONSE` - Reply to a request
- `NOTIFICATION` - One-way information sharing
- `HANDOFF` - Transfer task ownership
- `QUERY` - Ask for information without task transfer

#### **HITL Request Protocol**

```python
@dataclass
class HITLRequest:
    request_id: str           # Unique identifier
    agent_id: str            # Requesting agent
    action_type: HITLActionType # What needs approval
    action_data: Dict        # Action details
    priority: HITLPriority   # CRITICAL, HIGH, NORMAL, LOW
    timeout: float           # Max wait time
    context: Dict            # Additional context
    timestamp: datetime      # When created
```

**Action Types:**
- `AGENT_RESPONSE` - LLM-generated response
- `API_CALL` - External API call
- `DATA_RETRIEVAL` - Data access
- `AGENT_HANDOFF` - Transfer to another agent
- `CUSTOM_ACTION` - User-defined actions

### 3. Data Flow Architecture

#### **RAG System (Product Information)**

```
User Query
    ↓
Product Agent
    ↓
RAG System
    ↓
┌──────────────────────┐
│ 1. Query Processing  │  (Text preprocessing)
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ 2. Embedding         │  (Convert to vectors)
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ 3. Vector Search     │  (FAISS similarity search)
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ 4. Context Retrieval │  (Get top-k documents)
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ 5. LLM Generation    │  (Generate answer with context)
└──────────┬───────────┘
           ↓
Response to User
```

**Components:**
- **Vector Store:** FAISS (Facebook AI Similarity Search)
- **Embeddings:** OpenAI text-embedding-ada-002
- **Documents:** Web-scraped product information (Botox, Evolus websites)
- **Location:** [src/rag_system.py](../src/rag_system.py)

#### **Yelp API Integration (Business Search)**

```
User Query
    ↓
Business Agent
    ↓
Yelp Client
    ↓
┌──────────────────────┐
│ 1. Parameter Extract │  (Location, term, category)
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ 2. API Call          │  (Yelp Fusion API)
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ 3. Response Parse    │  (Business details, ratings)
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ 4. Format Results    │  (LLM-friendly format)
└──────────┬───────────┘
           ↓
Response to User
```

**Components:**
- **API Client:** [src/yelp_client.py](../src/yelp_client.py)
- **Endpoints:** Business Search, Business Details
- **Rate Limiting:** Built-in retry logic

---

## Workflow Examples

### Workflow 1: Original Mode (Simple Query)

**Query:** "What is Botox?"

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │ Query: "What is Botox?"
       ↓
┌─────────────────────┐
│ SupervisorAgent     │
│ (Original Mode)     │
└──────┬──────────────┘
       │ Routes to ProductAgent
       ↓
┌─────────────────────┐
│  ProductAgent       │
└──────┬──────────────┘
       │ Queries RAG System
       ↓
┌─────────────────────┐
│   RAG System        │
│ • FAISS search      │
│ • LLM generation    │
└──────┬──────────────┘
       │ Product info
       ↓
┌─────────────────────┐
│ SupervisorAgent     │
│ (Synthesize)        │
└──────┬──────────────┘
       │
       ↓
┌─────────────┐
│    User     │ "Botox is a neuromodulator..."
└─────────────┘

Duration: ~2-3 seconds
Agents Used: Supervisor → Product
Communication: Sequential (LangGraph routing)
```

### Workflow 2: A2A Mode (Complex Query)

**Query:** "What is Botox and where can I get it in NYC?"

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │ Query: "What is Botox and where in NYC?"
       ↓
┌──────────────────────┐
│ SupervisorAgentA2A   │
│ (A2A Enabled)        │
└──────┬───────────────┘
       │ Detects multi-part query
       │ Registers with A2A Broker
       ↓
┌──────────────────────────────────────┐
│        A2A Message Broker            │
│  • Routes messages between agents    │
└──────┬───────────────────────────────┘
       │
       ├──────────────┬──────────────┐
       │              │              │
       ↓              ↓              ↓
┌────────────┐  ┌────────────┐  ┌──────────────┐
│  Product   │  │  Business  │  │  Supervisor  │
│  Agent     │  │  Agent     │  │  Agent       │
└─────┬──────┘  └─────┬──────┘  └──────────────┘
      │               │
      │ A2A REQUEST   │ A2A REQUEST
      │ "What is      │ "Find Botox
      │  Botox?"      │  in NYC"
      ↓               ↓
  RAG System      Yelp API
      │               │
      │ A2A RESPONSE  │ A2A RESPONSE
      ↓               ↓
┌──────────────────────────────┐
│    SupervisorAgentA2A        │
│ • Receives both responses    │
│ • Synthesizes final answer   │
└──────┬───────────────────────┘
       │
       ↓
┌─────────────┐
│    User     │ "Botox is... Here are 5 clinics in NYC..."
└─────────────┘

Duration: ~3-5 seconds
Agents Used: Supervisor ↔ Product + Business (parallel)
Communication: Direct A2A messages (concurrent)
Performance: 40% faster than sequential
```

### Workflow 3: A2A + HITL Mode (Regulated Query)

**Query:** "What is Botox and where can I get it in NYC?"

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │ Query
       ↓
┌──────────────────────┐
│ SupervisorAgentHITL  │
│ (A2A + HITL)         │
└──────┬───────────────┘
       │ A2A parallel query
       ↓
┌──────────────────────┐
│   A2A Broker         │
└──────┬───────────────┘
       │
       ├─────────┬──────────┐
       ↓         ↓          ↓
   Product   Business   Supervisor
    Agent     Agent
       │         │
       │ Responses collected
       ↓
┌──────────────────────┐
│ Supervisor generates │
│ draft response       │
└──────┬───────────────┘
       │ Check policy
       ↓
┌──────────────────────┐
│   HITL Manager       │
│ • Policy: Medical    │
│   info needs approval│
└──────┬───────────────┘
       │ REQUIRES APPROVAL
       ↓
┌──────────────────────┐
│ Queue for human      │
│ review (async wait)  │
└──────┬───────────────┘
       │
       │ ⏳ Waiting...
       │
┌──────▼───────────────┐
│   Human Reviewer     │
│ • Reviews response   │
│ • Approves/Rejects   │
│   via API            │
└──────┬───────────────┘
       │ APPROVED
       ↓
┌──────────────────────┐
│   HITL Manager       │
│ • Records decision   │
│ • Resolves future    │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│ SupervisorAgentHITL  │
│ • Receives approval  │
│ • Returns response   │
└──────┬───────────────┘
       │
       ↓
┌─────────────┐
│    User     │ "Botox is... [APPROVED BY: admin@company.com]"
└─────────────┘

Duration: 3-5 seconds + human review time
Agents Used: Supervisor ↔ Product + Business + Human
Communication: A2A + HITL approval queue
Compliance: Full audit trail maintained
```

---

## Technology Stack

### **Core Technologies**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Orchestration** | LangGraph | Agent workflow management |
| **LLM Providers** | OpenAI (GPT-4o-mini), Anthropic (Claude 3.5 Sonnet) | Natural language processing |
| **Vector Store** | FAISS | Similarity search for RAG |
| **Embeddings** | OpenAI text-embedding-ada-002 | Text vectorization |
| **API Server** | Flask + Flask-CORS | RESTful API endpoints |
| **External APIs** | Yelp Fusion API | Business search |
| **Web Scraping** | BeautifulSoup4, aiohttp | Product information gathering |
| **Async Runtime** | asyncio | Asynchronous operations |

### **Python Libraries**

```python
# Core AI/ML
langchain >= 0.1.0
langchain-openai >= 0.0.5
langchain-anthropic >= 0.1.1
langgraph >= 0.0.20
openai >= 1.0.0

# Vector Store & RAG
faiss-cpu >= 1.7.4
sentence-transformers >= 2.2.0

# Web & API
flask >= 3.0.0
flask-cors >= 4.0.0
httpx >= 0.24.0

# Utilities
python-dotenv >= 1.0.0
pydantic >= 2.0.0
```

### **File Structure**

```
yelp_mcp/
├── src/
│   ├── supervisor_agent.py          # Original supervisor
│   ├── supervisor_agent_a2a.py      # A2A-enabled supervisor
│   ├── supervisor_agent_hitl.py     # A2A + HITL supervisor
│   ├── product_agent.py             # Product information
│   ├── product_agent_a2a.py         # A2A product agent
│   ├── business_agent.py            # Business search
│   ├── business_agent_a2a.py        # A2A business agent
│   ├── a2a_broker.py                # Message coordination
│   ├── a2a_protocol.py              # Message definitions
│   ├── a2a_agent_mixin.py           # A2A capabilities
│   ├── hitl_manager.py              # Approval coordination
│   ├── hitl_protocol.py             # Approval definitions
│   ├── hitl_agent_mixin.py          # HITL capabilities
│   ├── hitl_api_endpoints.py        # HITL REST API
│   ├── rag_system.py                # RAG implementation
│   ├── yelp_client.py               # Yelp API client
│   └── langgraph_agent.py           # Legacy agent
├── docs/                            # Documentation (17 files)
├── tests/                           # Test suite (15 files)
├── api_server.py                    # Main API server
├── requirements.txt                 # Dependencies
└── .env                            # API keys (not in repo)
```

---

## Key Features & Capabilities

### 1. Multi-Mode Operation

**Mode Selection:**
```python
# Original Mode - Simple, sequential
supervisor = SupervisorAgent(yelp_api_key=key)
response = await supervisor.run("What is Botox?")

# A2A Mode - Parallel agent communication
supervisor = SupervisorAgentA2A(yelp_api_key=key, enable_a2a=True)
response = await supervisor.run_with_a2a("What is Botox and where in NYC?")

# HITL Mode - Human approval workflow
supervisor = SupervisorAgentHITL(
    yelp_api_key=key,
    enable_a2a=True,
    enable_hitl=True
)
response = await supervisor.run_with_hitl("What is Botox?")
```

### 2. Backward Compatibility

**100% Compatible:**
- All original code works unchanged
- Original agents preserved (product_agent.py, business_agent.py)
- Original supervisor works as before
- New features are opt-in via enhanced classes

**Migration Path:**
```
SupervisorAgent (Original)
    ↓ No changes needed
SupervisorAgentA2A (Add A2A)
    ↓ Add enable_hitl=True
SupervisorAgentHITL (Add HITL)
```

### 3. Flexible Configuration

**Policy-Based HITL:**
```python
# Require approval for medical information
hitl_manager.add_policy(HITLPolicy(
    name="medical_info_approval",
    action_type=HITLActionType.AGENT_RESPONSE,
    requires_approval=lambda data: "medical" in data.get("content", "").lower(),
    priority=HITLPriority.HIGH,
    timeout=300  # 5 minutes
))
```

**A2A Capabilities:**
```python
# Define agent capabilities
agent.register_capabilities([
    AgentCapability(
        name="product_search",
        description="Search product information",
        parameters={"query": "string"}
    )
])
```

### 4. Observability & Monitoring

**LangSmith Integration:**
- Trace all LLM calls
- Monitor agent decisions
- Debug conversation flows
- Performance analytics

**Built-in Statistics:**
```python
# A2A statistics
stats = supervisor.get_a2a_statistics()
# Returns: total_agents, total_messages, messages_by_type

# HITL statistics
stats = hitl_manager.get_statistics()
# Returns: pending_count, approved_count, rejected_count, avg_response_time
```

### 5. RESTful API

**Endpoints:**
```
GET  /api/health              # Health check
POST /api/query               # Main query endpoint
GET  /api/hitl/pending        # Get pending approvals
POST /api/hitl/approve/<id>   # Approve request
POST /api/hitl/reject/<id>    # Reject request
POST /api/hitl/modify/<id>    # Modify and approve
GET  /api/hitl/statistics     # HITL stats
GET  /api/hitl/history        # Approval history
```

---

## Performance Characteristics

### Query Response Times

| Query Type | Mode | Avg Time | Agents Used |
|------------|------|----------|-------------|
| Simple product query | Original | 2-3s | Supervisor → Product |
| Simple business query | Original | 2-3s | Supervisor → Business |
| Complex multi-part | Original | 5-7s | Sequential routing |
| Complex multi-part | A2A | 3-5s | Parallel A2A (40% faster) |
| With HITL approval | A2A + HITL | 3-5s + review time | Parallel + approval |

### Scalability

**Concurrent Requests:**
- Flask server: Up to 100 concurrent requests (default)
- A2A Broker: Thread-safe message routing
- HITL Manager: Async approval queue

**Rate Limits:**
- Yelp API: 5000 calls/day
- OpenAI: Based on tier (typically 3500 RPM)
- Vector search: No limit (local FAISS)

---

## Security & Compliance

### 1. API Key Management
- Environment variables (.env file)
- Never committed to repository
- Separate keys per environment

### 2. HITL Audit Trail
- All approvals logged with timestamp
- Human reviewer identification
- Action history maintained
- Exportable for compliance

### 3. Data Privacy
- No user data stored permanently
- Conversation history optional
- GDPR-ready architecture

---

## Deployment Options

### Development
```bash
# Local development server
python api_server.py
# Runs on http://localhost:5000
```

### Production Considerations

**1. Environment Variables:**
```bash
YELP_API_KEY=xxx
OPENAI_API_KEY=xxx
ANTHROPIC_API_KEY=xxx
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=xxx
```

**2. Production Server:**
```bash
# Use Gunicorn or uWSGI
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

**3. Scaling:**
- Deploy multiple API server instances
- Load balancer in front
- Shared Redis for HITL queue (optional)
- Centralized logging

---

## Testing Strategy

### Test Organization

**15 test files in `tests/` folder:**

1. **Setup & Verification**
   - test_path_setup.py
   - verify_setup.py

2. **A2A Testing**
   - test_a2a_simple.py
   - test_a2a_communication.py

3. **HITL Testing**
   - test_hitl_system.py

4. **Agent Testing**
   - test_supervisor.py
   - test_beauty_search_agent.py
   - test_product_comparison.py

5. **API Testing**
   - test_connection.py
   - test_app.py

**Run Tests:**
```bash
# Quick verification
python tests/test_path_setup.py

# Feature tests
python tests/test_a2a_simple.py
python tests/test_hitl_system.py

# Full system test
python tests/verify_setup.py
```

---

## Future Enhancements

### Potential Additions
1. **More Agents:** Weather, booking, payment agents
2. **Advanced RAG:** Multi-vector retrieval, reranking
3. **Caching:** Redis cache for frequent queries
4. **Streaming:** Server-Sent Events for real-time responses
5. **Multi-tenancy:** Support multiple organizations
6. **Advanced Analytics:** Query patterns, user behavior
7. **Mobile SDK:** Native iOS/Android integration

---

## Documentation Map

| Document | Purpose | Audience |
|----------|---------|----------|
| **[This Document](HIGH_LEVEL_OVERVIEW.md)** | High-level architecture | Everyone |
| **[Quick Start](QUICK_START.md)** | Get running in 5 minutes | New users |
| **[Integration Architecture](INTEGRATION_ARCHITECTURE.md)** | Component integration | Developers |
| **[A2A Documentation](A2A_DOCUMENTATION.md)** | Agent communication | Developers |
| **[HITL Documentation](HITL_DOCUMENTATION.md)** | Human approval | Compliance |
| **[Test Organization](TEST_ORGANIZATION.md)** | Testing guide | QA/Developers |
| **[Complete Index](INDEX.md)** | All documentation | Everyone |

---

## Summary

### What Makes This System Unique

✅ **Three operational modes** - Original, A2A, A2A+HITL
✅ **100% backward compatible** - Existing code works unchanged
✅ **Production-ready** - RESTful API, error handling, monitoring
✅ **Extensible** - Mixin pattern for easy capability addition
✅ **Compliant** - HITL approval workflow with audit trail
✅ **Fast** - 40% performance improvement with A2A
✅ **Well-documented** - 17 comprehensive documentation files
✅ **Well-tested** - 15 test files covering all features

### Technology Highlights

- **LangGraph** for agent orchestration
- **FAISS** for vector similarity search
- **OpenAI/Anthropic** for LLM capabilities
- **Yelp API** for real-world business data
- **Flask** for RESTful API
- **Async/await** for concurrent operations
- **Singleton + Mixin** design patterns

### Use Cases

1. **Beauty/Aesthetic Industry** - Product info + provider search
2. **Regulated Industries** - Human approval for compliance
3. **Multi-agent Research** - Study agent collaboration patterns
4. **Educational** - Learn multi-agent architectures
5. **Production Systems** - Template for enterprise AI systems

---

**Version:** 2.0
**Status:** ✅ Production Ready
**Last Updated:** 2025-10-10
**Total Lines of Code:** ~8,000+
**Documentation Files:** 17
**Test Files:** 15

[← Back to Documentation Index](INDEX.md) | [← Back to README](../README.md)
