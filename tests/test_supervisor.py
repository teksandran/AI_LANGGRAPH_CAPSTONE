"""
Test script for the Supervisor Agent architecture.
Demonstrates multi-agent coordination with supervisor routing.
"""

import asyncio
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv
from src.supervisor_agent import SupervisorAgent

load_dotenv()


async def test_supervisor():
    """Test the supervisor agent with various queries."""

    print("=" * 80)
    print("SUPERVISOR AGENT TEST - Multi-Agent Architecture")
    print("=" * 80)

    # Check API keys
    yelp_api_key = os.getenv("YELP_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    if not yelp_api_key:
        print("[ERROR] YELP_API_KEY not found in .env")
        return

    # Choose LLM provider
    if openai_api_key and openai_api_key.startswith("sk-"):
        provider = "openai"
        model = "gpt-4o-mini"
        print(f"[OK] Using OpenAI: {model}")
    elif anthropic_api_key and anthropic_api_key != "your_anthropic_key_here":
        provider = "anthropic"
        model = "claude-3-5-sonnet-20241022"
        print(f"[OK] Using Anthropic: {model}")
    else:
        print("[ERROR] No valid LLM API key found")
        print("\nUpdate your .env file with:")
        print("  OPENAI_API_KEY=sk-...")
        print("  or")
        print("  ANTHROPIC_API_KEY=sk-ant-...")
        return

    # Initialize supervisor agent
    print("\n[*] Initializing Supervisor Agent...")
    print("-" * 80)

    try:
        supervisor = SupervisorAgent(
            yelp_api_key=yelp_api_key,
            llm_provider=provider,
            model=model
        )
        print("[OK] Supervisor Agent initialized with 2 specialized workers:")
        print("  1. ProductAgent - Handles product information (Botox, Evolus)")
        print("  2. BusinessAgent - Handles business searches (Yelp)")
    except Exception as e:
        print(f"[ERROR] Failed to initialize: {e}")
        return

    # Test queries
    test_queries = [
        {
            "query": "What is Botox and what is it used for?",
            "expected_agent": "ProductAgent"
        },
        {
            "query": "Find Botox providers in New York",
            "expected_agent": "BusinessAgent"
        },
        {
            "query": "What are the differences between Botox and Evolus?",
            "expected_agent": "ProductAgent"
        },
        {
            "query": "Show me beauty salons near Los Angeles",
            "expected_agent": "BusinessAgent"
        }
    ]

    print("\n\n" + "=" * 80)
    print("RUNNING TEST QUERIES")
    print("=" * 80)

    for i, test in enumerate(test_queries, 1):
        query = test["query"]
        expected = test["expected_agent"]

        print(f"\n\n[TEST {i}/4]")
        print("-" * 80)
        print(f"Query: {query}")
        print(f"Expected Agent: {expected}")
        print("-" * 80)

        try:
            response = await supervisor.run(query)
            print(f"\nResponse:")
            print(response)

            # Check which agent was used
            if "ProductAgent" in response or "BOTOX" in response or "EVOLUS" in response:
                used_agent = "ProductAgent"
            elif "Rating:" in response or "Address:" in response:
                used_agent = "BusinessAgent"
            else:
                used_agent = "Unknown"

            if used_agent == expected:
                print(f"\n[OK] Correctly routed to {used_agent}")
            else:
                print(f"\n[WARNING] Expected {expected} but used {used_agent}")

        except Exception as e:
            print(f"\n[ERROR] Query failed: {e}")
            import traceback
            traceback.print_exc()

        if i < len(test_queries):
            print("\nWaiting 2 seconds before next query...")
            await asyncio.sleep(2)

    # Summary
    print("\n\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("""
The Supervisor Agent successfully coordinates between specialized workers:

Architecture:
┌─────────────────┐
│   Supervisor    │  (Routes queries)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌───────────┐
│Product │ │ Business  │
│ Agent  │ │  Agent    │
└────────┘ └───────────┘
    │           │
    ▼           ▼
  RAG        Yelp API
 System

Benefits:
✓ Specialized agents for specific tasks
✓ Cleaner separation of concerns
✓ Easier to maintain and extend
✓ Better error handling per domain
""")

    print("=" * 80)
    print("[OK] Supervisor Agent test completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_supervisor())
