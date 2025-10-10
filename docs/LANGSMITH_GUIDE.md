# LangSmith Integration Guide

This guide explains how LangSmith tracing and monitoring is integrated into the Beauty & Aesthetics Multi-Agent System.

---

## 🎯 What is LangSmith?

**LangSmith** is a platform for debugging, testing, evaluating, and monitoring LLM applications. It provides:
- **Tracing** - Track every step of your agent's decision-making process
- **Debugging** - See exactly what happened when things go wrong
- **Monitoring** - Track performance, latency, and costs
- **Evaluation** - Test and improve agent responses

**Dashboard:** https://smith.langchain.com/

---

## ✅ LangSmith is Already Configured!

Your system is already set up with LangSmith. Here's what's configured:

### Environment Variables (`.env`)

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langchain_api_key_here
LANGCHAIN_PROJECT=beauty-aesthetics-agent
```

### What Gets Traced Automatically:

1. **SupervisorAgent** - All routing decisions
2. **ProductAgent** - RAG queries and responses
3. **BusinessAgent** - Yelp API calls
4. **LangChain/LangGraph** - All LLM calls, tool usage, agent steps

---

## 📊 What LangSmith Captures

### Automatic Tracing (Built into LangChain):

- **LLM Calls** - Every OpenAI/Anthropic API call
- **Agent Steps** - Each decision the SupervisorAgent makes
- **Tool Usage** - When agents call tools (RAG search, Yelp API)
- **Prompts & Responses** - Full conversation history
- **Latency** - How long each step takes
- **Tokens** - Token usage for cost tracking

### Custom Logging (We Added):

- **Query Metadata** - User queries, endpoints hit
- **Agent Execution Time** - Duration in milliseconds
- **Success/Error Status** - Whether query succeeded
- **Response Length** - Size of responses

---

## 🚀 How to Use LangSmith

### Step 1: Start the Server

```bash
cd "C:\New Development 2025\AI ML\Agentic AI\Capstone Demo\yelp_mcp"
python api_server.py
```

You'll see:

```
============================================================
LangSmith Tracing Configuration
============================================================
Enabled: True
Project: beauty-aesthetics-agent
Endpoint: https://api.smith.langchain.com
API Key Set: True

[OK] LangSmith tracing is ACTIVE
  View traces at: https://smith.langchain.com/
  Project: beauty-aesthetics-agent
============================================================
```

### Step 2: Send Some Queries

```bash
# Product query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Botox?"}'

# Business query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find beauty salons in New York"}'
```

### Step 3: View Traces in LangSmith

1. Go to https://smith.langchain.com/
2. Sign in (if needed)
3. Select project: `beauty-aesthetics-agent`
4. You'll see all your traces!

---

## 🔍 Understanding Traces

### What You'll See in LangSmith:

#### 1. **Trace Overview**
- Total execution time
- Number of steps
- Success/failure status
- Input query and final output

#### 2. **Agent Steps**
```
SupervisorAgent
  ├─ LLM Call (OpenAI gpt-4o-mini)
  │   ├─ Prompt: "Route this query..."
  │   └─ Response: "product_agent"
  ├─ ProductAgent
  │   ├─ RAG Search
  │   │   ├─ Vector DB Query
  │   │   └─ Retrieved Documents
  │   └─ Response Generation
  └─ Final Response
```

#### 3. **Detailed Metrics**
- **Latency**: Time for each step
- **Tokens**: Input/output tokens per LLM call
- **Cost**: Estimated API costs
- **Metadata**: Custom data we logged

---

## 📈 What to Monitor

### Key Metrics to Track:

1. **Average Response Time**
   - ProductAgent: Should be 2-5 seconds (after indexing)
   - BusinessAgent: Should be 3-8 seconds

2. **Token Usage**
   - Monitor costs
   - Optimize prompts if tokens are high

3. **Error Rate**
   - Track failed queries
   - Debug issues faster

4. **Agent Routing**
   - See how often SupervisorAgent routes to each agent
   - Verify routing logic works correctly

---

## 🛠️ Code Implementation

### How It Works:

#### 1. **Automatic Tracing** (LangChain Built-in)

LangChain automatically sends traces to LangSmith when these env vars are set:
```python
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key_here...
```

No code changes needed! Every LangChain/LangGraph call is automatically traced.

#### 2. **Custom Logging** (We Added)

In `api_server.py`, we added custom logging:

```python
from src.langsmith_config import log_agent_execution

# In the /api/query endpoint:
if is_langsmith_enabled():
    log_agent_execution(
        agent_name="SupervisorAgent",
        query=query,
        response=response,
        duration_ms=duration_ms,
        metadata={
            'endpoint': '/api/query',
            'status': 'success',
            'response_length': len(response)
        }
    )
```

This adds extra context that shows up in LangSmith logs.

---

## 🎨 Viewing Traces

### In the LangSmith Dashboard:

#### Filter by Project:
```
Project: beauty-aesthetics-agent
```

#### Filter by Agent:
```
Tags: SupervisorAgent, ProductAgent, BusinessAgent
```

#### Filter by Status:
```
Status: success, error
```

#### Search by Query:
```
Input contains: "Botox"
```

---

## 🧪 Testing with LangSmith

### Test Different Query Types:

```bash
# 1. Product Information (ProductAgent)
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare Botox and Evolus"}'

