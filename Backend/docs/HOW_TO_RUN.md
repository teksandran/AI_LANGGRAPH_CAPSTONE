# How to Run the Multi-Agent Beauty & Aesthetics Project

This guide will walk you through setting up and running the complete system.

---

## 📋 Prerequisites

- **Python 3.12+** installed
- **Node.js 16+** and npm (for React frontend)
- **API Keys** (obtain these first):
  - Yelp API Key: https://www.yelp.com/developers
  - OpenAI API Key: https://platform.openai.com/api-keys
  - OR Anthropic API Key: https://console.anthropic.com/

---

## 🚀 Quick Start (3 Steps)

### Step 1: Set Up the Backend (Flask API)

```bash
# 1. Navigate to the project directory
cd "C:\New Development 2025\AI ML\Agentic AI\Capstone Demo\yelp_mcp"

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure environment variables
# Make sure .env file exists with your API keys
# (Already present in your project)

# 4. Start the API server
python api_server.py
```

**Expected Output:**
```
============================================================
Multi-Agent API Server
============================================================
LLM Provider: OPENAI
SupervisorAgent: [OK] Initialized
RAG System: [OK] Ready
============================================================

Server starting on http://localhost:5000
Ready for React frontend integration!
```

### Step 2: Index Products (One-time setup)

**Open a NEW terminal** and run:

```bash
curl -X POST http://localhost:5000/api/index-products
```

This will:
- Scrape Botox.com and Evolus.com
- Index content into RAG vector database
- Takes 2-3 minutes

**Expected Response:**
```json
{
  "status": "success",
  "message": "Products indexed successfully",
  "statistics": {
    "botox": 15,
    "evolus": 12,
    "total_documents": 450
  }
}
```

### Step 3: Set Up the Frontend (React)

```bash
# 1. Navigate to your React project
cd "C:\path\to\your\react-project"

# 2. Install axios for API calls
npm install axios

# 3. Create the API service file
# Create: src/services/apiService.js
# (Copy the code from the updated React integration guide)

# 4. Update your App.jsx
# (Copy the updated App.jsx code provided earlier)

# 5. Start the React app
npm start
```

Your React app will open at: http://localhost:3000

---

## 📂 Project Structure

```
yelp_mcp/
├── api_server.py              # Main Flask API server (NEW - Use this!)
├── app.py                     # Old Flask app (ignore this)
├── src/
│   ├── supervisor_agent.py    # Coordinator agent
│   ├── product_agent.py       # RAG-based product info
│   ├── business_agent.py      # Yelp business search
│   └── rag_system.py          # Vector database system
├── .env                       # API keys (already configured)
├── requirements.txt           # Python dependencies
└── REACT_API_GUIDE.md        # React integration guide

Your React Project/
├── src/
│   ├── services/
│   │   └── apiService.js     # API service (create this)
│   └── App.jsx               # Main component (update this)
└── package.json
```

---

## 🔧 Detailed Setup Instructions

### A. Backend Setup (Flask API)

#### 1. Install Dependencies

```bash
cd "C:\New Development 2025\AI ML\Agentic AI\Capstone Demo\yelp_mcp"
pip install -r requirements.txt
```

#### 2. Verify API Keys

Check your `.env` file has:

```env
YELP_API_KEY=your_yelp_key_here
OPENAI_API_KEY=your_openai_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_key_here
```

#### 3. Start the Server

**Option A: Using Python directly**
```bash
python api_server.py
```

**Option B: Using batch file (Windows)**
```bash
start_api.bat
```

**Server will run on:** http://localhost:5000

#### 4. Verify Server is Running

```bash
# Test health endpoint
curl http://localhost:5000/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "supervisor_agent": true,
  "rag_indexed": false,
  "llm_provider": "openai"
}
```

#### 5. Index Products (Required!)

```bash
curl -X POST http://localhost:5000/api/index-products
```

Wait 2-3 minutes for completion. You'll see:
```json
{
  "status": "success",
  "message": "Products indexed successfully"
}
```

---

### B. Frontend Setup (React)

#### 1. Create API Service File

Create `src/services/apiService.js`:

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Main query - SupervisorAgent routes automatically
export const queryAgent = async (query) => {
  try {
    const response = await api.post('/api/query', { query });
    return { success: true, data: response.data };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.message || error.message,
    };
  }
};

// Product query - Direct to ProductAgent
export const queryProducts = async (query, brand = null) => {
  try {
    const response = await api.post('/api/product-query', {
      query, brand, limit: 3
    });
    return { success: true, data: response.data };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.message || error.message,
    };
  }
};

// Business query - Direct to BusinessAgent
export const queryBusinesses = async (query, location = '') => {
  try {
    const response = await api.post('/api/business-query', {
      query, location
    });
    return { success: true, data: response.data };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.message || error.message,
    };
  }
};

