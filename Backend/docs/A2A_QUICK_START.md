# A2A Quick Start Guide

## 🚀 5-Minute Setup

### 1. Test That Everything Works

```bash
python test_a2a_simple.py
```

Should output:
```
ALL TESTS PASSED!
```

### 2. Use in Your Code

#### Option A: Backward Compatible (Traditional Routing)

```python
from src.supervisor_agent_a2a import SupervisorAgentA2A

supervisor = SupervisorAgentA2A(
    yelp_api_key="your_key",
    enable_a2a=False  # Traditional mode
)

response = await supervisor.run("What is Botox?")
```

#### Option B: Enable A2A (Agent Collaboration)

```python
from src.supervisor_agent_a2a import SupervisorAgentA2A

supervisor = SupervisorAgentA2A(
    yelp_api_key="your_key",
    enable_a2a=True  # A2A mode
)

result = await supervisor.run_with_a2a("What is Botox and where can I get it in NYC?")

print(result['response'])      # The answer
print(result['method'])        # How it was processed
print(result['agents_used'])   # Which agents helped
```

## 📋 Common Use Cases

### Use Case 1: Simple Query (Single Agent)

```python
result = await supervisor.run_with_a2a("What is Botox?")
# ProductAgent handles this alone
```

### Use Case 2: Complex Query (Multiple Agents)

```python
result = await supervisor.run_with_a2a(
    "Tell me about Botox and find providers in Miami"
)
# ProductAgent gets info, then hands off to BusinessAgent
```

### Use Case 3: Direct Agent Communication

```python
response = await product_agent.send_request(
    recipient="business_agent",
    task="business_search",
    parameters={
        "query": "Botox clinics",
        "location": "New York, NY"
    },
    wait_for_response=True
)
```

### Use Case 4: Get Statistics

```python
stats = supervisor.get_a2a_statistics()
print(f"Total agents: {stats['total_agents']}")
print(f"Messages sent: {stats['total_messages']}")
```

## 📊 Key Methods

### SupervisorAgentA2A

```python
# New A2A method
result = await supervisor.run_with_a2a(query)
# Returns: {
#   'response': str,
#   'method': str,
#   'agents_used': list,
#   'conversation_id': str
# }

# Traditional method (still works!)
response = await supervisor.run(query)
# Returns: str

# Get statistics
stats = supervisor.get_a2a_statistics()
```

### Agent Communication

```python
# Send request
response = await agent.send_request(
    recipient="agent_id",
    task="task_name",
    parameters={...},
    wait_for_response=True
)

# Hand off task
response = await agent.handoff_to_agent(
    recipient="agent_id",
    task="task_name",
    user_message="original query",
    context={...},
    reason="why handing off",
    conversation_id="conv_123"
)

# Send notification
await agent.send_notification(
    recipient="agent_id",
    event="event_name",
    data={...}
)
```

## 🔍 Debugging

### Check Registered Agents

```python
from src.a2a_broker import get_broker

broker = get_broker()
agents = broker.list_agents()

for agent in agents:
    print(f"{agent.agent_id}: {agent.agent_type} ({agent.status})")
```

### View Message History

```python
broker = get_broker()
history = broker.get_conversation_history(conversation_id)

for msg in history:
    print(f"{msg.sender} -> {msg.recipient}: {msg.message_type}")
```

### Get Agent Capabilities

```python
profile = broker.get_agent_profile("product_agent")
for cap in profile.capabilities:
    print(f"- {cap.name}: {cap.description}")
```

## 🛠️ Common Patterns

### Pattern 1: Request-Response

```python
# Agent A requests help from Agent B
response = await agentA.send_request(
    recipient="agentB",
    task="do_something",
    parameters={"param": "value"},
    wait_for_response=True,
    timeout=30.0
)

if response and response.content.get("success"):
    data = response.content.get("data")
    # Process data
```

### Pattern 2: Task Handoff

```python
# Agent A hands off task to Agent B
response = await agentA.handoff_to_agent(
    recipient="agentB",
    task="complete_this",
    user_message=original_query,
    context={"info": "from A"},
    reason="Agent B is better suited",
    conversation_id=conv_id
)
```

### Pattern 3: Find Agent by Capability

```python
# Find any agent that can do "product_search"
response = await agent.request_agent_help(
    capability="product_search",
    task="product_search",
    parameters={"query": "Botox"}
)
```

## 📖 Full Documentation

For complete details, see:
- [A2A_DOCUMENTATION.md](A2A_DOCUMENTATION.md) - Full documentation
- [A2A_SUMMARY.md](A2A_SUMMARY.md) - Implementation summary

## ❓ FAQ

**Q: Do I need to change my existing code?**
A: No! All existing code works without changes.

**Q: Can I use both traditional and A2A modes?**
A: Yes! You can use both simultaneously for testing.

**Q: What happens if A2A fails?**
A: The system falls back to traditional routing.

**Q: How do I add a new agent?**
A: Inherit from `A2AAgentMixin`, define capabilities, call `_setup_a2a()`.

**Q: Is it production ready?**
A: Yes! Fully tested and backward compatible.

## 🎯 Next Steps

1. ✅ Run `test_a2a_simple.py` to verify setup
2. ✅ Try both modes (traditional and A2A)
3. ✅ Check broker statistics
4. ✅ Read full documentation for advanced features

---

**Questions?** See [A2A_DOCUMENTATION.md](A2A_DOCUMENTATION.md)
**Issues?** Check the Troubleshooting section in the docs
