# Integration Architecture: Supervisor + A2A + HITL

## 🏗️ Architecture Overview

The system uses **inheritance and composition** to layer capabilities without breaking existing code.

```
SupervisorAgent (Original)
     ↓
     └─ Extends ─→ SupervisorAgentA2A (Adds A2A)
                        ↓
                        └─ Extends ─→ SupervisorAgentHITL (Adds HITL)
```

---

## 📊 Class Hierarchy

### Level 1: Original Supervisor (Base)

```python
# src/supervisor_agent.py
class SupervisorAgent:
    """Original supervisor - routes queries to agents via LangGraph"""

    def __init__(self, yelp_api_key, llm_provider, model):
        self.llm = ChatOpenAI(...)
        self.product_agent = ProductAgent(llm)
        self.business_agent = BusinessAgent(yelp_api_key, llm)
        self.graph = self._build_graph()  # LangGraph workflow

    async def run(self, user_message: str) -> str:
        """Traditional routing via LangGraph"""
        # 1. Supervisor decides: product_agent or business_agent
        # 2. Route to chosen agent
        # 3. Agent processes and returns
        # 4. Return response
```

**Capabilities**:
- ✅ Sequential routing (Supervisor → Agent)
- ✅ LangGraph state management
- ✅ Basic agent coordination

**Limitations**:
- ❌ Agents can't communicate directly
- ❌ No human oversight
- ❌ No collaboration between agents

---

### Level 2: A2A-Enhanced Supervisor (Adds Collaboration)

```python
# src/supervisor_agent_a2a.py
class SupervisorAgentA2A(SupervisorAgent, A2AAgentMixin):
    """Extends SupervisorAgent + adds A2A communication"""

    def __init__(self, yelp_api_key, llm_provider, model, enable_a2a=True):
        # Call parent __init__
        SupervisorAgent.__init__(self, yelp_api_key, llm_provider, model)

        if enable_a2a:
            # Replace agents with A2A-enabled versions
            self.product_agent = ProductAgentA2A(llm, agent_id="product_agent")
            self.business_agent = BusinessAgentA2A(yelp_api_key, llm, agent_id="business_agent")

            # Setup A2A for supervisor
            self._setup_a2a(agent_id="supervisor", agent_type="supervisor", capabilities=[...])

    async def run(self, user_message: str) -> str:
        """Original routing - calls parent method"""
        return await super().run(user_message)

    async def run_with_a2a(self, user_message: str) -> Dict[str, Any]:
        """NEW: A2A-enabled routing with agent collaboration"""
        # 1. Analyze query complexity
        # 2. If needs multiple agents:
        #    a. ProductAgent gets info
        #    b. ProductAgent hands off to BusinessAgent (A2A message)
        #    c. BusinessAgent receives context from ProductAgent
        #    d. Combined response
        # 3. Return result with metadata
```

**New Capabilities**:
- ✅ Direct agent-to-agent messaging
- ✅ Task handoffs with context
- ✅ Parallel agent operations
- ✅ Agent discovery by capability
- ✅ Backward compatible (original `run()` still works)

**How A2A Works**:
```python
# ProductAgent wants help from BusinessAgent
response = await product_agent.send_request(
    recipient="business_agent",
    task="find_providers",
    parameters={"location": "NYC"},
    wait_for_response=True
)
# → Message goes through A2A Broker
# → BusinessAgent receives message
# → BusinessAgent processes
# → Response sent back through broker
# → ProductAgent receives response
```

---

### Level 3: HITL-Enhanced Supervisor (Adds Human Oversight)

```python
# src/supervisor_agent_hitl.py
class SupervisorAgentHITL(SupervisorAgentA2A, HITLAgentMixin):
    """Extends SupervisorAgentA2A + adds HITL approval"""

    def __init__(self, yelp_api_key, llm_provider, model, enable_a2a=True, enable_hitl=False):
        # Call parent __init__ (gets A2A capabilities)
        SupervisorAgentA2A.__init__(self, yelp_api_key, llm_provider, model, enable_a2a)

        # Setup HITL
        self._setup_hitl(agent_id="supervisor", enable_hitl=enable_hitl)

    async def run(self, user_message: str) -> str:
        """Original routing - no HITL (backward compatible)"""
        return await SupervisorAgentA2A.run(self, user_message)

    async def run_with_a2a(self, user_message: str) -> Dict[str, Any]:
        """A2A routing - no HITL (backward compatible)"""
        return await SupervisorAgentA2A.run_with_a2a(self, user_message)

    async def run_with_hitl(self, user_message: str) -> Dict[str, Any]:
        """NEW: A2A + HITL routing with human approval"""
        # 1. Get response using A2A (agents collaborate)
        if self.enable_a2a:
            result = await self.run_with_a2a(user_message)
            response_text = result['response']
        else:
            response_text = await self.run(user_message)

        # 2. Check if human approval required
        if self.hitl_enabled:
            approval = await self.check_response_approval(
                response_text=response_text,
                user_query=user_message,
                confidence=1.0
            )

            if not approval["approved"]:
                # Rejected - return error message
                return {"response": "Response rejected", "hitl_approved": False}

            # Use modified response if provided
            response_text = approval.get("response", response_text)

        # 3. Return final response
        return {"response": response_text, "hitl_approved": True}
```

