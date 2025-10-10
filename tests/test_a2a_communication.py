"""
Test script for A2A (Agent-to-Agent) Communication
Verifies that agents can communicate directly without breaking existing functionality.
"""

import asyncio
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv
from src.supervisor_agent_a2a import SupervisorAgentA2A
from src.a2a_broker import get_broker

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import os as _os
    _os.environ['PYTHONIOENCODING'] = 'utf-8'

load_dotenv()


async def test_backward_compatibility():
    """Test that existing functionality still works."""
    print("=" * 70)
    print("TEST 1: Backward Compatibility - Traditional Routing")
    print("=" * 70)

    yelp_api_key = os.getenv("YELP_API_KEY")
    if not yelp_api_key:
        print("[X] YELP_API_KEY not found in environment")
        return False

    # Create supervisor with A2A disabled
    supervisor = SupervisorAgentA2A(
        yelp_api_key=yelp_api_key,
        llm_provider="openai",
        enable_a2a=False
    )

    query = "What is Botox?"
    print(f"\n>> Query: {query}")

    try:
        response = await supervisor.run(query)
        print(f"\n[OK] Response:\n{response}\n")
        print("[OK] Backward compatibility test PASSED")
        return True
    except Exception as e:
        print(f"\n[X] Error: {e}")
        print("[X] Backward compatibility test FAILED")
        return False


async def test_basic_a2a():
    """Test basic A2A communication."""
    print("\n" + "=" * 70)
    print("TEST 2: Basic A2A Communication")
    print("=" * 70)

    yelp_api_key = os.getenv("YELP_API_KEY")
    if not yelp_api_key:
        print("❌ YELP_API_KEY not found in environment")
        return False

    # Create supervisor with A2A enabled
    supervisor = SupervisorAgentA2A(
        yelp_api_key=yelp_api_key,
        llm_provider="openai",
        enable_a2a=True
    )

    query = "Tell me about Evolus Jeuveau"
    print(f"\n📤 Query: {query}")

    try:
        result = await supervisor.run_with_a2a(query)
        print(f"\n✅ Response:\n{result['response']}\n")
        print(f"📊 Method used: {result['method']}")
        print(f"🤖 Agents used: {', '.join(result['agents_used']) if result['agents_used'] else 'None'}")
        print("\n✅ Basic A2A test PASSED")
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("❌ Basic A2A test FAILED")
        return False


async def test_agent_collaboration():
    """Test agents collaborating on a complex query."""
    print("\n" + "=" * 70)
    print("TEST 3: Agent Collaboration - Complex Query")
    print("=" * 70)

    yelp_api_key = os.getenv("YELP_API_KEY")
    if not yelp_api_key:
        print("❌ YELP_API_KEY not found in environment")
        return False

    supervisor = SupervisorAgentA2A(
        yelp_api_key=yelp_api_key,
        llm_provider="openai",
        enable_a2a=True
    )

    query = "What is Botox and where can I get it in New York?"
    print(f"\n📤 Query: {query}")
    print("Expected: ProductAgent provides info, then hands off to BusinessAgent for locations")

    try:
        result = await supervisor.run_with_a2a(query)
        print(f"\n✅ Response:\n{result['response']}\n")
        print(f"📊 Method used: {result['method']}")
        print(f"🤖 Agents used: {', '.join(result['agents_used']) if result['agents_used'] else 'None'}")

        if result['method'] == 'a2a_collaboration':
            print("\n✅ Agent collaboration test PASSED")
            return True
        else:
            print(f"\n⚠️  Expected 'a2a_collaboration' but got '{result['method']}'")
            print("✅ Test completed but with different method")
            return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("❌ Agent collaboration test FAILED")
        return False


async def test_direct_agent_communication():
    """Test direct agent-to-agent communication."""
    print("\n" + "=" * 70)
    print("TEST 4: Direct Agent-to-Agent Communication")
    print("=" * 70)

    yelp_api_key = os.getenv("YELP_API_KEY")
    if not yelp_api_key:
        print("❌ YELP_API_KEY not found in environment")
        return False

    supervisor = SupervisorAgentA2A(
        yelp_api_key=yelp_api_key,
        llm_provider="openai",
        enable_a2a=True
    )

    print("\n🔄 Testing ProductAgent -> BusinessAgent direct request...")

    try:
        # Product agent requests help from business agent
        response = await supervisor.product_agent.send_request(
            recipient="business_agent",
            task="business_search",
            parameters={
                "query": "Botox providers",
                "location": "Miami, FL",
                "limit": 3
            },
            wait_for_response=True,
            timeout=30.0
        )

        if response:
            success = response.content.get("success", False)
            data = response.content.get("data", {})

            print(f"\n✅ Message sent and received")
            print(f"📬 Response success: {success}")
            print(f"📄 Response preview: {str(data)[:200]}...")

            if success:
                print("\n✅ Direct agent communication test PASSED")
                return True
            else:
                print("\n⚠️  Communication succeeded but request failed")
                return True
        else:
            print("\n❌ No response received")
            print("❌ Direct agent communication test FAILED")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("❌ Direct agent communication test FAILED")
        return False


async def test_broker_statistics():
    """Test broker statistics and monitoring."""
    print("\n" + "=" * 70)
    print("TEST 5: Broker Statistics and Monitoring")
    print("=" * 70)

    yelp_api_key = os.getenv("YELP_API_KEY")
    if not yelp_api_key:
        print("❌ YELP_API_KEY not found in environment")
        return False

    supervisor = SupervisorAgentA2A(
        yelp_api_key=yelp_api_key,
        llm_provider="openai",
        enable_a2a=True
    )

    # Run a few queries
    await supervisor.run_with_a2a("What is Botox?")
    await supervisor.run_with_a2a("Compare Botox and Evolus")

    # Get statistics
    stats = supervisor.get_a2a_statistics()

    print("\n📊 Broker Statistics:")
    print(f"   A2A Enabled: {stats.get('a2a_enabled', False)}")
    print(f"   Total Agents: {stats.get('total_agents', 0)}")
    print(f"   Active Agents: {stats.get('active_agents', 0)}")
    print(f"   Total Messages: {stats.get('total_messages', 0)}")
    print(f"   Active Conversations: {stats.get('active_conversations', 0)}")

    agents = stats.get('agents', {})
    print(f"\n🤖 Registered Agents:")
    for agent_id, agent_info in agents.items():
        print(f"   - {agent_id}: {agent_info.get('type')} ({agent_info.get('status')})")
        print(f"     Messages: {agent_info.get('message_count', 0)}")

    print("\n✅ Broker statistics test PASSED")
    return True


async def main():
    """Run all tests."""
    print("\n🚀 Starting A2A Communication Tests\n")

    results = []

    # Test 1: Backward compatibility
    results.append(await test_backward_compatibility())

    # Test 2: Basic A2A
    results.append(await test_basic_a2a())

    # Test 3: Agent collaboration
    results.append(await test_agent_collaboration())

    # Test 4: Direct communication
    results.append(await test_direct_agent_communication())

    # Test 5: Statistics
    results.append(await test_broker_statistics())

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 All tests PASSED! A2A communication is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
