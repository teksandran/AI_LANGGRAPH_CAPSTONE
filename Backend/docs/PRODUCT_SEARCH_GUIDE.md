# Enhanced Product Search Guide

## Overview

The Beauty Search Agent has been enhanced with comprehensive product information capabilities for **Botox** and **Evolus (Jeuveau)** cosmetic treatments. The system now provides detailed product descriptions, FDA-approved uses, treatment areas, benefits, and more.

## What's New

### 1. **RAG-Powered Product Information**
The system uses Retrieval-Augmented Generation (RAG) to scrape and index official product information from:
- **Botox.com** - Official Botox Cosmetic website
- **Evolus.com** - Official Evolus (Jeuveau) website

### 2. **Enhanced Agent Tools**
Three new tools have been added to the agent:

#### `index_product_websites()`
- Scrapes official product websites
- Extracts detailed product information
- Creates searchable knowledge base with FAISS vector store
- Returns indexing statistics

#### `search_product_information(query, brand=None, limit=5)`
- Searches indexed product data using semantic similarity
- Filters by brand (optional): "botox" or "evolus"
- Returns detailed product descriptions with metadata

#### `get_indexed_products_summary(brand=None)`
- Provides summary statistics of indexed products
- Shows total documents, products, and brands
- Lists sample products found

### 3. **Comprehensive Product Metadata**
Each product result includes:
- **Product Name** - Brand or product name
- **Description** - Detailed product description
- **Uses & Indications** - FDA-approved uses
- **Benefits** - Expected results and benefits
- **Treatment Areas** - Forehead, frown lines, crow's feet, etc.
- **Product Type** - Injectable Neurotoxin, Dermal Filler, etc.
- **Brand** - Botox, Evolus, etc.
- **Source URL** - Original webpage

## Example Searches

### Search for Botox Information
```python
Query: "What is Botox and what is it used for?"

Agent Response:
✓ Searches indexed Botox information
✓ Returns detailed description
✓ Lists FDA-approved treatment areas (frown lines, forehead lines, crow's feet)
✓ Explains it's an injectable neurotoxin for aesthetic improvements
✓ Provides benefits and expected results
```

### Search for Evolus Products
```python
Query: "Tell me about Evolus Jeuveau"

Agent Response:
✓ Searches indexed Evolus/Jeuveau information
✓ Returns product description and uses
✓ Lists treatment areas and benefits
✓ Explains product type and category
✓ Provides comprehensive information
```

### Compare Products
```python
Query: "What are the differences between Botox and Evolus?"

Agent Response:
✓ Retrieves information for both brands
✓ Compares treatment areas, uses, and benefits
✓ Highlights similarities and differences
✓ Provides balanced comparison
```

## How It Works

### 1. **Web Scraping**
```python
# The system scrapes official websites with:
- Recursive crawling (max depth: 2)
- Content extraction and cleaning
- Product-specific information extraction
- Metadata collection
```