**New Capabilities**:
- ✅ Policy-based approval workflow
- ✅ Human can approve/reject/modify
- ✅ Timeout handling with auto-decisions
- ✅ Audit trail
- ✅ Backward compatible (A2A and original methods still work)

---

## 🔄 Integration Flow Diagrams

### Flow 1: Original Supervisor (No A2A, No HITL)

```
User Query: "What is Botox?"
     ↓
SupervisorAgent.run()
     ↓
LangGraph decides: ProductAgent
     ↓
ProductAgent.run()
     ↓
Response: "Botox is..."
     ↓
User receives response
```

**Code**:
```python
from src.supervisor_agent import SupervisorAgent

supervisor = SupervisorAgent(yelp_api_key=key)
response = await supervisor.run("What is Botox?")
```

---

### Flow 2: With A2A (Agent Collaboration)

```
User Query: "What is Botox and where can I get it in NYC?"
     ↓
SupervisorAgentA2A.run_with_a2a()
     ↓
Supervisor detects: needs product + business info
     ↓
ProductAgentA2A.run_async() → Gets Botox info
     ↓
ProductAgent sends A2A message to BusinessAgent
     │
     └─→ A2A Broker
          ↓
     BusinessAgentA2A receives handoff
          ↓
     BusinessAgent finds NYC providers
          ↓
     BusinessAgent sends response via A2A Broker
     ↓
ProductAgent receives business info
     ↓
Combined response: "Botox is... Here are providers in NYC..."
     ↓
User receives combined response
```

**Code**:
```python
from src.supervisor_agent_a2a import SupervisorAgentA2A

supervisor = SupervisorAgentA2A(yelp_api_key=key, enable_a2a=True)
result = await supervisor.run_with_a2a("What is Botox and where can I get it in NYC?")
# result = {
#   'response': "...",
#   'agents_used': ['product_agent', 'business_agent'],
#   'method': 'a2a_collaboration'
# }
```

---

### Flow 3: With A2A + HITL (Full System)

```
User Query: "What is Botox and where can I get it in NYC?"
     ↓
SupervisorAgentHITL.run_with_hitl()
     ↓
Step 1: A2A Collaboration (same as Flow 2)
     ↓
ProductAgent + BusinessAgent collaborate
     ↓
Combined response generated: "Botox is... Here are providers..."
     ↓
Step 2: HITL Approval Check
     ↓
HITL Manager checks policies
     ↓
Policy: "always_approve_responses" → Approval required
     ↓
HITL Request created
     ↓
Request queued (priority: normal)
     ↓
     ┌─────────────────────────┐
     │   Waiting for Human     │
     │   (via API)             │
     └─────────────────────────┘
          ↓
Human reviews via API: GET /api/hitl/pending
     ↓
Human sees:
  - Original query
  - Generated response
  - Agent confidence
  - Context
     ↓
Human decides:
  Option 1: Approve → POST /api/hitl/approve/{id}
  Option 2: Reject → POST /api/hitl/reject/{id}
  Option 3: Modify → POST /api/hitl/modify/{id} with new text
     ↓
Decision submitted to HITL Manager
     ↓
HITL Manager resolves the waiting request
     ↓
If Approved or Modified:
     ↓
Response (possibly modified) returned to user
     ↓
User receives: "Botox is... [possibly with human edits]"
     ↓
Entire interaction logged for audit
```

**Code**:
```python
from src.supervisor_agent_hitl import SupervisorAgentHITL
from src.hitl_manager import get_hitl_manager
from src.hitl_protocol import DefaultHITLPolicies

# Configure HITL
manager = get_hitl_manager()
manager.remove_policy("no_approval")
manager.add_policy(DefaultHITLPolicies.always_approve_responses())

# Create supervisor
supervisor = SupervisorAgentHITL(
    yelp_api_key=key,
    enable_a2a=True,    # Agent collaboration
    enable_hitl=True    # Human approval
)

# Run query (will wait for human approval)
result = await supervisor.run_with_hitl("What is Botox and where can I get it in NYC?")
# result = {
#   'response': "...",
#   'agents_used': ['product_agent', 'business_agent'],
#   'method': 'a2a_collaboration',
#   'hitl_approved': True,
#   'hitl_decision': 'approved',
#   'hitl_modified': False
# }
```

