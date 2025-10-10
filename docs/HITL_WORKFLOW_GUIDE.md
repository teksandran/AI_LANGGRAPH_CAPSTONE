# HITL Workflow Guide: How Human-in-the-Loop Works in This Project

## Table of Contents
1. [What is HITL?](#what-is-hitl)
2. [Why HITL in This Project?](#why-hitl-in-this-project)
3. [Complete Workflow](#complete-workflow)
4. [Components Involved](#components-involved)
5. [Step-by-Step Example](#step-by-step-example)
6. [Policy Configuration](#policy-configuration)
7. [API Workflow](#api-workflow)
8. [Code Examples](#code-examples)
9. [Real-World Scenarios](#real-world-scenarios)
10. [Troubleshooting](#troubleshooting)

---

## What is HITL?

**Human-in-the-Loop (HITL)** is a workflow pattern where AI-generated outputs are queued for human review and approval before being delivered to the end user. In this project, HITL ensures that sensitive or critical information (especially medical/aesthetic product information) is reviewed by qualified personnel before reaching users.

### Key Concepts

- **Approval Queue:** Agent responses that need review are placed in a queue
- **Policy Engine:** Rules determine which responses require approval
- **Async Waiting:** System waits (non-blocking) for human decision
- **Decision Types:** APPROVE, REJECT, MODIFY, ESCALATE
- **Audit Trail:** Complete logging of all decisions with timestamps

---

## Why HITL in This Project?

### Business Reasons

1. **Regulatory Compliance**
   - Medical product information (Botox, Evolus) requires accuracy
   - Healthcare compliance (FDA, HIPAA guidelines)
   - Legal liability protection

2. **Quality Assurance**
   - Prevent AI hallucinations from reaching users
   - Ensure consistent brand messaging
   - Verify factual accuracy

3. **Risk Mitigation**
   - Medical misinformation prevention
   - Sensitive content filtering
   - Brand reputation protection

### Use Cases in This Project

| Scenario | Why HITL? | Reviewer |
|----------|-----------|----------|
| Botox side effects query | Medical information accuracy | Nurse/Doctor |
| Product comparison | Ensure balanced, accurate comparison | Product Expert |
| Pricing information | Verify current pricing | Business Admin |
| Business recommendations | Quality check for provider list | Manager |
| Medical contraindications | Legal compliance | Medical Professional |

---

## Complete Workflow

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER QUERY                               │
│              "What are the side effects of Botox?"              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   SUPERVISOR AGENT (HITL)                       │
│  • Receives query                                               │
│  • Routes to ProductAgent for information                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCT AGENT (A2A)                          │
│  • Queries RAG system                                           │
│  • Generates draft response about Botox side effects           │
│  • Returns response to Supervisor                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   SUPERVISOR RECEIVES RESPONSE                  │
│  • Has draft response ready                                     │
│  • Needs to check if approval required                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    HITL MANAGER - POLICY CHECK                  │
│  ┌──────────────────────────────────────────────────┐          │
│  │  Policy: "medical_info_approval"                 │          │
│  │  Condition: content contains medical keywords    │          │
│  │  Action: REQUIRES_APPROVAL                       │          │
│  │  Priority: HIGH                                  │          │
│  │  Timeout: 300 seconds (5 minutes)               │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                 │
│  ✓ Policy matched: Medical information detected               │
│  ✓ Creating approval request...                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    APPROVAL REQUEST CREATED                     │
│  {                                                              │
│    "request_id": "hitl_abc123",                                │
│    "agent_id": "supervisor",                                   │
│    "action_type": "AGENT_RESPONSE",                           │
│    "action_data": {                                            │
│      "query": "What are the side effects...",                 │
│      "response": "Botox side effects include...",             │
│      "detected_keywords": ["medical", "side effects"]         │
│    },                                                          │
│    "priority": "HIGH",                                         │
│    "timeout": 300,                                             │
│    "timestamp": "2025-10-10T10:30:00Z"                        │
│  }                                                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   REQUEST ADDED TO QUEUE                        │
│  • Request stored in pending queue                             │
│  • Future object created (async wait)                          │
│  • System now waits for human decision                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ ⏳ WAITING (Non-blocking)
                         │
      ┌──────────────────┴──────────────────┐
      │                                     │
      ↓                                     ↓
┌──────────────────┐              ┌──────────────────┐
│  TIMEOUT PATH    │              │  APPROVAL PATH   │
│  (5 min expires) │              │  (Human reviews) │
└──────┬───────────┘              └────────┬─────────┘
       │                                   │
       ↓                                   ↓
┌──────────────────┐              ┌──────────────────────────────┐
│  Auto-reject     │              │   HUMAN REVIEWER             │
│  with message    │              │   (via API/Dashboard)        │
└──────────────────┘              │                              │
                                  │  1. GET /api/hitl/pending    │
                                  │     (Fetches pending items)  │
                                  │                              │
                                  │  2. Reviews content:         │
                                  │     - Query context          │
                                  │     - Generated response     │
                                  │     - Priority level         │
                                  │                              │
                                  │  3. Makes decision:          │
                                  │     • APPROVE (as-is)        │
                                  │     • REJECT (block)         │
                                  │     • MODIFY (edit first)    │
                                  │     • ESCALATE (to senior)   │
                                  │                              │
                                  │  4. POST /api/hitl/approve/  │
                                  │     or modify/reject         │
                                  └────────┬─────────────────────┘
                                           │
                                           ↓
                         ┌──────────────────────────────────────┐
                         │    HITL MANAGER RECEIVES DECISION    │
                         │  • Validates decision                │
                         │  • Logs to audit trail               │
                         │  • Resolves Future object            │
                         └────────┬─────────────────────────────┘
                                  │
                                  ↓
                         ┌──────────────────────────────────────┐
                         │    SUPERVISOR RECEIVES APPROVAL      │
                         │  {                                   │
                         │    "approved": true,                 │
                         │    "decision": "APPROVED",           │
                         │    "modified_response": null,        │
                         │    "reviewer_id": "admin@clinic.com",│
                         │    "timestamp": "2025-10-10T10:32:00"│
                         │  }                                   │
                         └────────┬─────────────────────────────┘
                                  │
                                  ↓
                         ┌──────────────────────────────────────┐
                         │    RESPONSE SENT TO USER             │
                         │  "Botox side effects include..."     │
                         │                                      │
                         │  [Approved by: admin@clinic.com]     │
                         │  [Approval time: 2 minutes]          │
                         └──────────────────────────────────────┘
```

---

## Components Involved

### 1. SupervisorAgentHITL
**File:** [src/supervisor_agent_hitl.py](../src/supervisor_agent_hitl.py)

**Role:** Main orchestrator with HITL capabilities

**Key Method:**
```python
async def run_with_hitl(self, user_message: str):
    """
    Process query with human approval workflow

    Flow:
    1. Get response using A2A (parallel agent queries)
    2. Check if approval required (via HITLAgentMixin)
    3. If required, wait for human decision
    4. Return approved/modified response or rejection
    """
```

**Inherits From:**
- `SupervisorAgentA2A` (for A2A communication)
- `HITLAgentMixin` (for HITL capabilities)

### 2. HITLAgentMixin
**File:** [src/hitl_agent_mixin.py](../src/hitl_agent_mixin.py)

**Role:** Reusable HITL capabilities for any agent

**Key Methods:**
```python
def _setup_hitl(self, agent_id: str):
    """Register with HITL manager"""

async def request_human_approval(
    self,
    action_type: HITLActionType,
    action_data: Dict[str, Any],
    priority: HITLPriority = HITLPriority.NORMAL,
    timeout: float = 300.0
) -> HITLResponse:
    """
    Request approval for an action
    Returns: HITLResponse with decision
    """

async def check_response_approval(
    self,
    query: str,
    response: str
) -> Dict[str, Any]:
    """
    Check if response needs approval
    Automatically requests approval if needed
    Returns: {"approved": bool, "response": str, ...}
    """
```

### 3. HITLManager (Singleton)
**File:** [src/hitl_manager.py](../src/hitl_manager.py)

**Role:** Central coordinator for all approval workflows

**Key Responsibilities:**
- Policy management (add, remove, check policies)
- Request queuing and tracking
- Timeout handling
- Decision recording
- Statistics and audit trail

**Key Methods:**
```python
def add_policy(self, policy: HITLPolicy):
    """Add approval policy"""

def remove_policy(self, policy_name: str):
    """Remove policy"""

async def request_approval(
    self,
    action_type: HITLActionType,
    agent_id: str,
    action_data: Dict[str, Any],
    priority: HITLPriority = HITLPriority.NORMAL,
    timeout: float = 300.0
) -> HITLResponse:
    """
    Request approval - blocks until human responds or timeout
    Uses asyncio.Future for non-blocking wait
    """

async def submit_response(
    self,
    request_id: str,
    decision: HITLDecision,
    reviewer_id: str,
    comments: Optional[str] = None,
    modified_data: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Submit human decision
    Resolves the Future object, unblocking the waiting agent
    """

def get_pending_requests(self) -> List[Dict[str, Any]]:
    """Get all pending approval requests"""

def get_statistics(self) -> Dict[str, Any]:
    """Get approval statistics"""
```

### 4. HITLAPIEndpoints
**File:** [src/hitl_api_endpoints.py](../src/hitl_api_endpoints.py)

**Role:** RESTful API for human reviewers

**Endpoints:**
```python
GET  /api/hitl/pending        # Get pending approvals
GET  /api/hitl/request/<id>   # Get specific request
POST /api/hitl/approve/<id>   # Approve request
POST /api/hitl/reject/<id>    # Reject request
POST /api/hitl/modify/<id>    # Modify and approve
POST /api/hitl/escalate/<id>  # Escalate to senior
GET  /api/hitl/statistics     # Get stats
GET  /api/hitl/history        # Get approval history
```

### 5. HITLProtocol
**File:** [src/hitl_protocol.py](../src/hitl_protocol.py)

**Role:** Data structures and enums

**Key Classes:**
```python
class HITLActionType(Enum):
    AGENT_RESPONSE = "agent_response"     # LLM-generated response
    API_CALL = "api_call"                 # External API call
    DATA_RETRIEVAL = "data_retrieval"     # Data access
    AGENT_HANDOFF = "agent_handoff"       # Transfer to another agent
    CUSTOM_ACTION = "custom_action"       # User-defined

class HITLDecision(Enum):
    APPROVED = "approved"       # Accept as-is
    REJECTED = "rejected"       # Block response
    MODIFIED = "modified"       # Accept with changes
    ESCALATED = "escalated"    # Send to higher authority

class HITLPriority(Enum):
    CRITICAL = 1  # Immediate attention required
    HIGH = 2      # Important, review soon
    NORMAL = 3    # Standard review
    LOW = 4       # Review when convenient

@dataclass
class HITLRequest:
    request_id: str
    agent_id: str
    action_type: HITLActionType
    action_data: Dict[str, Any]
    priority: HITLPriority
    timeout: float
    context: Dict[str, Any]
    timestamp: datetime

@dataclass
class HITLResponse:
    request_id: str
    decision: HITLDecision
    reviewer_id: str
    comments: Optional[str]
    modified_data: Optional[Dict[str, Any]]
    timestamp: datetime
```

---

## Step-by-Step Example

### Scenario: User Asks About Botox Side Effects

#### Step 1: User Query Arrives
```python
# User sends query via API
POST /api/query
{
    "query": "What are the side effects of Botox?",
    "mode": "hitl"  # Use HITL-enabled supervisor
}
```

#### Step 2: API Server Routes to HITL Supervisor
```python
# api_server.py
from src.supervisor_agent_hitl import SupervisorAgentHITL

supervisor = SupervisorAgentHITL(
    yelp_api_key=os.getenv("YELP_API_KEY"),
    enable_a2a=True,
    enable_hitl=True  # HITL enabled
)

result = await supervisor.run_with_hitl(user_query)
```

#### Step 3: Supervisor Processes with A2A
```python
# SupervisorAgentHITL.run_with_hitl()

# First, use A2A to get product information
a2a_result = await self.run_with_a2a(user_message)

# Extract the response
draft_response = a2a_result['response']
agents_used = a2a_result.get('agents_used', [])

# Now check if HITL approval needed
if self.hitl_enabled:
    approval = await self.check_response_approval(
        query=user_message,
        response=draft_response
    )

    if not approval["approved"]:
        # Response was rejected or timed out
        return {
            "response": approval["response"],
            "hitl_approved": False,
            "rejection_reason": approval.get("reason")
        }

    # Response was approved (possibly modified)
    final_response = approval["response"]
else:
    final_response = draft_response

return {
    "response": final_response,
    "hitl_approved": True,
    "agents_used": agents_used
}
```

#### Step 4: Check Response Approval
```python
# HITLAgentMixin.check_response_approval()

async def check_response_approval(self, query: str, response: str):
    """Check if response needs human approval"""

    # Check all policies
    manager = get_hitl_manager()

    # See if any policy requires approval
    requires_approval = False
    for policy in manager.policies.values():
        if policy.action_type == HITLActionType.AGENT_RESPONSE:
            # Check policy condition
            if policy.requires_approval({
                "query": query,
                "response": response,
                "agent_id": self.hitl_agent_id
            }):
                requires_approval = True
                break

    if not requires_approval:
        # No approval needed, return as-is
        return {
            "approved": True,
            "response": response
        }

    # Approval required - request it
    approval_response = await self.request_human_approval(
        action_type=HITLActionType.AGENT_RESPONSE,
        action_data={
            "query": query,
            "response": response,
            "agent_id": self.hitl_agent_id
        },
        priority=HITLPriority.HIGH,
        timeout=300.0  # 5 minutes
    )

    # Process the decision
    if approval_response.decision == HITLDecision.APPROVED:
        return {
            "approved": True,
            "response": response,
            "reviewer": approval_response.reviewer_id
        }
    elif approval_response.decision == HITLDecision.MODIFIED:
        return {
            "approved": True,
            "response": approval_response.modified_data.get("response", response),
            "reviewer": approval_response.reviewer_id,
            "modified": True
        }
    else:  # REJECTED
        return {
            "approved": False,
            "response": "This response requires review and was not approved.",
            "reason": approval_response.comments
        }
```

#### Step 5: HITL Manager Queues Request
```python
# HITLManager.request_approval()

async def request_approval(self, action_type, agent_id, action_data, priority, timeout):
    """Queue request and wait for human decision"""

    # Create request
    request = HITLRequest(
        request_id=f"hitl_{uuid.uuid4().hex[:8]}",
        agent_id=agent_id,
        action_type=action_type,
        action_data=action_data,
        priority=priority,
        timeout=timeout,
        context={},
        timestamp=datetime.now()
    )

    # Add to pending queue
    self._pending_requests[request.request_id] = request

    # Create Future for async wait
    future = asyncio.Future()
    self._request_futures[request.request_id] = future

    # Wait for human decision (with timeout)
    try:
        response = await asyncio.wait_for(future, timeout=timeout)
        self._approved_count += 1
        return response
    except asyncio.TimeoutError:
        # Timeout - auto-reject
        self._rejected_count += 1
        del self._pending_requests[request.request_id]
        del self._request_futures[request.request_id]

        return HITLResponse(
            request_id=request.request_id,
            decision=HITLDecision.REJECTED,
            reviewer_id="system",
            comments="Request timed out",
            modified_data=None,
            timestamp=datetime.now()
        )
```

#### Step 6: Human Reviewer Checks Queue
```bash
# Human reviewer dashboard polls for pending requests
GET http://localhost:5000/api/hitl/pending

# Response:
{
  "pending_requests": [
    {
      "request_id": "hitl_abc123",
      "agent_id": "supervisor",
      "action_type": "agent_response",
      "action_data": {
        "query": "What are the side effects of Botox?",
        "response": "Botox side effects may include: temporary bruising at injection site, headache, flu-like symptoms, droopy eyelids (if improperly administered), and muscle weakness. Most side effects are temporary and resolve within a few weeks. Serious side effects are rare but can include difficulty breathing, swallowing, or speaking. Contact your healthcare provider immediately if you experience any severe reactions.",
        "agent_id": "supervisor"
      },
      "priority": "HIGH",
      "timeout": 300,
      "timestamp": "2025-10-10T10:30:00Z",
      "time_remaining": 240
    }
  ],
  "total_pending": 1
}
```

#### Step 7: Human Makes Decision

**Option A: Approve As-Is**
```bash
POST http://localhost:5000/api/hitl/approve/hitl_abc123
{
  "reviewer_id": "nurse@clinic.com",
  "comments": "Medical information is accurate and appropriate"
}

# Response:
{
  "success": true,
  "message": "Request approved",
  "request_id": "hitl_abc123"
}
```

**Option B: Modify Then Approve**
```bash
POST http://localhost:5000/api/hitl/modify/hitl_abc123
{
  "reviewer_id": "doctor@clinic.com",
  "modified_data": {
    "response": "Botox side effects may include: temporary bruising at injection site, headache, flu-like symptoms, droopy eyelids (if improperly administered), and muscle weakness. Most side effects are temporary and resolve within a few weeks. Serious side effects are rare but can include difficulty breathing, swallowing, or speaking. **Always consult with a qualified healthcare provider before undergoing Botox treatment.** Contact your healthcare provider immediately if you experience any severe reactions."
  },
  "comments": "Added disclaimer about consulting healthcare provider"
}

# Response:
{
  "success": true,
  "message": "Request modified and approved",
  "request_id": "hitl_abc123"
}
```

**Option C: Reject**
```bash
POST http://localhost:5000/api/hitl/reject/hitl_abc123
{
  "reviewer_id": "compliance@clinic.com",
  "comments": "Response needs more specific warnings about contraindications"
}

# Response:
{
  "success": true,
  "message": "Request rejected",
  "request_id": "hitl_abc123"
}
```

#### Step 8: Decision Resolves Future
```python
# HITLManager.submit_response()

async def submit_response(self, request_id, decision, reviewer_id, comments, modified_data):
    """Submit human decision and resolve waiting Future"""

    # Create response
    response = HITLResponse(
        request_id=request_id,
        decision=decision,
        reviewer_id=reviewer_id,
        comments=comments,
        modified_data=modified_data,
        timestamp=datetime.now()
    )

    # Add to history
    self._history.append(response)

    # Remove from pending
    if request_id in self._pending_requests:
        del self._pending_requests[request_id]

    # Resolve the Future (unblocks waiting agent)
    if request_id in self._request_futures:
        future = self._request_futures[request_id]
        future.set_result(response)  # ← This unblocks the agent!
        del self._request_futures[request_id]

    return True
```

#### Step 9: Response Returned to User
```json
{
  "response": "Botox side effects may include: temporary bruising at injection site, headache, flu-like symptoms, droopy eyelids (if improperly administered), and muscle weakness. Most side effects are temporary and resolve within a few weeks. Serious side effects are rare but can include difficulty breathing, swallowing, or speaking. **Always consult with a qualified healthcare provider before undergoing Botox treatment.** Contact your healthcare provider immediately if you experience any severe reactions.",
  "hitl_approved": true,
  "reviewer": "doctor@clinic.com",
  "approval_time": 120,
  "modified": true,
  "agents_used": ["supervisor", "product_agent"],
  "method": "hitl"
}
```

---

## Policy Configuration

### Default Policies

The system comes with pre-configured policies in `src/hitl_protocol.py`:

```python
class DefaultHITLPolicies:
    """Pre-configured approval policies"""

    @staticmethod
    def medical_information_policy() -> HITLPolicy:
        """Require approval for medical information"""
        return HITLPolicy(
            name="medical_info_approval",
            description="Require human approval for medical information responses",
            action_type=HITLActionType.AGENT_RESPONSE,
            requires_approval=lambda data: any(
                keyword in data.get("response", "").lower()
                for keyword in ["medical", "side effects", "treatment", "dosage", "contraindication"]
            ),
            priority=HITLPriority.HIGH,
            timeout=300.0  # 5 minutes
        )

    @staticmethod
    def pricing_information_policy() -> HITLPolicy:
        """Require approval for pricing information"""
        return HITLPolicy(
            name="pricing_approval",
            description="Require approval for pricing information",
            action_type=HITLActionType.AGENT_RESPONSE,
            requires_approval=lambda data: any(
                keyword in data.get("response", "").lower()
                for keyword in ["price", "cost", "$", "pricing", "expensive", "cheap"]
            ),
            priority=HITLPriority.NORMAL,
            timeout=600.0  # 10 minutes
        )

    @staticmethod
    def external_api_policy() -> HITLPolicy:
        """Require approval for external API calls"""
        return HITLPolicy(
            name="api_call_approval",
            description="Require approval before making external API calls",
            action_type=HITLActionType.API_CALL,
            requires_approval=lambda data: True,  # Always require approval
            priority=HITLPriority.HIGH,
            timeout=180.0  # 3 minutes
        )
```

### Adding Custom Policies

```python
from src.hitl_manager import get_hitl_manager
from src.hitl_protocol import HITLPolicy, HITLActionType, HITLPriority

# Get HITL manager
manager = get_hitl_manager()

# Add custom policy
custom_policy = HITLPolicy(
    name="competitor_mention_policy",
    description="Require approval when competitor products are mentioned",
    action_type=HITLActionType.AGENT_RESPONSE,
    requires_approval=lambda data: any(
        competitor in data.get("response", "").lower()
        for competitor in ["competitor1", "competitor2"]
    ),
    priority=HITLPriority.NORMAL,
    timeout=300.0
)

manager.add_policy(custom_policy)
```

### Removing Policies

```python
# Remove policy by name
manager.remove_policy("pricing_approval")
```

---

## API Workflow

### For Human Reviewers

#### 1. Get Pending Approvals
```bash
GET /api/hitl/pending

Response:
{
  "pending_requests": [
    {
      "request_id": "hitl_abc123",
      "agent_id": "supervisor",
      "action_type": "agent_response",
      "action_data": {...},
      "priority": "HIGH",
      "time_remaining": 240
    }
  ],
  "total_pending": 1
}
```

#### 2. Get Specific Request Details
```bash
GET /api/hitl/request/hitl_abc123

Response:
{
  "request_id": "hitl_abc123",
  "agent_id": "supervisor",
  "action_type": "agent_response",
  "action_data": {
    "query": "What are the side effects of Botox?",
    "response": "Botox side effects may include..."
  },
  "priority": "HIGH",
  "timeout": 300,
  "timestamp": "2025-10-10T10:30:00Z",
  "time_remaining": 240
}
```

#### 3. Approve Request
```bash
POST /api/hitl/approve/hitl_abc123
Content-Type: application/json

{
  "reviewer_id": "nurse@clinic.com",
  "comments": "Information is accurate"
}

Response:
{
  "success": true,
  "message": "Request approved",
  "request_id": "hitl_abc123"
}
```

#### 4. Modify and Approve
```bash
POST /api/hitl/modify/hitl_abc123
Content-Type: application/json

{
  "reviewer_id": "doctor@clinic.com",
  "modified_data": {
    "response": "Updated response with additional disclaimers..."
  },
  "comments": "Added required disclaimers"
}

Response:
{
  "success": true,
  "message": "Request modified and approved",
  "request_id": "hitl_abc123"
}
```

#### 5. Reject Request
```bash
POST /api/hitl/reject/hitl_abc123
Content-Type: application/json

{
  "reviewer_id": "compliance@clinic.com",
  "comments": "Response contains inaccurate information"
}

Response:
{
  "success": true,
  "message": "Request rejected",
  "request_id": "hitl_abc123"
}
```

#### 6. Get Statistics
```bash
GET /api/hitl/statistics

Response:
{
  "pending_count": 2,
  "approved_count": 145,
  "rejected_count": 12,
  "modified_count": 38,
  "total_processed": 195,
  "average_response_time": 127.5,
  "approval_rate": 0.938
}
```

#### 7. Get History
```bash
GET /api/hitl/history?limit=10

Response:
{
  "history": [
    {
      "request_id": "hitl_abc123",
      "decision": "APPROVED",
      "reviewer_id": "nurse@clinic.com",
      "timestamp": "2025-10-10T10:32:00Z",
      "response_time": 120
    },
    ...
  ],
  "total_count": 195
}
```

---

## Code Examples

### Example 1: Enable HITL in Your Code

```python
import asyncio
from src.supervisor_agent_hitl import SupervisorAgentHITL
from src.hitl_manager import get_hitl_manager
from src.hitl_protocol import DefaultHITLPolicies

async def run_query_with_hitl():
    # Initialize supervisor with HITL enabled
    supervisor = SupervisorAgentHITL(
        yelp_api_key="your_yelp_key",
        llm_provider="openai",
        enable_a2a=True,
        enable_hitl=True  # Enable HITL
    )

    # Add policies
    manager = get_hitl_manager()
    manager.add_policy(DefaultHITLPolicies.medical_information_policy())

    # Run query
    result = await supervisor.run_with_hitl(
        "What are the side effects of Botox?"
    )

    print(f"Response: {result['response']}")
    print(f"HITL Approved: {result['hitl_approved']}")
    if result.get('reviewer'):
        print(f"Approved by: {result['reviewer']}")

# Run
asyncio.run(run_query_with_hitl())
```

### Example 2: Custom Policy

```python
from src.hitl_protocol import HITLPolicy, HITLActionType, HITLPriority

def business_recommendation_policy() -> HITLPolicy:
    """Require approval when recommending specific businesses"""
    return HITLPolicy(
        name="business_recommendation",
        description="Require approval for business recommendations",
        action_type=HITLActionType.AGENT_RESPONSE,
        requires_approval=lambda data: (
            "yelp" in data.get("agents_used", []) and
            any(word in data.get("response", "").lower()
                for word in ["recommend", "best", "top rated"])
        ),
        priority=HITLPriority.NORMAL,
        timeout=600.0
    )

# Add policy
manager = get_hitl_manager()
manager.add_policy(business_recommendation_policy())
```

### Example 3: HITL Disabled (Bypass)

```python
# For queries that don't need approval
supervisor = SupervisorAgentHITL(
    yelp_api_key="your_key",
    enable_a2a=True,
    enable_hitl=False  # Disable HITL
)

# Or use run_with_a2a() method instead
result = await supervisor.run_with_a2a("What is Botox?")
# No approval required, direct response
```

---

## Real-World Scenarios

### Scenario 1: Healthcare Clinic Portal

**Setup:**
```python
# Add strict medical policies
manager.add_policy(DefaultHITLPolicies.medical_information_policy())
manager.add_policy(DefaultHITLPolicies.pricing_information_policy())

# Custom policy for contraindications
contraindication_policy = HITLPolicy(
    name="contraindication_policy",
    description="Always require approval for contraindication information",
    action_type=HITLActionType.AGENT_RESPONSE,
    requires_approval=lambda data: "contraindication" in data.get("query", "").lower(),
    priority=HITLPriority.CRITICAL,
    timeout=180.0  # 3 minutes for critical items
)
manager.add_policy(contraindication_policy())
```

**Workflow:**
1. Patient asks: "Can I get Botox if I'm pregnant?"
2. System generates response
3. CRITICAL priority → immediate nurse/doctor review
4. Reviewer checks response, adds specific warnings
5. Approved response sent to patient
6. Full audit trail logged for compliance

### Scenario 2: Beauty Salon Chatbot

**Setup:**
```python
# Lighter policies for customer-facing chatbot
manager.add_policy(DefaultHITLPolicies.pricing_information_policy())

# Custom policy for booking-related queries
booking_policy = HITLPolicy(
    name="booking_confirmation",
    description="Require approval before confirming bookings",
    action_type=HITLActionType.CUSTOM_ACTION,
    requires_approval=lambda data: data.get("action") == "book_appointment",
    priority=HITLPriority.HIGH,
    timeout=300.0
)
manager.add_policy(booking_policy)
```

**Workflow:**
1. Customer asks: "How much does Botox cost?"
2. System generates pricing response
3. Manager reviews pricing accuracy
4. Approved response sent to customer
5. Customer proceeds to book → another approval for booking confirmation

### Scenario 3: Research Platform (No HITL)

**Setup:**
```python
# Research platform doesn't need approval
supervisor = SupervisorAgentHITL(
    yelp_api_key="your_key",
    enable_a2a=True,
    enable_hitl=False  # No approval needed
)
```

**Workflow:**
1. Researcher queries: "Compare Botox market presence in NYC vs LA"
2. System generates comprehensive analysis
3. No approval required
4. Direct response to researcher

---

## Troubleshooting

### Issue 1: Requests Timing Out

**Problem:** Approval requests consistently timing out

**Solutions:**
```python
# 1. Increase timeout
policy = HITLPolicy(
    name="my_policy",
    timeout=900.0  # 15 minutes instead of 5
    # ... other fields
)

# 2. Lower priority for non-urgent items
policy = HITLPolicy(
    name="my_policy",
    priority=HITLPriority.LOW,  # Review when convenient
    # ... other fields
)

# 3. Add auto-approval for timeouts (custom logic)
# In your code, handle timeout gracefully
if result.get('hitl_approved') == False:
    if "timeout" in result.get('reason', ''):
        # Log warning and use response anyway
        logging.warning("HITL timeout, using response")
```

### Issue 2: Too Many Approval Requests

**Problem:** Review queue is overwhelming

**Solutions:**
```python
# 1. Make policies more specific
def refined_medical_policy():
    return HITLPolicy(
        name="critical_medical_only",
        requires_approval=lambda data: any(
            keyword in data.get("response", "").lower()
            for keyword in ["contraindication", "serious side effects", "emergency"]
            # Removed less critical terms
        ),
        # ... other fields
    )

# 2. Use priority levels effectively
# CRITICAL: Immediate review required
# HIGH: Review within 5 minutes
# NORMAL: Review within 10 minutes
# LOW: Review when convenient

# 3. Implement business hours
def is_business_hours():
    now = datetime.now()
    return 9 <= now.hour < 17 and now.weekday() < 5

# Only require approval during business hours
policy = HITLPolicy(
    requires_approval=lambda data: (
        is_business_hours() and
        "medical" in data.get("response", "")
    ),
    # ... other fields
)
```

### Issue 3: Policies Not Triggering

**Problem:** Expected approvals not being requested

**Debug:**
```python
# 1. Check policy is added
manager = get_hitl_manager()
print("Active policies:", list(manager.policies.keys()))

# 2. Test policy condition
policy = manager.policies.get("medical_info_approval")
test_data = {
    "response": "Botox side effects include...",
    "query": "What are side effects?"
}
print("Policy triggers:", policy.requires_approval(test_data))

# 3. Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# 4. Check HITL is enabled
print("HITL enabled:", supervisor.hitl_enabled)
```

### Issue 4: API Endpoints Not Accessible

**Problem:** Human reviewers can't access approval API

**Solutions:**
```python
# 1. Ensure HITL endpoints are registered
from src.hitl_api_endpoints import hitl_bp
app.register_blueprint(hitl_bp)

# 2. Check CORS settings
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 3. Verify server is running
# http://localhost:5000/api/hitl/pending should work

# 4. Check firewall/network settings
```

---

## Summary

### HITL in This Project Provides:

✅ **Policy-Based Approval** - Flexible rules engine for determining when approval needed

✅ **Async Non-Blocking** - System doesn't freeze while waiting for human review

✅ **Multiple Decision Types** - APPROVE, REJECT, MODIFY, ESCALATE

✅ **Priority Levels** - CRITICAL to LOW for urgency management

✅ **Timeout Handling** - Auto-reject after configured time

✅ **Complete Audit Trail** - All decisions logged with timestamps and reviewers

✅ **RESTful API** - Easy integration with dashboards and workflows

✅ **Statistics & Monitoring** - Track approval rates and response times

✅ **Extensible** - Add custom policies without code changes

### Typical Use Cases:

1. **Healthcare/Medical** - Ensure medical information accuracy and compliance
2. **Financial Services** - Approve pricing and financial advice
3. **Legal** - Review contract terms and legal guidance
4. **E-commerce** - Verify product information and pricing
5. **Customer Service** - Quality check responses before sending

### Next Steps:

1. Read [HITL Documentation](HITL_DOCUMENTATION.md) for detailed API reference
2. See [HITL Summary](HITL_SUMMARY.md) for implementation overview
3. Try [tests/test_hitl_system.py](../tests/test_hitl_system.py) for working examples
4. Review [Integration Architecture](INTEGRATION_ARCHITECTURE.md) for system design

---

**Last Updated:** 2025-10-10
**Status:** ✅ Production Ready
**Related Docs:** [HITL_DOCUMENTATION.md](HITL_DOCUMENTATION.md), [HITL_SUMMARY.md](HITL_SUMMARY.md)

[← Back to Documentation Index](INDEX.md)
