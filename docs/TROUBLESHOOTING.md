# Troubleshooting Guide

Common issues and solutions for the Multi-Agent Beauty & Aesthetics System.

---

## 🔴 ModuleNotFoundError: No module named 'flask_cors'

### Problem:
```
Traceback (most recent call last):
  File "api_server.py", line 7, in <module>
    from flask_cors import CORS
ModuleNotFoundError: No module named 'flask_cors'
```

### Solution 1: Use the Startup Script (Recommended)
```bash
# Windows
start_api.bat

# The script automatically installs dependencies
```

### Solution 2: Install Dependencies Manually
```bash
cd "C:\New Development 2025\AI ML\Agentic AI\Capstone Demo\yelp_mcp"
pip install -r requirements.txt
```

### Solution 3: Install Individual Package
```bash
pip install flask-cors
# or
python -m pip install flask-cors
```

### Solution 4: Check Python Environment
You might have multiple Python installations. Check which one you're using:
```bash
where python
python --version
```

Then install to the correct Python:
```bash
C:\Python312\python.exe -m pip install flask-cors
```

---

## 🔴 Timeout Error (30 seconds)

### Problem:
```
Error: timeout of 30000ms exceeded
Please ensure the Flask API server is running at http://localhost:5000
```

### Why It Happens:
- First product query triggers automatic indexing (scrapes websites)
- Indexing takes 30-60 seconds
- React timeout is 30 seconds (default)

### Solution 1: Pre-Index Products (Recommended)
```bash
curl -X POST http://localhost:5000/api/index-products
```

Wait 2-3 minutes for completion. After this, all queries will be fast (2-5 seconds).

### Solution 2: Increase React Timeout

In your `apiService.js`, change timeout:
```javascript
const api = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 120000, // Changed from 30000 to 120000 (2 minutes)
});
```

### Solution 3: Just Wait
After the first query completes (even if it times out in React), subsequent queries will be fast because products are now indexed.

---

## 🔴 Port 5000 Already in Use

### Problem:
```
OSError: [Errno 98] Address already in use
```

### Solution 1: Kill Existing Process (Windows)
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

### Solution 2: Change Port

In `api_server.py`, line 378, change port:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

Then update React to use new port:
```javascript
const API_BASE_URL = 'http://localhost:5001';
```

---

## 🔴 SupervisorAgent Not Initialized

### Problem:
```json
{
  "status": "error",
  "message": "SupervisorAgent not initialized. Check API keys."
}
```

### Solution:

1. **Check .env file exists:**
```bash
cd "C:\New Development 2025\AI ML\Agentic AI\Capstone Demo\yelp_mcp"
dir .env
```

2. **Verify API keys in .env:**
```env
YELP_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
# OR
ANTHROPIC_API_KEY=your_key_here
```

3. **Restart the server:**
```bash
python api_server.py
```

4. **Check server logs:**
Look for:
```
SupervisorAgent: [OK] Initialized
```

---

## 🔴 RAG System Not Indexed

### Problem:
```json
{
  "status": "error",
  "message": "RAG system not indexed"
}
```

### Solution:

Run the indexing endpoint:
```bash
curl -X POST http://localhost:5000/api/index-products
```

Or in PowerShell:
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/index-products" -Method POST
```

Wait 2-3 minutes. You should see:
```json
{
  "status": "success",
  "message": "Products indexed successfully"
}
```

---

## 🔴 CORS Errors in React

### Problem:
```
Access to XMLHttpRequest at 'http://localhost:5000/api/query' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

### Solution:

1. **Ensure Flask server is running:**
```bash
curl http://localhost:5000/api/health
```

2. **Check CORS is enabled in api_server.py:**
```python
from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # This should be present
```

3. **Restart Flask server:**
```bash
python api_server.py
```

---

## 🔴 Unicode Encoding Errors (Windows)

### Problem:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'
```

### Solution:
This has been fixed in the code. Unicode characters (✓, ✗) have been replaced with [OK] and [ERROR].

If you still see this, update to the latest code or manually replace Unicode characters with ASCII.

---

## 🔴 LangSmith Not Showing Traces

### Problem:
Traces not appearing in LangSmith dashboard.

### Solution:

1. **Check environment variables:**
```bash
# In command prompt
echo %LANGCHAIN_TRACING_V2%
echo %LANGCHAIN_API_KEY%
```

Should show:
```
true
lsv2_pt_...
```

2. **Verify LangSmith status on startup:**
Look for:
```
[OK] LangSmith tracing is ACTIVE
View traces at: https://smith.langchain.com/
```

3. **Check API key is valid:**
Go to https://smith.langchain.com/settings and verify your API key.

4. **Send a test query:**
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is Botox?\"}"
```

Then check https://smith.langchain.com/ for the trace.