---

## 🧩 Component Integration

### A2A Broker Integration

The A2A Broker is a **singleton** that coordinates all agent messages:

```python
# src/a2a_broker.py
class A2AMessageBroker:
    """Central message coordinator"""

    def __init__(self):
        self._agents = {}           # {agent_id: AgentProfile}
        self._message_handlers = {}  # {agent_id: handler_function}
        self._message_queue = []
        self._message_history = {}

# Global instance
_global_broker = None

def get_broker() -> A2AMessageBroker:
    """Get singleton instance"""
    global _global_broker
    if _global_broker is None:
        _global_broker = A2AMessageBroker()
    return _global_broker
```

**How Agents Register**:
```python
# When ProductAgentA2A is created:
from src.a2a_broker import get_broker

class ProductAgentA2A(ProductAgent, A2AAgentMixin):
    def __init__(self, llm, agent_id="product_agent"):
        ProductAgent.__init__(self, llm)

        # Register with broker
        self._setup_a2a(
            agent_id=agent_id,
            agent_type="product_specialist",
            capabilities=[...]
        )
        # This calls: get_broker().register_agent(profile, handler)
```

**All registered agents can communicate**:
```
A2A Broker
├── supervisor (registered)
├── product_agent (registered)
└── business_agent (registered)

Any agent can send messages to any other agent!
```

---

### HITL Manager Integration

The HITL Manager is also a **singleton**:

```python
# src/hitl_manager.py
class HITLManager:
    """Manages approval requests"""

    def __init__(self):
        self._policies = []
        self._pending_requests = {}
        self._responses = {}
        self._request_futures = {}  # For async waiting

# Global instance
_global_hitl_manager = None

def get_hitl_manager() -> HITLManager:
    """Get singleton instance"""
    global _global_hitl_manager
    if _global_hitl_manager is None:
        _global_hitl_manager = HITLManager()
        # Add default "no approval" policy
        _global_hitl_manager.add_policy(DefaultHITLPolicies.no_approval())
    return _global_hitl_manager
```

**How Agents Use HITL**:
```python
# When SupervisorAgentHITL is created:
from src.hitl_manager import get_hitl_manager

class SupervisorAgentHITL(SupervisorAgentA2A, HITLAgentMixin):
    def __init__(self, ...):
        SupervisorAgentA2A.__init__(self, ...)

        # Setup HITL
        self._setup_hitl(agent_id="supervisor", enable_hitl=enable_hitl)
        # This sets: self.hitl_manager = get_hitl_manager()
```

**Request/Response Flow**:
```
Agent → check_response_approval()
    ↓
request_human_approval()
    ↓
HITL Manager.request_approval()
    ↓
Create HITLRequest, add to queue
    ↓
Create asyncio.Future (blocks here)
    ↓
[Human reviews via API]
    ↓
Human → POST /api/hitl/approve/{id}
    ↓
HITL Manager.submit_response()
    ↓
Resolve Future (unblocks)
    ↓
Agent receives approval/rejection
    ↓
Agent proceeds or stops
```

---

## 🔗 Communication Patterns

### Pattern 1: Supervisor → Agent (Original)

```python
# Traditional LangGraph routing
Supervisor._supervisor_node()
    ↓
Decide: "product_agent"
    ↓
Supervisor._product_agent_node()
    ↓
Call: self.product_agent.run()
    ↓
Return response
```

### Pattern 2: Agent → Agent (A2A)

```python
# Direct agent communication
ProductAgent.send_request()
    ↓
Create A2AMessage
    ↓
A2A Broker.send_message()
    ↓
Route to BusinessAgent
    ↓
BusinessAgent._handle_a2a_message()
    ↓
Process request
    ↓
Create A2AResponse
    ↓
A2A Broker sends response back
    ↓
ProductAgent receives response
```

### Pattern 3: Agent → Human → Agent (HITL)

```python
# Human approval workflow
Agent.check_response_approval()
    ↓
HITL Manager.request_approval()
    ↓
Create request, await Future
    ↓
[System waits...]
    ↓
Human reviews: GET /api/hitl/pending
    ↓
Human decides: POST /api/hitl/approve/{id}
    ↓
HITL Manager.submit_response()
    ↓
Resolve Future
    ↓
Agent receives approval
    ↓
Agent continues
```

---

## 📦 Dependency Graph

