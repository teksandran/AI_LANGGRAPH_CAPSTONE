# Agent-to-Agent (A2A) Communication System

## Overview

The A2A Communication System enables direct communication between agents in the Beauty Search multi-agent system. This allows agents to collaborate, share information, and coordinate actions without always going through the supervisor, enabling more flexible and efficient workflows.

## 🎯 Key Features

- **Direct Agent Communication**: Agents can send messages directly to each other
- **Backward Compatible**: Existing code continues to work without modification
- **Message Routing**: Central broker coordinates all agent interactions
- **Collaboration Patterns**: Support for handoffs, requests, and notifications
- **Monitoring**: Built-in statistics and conversation tracking
- **Async/Await**: Fully asynchronous for better performance

## 📋 Architecture

### Components

1. **A2A Protocol** (`a2a_protocol.py`)
   - Standardized message formats
   - Agent capability definitions
   - Message types and schemas

2. **Message Broker** (`a2a_broker.py`)
   - Central coordinator for all messages
   - Agent registration and discovery
   - Message routing and delivery
   - History and statistics tracking

3. **Agent Mixin** (`a2a_agent_mixin.py`)
   - Base class providing A2A capabilities
   - Common messaging methods
   - Request/response handling

4. **Enhanced Agents**
   - `ProductAgentA2A`: Product agent with A2A
   - `BusinessAgentA2A`: Business agent with A2A
   - `SupervisorAgentA2A`: Supervisor with A2A coordination

## 🔧 How It Works

### Message Flow

```
┌─────────────┐
│   Agent A   │
│             │
│ Send Request│──────┐
└─────────────┘      │
                     │
                     ▼
              ┌─────────────┐
              │   Broker    │
              │             │
              │  Routes Msg │
              └─────────────┘
                     │
                     │
                     ▼
              ┌─────────────┐
              │   Agent B   │
              │             │
              │Process & Rsp│──────┐
              └─────────────┘      │
                     ▲              │
                     │              │
                     └──────────────┘
```

### Message Types

1. **REQUEST**: Ask another agent to perform a task
2. **RESPONSE**: Reply to a request
3. **NOTIFICATION**: Inform another agent about an event
4. **HANDOFF**: Transfer a task to another agent
5. **QUERY**: Ask about agent capabilities

## 🚀 Usage

### Basic Setup

```python
from src.supervisor_agent_a2a import SupervisorAgentA2A

# Create supervisor with A2A enabled
supervisor = SupervisorAgentA2A(
    yelp_api_key="your_key",
    llm_provider="openai",
    enable_a2a=True  # Enable A2A communication
)

# Run a query using A2A
result = await supervisor.run_with_a2a("What is Botox?")
print(result['response'])
print(f"Agents used: {result['agents_used']}")
```

### Backward Compatibility

```python
# Old code still works - no changes needed!
supervisor = SupervisorAgentA2A(
    yelp_api_key="your_key",
    enable_a2a=False  # Disable A2A for traditional routing
)

response = await supervisor.run("What is Botox?")
```

### Direct Agent Communication

```python
# ProductAgent requests help from BusinessAgent
response = await product_agent.send_request(
    recipient="business_agent",
    task="business_search",
    parameters={
        "query": "Botox providers",
        "location": "New York, NY"
    },
    wait_for_response=True
)

if response.content.get("success"):
    data = response.content.get("data")
    print(data)
```

### Agent Handoff

```python
# ProductAgent hands off to BusinessAgent
response = await product_agent.handoff_to_agent(
    recipient="business_agent",
    task="find_providers",
    user_message=original_query,
    context={"product_info": product_details},
    reason="User needs provider locations",
    conversation_id=conv_id
)
```

### Request by Capability

```python
# Find any agent that can handle product search
response = await agent.request_agent_help(
    capability="product_search",
    task="product_search",
    parameters={"query": "Botox"}
)
```

## 📝 Message Examples

### Creating a Request

```python
from src.a2a_protocol import create_request_message

message = create_request_message(
    sender="product_agent",
    recipient="business_agent",
    task="business_search",
    parameters={
        "query": "Botox clinics",
        "location": "Miami, FL",
        "limit": 5
    },
    context={"user_preference": "high_rated"}
)
```