### 2. **Information Extraction**
The system extracts:
- Product names and descriptions
- Uses and indications
- Benefits and results
- Treatment areas (forehead, frown lines, crow's feet, etc.)
- Product categorization (Injectable Neurotoxin, Dermal Filler, etc.)

### 3. **Vector Indexing**
```python
# Documents are:
1. Split into chunks (1000 chars with 200 overlap)
2. Embedded using sentence-transformers/all-MiniLM-L6-v2
3. Indexed in FAISS vector store
4. Searchable via semantic similarity
```

### 4. **Smart Search**
```python
# Query enhancement:
- Automatically adds aesthetic context
- Prioritizes product documents over general content
- Applies brand and type filters
- Returns top-k relevant results
```

## Usage Examples

### Using the Agent
```python
from src.langgraph_agent import BeautySearchAgent

# Initialize agent
agent = BeautySearchAgent(
    yelp_api_key="your-yelp-key",
    llm_provider="openai",
    model="gpt-4o"
)

# Ask about products
response = await agent.run("What is Botox used for?")
print(response)
```

### Using RAG System Directly
```python
from src.rag_system import get_rag_system
import asyncio

# Get RAG system
rag = get_rag_system()

# Index websites
stats = await rag.index_product_websites()

# Search for products
results = rag.search_products("Botox cosmetic uses", k=5)

# Filter by brand
botox_only = rag.search_products("wrinkles", k=5, filter_brand="botox")

# Search by treatment area
frown_results = rag.search_aesthetic_treatments("frown lines", k=5)
```

## Running Examples

### 1. Enhanced Product Search Example
```bash
.venv\Scripts\python examples\enhanced_product_search.py
```

This demonstrates:
- Indexing product websites
- Searching for Botox and Evolus
- Comparing products
- Searching by treatment area
- Viewing summary statistics

### 2. Agent Test Script
```bash
.venv\Scripts\python test_agent.py
```

This tests:
- Agent initialization
- Product information queries
- Comprehensive responses with details

### 3. Web Application
```bash
.venv\Scripts\python app.py
```

Access at: http://localhost:5000

API Endpoints:
- `POST /api/index-products` - Index product websites
- `POST /api/search-products` - Search products
- `POST /api/search-treatments` - Search by treatment area
- `GET /api/product-summary` - Get summary

## Enhanced System Prompt

The agent now includes detailed instructions for:
1. **Product Information Queries** - When to use product search vs Yelp search
2. **Comprehensive Responses** - What information to include
3. **Indexing Strategy** - When to index websites first
4. **User Guidance** - Suggesting local providers

## Product Information Coverage

### Botox
- ✓ Product description and overview
- ✓ FDA-approved uses and indications
- ✓ Treatment areas (frown lines, forehead lines, crow's feet)
- ✓ Product type (injectable neurotoxin)
- ✓ Benefits and expected results
- ✓ Safety information and considerations

### Evolus (Jeuveau)
- ✓ Product description and overview
- ✓ FDA-approved uses and indications
- ✓ Treatment areas
- ✓ Product type and category
- ✓ Benefits and results
- ✓ Company information

## Benefits

### For Users
- Get detailed product information instantly
- Understand uses and benefits clearly
- Compare products side-by-side
- Find local providers offering treatments
- Make informed decisions

### For Developers
- Extensible RAG system
- Easy to add new product sources
- Customizable search filters
- Rich metadata for analysis
- Persistent vector store

## Configuration

### Environment Variables
```bash
YELP_API_KEY=your-yelp-api-key
OPENAI_API_KEY=your-openai-api-key
# or
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### RAG System Settings
```python
# In src/rag_system.py
embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
chunk_size = 1000
chunk_overlap = 200
max_depth = 2  # Website crawl depth
```

### Product URLs
```python
# In src/rag_system.py
product_urls = {
    "evolus": "https://www.evolus.com/",
    "botox": "https://www.botox.com/"
}
```

## Troubleshooting

### No Results Found
- Ensure websites are indexed first: `await rag.index_product_websites()`
- Check if websites are accessible
- Verify embedding model is downloaded

### Slow Indexing
- Reduce max_depth in scraping
- Limit links per page
- Use saved index: `rag.save_index()` and `rag.load_index()`

### Import Errors
- Install dependencies: `.venv\Scripts\pip install -r requirements.txt`
- Check Python path includes src directory

## Future Enhancements

Potential improvements:
- Add more aesthetic product brands
- Include pricing information
- Add before/after image analysis
- Provider recommendations based on product
- Real-time product update checks
- Multi-language support
- Customer review sentiment analysis

## Support

For issues or questions:
1. Check the examples in `/examples` directory
2. Review the code documentation
3. Test with `test_agent.py`
4. Check the web UI at http://localhost:5000

---

**Last Updated:** 2025-10-09
**Version:** 2.0 - Enhanced Product Search