```
┌──────────────────────┐
│  Original Code       │
│  (UNCHANGED)         │
│  - supervisor_agent  │
│  - product_agent     │
│  - business_agent    │
└──────────────────────┘
           ↑
           │ (inherits from)
           │
┌──────────────────────┐
│  A2A Layer           │
│  - a2a_protocol      │
│  - a2a_broker        │
│  - a2a_agent_mixin   │
│  - *_agent_a2a       │
└──────────────────────┘
           ↑
           │ (inherits from)
           │
┌──────────────────────┐
│  HITL Layer          │
│  - hitl_protocol     │
│  - hitl_manager      │
│  - hitl_agent_mixin  │
│  - supervisor_hitl   │
└──────────────────────┘
```

**Key Points**:
1. **Original code** = Foundation (unchanged)
2. **A2A layer** = Extends original (adds collaboration)
3. **HITL layer** = Extends A2A (adds oversight)
4. Each layer is **optional** and **backward compatible**

---

## 🎯 Usage Examples

### Example 1: Use Original (No Changes)

```python
from src.supervisor_agent import SupervisorAgent

supervisor = SupervisorAgent(yelp_api_key=key)
response = await supervisor.run("What is Botox?")
```

**What happens**: Traditional routing, no A2A, no HITL

---

### Example 2: Use A2A Only

```python
from src.supervisor_agent_a2a import SupervisorAgentA2A

supervisor = SupervisorAgentA2A(yelp_api_key=key, enable_a2a=True)

# Method 1: Traditional routing (no A2A)
response = await supervisor.run("What is Botox?")

# Method 2: With A2A collaboration
result = await supervisor.run_with_a2a("What is Botox and where in NYC?")
print(result['agents_used'])  # ['product_agent', 'business_agent']
```

**What happens**: Agents can collaborate directly

---

### Example 3: Use A2A + HITL

```python
from src.supervisor_agent_hitl import SupervisorAgentHITL
from src.hitl_manager import get_hitl_manager
from src.hitl_protocol import DefaultHITLPolicies

# Configure HITL
manager = get_hitl_manager()
manager.remove_policy("no_approval")
manager.add_policy(DefaultHITLPolicies.always_approve_responses())

supervisor = SupervisorAgentHITL(
    yelp_api_key=key,
    enable_a2a=True,    # A2A on
    enable_hitl=True    # HITL on
)

# Method 1: Traditional routing (no A2A, no HITL)
response = await supervisor.run("What is Botox?")

# Method 2: With A2A (no HITL)
result = await supervisor.run_with_a2a("What is Botox?")

# Method 3: With A2A + HITL (full system)
result = await supervisor.run_with_hitl("What is Botox?")
# This will wait for human approval!
```

**What happens**: Agents collaborate, then human approves

---

## 🔧 Configuration Matrix

| Supervisor Class | `enable_a2a` | `enable_hitl` | Methods Available | Behavior |
|------------------|--------------|---------------|-------------------|----------|
| `SupervisorAgent` | N/A | N/A | `run()` | Original routing only |
| `SupervisorAgentA2A` | `False` | N/A | `run()`, `run_with_a2a()` | A2A disabled, acts like original |
| `SupervisorAgentA2A` | `True` | N/A | `run()`, `run_with_a2a()` | A2A enabled for `run_with_a2a()` |
| `SupervisorAgentHITL` | `False` | `False` | All 3 methods | Acts like original |
| `SupervisorAgentHITL` | `True` | `False` | All 3 methods | A2A enabled, HITL disabled |
| `SupervisorAgentHITL` | `True` | `True` | All 3 methods | Full system: A2A + HITL |

---

## 📊 Summary

### Integration Points

1. **Inheritance**: Each layer extends the previous
   - `SupervisorAgent` → `SupervisorAgentA2A` → `SupervisorAgentHITL`

2. **Mixins**: Reusable capabilities
   - `A2AAgentMixin` - Adds A2A methods to any agent
   - `HITLAgentMixin` - Adds HITL methods to any agent

3. **Singletons**: Shared coordinators
   - `A2AMessageBroker` - One broker for all agents
   - `HITLManager` - One manager for all approval requests

4. **Backward Compatibility**: Old methods always work
   - `run()` - Original behavior preserved
   - `run_with_a2a()` - New A2A behavior
   - `run_with_hitl()` - New A2A + HITL behavior

### Benefits

✅ **Zero Breaking Changes** - Old code works unchanged
✅ **Gradual Adoption** - Use features when ready
✅ **Modular Design** - Each layer independent
✅ **Flexible Configuration** - Enable/disable per instance

---

**Created**: 2025-10-09
**Status**: Production Ready
