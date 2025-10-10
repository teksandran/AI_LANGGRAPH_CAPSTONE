# Enhanced System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                         │
│  (CLI, Web App, API)                                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH BEAUTY AGENT                        │
│  • Enhanced System Prompt                                        │
│  • Tool Selection Logic                                          │
│  • Response Formatting                                           │
└───┬──────────────────────┬──────────────────────┬───────────────┘
    │                      │                      │
    │                      │                      │
    ▼                      ▼                      ▼
┌─────────────┐    ┌───────────────┐    ┌──────────────────┐
│ YELP TOOLS  │    │  RAG TOOLS    │    │  UTILITY TOOLS   │
│             │    │               │    │                  │
│ • Search    │    │ • Index Sites │    │ • Get Summary    │
│   Salons    │    │ • Search      │    │ • Get Details    │
│ • Search    │    │   Products    │    │ • Get Reviews    │
│   Products  │    │ • Search by   │    │                  │
│ • Get       │    │   Treatment   │    │                  │
│   Details   │    │   Area        │    │                  │
│ • Get       │    │               │    │                  │
│   Reviews   │    │               │    │                  │
└──────┬──────┘    └───────┬───────┘    └────────┬─────────┘
       │                   │                     │
       │                   │                     │
       ▼                   ▼                     ▼
┌────────────┐    ┌─────────────────┐    ┌──────────────┐
│ YELP API   │    │ RAG SYSTEM      │    │ METADATA     │
│            │    │                 │    │ STORE        │
│ • Business │    │ • Web Scraper   │    │              │
│   Search   │    │ • Info Extract  │    │ • Statistics │
│ • Details  │    │ • Vector Store  │    │ • Cache      │
│ • Reviews  │    │ • Embeddings    │    │              │
└────────────┘    └────────┬────────┘    └──────────────┘
                           │
                           │
                           ▼
              ┌──────────────────────────┐
              │  EXTERNAL DATA SOURCES   │
              │                          │
              │  • Botox.com            │
              │  • Evolus.com           │
              │  • [Future sources]     │
              └──────────────────────────┘
```

## RAG System Data Flow

```
INDEXING PHASE:
═══════════════

Official Websites
    │
    ├── Botox.com ────────┐
    └── Evolus.com ───────┤
                          │
                          ▼
                 ┌────────────────┐
                 │  Web Scraper   │
                 │  (Beautiful    │
                 │   Soup)        │
                 └───────┬────────┘
                         │
                         ▼
                 ┌────────────────┐
                 │   HTML Parser  │
                 │   • Title      │
                 │   • Meta       │
                 │   • Content    │
                 └───────┬────────┘
                         │
                         ▼
                 ┌────────────────────────┐
                 │  Product Extractor     │
                 │  • Name                │
                 │  • Description         │
                 │  • Uses                │
                 │  • Benefits            │
                 │  • Treatment Areas     │
                 │  • Product Type        │
                 └───────┬────────────────┘
                         │
                         ▼
                 ┌────────────────┐
                 │  Text Splitter │
                 │  (1000 chars   │
                 │   200 overlap) │
                 └───────┬────────┘
                         │
                         ▼
                 ┌────────────────┐
                 │  Embeddings    │
                 │  (sentence-    │
                 │   transformers)│
                 └───────┬────────┘
                         │
                         ▼
                 ┌────────────────┐
                 │  FAISS Vector  │
                 │  Store         │
                 └────────────────┘


SEARCH PHASE:
═════════════

User Query: "What is Botox?"
         │
         ▼
┌─────────────────┐
│ Query Enhancer  │
│ "Botox          │
│  aesthetic      │
│  treatment"     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Embedding       │
│ Generation      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Vector Search   │
│ (Semantic       │
│  Similarity)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Apply Filters   │
│ • Brand         │
│ • Type          │
│ • Area          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Prioritize      │
│ • Products      │
│ • Over webpages │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Format Results  │
│ • Content       │
│ • Metadata      │
│ • Sources       │
└────────┬────────┘
         │
         ▼
Return to Agent
```

## Agent Decision Flow

```
User Query Received
         │
         ▼
    ┌────────┐
    │ Agent  │
    │ Router │
    └───┬────┘
        │
        ├─── Contains product names? ───┐
        │    (Botox, Evolus, Jeuveau)   │
        │                                │
        ├─── About treatments? ─────────┤
        │    (wrinkles, injectables)    │
        │                                │
        └─── About services? ───────────┤
             (salon, spa, location)     │
                                        │
        ┌───────────────────────────────┴───────────────┐
        │                                               │
        ▼                                               ▼