### Creating a Response

```python
from src.a2a_protocol import create_response_message

response = create_response_message(
    sender="business_agent",
    recipient="product_agent",
    success=True,
    data={"businesses": [...], "total": 5},
    reply_to=request_message.message_id,
    conversation_id=request_message.conversation_id
)
```

## 🔍 Monitoring & Debugging

### Get Broker Statistics

```python
stats = supervisor.get_a2a_statistics()

print(f"Total Agents: {stats['total_agents']}")
print(f"Total Messages: {stats['total_messages']}")
print(f"Active Conversations: {stats['active_conversations']}")

for agent_id, info in stats['agents'].items():
    print(f"{agent_id}: {info['message_count']} messages")
```

### View Conversation History

```python
from src.a2a_broker import get_broker

broker = get_broker()
history = broker.get_conversation_history(conversation_id)

for message in history:
    print(f"{message.sender} -> {message.recipient}: {message.message_type}")
```

## 🎨 Integration Examples

### API Server Integration

```python
# api_server.py
from src.supervisor_agent_a2a import SupervisorAgentA2A

supervisor = SupervisorAgentA2A(
    yelp_api_key=yelp_key,
    enable_a2a=True
)

@app.route('/api/query-a2a', methods=['POST'])
async def query_with_a2a():
    data = request.json
    result = await supervisor.run_with_a2a(data['query'])

    return jsonify({
        'response': result['response'],
        'method': result['method'],
        'agents_used': result['agents_used']
    })
```

### Custom Agent with A2A

```python
from src.a2a_agent_mixin import A2AAgentMixin
from src.a2a_protocol import AgentCapability

class CustomAgent(A2AAgentMixin):
    def __init__(self):
        super().__init__()

        capabilities = [
            AgentCapability(
                name="custom_task",
                description="My custom task",
                input_schema={"param": "string"},
                output_schema={"result": "string"}
            )
        ]

        self._setup_a2a(
            agent_id="custom_agent",
            agent_type="specialist",
            capabilities=capabilities
        )

    async def _handle_request(self, message):
        task = message.content.get("task")

        if task == "custom_task":
            # Process the task
            result = self.do_custom_work(message.content)

            return create_response_message(
                sender=self.agent_id,
                recipient=message.sender,
                success=True,
                data={"result": result},
                reply_to=message.message_id,
                conversation_id=message.conversation_id
            )

        return await super()._handle_request(message)
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_a2a_communication.py
```

Tests include:
- ✅ Backward compatibility
- ✅ Basic A2A communication
- ✅ Agent collaboration
- ✅ Direct agent communication
- ✅ Broker statistics

## 📊 Performance Considerations

### Message Delivery
- **Async messaging**: Non-blocking, efficient
- **Timeout support**: Configurable timeouts (default: 30s)
- **Error handling**: Graceful fallbacks

### Memory Usage
- **Message history**: Stored in memory (can be cleared)
- **Conversation tracking**: Per-conversation histories
- **Agent registry**: Lightweight profile storage

### Scalability
- **Concurrent messages**: Fully async, handles multiple concurrent messages
- **Agent discovery**: O(n) capability search (fast for small agent counts)
- **Broker overhead**: Minimal, single-threaded coordination

## 🔐 Best Practices

### 1. Always Handle Errors

```python
try:
    response = await agent.send_request(...)
    if response and response.content.get("success"):
        # Process success
    else:
        # Handle failure
except Exception as e:
    logger.error(f"A2A error: {e}")
    # Fallback logic
```

### 2. Use Timeouts

```python
response = await agent.send_request(
    ...,
    wait_for_response=True,
    timeout=10.0  # Don't wait forever
)
```

### 3. Clean Up History

```python
# Clear old conversations periodically
broker.clear_history(conversation_id="old_conv_123")
```

### 4. Monitor Agent Status

```python
profile = broker.get_agent_profile("product_agent")
if profile.status != "active":
    logger.warning(f"Agent {profile.agent_id} is {profile.status}")
```