# 2. Business Search (BusinessAgent)
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find spas in Los Angeles"}'

# 3. Ambiguous Query (Tests Routing)
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about Botox and where to get it"}'
```

Then check LangSmith to see:
- Which agent handled each query
- How long each step took
- What the LLM decision-making process was

---

## 📝 Custom Logging Functions

### Available Utility Functions:

```python
from src.langsmith_config import (
    is_langsmith_enabled,
    log_agent_decision,
    log_agent_execution,
    trace_agent
)
```

#### 1. `is_langsmith_enabled()`
Check if LangSmith is active:
```python
if is_langsmith_enabled():
    print("LangSmith is tracking this!")
```

#### 2. `log_agent_decision()`
Log routing decisions:
```python
log_agent_decision(
    agent_name="SupervisorAgent",
    query="What is Botox?",
    decision="Route to ProductAgent",
    metadata={"confidence": 0.95}
)
```

#### 3. `log_agent_execution()`
Log execution metrics:
```python
log_agent_execution(
    agent_name="ProductAgent",
    query="What is Botox?",
    response="Botox is an injectable...",
    duration_ms=2547.23,
    metadata={"source": "RAG"}
)
```

#### 4. `@trace_agent` Decorator
Automatically trace a function:
```python
from src.langsmith_config import trace_agent

@trace_agent("ProductAgent")
async def run(self, query: str):
    # Function is automatically traced
    return result
```

---

## 🔧 Configuration Options

### Disable LangSmith (if needed):

In `.env`, change:
```env
LANGCHAIN_TRACING_V2=false
```

### Change Project Name:

In `.env`, change:
```env
LANGCHAIN_PROJECT=my-custom-project-name
```

### Use Different Endpoint:

```env
LANGCHAIN_ENDPOINT=https://my-custom-langsmith-instance.com
```

---

## 🎯 Best Practices

### 1. **Monitor Regularly**
- Check traces daily during development
- Look for slow queries
- Identify error patterns

### 2. **Use Metadata**
- Add context to traces with metadata
- Tag traces by feature/user/session

### 3. **Debug with Traces**
- When something breaks, check the trace
- See exact LLM inputs/outputs
- Identify where it failed

### 4. **Optimize Based on Data**
- Find slow agents
- Reduce unnecessary LLM calls
- Optimize prompts for fewer tokens

---

## 📚 Example Trace Analysis

### Scenario: "What is Botox?" Query

**Trace Breakdown:**

1. **HTTP Request** (0ms)
   - Endpoint: POST /api/query
   - Input: {"query": "What is Botox?"}

2. **SupervisorAgent** (1,234ms)
   - LLM Call #1: Route decision
   - Decision: "product_agent"

3. **ProductAgent** (2,100ms)
   - RAG Search: Vector similarity search
   - Retrieved: 3 documents
   - LLM Call #2: Generate response

4. **Response** (3,334ms total)
   - Output: "BOTOX is an Injectable Neurotoxin..."
   - Tokens: 450 input, 200 output
   - Cost: $0.0032

**Insights:**
- Most time spent in RAG search (2.1s)
- Consider caching frequent queries
- Token usage is reasonable

---

## 🚨 Troubleshooting

### LangSmith Not Showing Traces:

1. **Check Environment Variables:**
   ```bash
   echo $LANGCHAIN_TRACING_V2
   echo $LANGCHAIN_API_KEY
   ```

2. **Verify API Key:**
   - Make sure key is valid
   - Check at https://smith.langchain.com/settings

3. **Check Logs:**
   - Look for "LangSmith tracing enabled" in server logs
   - Check for connection errors

### Traces Missing Information:

- Custom metadata might not be showing
- Check that `log_agent_execution()` is being called
- Verify metadata is structured correctly

---

## 📊 Metrics Dashboard

### Key Metrics to Track:

| Metric | Target | Current |
|--------|--------|---------|
| Avg Response Time | < 5s | Check Dashboard |
| Error Rate | < 5% | Check Dashboard |
| Token Usage | Track | Check Dashboard |
| Cost per Query | Minimize | Check Dashboard |

### Access Metrics:
https://smith.langchain.com/o/[your-org]/projects/p/beauty-aesthetics-agent

---

## 🎓 Learn More

- **LangSmith Docs:** https://docs.smith.langchain.com/
- **LangChain Tracing:** https://python.langchain.com/docs/langsmith/
- **API Reference:** https://api.smith.langchain.com/docs

---

## ✅ Summary

- ✅ LangSmith is **enabled** and **configured**
- ✅ All agent calls are **automatically traced**
- ✅ Custom logging adds **extra context**
- ✅ View traces at https://smith.langchain.com/
- ✅ Project name: `beauty-aesthetics-agent`

**Start sending queries and watch the traces appear in real-time!** 🚀