┌────────────────┐                              ┌──────────────┐
│ PRODUCT PATH   │                              │ SERVICE PATH │
└───────┬────────┘                              └──────┬───────┘
        │                                              │
        ▼                                              ▼
┌────────────────┐                              ┌──────────────┐
│ Check if       │                              │ Check for    │
│ indexed        │                              │ location     │
└───┬────────────┘                              └──────┬───────┘
    │                                                  │
    ├── No ──► Index Websites                         │
    │                                                  │
    └── Yes ──┐                                       │
              │                                        │
              ▼                                        ▼
      ┌───────────────┐                        ┌──────────────┐
      │ Search Product│                        │ Search Yelp  │
      │ Information   │                        │ Businesses   │
      └───────┬───────┘                        └──────┬───────┘
              │                                       │
              ▼                                       ▼
      ┌───────────────┐                        ┌──────────────┐
      │ Format with:  │                        │ Format with: │
      │ • Description │                        │ • Name       │
      │ • Uses        │                        │ • Rating     │
      │ • Benefits    │                        │ • Address    │
      │ • Areas       │                        │ • Price      │
      │ • Type        │                        │ • Phone      │
      └───────┬───────┘                        └──────┬───────┘
              │                                       │
              ├──► Suggest local providers           │
              │                                       │
              └───────────────┬───────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Return Response  │
                    │ to User          │
                    └──────────────────┘
```

## Tool Interaction Matrix

```
┌─────────────────────────┬──────────┬──────────┬──────────┬──────────┐
│ User Query Type         │ Yelp API │ RAG      │ Vector   │ LLM      │
│                         │          │ Scraper  │ Store    │          │
├─────────────────────────┼──────────┼──────────┼──────────┼──────────┤
│ "Find Botox providers"  │    ✓     │          │          │    ✓     │
│ "What is Botox?"        │          │    ✓     │    ✓     │    ✓     │
│ "Compare products"      │          │          │    ✓     │    ✓     │
│ "Salons near me"        │    ✓     │          │          │    ✓     │
│ "Treatment areas"       │          │          │    ✓     │    ✓     │
│ "Business details"      │    ✓     │          │          │    ✓     │
│ "Product summary"       │          │          │    ✓     │    ✓     │
└─────────────────────────┴──────────┴──────────┴──────────┴──────────┘
```

## Component Integration

```
┌───────────────────────────────────────────────────────────────┐
│                     Flask Web Application                      │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐       │
│  │   Routes    │  │   Templates  │  │   Static Files │       │
│  └──────┬──────┘  └──────────────┘  └────────────────┘       │
└─────────┼─────────────────────────────────────────────────────┘
          │
          ▼
┌───────────────────────────────────────────────────────────────┐
│                      Agent Layer                               │
│  ┌──────────────────────────────────────────────────┐         │
│  │  BeautySearchAgent (LangGraph)                   │         │
│  │  • State Management                              │         │
│  │  • Tool Binding                                  │         │
│  │  • Workflow Orchestration                        │         │
│  └───────────────────┬──────────────────────────────┘         │
└──────────────────────┼────────────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐
    │  Yelp   │  │   RAG   │  │ Utility │
    │  Tools  │  │  Tools  │  │  Tools  │
    └────┬────┘  └────┬────┘  └────┬────┘
         │            │            │
         ▼            ▼            ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐
    │ Yelp    │  │   RAG   │  │ Config  │
    │ Client  │  │ System  │  │ Manager │
    └────┬────┘  └────┬────┘  └────┬────┘
         │            │            │
         ▼            ▼            ▼
    ┌─────────┐  ┌─────────────────┐  ┌─────────┐
    │ Yelp    │  │  Vector Store   │  │  Cache  │
    │ API     │  │  • FAISS        │  │  Store  │
    └─────────┘  │  • Embeddings   │  └─────────┘
                 │  • Documents    │
                 └─────────────────┘
