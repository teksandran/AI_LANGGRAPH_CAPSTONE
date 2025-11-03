"""
Simple A2A Communication Test (No Emojis)
Tests basic A2A functionality without Unicode issues on Windows.
"""

import asyncio
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

load_dotenv()


async def test_a2a_basic():
    """Test basic A2A communication."""
    print("\n" + "=" * 70)
    print("A2A Communication Test")
    print("=" * 70)

    try:
        from src.supervisor_agent_a2a import SupervisorAgentA2A

        yelp_api_key = os.getenv("YELP_API_KEY")
        if not yelp_api_key:
            print("\n[ERROR] YELP_API_KEY not found in environment")
            return False

        print("\n[1/4] Creating supervisor with A2A enabled...")
        supervisor = SupervisorAgentA2A(
            yelp_api_key=yelp_api_key,
            llm_provider="openai",
            enable_a2a=True
        )
        print("[OK] Supervisor created")

        print("\n[2/4] Testing product query...")
        query = "What is Botox?"
        result = await supervisor.run_with_a2a(query)
        print(f"[OK] Query: {query}")
        print(f"[OK] Method: {result['method']}")
        print(f"[OK] Agents: {', '.join(result.get('agents_used', []))}")
        print(f"\nResponse preview: {result['response'][:200]}...")

        print("\n[3/4] Getting broker statistics...")
        stats = supervisor.get_a2a_statistics()
        print(f"[OK] Total agents: {stats.get('total_agents', 0)}")
        print(f"[OK] Active agents: {stats.get('active_agents', 0)}")
        print(f"[OK] Total messages: {stats.get('total_messages', 0)}")

        print("\n[4/4] Testing backward compatibility...")
        old_response = await supervisor.run("Tell me about Evolus")
        print(f"[OK] Traditional routing works: {len(old_response)} chars")

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED!")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_a2a_basic())
    sys.exit(0 if success else 1)
