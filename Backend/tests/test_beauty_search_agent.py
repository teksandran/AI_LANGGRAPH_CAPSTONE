"""
Test script for the enhanced Beauty Search Agent with product information.
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

load_dotenv()


async def test_agent():
    """Test the agent with various queries."""

    print("=" * 80)
    print("BEAUTY SEARCH AGENT - ENHANCED WITH PRODUCT INFORMATION")
    print("=" * 80)

    # Initialize agent
    yelp_api_key = os.getenv("YELP_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not yelp_api_key:
        print("❌ Error: YELP_API_KEY not found in .env file")
        return

    if not openai_api_key:
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        return

    print("\n✓ API keys loaded successfully")
    print("\n⏳ Initializing agent...")

    agent = BeautySearchAgent(
        yelp_api_key=yelp_api_key,
        llm_provider="openai",
        model="gpt-4o"
    )

    print("✓ Agent initialized!\n")

    # Test queries
    test_queries = [
        "What is Botox and what is it used for?",
        "Tell me about Evolus Jeuveau products",
        "What are the differences between Botox and Evolus?",
    ]

    for i, query in enumerate(test_queries, 1):
        print("=" * 80)
        print(f"TEST #{i}")
        print("=" * 80)
        print(f"Query: {query}\n")
        print("Agent Response:")
        print("-" * 80)

        try:
            response = await agent.run(query)
            print(response)
        except Exception as e:
            print(f"❌ Error: {e}")

        print("\n")

        if i < len(test_queries):
            await asyncio.sleep(2)  # Brief pause between queries

    print("=" * 80)
    print("✓ Testing completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_agent())