```

## Data Storage Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    In-Memory Storage                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────┐            │
│  │  FAISS Vector Store                    │            │
│  │  • Product embeddings                  │            │
│  │  • Webpage embeddings                  │            │
│  │  • ~50-100MB                           │            │
│  └────────────────────────────────────────┘            │
│                                                          │
│  ┌────────────────────────────────────────┐            │
│  │  Document Cache                        │            │
│  │  • Raw documents                       │            │
│  │  • Metadata                            │            │
│  │  • ~10-20MB                            │            │
│  └────────────────────────────────────────┘            │
│                                                          │
│  ┌────────────────────────────────────────┐            │
│  │  Embeddings Model                      │            │
│  │  • sentence-transformers               │            │
│  │  • ~100MB                              │            │
│  └────────────────────────────────────────┘            │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   Persistent Storage                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────┐            │
│  │  Saved Index (Optional)                │            │
│  │  • ./product_index/                    │            │
│  │  • FAISS index files                   │            │
│  │  • Metadata files                      │            │
│  └────────────────────────────────────────┘            │
│                                                          │
│  ┌────────────────────────────────────────┐            │
│  │  Configuration                         │            │
│  │  • .env (API keys)                     │            │
│  │  • config.py (settings)                │            │
│  └────────────────────────────────────────┘            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Performance Characteristics

```
┌──────────────────────┬──────────────┬─────────────┬──────────┐
│ Operation            │ First Time   │ Cached      │ Memory   │
├──────────────────────┼──────────────┼─────────────┼──────────┤
│ Index Websites       │ 30-60s       │ N/A         │ 100MB    │
│ Load Saved Index     │ 1-2s         │ N/A         │ 150MB    │
│ Search Products      │ 200-500ms    │ 100-200ms   │ 160MB    │
│ Yelp Search          │ 500-1000ms   │ 500-1000ms  │ <10MB    │
│ Format Response      │ 5-10ms       │ 5-10ms      │ <1MB     │
│ LLM Call (GPT-4)     │ 2-5s         │ N/A         │ <1MB     │
└──────────────────────┴──────────────┴─────────────┴──────────┘
```

## Security & Privacy

```
┌─────────────────────────────────────────────────────────┐
│                    Security Layers                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. API Key Management                                  │
│     • Environment variables only                        │
│     • No hardcoded keys                                 │
│     • .env in .gitignore                               │
│                                                          │
│  2. Data Scraping                                       │
│     • Respects robots.txt                              │
│     • Rate limiting (1s delay)                          │
│     • User-Agent headers                                │
│                                                          │
│  3. Input Validation                                    │
│     • Query sanitization                                │
│     • Parameter validation                              │
│     • Type checking                                     │
│                                                          │
│  4. Data Storage                                        │
│     • No PII collected                                  │
│     • Public data only                                  │
│     • Local storage option                              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Scalability Considerations

```
Current Implementation:
• Single-process Flask app
• In-memory vector store
• Synchronous web scraping
• Local file storage

Suitable for: Development, demos, small teams

Scaling Options:
┌─────────────────────────────────────────────────────────┐
│ Component         │ Current      │ Scale-up Option      │
├───────────────────┼──────────────┼─────────────────────┤
│ Web Server        │ Flask dev    │ Gunicorn + Nginx    │
│ Vector Store      │ FAISS local  │ Pinecone/Weaviate   │
│ Scraping          │ Sync httpx   │ Celery workers      │
│ Cache             │ In-memory    │ Redis/Memcached     │
│ Database          │ None         │ PostgreSQL          │
│ File Storage      │ Local disk   │ S3/Cloud Storage    │
│ LLM Calls         │ OpenAI API   │ Self-hosted LLM     │
└───────────────────┴──────────────┴─────────────────────┘
```

## Deployment Architecture (Future)

```
                    ┌─────────────┐
                    │   Users     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   CDN/Edge  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Load        │
                    │ Balancer    │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐   ┌──────────┐
    │ Web App  │    │ Web App  │   │ Web App  │
    │ Instance │    │ Instance │   │ Instance │
    └─────┬────┘    └─────┬────┘   └─────┬────┘
          │               │              │
          └───────────────┼──────────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
       ┌─────────────┐         ┌─────────────┐
       │   Redis     │         │  Celery     │
       │   Cache     │         │  Workers    │
       └─────────────┘         └─────┬───────┘
                                     │
                    ┌────────────────┴───────────┐
                    │                            │
                    ▼                            ▼
             ┌─────────────┐            ┌──────────────┐
             │  Vector DB  │            │  PostgreSQL  │
             │  (Pinecone) │            │  (Metadata)  │
             └─────────────┘            └──────────────┘
```

---

**Document Version:** 1.0
**Last Updated:** 2025-10-09