---

## 🔴 Query Returns Empty Results

### Problem:
```
I couldn't find specific information about that product
```

### Solutions:

1. **Ensure products are indexed:**
```bash
curl http://localhost:5000/api/rag-status
```

Should show `"indexed": true`

2. **Try more specific queries:**
- ❌ "product"
- ✅ "What is Botox?"
- ✅ "Tell me about Evolus"

3. **Check server logs:**
Look for errors in the terminal running the server.

---

## 🔴 Yelp API Errors

### Problem:
```
Unable to reach Yelp API
```

### Solutions:

1. **Verify Yelp API key:**
Check `.env` has valid `YELP_API_KEY`

2. **Test Yelp API directly:**
```bash
curl -H "Authorization: Bearer YOUR_YELP_API_KEY" \
  "https://api.yelp.com/v3/businesses/search?location=NYC&term=spa"
```

3. **Check API quota:**
Yelp API has rate limits. Check https://www.yelp.com/developers/

---

## 🔴 Server Starts but Immediately Crashes

### Problem:
Server starts then exits immediately.

### Solution:

1. **Check for port conflicts:**
```bash
netstat -ano | findstr :5000
```

2. **Run with more verbose logging:**
```bash
python api_server.py
```

Look for error messages in output.

3. **Check Python version:**
```bash
python --version
```

Need Python 3.12 or higher.

4. **Verify all dependencies:**
```bash
pip install -r requirements.txt
```

---

## 🔴 React App Can't Connect to Backend

### Problem:
```
Unable to reach backend server
```

### Solutions:

1. **Verify Flask is running:**
```bash
curl http://localhost:5000/api/health
```

Should return:
```json
{
  "status": "healthy",
  "supervisor_agent": true
}
```

2. **Check React is using correct URL:**
In `apiService.js`:
```javascript
const API_BASE_URL = 'http://localhost:5000';
```

3. **Check firewall:**
Windows Firewall might be blocking. Allow Python through firewall.

4. **Try using 127.0.0.1:**
```javascript
const API_BASE_URL = 'http://127.0.0.1:5000';
```

---

## 🔴 Slow Query Performance

### Problem:
Queries taking too long (> 10 seconds).

### Solutions:

1. **First query is always slow:**
   - First product query: 30-60s (indexing)
   - After indexing: 2-5s

2. **Check if indexing is complete:**
```bash
curl http://localhost:5000/api/rag-status
```

3. **Monitor with LangSmith:**
Check https://smith.langchain.com/ to see where time is spent.

4. **Optimize if needed:**
   - Reduce `k` parameter in searches
   - Cache frequent queries
   - Use faster LLM model

---

## 🔴 Import Errors

### Problem:
```
ModuleNotFoundError: No module named 'src'
```

### Solution:

Make sure you're running from the correct directory:
```bash
cd "C:\New Development 2025\AI ML\Agentic AI\Capstone Demo\yelp_mcp"
python api_server.py
```

Not from `src/` directory.

---

## 🛠️ General Debugging Steps

### 1. Check API Health
```bash
curl http://localhost:5000/api/health
```

### 2. Check Server Logs
Look at terminal running `python api_server.py` for errors.

### 3. Test with cURL
Before testing in React, test with cURL:
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is Botox?\"}"
```

### 4. Check Environment
```bash
python --version
pip list | grep -E "flask|langchain|langsmith"
```

### 5. Fresh Start
```bash
# Kill all Python processes
taskkill /F /IM python.exe

# Reinstall dependencies
pip install -r requirements.txt

# Start server
python api_server.py
```

---

## 📞 Still Having Issues?

### Check These Files:

1. **[HOW_TO_RUN.md](HOW_TO_RUN.md)** - Complete setup guide
2. **[START_HERE.txt](START_HERE.txt)** - Quick reference
3. **[LANGSMITH_GUIDE.md](LANGSMITH_GUIDE.md)** - LangSmith setup

### Common Command Reference:

```bash
# Start server
python api_server.py

# Or use startup script
start_api.bat

# Index products
curl -X POST http://localhost:5000/api/index-products

# Health check
curl http://localhost:5000/api/health

# Test query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is Botox?\"}"
```

---

## ✅ Verification Checklist

Before asking for help, verify:

- [ ] Python 3.12+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file exists with valid API keys
- [ ] Flask server running (`curl http://localhost:5000/api/health`)
- [ ] Products indexed (`curl http://localhost:5000/api/rag-status`)
- [ ] Port 5000 not in use
- [ ] No firewall blocking
- [ ] React using correct API URL

---

**Most issues are resolved by:**
1. Installing dependencies: `pip install -r requirements.txt`
2. Indexing products: `curl -X POST http://localhost:5000/api/index-products`
3. Using the startup script: `start_api.bat`
