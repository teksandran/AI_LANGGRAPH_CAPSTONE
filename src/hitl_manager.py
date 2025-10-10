"""
Human-in-the-Loop Manager
Manages human approval requests, responses, and policy enforcement.
"""

from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict
from datetime import datetime
import asyncio
import logging
from .hitl_protocol import (
    HITLRequest,
    HITLResponse,
    HITLPolicy,
    HITLActionType,
    HITLDecision,
    HITLPriority,
    DefaultHITLPolicies
)


logger = logging.getLogger(__name__)


class HITLManager:
    """
    Manages human-in-the-loop approval workflow.

    Features:
    - Policy-based approval requirements
    - Request queuing and prioritization
    - Timeout handling
    - Response tracking
    - Statistics and monitoring
    """

    def __init__(self):
        """Initialize HITL manager."""
        self._policies: List[HITLPolicy] = []
        self._pending_requests: Dict[str, HITLRequest] = {}
        self._responses: Dict[str, HITLResponse] = {}
        self._request_futures: Dict[str, asyncio.Future] = {}
        self._history: List[Dict[str, Any]] = []
        self._callbacks: Dict[str, List[Callable]] = defaultdict(list)

        # Statistics
        self._stats = {
            "total_requests": 0,
            "approved": 0,
            "rejected": 0,
            "modified": 0,
            "timeout": 0,
            "pending": 0
        }

    def add_policy(self, policy: HITLPolicy):
        """Add a HITL policy."""
        self._policies.append(policy)
        logger.info(f"Added HITL policy: {policy.name}")

    def remove_policy(self, policy_name: str) -> bool:
        """Remove a policy by name."""
        for i, policy in enumerate(self._policies):
            if policy.name == policy_name:
                self._policies.pop(i)
                logger.info(f"Removed HITL policy: {policy_name}")
                return True
        return False

    def get_policies(self) -> List[HITLPolicy]:
        """Get all active policies."""
        return self._policies.copy()

    def should_require_approval(
        self,
        action_type: HITLActionType,
        action_data: Dict[str, Any]
    ) -> bool:
        """
        Check if action requires human approval based on policies.

        Args:
            action_type: Type of action
            action_data: Action data

        Returns:
            True if approval required
        """
        for policy in self._policies:
            if policy.should_trigger(action_type, action_data):
                logger.info(
                    f"Policy '{policy.name}' triggered for {action_type.value}"
                )
                return True

        return False

    async def request_approval(
        self,
        action_type: HITLActionType,
        agent_id: str,
        action_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[float] = None
    ) -> HITLResponse:
        """
        Request human approval for an action.

        Args:
            action_type: Type of action
            agent_id: Agent requesting approval
            action_data: Data about the action
            context: Additional context
            timeout_seconds: Timeout for response

        Returns:
            HITLResponse with human's decision
        """
        # Find applicable policy for timeout/priority
        applicable_policy = None
        for policy in self._policies:
            if policy.should_trigger(action_type, action_data):
                applicable_policy = policy
                break

        # Create request
        from .hitl_protocol import create_hitl_request

        request = create_hitl_request(
            action_type=action_type,
            agent_id=agent_id,
            action_data=action_data,
            context=context,
            priority=applicable_policy.priority if applicable_policy else HITLPriority.NORMAL,
            timeout_seconds=timeout_seconds or (
                applicable_policy.timeout_seconds if applicable_policy else None
            )
        )

        # Store request
        self._pending_requests[request.request_id] = request
        self._stats["total_requests"] += 1
        self._stats["pending"] += 1

        logger.info(
            f"HITL request {request.request_id} created by {agent_id} "
            f"for {action_type.value}"
        )

        # Create future for waiting
        future = asyncio.Future()
        self._request_futures[request.request_id] = future

        # Trigger callbacks
        await self._trigger_callbacks("request_created", request)

        # Wait for response with timeout
        try:
            if request.expires_at:
                timeout = (request.expires_at - datetime.now()).total_seconds()
                response = await asyncio.wait_for(future, timeout=timeout)
            else:
                response = await future

            return response

        except asyncio.TimeoutError:
            logger.warning(f"HITL request {request.request_id} timed out")
            self._stats["timeout"] += 1
            self._stats["pending"] -= 1

            # Use policy's auto decision or reject
            auto_decision = (
                applicable_policy.auto_decision
                if applicable_policy and applicable_policy.auto_decision
                else HITLDecision.REJECTED
            )

            response = HITLResponse(
                request_id=request.request_id,
                decision=auto_decision,
                feedback="Automatic decision due to timeout",
                decided_by="system"
            )

            # Record response
            self._responses[request.request_id] = response
            self._record_history(request, response)

            # Clean up
            del self._pending_requests[request.request_id]
            del self._request_futures[request.request_id]

            return response

    def submit_response(self, response: HITLResponse) -> bool:
        """
        Submit a human's response to a pending request.

        Args:
            response: Human's response

        Returns:
            True if successful
        """
        request_id = response.request_id

        if request_id not in self._pending_requests:
            logger.warning(f"No pending request found for {request_id}")
            return False

        request = self._pending_requests[request_id]

        # Store response
        self._responses[request_id] = response

        # Update statistics
        self._stats["pending"] -= 1
        if response.decision == HITLDecision.APPROVED:
            self._stats["approved"] += 1
        elif response.decision == HITLDecision.REJECTED:
            self._stats["rejected"] += 1
        elif response.decision == HITLDecision.MODIFIED:
            self._stats["modified"] += 1

        logger.info(
            f"HITL response received for {request_id}: {response.decision.value}"
        )

        # Record in history
        self._record_history(request, response)

        # Resolve future
        if request_id in self._request_futures:
            self._request_futures[request_id].set_result(response)
            del self._request_futures[request_id]

        # Clean up
        del self._pending_requests[request_id]

        return True

    def get_pending_requests(
        self,
        agent_id: Optional[str] = None,
        action_type: Optional[HITLActionType] = None,
        priority: Optional[HITLPriority] = None
    ) -> List[HITLRequest]:
        """
        Get pending requests with optional filters.

        Args:
            agent_id: Filter by agent ID
            action_type: Filter by action type
            priority: Filter by priority

        Returns:
            List of matching requests
        """
        requests = list(self._pending_requests.values())

        if agent_id:
            requests = [r for r in requests if r.agent_id == agent_id]

        if action_type:
            requests = [r for r in requests if r.action_type == action_type]

        if priority:
            requests = [r for r in requests if r.priority == priority]

        # Sort by priority (critical first) then by created time
        priority_order = {
            HITLPriority.CRITICAL: 0,
            HITLPriority.HIGH: 1,
            HITLPriority.NORMAL: 2,
            HITLPriority.LOW: 3
        }

        requests.sort(key=lambda r: (priority_order[r.priority], r.created_at))

        return requests

    def get_request(self, request_id: str) -> Optional[HITLRequest]:
        """Get a specific request by ID."""
        return self._pending_requests.get(request_id)

    def get_response(self, request_id: str) -> Optional[HITLResponse]:
        """Get response for a request."""
        return self._responses.get(request_id)

    def get_history(
        self,
        limit: Optional[int] = None,
        agent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get history of requests/responses.

        Args:
            limit: Maximum number of items to return
            agent_id: Filter by agent ID

        Returns:
            List of history items
        """
        history = self._history

        if agent_id:
            history = [h for h in history if h["request"]["agent_id"] == agent_id]

        if limit:
            history = history[-limit:]

        return history

    def get_statistics(self) -> Dict[str, Any]:
        """Get HITL statistics."""
        return {
            **self._stats,
            "active_policies": len(self._policies),
            "approval_rate": (
                self._stats["approved"] / self._stats["total_requests"]
                if self._stats["total_requests"] > 0
                else 0.0
            ),
            "modification_rate": (
                self._stats["modified"] / self._stats["total_requests"]
                if self._stats["total_requests"] > 0
                else 0.0
            ),
            "timeout_rate": (
                self._stats["timeout"] / self._stats["total_requests"]
                if self._stats["total_requests"] > 0
                else 0.0
            )
        }

    def register_callback(self, event: str, callback: Callable):
        """
        Register a callback for HITL events.

        Events:
        - request_created: When new request is created
        - response_submitted: When response is submitted

        Args:
            event: Event name
            callback: Async callback function
        """
        self._callbacks[event].append(callback)

    async def _trigger_callbacks(self, event: str, data: Any):
        """Trigger callbacks for an event."""
        for callback in self._callbacks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Error in HITL callback: {e}", exc_info=True)

    def _record_history(self, request: HITLRequest, response: HITLResponse):
        """Record request/response in history."""
        self._history.append({
            "request": request.to_dict(),
            "response": response.to_dict(),
            "completed_at": datetime.now().isoformat()
        })

        # Keep history size manageable (last 1000 items)
        if len(self._history) > 1000:
            self._history = self._history[-1000:]

    def clear_history(self):
        """Clear history (for testing or privacy)."""
        self._history.clear()
        logger.info("HITL history cleared")

    def reset_statistics(self):
        """Reset statistics counters."""
        self._stats = {
            "total_requests": 0,
            "approved": 0,
            "rejected": 0,
            "modified": 0,
            "timeout": 0,
            "pending": len(self._pending_requests)
        }
        logger.info("HITL statistics reset")


# Global HITL manager instance (singleton)
_global_hitl_manager: Optional[HITLManager] = None


def get_hitl_manager() -> HITLManager:
    """Get the global HITL manager instance."""
    global _global_hitl_manager
    if _global_hitl_manager is None:
        _global_hitl_manager = HITLManager()

        # Add default policy: no approval (can be changed by application)
        _global_hitl_manager.add_policy(DefaultHITLPolicies.no_approval())

    return _global_hitl_manager


def reset_hitl_manager():
    """Reset the global HITL manager (useful for testing)."""
    global _global_hitl_manager
    _global_hitl_manager = None
