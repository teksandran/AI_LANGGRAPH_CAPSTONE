# React Integration Guide - Multi-Agent API

This guide shows you how to integrate the Multi-Agent System API with your React application.

## Table of Contents
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [React Integration Examples](#react-integration-examples)
- [Architecture Overview](#architecture-overview)

---

## Quick Start

### 1. Start the API Server

```bash
# Navigate to the yelp_mcp directory
cd "C:\New Development 2025\AI ML\Agentic AI\Capstone Demo\yelp_mcp"

# Install dependencies (if not already done)
pip install -r requirements.txt

# Set up environment variables (see .env.example)
# Required: YELP_API_KEY, OPENAI_API_KEY or ANTHROPIC_API_KEY

# Start the server
python api_server.py
```

Server will start at: **`http://localhost:5000`**

### 2. Index Products (First Time Setup)

Before using product queries, you need to index the product data:

```bash
curl -X POST http://localhost:5000/api/index-products
```

This scrapes and indexes Botox and Evolus websites into the RAG system.

---

## API Endpoints

### Base URL
```
http://localhost:5000
```

### 1. Health Check
**Endpoint:** `GET /api/health`

Check if the API is running and agents are initialized.

**Response:**
```json
{
  "status": "healthy",
  "supervisor_agent": true,
  "rag_indexed": true,
  "llm_provider": "openai",
  "agents": {
    "supervisor": true,
    "product_agent": true,
    "business_agent": true
  }
}
```

---

### 2. Main Query Endpoint (Supervisor Agent)
**Endpoint:** `POST /api/query`

Routes queries automatically to the appropriate agent (ProductAgent or BusinessAgent).

**Request Body:**
```json
{
  "query": "What is Botox used for?"
}
```

**Response:**
```json
{
  "status": "success",
  "query": "What is Botox used for?",
  "response": "**BOTOX (Botox)**\n\n**Type:** Injectable Neurotoxin\n**Treatment Areas:** Forehead, frown lines, crow's feet...",
  "agent_type": "supervisor"
}
```

**Use Case:** Let the supervisor automatically decide which agent to use based on the query.

---

### 3. Product Query (Direct to ProductAgent)
**Endpoint:** `POST /api/product-query`

Directly query the ProductAgent for product information.

**Request Body:**
```json
{
  "query": "Tell me about Botox",
  "brand": "botox",
  "limit": 3
}
```

**Parameters:**
- `query` (required): The product question
- `brand` (optional): Filter by brand ("botox" or "evolus")
- `limit` (optional): Number of results (default: 3)

**Response:**
```json
{
  "status": "success",
  "query": "Tell me about Botox",
  "brand_filter": "botox",
  "results": [
    {
      "product_name": "Botox Cosmetic",
      "brand": "botox",
      "product_type": "Injectable Neurotoxin",
      "treatment_areas": "forehead, frown lines, crow's feet",
      "content": "Product information...",
      "source": "https://www.botox.com/"
    }
  ],
  "total": 1,
  "agent_type": "product"
}
```

---

### 4. Business Query (Direct to BusinessAgent)
**Endpoint:** `POST /api/business-query`

Directly query the BusinessAgent for business/location searches via Yelp API.

**Request Body:**
```json
{
  "query": "Find Botox clinics",
  "location": "New York, NY"
}
```

**Parameters:**
- `query` (required): What you're looking for
- `location` (optional): Where to search (city, state, or zip)

**Response:**
```json
{
  "status": "success",
  "query": "Find Botox clinics",
  "location": "New York, NY",
  "response": "**Found 5 botox injections in New York:**\n\n**1. ABC Med Spa**\n   Rating: 4.5 ⭐ (120 reviews)\n   Price: $$$\n   Address: 123 Park Ave...",
  "agent_type": "business"
}
```

---

### 5. Compare Products
**Endpoint:** `POST /api/compare-products`

Compare two products side-by-side.

**Request Body:**
```json
{
  "product1": "botox",
  "product2": "evolus"
}
```

**Response:**
```json
{
  "status": "success",
  "comparison": {
    "botox": [
      {
        "product_name": "Botox Cosmetic",
        "product_type": "Injectable Neurotoxin",
        "treatment_areas": "forehead, frown lines",
        "content": "Product details..."
      }
    ],
    "evolus": [
      {
        "product_name": "Jeuveau",
        "product_type": "Injectable Neurotoxin",
        "treatment_areas": "glabellar lines, frown lines",
        "content": "Product details..."
      }
    ]
  },
  "agent_type": "product"
}
```

---

### 6. Index Products
**Endpoint:** `POST /api/index-products`

Index product websites into the RAG system (run once on first setup).

**Response:**
```json
{
  "status": "success",
  "message": "Products indexed successfully",
  "statistics": {
    "botox": 15,
    "evolus": 12,
    "total_documents": 450,
    "total_pages": 27
  }
}
```

---

### 7. RAG Status
**Endpoint:** `GET /api/rag-status`

Get RAG system status and statistics.

**Response:**
```json
{
  "status": "success",
  "indexed": true,
  "summary": {
    "total_documents": 450,
    "products": 35,
    "webpages": 27,
    "brands": ["botox", "evolus"],
    "indexed_urls": ["https://www.botox.com/", "https://www.evolus.com/"]
  }
}
```

---

## React Integration Examples

### Setup Axios (or Fetch)

```bash
npm install axios
```

### Create API Service File

**`src/services/api.js`**

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health check
export const checkHealth = async () => {
  const response = await api.get('/api/health');
  return response.data;
};

// Main query (supervisor routes automatically)
export const queryAgent = async (query) => {
  const response = await api.post('/api/query', { query });
  return response.data;
};

// Product query
export const queryProducts = async (query, brand = null, limit = 3) => {
  const response = await api.post('/api/product-query', {
    query,
    brand,
    limit,
  });
  return response.data;
};

// Business query
export const queryBusinesses = async (query, location = '') => {
  const response = await api.post('/api/business-query', {
    query,
    location,
  });
  return response.data;
};

// Compare products
export const compareProducts = async (product1 = 'botox', product2 = 'evolus') => {
  const response = await api.post('/api/compare-products', {
    product1,
    product2,
  });
  return response.data;
};

// Index products (first time setup)
export const indexProducts = async () => {
  const response = await api.post('/api/index-products');
  return response.data;
};

// Get RAG status
export const getRagStatus = async () => {
  const response = await api.get('/api/rag-status');
  return response.data;
};

export default api;
```

---

### Example React Component

**`src/components/SearchInterface.jsx`**

```javascript
import React, { useState, useEffect } from 'react';
import { queryAgent, checkHealth } from '../services/api';

function SearchInterface() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState(null);

  useEffect(() => {
    // Check API health on mount
    checkHealth()
      .then((data) => setApiStatus(data))
      .catch((err) => console.error('API health check failed:', err));
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResponse(null);

    try {
      const result = await queryAgent(query);
      setResponse(result);
    } catch (error) {
      console.error('Search failed:', error);
      setResponse({
        status: 'error',
        message: error.message || 'Search failed',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-interface">
      <h1>Multi-Agent Search</h1>

      {apiStatus && (
        <div className={`status ${apiStatus.status}`}>
          API Status: {apiStatus.status} |
          LLM: {apiStatus.llm_provider} |
          RAG Indexed: {apiStatus.rag_indexed ? 'Yes' : 'No'}
        </div>
      )}

      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about products or find businesses..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {response && (
        <div className={`response ${response.status}`}>
          {response.status === 'success' ? (
            <div>
              <h3>Response:</h3>
              <pre>{response.response}</pre>
              <p>
                <small>Agent: {response.agent_type}</small>
              </p>
            </div>
          ) : (
            <div className="error">
              <strong>Error:</strong> {response.message}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default SearchInterface;
```

---

### Product Comparison Component

**`src/components/ProductComparison.jsx`**

```javascript
import React, { useState } from 'react';
import { compareProducts } from '../services/api';

function ProductComparison() {
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCompare = async () => {
    setLoading(true);
    try {
      const result = await compareProducts('botox', 'evolus');
      setComparison(result.comparison);
    } catch (error) {
      console.error('Comparison failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="product-comparison">
      <h2>Product Comparison</h2>
      <button onClick={handleCompare} disabled={loading}>
        {loading ? 'Comparing...' : 'Compare Botox vs Evolus'}
      </button>

      {comparison && (
        <div className="comparison-results">
          <div className="product-column">
            <h3>Botox</h3>
            {comparison.botox.map((product, idx) => (
              <div key={idx} className="product-card">
                <h4>{product.product_name}</h4>
                <p><strong>Type:</strong> {product.product_type}</p>
                <p><strong>Areas:</strong> {product.treatment_areas}</p>
                <p>{product.content}</p>
              </div>
            ))}
          </div>

          <div className="product-column">
            <h3>Evolus</h3>
            {comparison.evolus.map((product, idx) => (
              <div key={idx} className="product-card">
                <h4>{product.product_name}</h4>
                <p><strong>Type:</strong> {product.product_type}</p>
                <p><strong>Areas:</strong> {product.treatment_areas}</p>
                <p>{product.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ProductComparison;
```

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         React Frontend                   │
│  (Your separate React project)          │
└──────────────┬──────────────────────────┘
               │ HTTP Requests
               │ (localhost:5000)
               ▼
┌─────────────────────────────────────────┐
│      Flask API Server (api_server.py)   │
│      Endpoint: http://localhost:5000    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│       SupervisorAgent (Coordinator)     │
│   Routes queries to specialized agents  │
└──────┬────────────────────┬─────────────┘
       │                    │
       ▼                    ▼
┌─────────────────┐  ┌──────────────────┐
│  ProductAgent   │  │  BusinessAgent   │
│  (RAG System)   │  │  (Yelp API)      │
└────────┬────────┘  └────────┬─────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌──────────────────┐
│  Product Info   │  │  Business Search │
│  (Botox/Evolus) │  │  (Salons/Spas)   │
└─────────────────┘  └──────────────────┘
```

### Agent Routing Logic

1. **SupervisorAgent** receives the query
2. Analyzes query content:
   - Contains product keywords (botox, evolus, ingredients) → Routes to **ProductAgent**
   - Contains location/business keywords (near, salon, clinic) → Routes to **BusinessAgent**
3. Agent processes query and returns response
4. SupervisorAgent sends final response back to API

### Data Sources

- **ProductAgent:** Uses RAG (Retrieval-Augmented Generation) with vector database (FAISS)
  - Data: Scraped from Botox.com and Evolus.com
  - Embeddings: sentence-transformers/all-MiniLM-L6-v2

- **BusinessAgent:** Uses Yelp Fusion API
  - Data: Real-time business listings, reviews, locations
  - Categories: Beauty salons, spas, medical spas, clinics

---

## Environment Variables

Create a `.env` file in the `yelp_mcp` directory:

```env
# Yelp API (Required for BusinessAgent)
YELP_API_KEY=your_yelp_api_key_here

# LLM Provider (Choose one)
OPENAI_API_KEY=your_openai_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_key_here
```

Get API keys:
- **Yelp API:** https://www.yelp.com/developers
- **OpenAI:** https://platform.openai.com/api-keys
- **Anthropic:** https://console.anthropic.com/

---

## Error Handling

All endpoints return consistent error format:

```json
{
  "status": "error",
  "message": "Description of the error"
}
```

HTTP status codes:
- `200` - Success
- `400` - Bad request (missing parameters)
- `500` - Server error

---

## CORS Configuration

The API server has CORS enabled for all origins. If you need to restrict origins in production:

```python
# In api_server.py
CORS(app, origins=["http://localhost:3000"])
```

---

## Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:5000/api/health

# Product query
curl -X POST http://localhost:5000/api/product-query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Botox?"}'

# Business query
curl -X POST http://localhost:5000/api/business-query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find spas", "location": "San Francisco, CA"}'
```

### Using Postman

1. Import the endpoints as a new collection
2. Set base URL: `http://localhost:5000`
3. Add requests for each endpoint

---

## Next Steps

1. Start the Flask API: `python api_server.py`
2. Index products: `curl -X POST http://localhost:5000/api/index-products`
3. Create your React app or integrate with existing one
4. Import the API service file
5. Start building components!

---

## Support

For issues or questions, refer to:
- [supervisor_agent.py](src/supervisor_agent.py) - Supervisor logic
- [product_agent.py](src/product_agent.py) - Product agent implementation
- [business_agent.py](src/business_agent.py) - Business agent implementation
- [api_server.py](api_server.py) - API endpoint definitions

---

**Happy Coding!**
