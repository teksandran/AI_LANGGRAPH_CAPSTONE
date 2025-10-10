"""
Test HITL (Human-in-the-Loop) System
Tests human approval workflow integration.
"""

import asyncio
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv

# Set UTF-8 encoding
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

load_dotenv()


async def test_hitl_disabled():
    """Test that HITL disabled works (auto-approve)."""
    print("\n" + "=" * 70)
    print("TEST 1: HITL Disabled (Auto-Approve)")
    print("=" * 70)

    try:
        from src.supervisor_agent_hitl import SupervisorAgentHITL

        yelp_api_key = os.getenv("YELP_API_KEY")
        if not yelp_api_key:
            print("[ERROR] YELP_API_KEY not found")
            return False

        print("\n[1/3] Creating supervisor with HITL disabled...")
        supervisor = SupervisorAgentHITL(
            yelp_api_key=yelp_api_key,
            enable_a2a=True,
            enable_hitl=False  # HITL disabled
        )
        print("[OK] Supervisor created")

        print("\n[2/3] Running query (should auto-approve)...")
        result = await supervisor.run_with_hitl("What is Botox?")

        print(f"[OK] Response received: {len(result['response'])} chars")
        print(f"[OK] HITL checked: {result['hitl_checked']}")
        print(f"[OK] Method: {result['method']}")

        print("\n[3/3] Verifying auto-approval...")
        if not result['hitl_checked']:
            print("[OK] HITL was bypassed (as expected)")
            print("\n[PASS] Test passed!")
            return True
        else:
            print("[WARN] HITL was checked unexpectedly")
            return False

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_hitl_enabled_with_policy():
    """Test HITL enabled with approval policy."""
    print("\n" + "=" * 70)
    print("TEST 2: HITL Enabled with Policy")
    print("=" * 70)

    try:
        from src.supervisor_agent_hitl import SupervisorAgentHITL
        from src.hitl_manager import get_hitl_manager
        from src.hitl_protocol import (
            DefaultHITLPolicies,
            HITLDecision,
            create_hitl_response
        )

        yelp_api_key = os.getenv("YELP_API_KEY")
        if not yelp_api_key:
            print("[ERROR] YELP_API_KEY not found")
            return False

        print("\n[1/5] Setting up HITL manager with policy...")
        manager = get_hitl_manager()

        # Remove default no-approval policy
        manager.remove_policy("no_approval")

        # Add policy requiring approval for all responses
        policy = DefaultHITLPolicies.always_approve_responses()
        manager.add_policy(policy)
        print(f"[OK] Added policy: {policy.name}")

        print("\n[2/5] Creating supervisor with HITL enabled...")
        supervisor = SupervisorAgentHITL(
            yelp_api_key=yelp_api_key,
            enable_a2a=True,
            enable_hitl=True  # HITL enabled
        )
        print("[OK] Supervisor created")

        print("\n[3/5] Running query async (will wait for approval)...")

        # Create a task for the query (it will wait for approval)
        query_task = asyncio.create_task(
            supervisor.run_with_hitl("What is Botox?")
        )

        # Give it a moment to create the HITL request
        await asyncio.sleep(1)

        print("\n[4/5] Checking pending requests...")
        pending = manager.get_pending_requests()
        print(f"[OK] Pending requests: {len(pending)}")

        if len(pending) > 0:
            request = pending[0]
            print(f"[OK] Request ID: {request.request_id}")
            print(f"[OK] Action type: {request.action_type.value}")

            print("\n[5/5] Simulating human approval...")
            response = create_hitl_response(
                request_id=request.request_id,
                decision=HITLDecision.APPROVED,
                feedback="Approved by automated test",
                decided_by="test_system"
            )

            manager.submit_response(response)
            print("[OK] Approval submitted")

            # Now the query should complete
            result = await query_task
            print(f"[OK] Query completed: {len(result['response'])} chars")
            print(f"[OK] HITL approved: {result.get('hitl_approved')}")

            print("\n[PASS] Test passed!")
            return True
        else:
            print("[ERROR] No pending requests found")
            # Cancel the task
            query_task.cancel()
            return False

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_hitl_modification():
    """Test HITL with response modification."""
    print("\n" + "=" * 70)
    print("TEST 3: HITL Response Modification")
    print("=" * 70)

    try:
        from src.supervisor_agent_hitl import SupervisorAgentHITL
        from src.hitl_manager import get_hitl_manager
        from src.hitl_protocol import (
            DefaultHITLPolicies,
            HITLDecision,
            create_hitl_response
        )

        yelp_api_key = os.getenv("YELP_API_KEY")
        if not yelp_api_key:
            print("[ERROR] YELP_API_KEY not found")
            return False

        print("\n[1/4] Setting up HITL with approval policy...")
        manager = get_hitl_manager()
        manager.remove_policy("no_approval")
        policy = DefaultHITLPolicies.always_approve_responses()
        manager.add_policy(policy)
        print("[OK] Policy configured")

        supervisor = SupervisorAgentHITL(
            yelp_api_key=yelp_api_key,
            enable_a2a=False,  # Use simple mode
            enable_hitl=True
        )

        print("\n[2/4] Running query...")
        query_task = asyncio.create_task(
            supervisor.run_with_hitl("Tell me about Evolus")
        )

        await asyncio.sleep(1)

        print("\n[3/4] Modifying response...")
        pending = manager.get_pending_requests()

        if len(pending) > 0:
            request = pending[0]

            # Create modified response
            modified_response = create_hitl_response(
                request_id=request.request_id,
                decision=HITLDecision.MODIFIED,
                modified_data={
                    "response": "MODIFIED: This is a human-modified response about Evolus."
                },
                feedback="Response modified by test",
                decided_by="test_system"
            )

            manager.submit_response(modified_response)
            print("[OK] Modified response submitted")

            result = await query_task

            print("\n[4/4] Verifying modification...")
            if "MODIFIED:" in result['response']:
                print("[OK] Response was modified as expected")
                print(f"[OK] Modified response: {result['response'][:80]}...")
                print("\n[PASS] Test passed!")
                return True
            else:
                print("[ERROR] Response was not modified")
                return False
        else:
            query_task.cancel()
            print("[ERROR] No pending requests")
            return False

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_hitl_statistics():
    """Test HITL statistics tracking."""
    print("\n" + "=" * 70)
    print("TEST 4: HITL Statistics")
    print("=" * 70)

    try:
        from src.supervisor_agent_hitl import SupervisorAgentHITL
        from src.hitl_manager import get_hitl_manager

        yelp_api_key = os.getenv("YELP_API_KEY")
        if not yelp_api_key:
            print("[ERROR] YELP_API_KEY not found")
            return False

        print("\n[1/2] Getting HITL statistics...")
        supervisor = SupervisorAgentHITL(
            yelp_api_key=yelp_api_key,
            enable_hitl=True
        )

        stats = supervisor.get_hitl_statistics()
        print(f"[OK] HITL enabled: {stats.get('hitl_enabled')}")
        print(f"[OK] Total requests: {stats.get('total_requests', 0)}")
        print(f"[OK] Approved: {stats.get('approved', 0)}")
        print(f"[OK] Rejected: {stats.get('rejected', 0)}")
        print(f"[OK] Modified: {stats.get('modified', 0)}")

        print("\n[2/2] Getting combined stats...")
        combined = supervisor.get_combined_statistics()
        print(f"[OK] A2A enabled: {combined['a2a'].get('a2a_enabled', False)}")
        print(f"[OK] HITL enabled: {combined['hitl'].get('hitl_enabled', False)}")

        print("\n[PASS] Test passed!")
        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all HITL tests."""
    print("\n" + "=" * 70)
    print("HITL SYSTEM TESTS")
    print("=" * 70)

    results = []

    # Test 1: HITL disabled
    results.append(await test_hitl_disabled())

    # Test 2: HITL with approval
    results.append(await test_hitl_enabled_with_policy())

    # Test 3: HITL with modification
    results.append(await test_hitl_modification())

    # Test 4: Statistics
    results.append(await test_hitl_statistics())

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"\n[OK] Passed: {passed}/{total}")
    print(f"[X] Failed: {total - passed}/{total}")

    if passed == total:
        print("\n[SUCCESS] All HITL tests passed!")
    else:
        print("\n[WARNING] Some tests failed")

    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