// Health check
export const checkHealth = async () => {
  try {
    const response = await api.get('/api/health');
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export default api;
```

#### 2. Update App.jsx

Replace your existing App.jsx with the updated code provided earlier (see previous response).

#### 3. Install Dependencies

```bash
npm install axios
```

#### 4. Start React App

```bash
npm start
```

App opens at: http://localhost:3000

---

## 🧪 Testing the System

### Test 1: Product Query (ProductAgent)

**In React UI, type:**
```
What is Botox used for?
```

**Expected:** Detailed product information from RAG system

**Or via curl:**
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is Botox used for?\"}"
```

### Test 2: Business Query (BusinessAgent)

**In React UI, type:**
```
Find Botox clinics in New York
```

**Expected:** List of businesses from Yelp API

**Or via curl:**
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Find Botox clinics in New York\"}"
```

### Test 3: Product Comparison

**In React UI, type:**
```
Compare Botox and Evolus
```

**Expected:** Side-by-side comparison

**Or via curl:**
```bash
curl -X POST http://localhost:5000/api/compare-products \
  -H "Content-Type: application/json" \
  -d "{\"product1\": \"botox\", \"product2\": \"evolus\"}"
```

---

## 🔍 API Endpoints Reference

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/api/health` | GET | Health check | `curl http://localhost:5000/api/health` |
| `/api/query` | POST | Main query (auto-routes) | `{"query": "What is Botox?"}` |
| `/api/product-query` | POST | Direct product query | `{"query": "Botox info", "brand": "botox"}` |
| `/api/business-query` | POST | Direct business query | `{"query": "Find spas", "location": "NYC"}` |
| `/api/compare-products` | POST | Compare products | `{"product1": "botox", "product2": "evolus"}` |
| `/api/index-products` | POST | Index products | (No body required) |
| `/api/rag-status` | GET | RAG system status | `curl http://localhost:5000/api/rag-status` |

---

## 🐛 Troubleshooting

### Issue 1: "ModuleNotFoundError: No module named 'flask_cors'"

**Solution:**
```bash
pip install flask-cors
# Or reinstall all dependencies:
pip install -r requirements.txt
```

### Issue 2: "SupervisorAgent not initialized"

**Cause:** Missing API keys

**Solution:**
1. Check `.env` file exists
2. Verify you have either `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
3. Restart the server

### Issue 3: "RAG system not indexed"

**Cause:** Products not indexed yet

**Solution:**
```bash
curl -X POST http://localhost:5000/api/index-products
```

### Issue 4: Port 5000 already in use

**Solution:**
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change port in api_server.py line 333:
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Issue 5: CORS errors in React

**Solution:**
- Ensure Flask server is running
- CORS is already enabled in `api_server.py`
- Check browser console for exact error

### Issue 6: "Unable to reach backend"

**Checklist:**
1. Flask server running? Check terminal for errors
2. Correct URL? Should be `http://localhost:5000`
3. Products indexed? Run index command
4. API keys valid? Check `.env` file

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────┐
│         React Frontend                   │
│        (localhost:3000)                  │
└──────────────┬──────────────────────────┘
               │ HTTP/REST API
               ▼
┌─────────────────────────────────────────┐
│      Flask API Server                    │
│      (localhost:5000)                    │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │     SupervisorAgent                │ │
│  │     (Query Router)                 │ │
│  └────────┬─────────────────┬─────────┘ │
│           │                 │            │
│           ▼                 ▼            │
│  ┌─────────────┐   ┌──────────────────┐ │
│  │ProductAgent │   │ BusinessAgent    │ │
│  │(RAG System) │   │ (Yelp API)       │ │
│  └──────┬──────┘   └────────┬─────────┘ │
│         │                   │            │
└─────────┼───────────────────┼────────────┘
          │                   │
          ▼                   ▼
    ┌──────────┐         ┌─────────┐
    │ FAISS DB │         │Yelp API │
    │ (Botox/  │         │(Business│
    │ Evolus)  │         │ Search) │
    └──────────┘         └─────────┘
```

---

## 🎯 Complete Workflow

1. **User enters query in React UI**
2. **React sends request to Flask API** (`/api/query`)
3. **SupervisorAgent analyzes the query**:
   - Product keywords? → Route to **ProductAgent**
   - Location/business keywords? → Route to **BusinessAgent**
4. **Agent processes query**:
   - **ProductAgent**: Searches FAISS vector DB (Botox/Evolus data)
   - **BusinessAgent**: Calls Yelp API for businesses
5. **Response sent back to React**
6. **React displays formatted results**

---

## 📝 Quick Commands Cheat Sheet

```bash
# Backend
cd "C:\New Development 2025\AI ML\Agentic AI\Capstone Demo\yelp_mcp"
python api_server.py                                    # Start server
curl -X POST http://localhost:5000/api/index-products  # Index products
curl http://localhost:5000/api/health                  # Health check

# Frontend
cd your-react-project
npm install axios                                       # Install deps
npm start                                              # Start React

# Testing
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is Botox?\"}"                 # Test product query

curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Find spas in LA\"}"                # Test business query
```

---

## 🎉 Success Checklist

- [ ] Python dependencies installed
- [ ] API keys configured in `.env`
- [ ] Flask server running on port 5000
- [ ] Products indexed successfully
- [ ] Health endpoint returns `"status": "healthy"`
- [ ] React app running on port 3000
- [ ] axios installed in React project
- [ ] API service file created
- [ ] App.jsx updated with new code
- [ ] Test queries working in React UI

---

## 📚 Additional Resources

- **API Documentation**: [REACT_API_GUIDE.md](REACT_API_GUIDE.md)
- **Quick Start**: [QUICK_START.md](QUICK_START.md)
- **Agent Code**:
  - [supervisor_agent.py](src/supervisor_agent.py)
  - [product_agent.py](src/product_agent.py)
  - [business_agent.py](src/business_agent.py)

---

## 🆘 Need Help?

If you encounter issues:
1. Check this guide's Troubleshooting section
2. Verify all prerequisites are met
3. Check terminal/console for error messages
4. Ensure API keys are valid and not expired

**Common Issues:**
- Missing dependencies → Run `pip install -r requirements.txt`
- Port conflicts → Change port in `api_server.py`
- RAG errors → Run product indexing
- CORS errors → Ensure Flask server is running

---

**You're all set! Happy coding! 🚀**