### 5. Use Conversation IDs

```python
# Group related messages
conv_id = f"user_{user_id}_{timestamp}"

message = create_request_message(
    ...,
    conversation_id=conv_id
)
```

## 🐛 Troubleshooting

### Messages Not Delivered

**Check agent registration:**
```python
broker = get_broker()
agents = broker.list_agents()
print([a.agent_id for a in agents])
```

**Check agent status:**
```python
profile = broker.get_agent_profile("agent_id")
print(f"Status: {profile.status}")
```

### Timeout Errors

**Increase timeout:**
```python
response = await agent.send_request(
    ...,
    timeout=60.0  # Increase from default 30s
)
```

**Check if agent is responsive:**
```python
# Test with a simple message first
test_response = await agent.send_request(
    recipient="test_agent",
    task="ping",
    parameters={},
    timeout=5.0
)
```

### Agent Not Found

**Verify agent ID:**
```python
# List all available agents
agents = agent.get_available_agents()
for a in agents:
    print(f"{a.agent_id}: {a.agent_type}")
```

### Memory Issues

**Clear history regularly:**
```python
# In production, clear old conversations
broker.clear_history()  # Clear all

# Or clear specific conversation
broker.clear_history(conversation_id="...")
```

## 🔄 Migration Guide

### From SupervisorAgent to SupervisorAgentA2A

**Before:**
```python
from src.supervisor_agent import SupervisorAgent

supervisor = SupervisorAgent(yelp_api_key=key)
response = await supervisor.run(query)
```

**After (with A2A):**
```python
from src.supervisor_agent_a2a import SupervisorAgentA2A

supervisor = SupervisorAgentA2A(
    yelp_api_key=key,
    enable_a2a=True
)

# Option 1: Use A2A
result = await supervisor.run_with_a2a(query)
response = result['response']

# Option 2: Traditional (still works!)
response = await supervisor.run(query)
```

## 📚 API Reference

### AgentMixin Methods

- `send_request()`: Send a request to another agent
- `send_notification()`: Send a notification
- `handoff_to_agent()`: Hand off a task
- `request_agent_help()`: Find and request help by capability
- `get_available_agents()`: List all agents
- `activate_a2a()` / `deactivate_a2a()`: Control agent availability

### Broker Methods

- `register_agent()`: Register an agent
- `send_message()`: Send a message
- `broadcast_message()`: Send to all agents
- `get_conversation_history()`: Get conversation messages
- `get_statistics()`: Get broker stats
- `clear_history()`: Clear message history

## 🎓 Advanced Topics

### Custom Message Types

Extend the protocol for custom use cases:

```python
from src.a2a_protocol import MessageType, A2AMessage

# Define custom content schema
class CustomSchema:
    @staticmethod
    def create(custom_field: str) -> Dict[str, Any]:
        return {"custom_field": custom_field}

# Create message
message = A2AMessage(
    sender="agent_a",
    recipient="agent_b",
    message_type=MessageType.REQUEST,
    content=CustomSchema.create("value")
)
```

### Multi-Agent Workflows

Chain multiple agents:

```python
async def complex_workflow(query):
    # Step 1: Product info
    product_response = await product_agent.send_request(...)

    # Step 2: Business search (using product context)
    business_response = await business_agent.send_request(
        context={"product_info": product_response.content}
    )

    # Step 3: Combine results
    final_response = combine_responses(
        product_response,
        business_response
    )

    return final_response
```

## 📖 Further Reading

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [Multi-Agent Systems](https://en.wikipedia.org/wiki/Multi-agent_system)
- [Agent Communication Languages](https://en.wikipedia.org/wiki/Agent_communication_language)

## 🤝 Contributing

When adding new agents:

1. Inherit from `A2AAgentMixin`
2. Define capabilities in `AgentCapability` objects
3. Call `_setup_a2a()` in `__init__`
4. Override `_handle_request()` for custom tasks
5. Register with the broker

## 📄 License

Same as the main project.

---

**Version**: 1.0
**Date**: 2025-10-09
**Status**: Production Ready ✅
