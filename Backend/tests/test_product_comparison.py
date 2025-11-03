"""
Simple test script to compare Botox and Evolus products.
Pre-indexes the data and then runs the agent query.
"""

import asyncio
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv
from src.langgraph_agent import BeautySearchAgent
from src.rag_system import get_rag_system

load_dotenv()


async def test_comparison():
    """Test comparing Botox and Evolus."""

    print("=" * 80)
    print("BOTOX vs EVOLUS COMPARISON TEST")
    print("=" * 80)

    # Step 1: Pre-index product data
    print("\n[*] Step 1: Indexing product information from websites...")
    print("-" * 80)

    rag_system = get_rag_system()

    try:
        stats = await rag_system.index_product_websites()
        print(f"[OK] Indexing completed!")
        print(f"  - Evolus pages: {stats.get('evolus', 0)}")
        print(f"  - Botox pages: {stats.get('botox', 0)}")
        print(f"  - Total documents: {stats.get('total_documents', 0)}")
    except Exception as e:
        print(f"[X] Indexing failed: {e}")
        return

    # Step 2: Test direct RAG search
    print("\n\n[*] Step 2: Testing direct RAG search...")
    print("-" * 80)

    # Search for Botox
    botox_results = rag_system.search_products("Botox uses benefits", k=2, filter_brand="botox")
    if botox_results:
        print("\n[BOTOX] Information:")
        print(f"Product: {botox_results[0].get('product_name', 'N/A')}")
        print(f"Type: {botox_results[0].get('product_type', 'N/A')}")
        print(f"Areas: {botox_results[0].get('treatment_areas', 'N/A')}")
        print(f"\nDescription:\n{botox_results[0]['content'][:300]}...")

    # Search for Evolus
    evolus_results = rag_system.search_products("Evolus Jeuveau uses benefits", k=2, filter_brand="evolus")
    if evolus_results:
        print("\n\n[EVOLUS] Information:")
        print(f"Product: {evolus_results[0].get('product_name', 'N/A')}")
        print(f"Type: {evolus_results[0].get('product_type', 'N/A')}")
        print(f"Areas: {evolus_results[0].get('treatment_areas', 'N/A')}")
        print(f"\nDescription:\n{evolus_results[0]['content'][:300]}...")

    # Step 3: Test with Agent
    print("\n\n[*] Step 3: Testing with LangGraph Agent...")
    print("-" * 80)

    # Check API keys
    yelp_api_key = os.getenv("YELP_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    if not yelp_api_key:
        print("[X] YELP_API_KEY not found in .env")
        return

    # Choose provider
    if openai_api_key and openai_api_key.startswith("sk-"):
        provider = "openai"
        model = "gpt-4o-mini"  # Using mini for faster/cheaper testing
        print(f"[OK] Using OpenAI with model: {model}")
    elif anthropic_api_key and anthropic_api_key != "your_anthropic_key_here":
        provider = "anthropic"
        model = "claude-3-haiku-20240307"  # Using haiku for faster/cheaper testing
        print(f"[OK] Using Anthropic with model: {model}")
    else:
        print("[X] No valid LLM API key found (OpenAI or Anthropic)")
        print("\nUpdate your .env file with a valid API key:")
        print("  OPENAI_API_KEY=sk-...")
        print("  or")
        print("  ANTHROPIC_API_KEY=sk-ant-...")
        return

    # Initialize agent
    try:
        agent = BeautySearchAgent(
            yelp_api_key=yelp_api_key,
            llm_provider=provider,
            model=model
        )
        print("[OK] Agent initialized successfully")
    except Exception as e:
        print(f"[X] Agent initialization failed: {e}")
        return

    # Test query
    query = "What are the differences between Botox and Evolus?"
    print(f"\n\nQuery: {query}")
    print("-" * 80)

    try:
        response = await agent.run(query)
        print("\nAgent Response:")
        print(response)
    except Exception as e:
        print(f"\n[X] Agent query failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("[OK] Test completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_comparison())
