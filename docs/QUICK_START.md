# Quick Start Guide - Multi-Agent API Server

Get the API server running in 3 simple steps!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure API Keys

1. Make sure `.env` file exists in the project root
2. Add your API keys to `.env`:

```env
YELP_API_KEY=your_yelp_key
OPENAI_API_KEY=your_openai_key
```

**Get API keys:**
- Yelp: https://www.yelp.com/developers
- OpenAI: https://platform.openai.com/api-keys

## Step 3: Start the Server

**Windows:**
```bash
start_api.bat
```

**Mac/Linux:**
```bash
python api_server.py
```

The server will start at **http://localhost:5000**

## Step 4: Index Products (First Time Only)

Open a new terminal and run:

```bash
curl -X POST http://localhost:5000/api/index-products
```

This scrapes Botox and Evolus websites (takes ~2-3 minutes).

## Test the API

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Product Query
```bash
curl -X POST http://localhost:5000/api/query -H "Content-Type: application/json" -d "{\"query\": \"What is Botox used for?\"}"
```

### Business Query
```bash
curl -X POST http://localhost:5000/api/query -H "Content-Type: application/json" -d "{\"query\": \"Find Botox clinics in New York\"}"
```

## React Integration

See [REACT_API_GUIDE.md](REACT_API_GUIDE.md) for complete React integration examples.

### Quick React Setup

1. In your React project, install axios:
```bash
npm install axios
```

2. Create `src/services/api.js`:
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000',
});

export const queryAgent = async (query) => {
  const response = await api.post('/api/query', { query });
  return response.data;
};
```

3. Use in your component:
```javascript
import { queryAgent } from './services/api';

function App() {
  const [response, setResponse] = useState('');

  const handleSearch = async () => {
    const result = await queryAgent('What is Botox?');
    setResponse(result.response);
  };

  return <div>{response}</div>;
}
```

## Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/query` | POST | Main query (auto-routes to agents) |
| `/api/product-query` | POST | Direct product queries |
| `/api/business-query` | POST | Direct business queries |
| `/api/compare-products` | POST | Compare products |
| `/api/index-products` | POST | Index product websites |
| `/api/rag-status` | GET | RAG system status |

## Architecture

```
React App → Flask API → SupervisorAgent
                              ├─→ ProductAgent (RAG)
                              └─→ BusinessAgent (Yelp)
```

## Troubleshooting

### "SupervisorAgent not initialized"
- Check that API keys are set in `.env`
- Make sure you have either OPENAI_API_KEY or ANTHROPIC_API_KEY

### "RAG system not indexed"
- Run: `curl -X POST http://localhost:5000/api/index-products`

### Port 5000 already in use
- Change port in `api_server.py` line 341

## Next Steps

1. Read [REACT_API_GUIDE.md](REACT_API_GUIDE.md) for detailed React integration
2. Check [supervisor_agent.py](src/supervisor_agent.py) for agent logic
3. Customize agents in [product_agent.py](src/product_agent.py) and [business_agent.py](src/business_agent.py)

**Happy building!**
