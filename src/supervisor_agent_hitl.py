"""
Supervisor Agent with HITL Support
Combines A2A communication with Human-in-the-Loop approval.
"""

from typing import Literal, Optional, Dict, Any
import asyncio
import logging
from .supervisor_agent_a2a import SupervisorAgentA2A
from .hitl_agent_mixin import HITLAgentMixin
from .hitl_protocol import HITLActionType, create_hitl_request, HITLPriority
import time


logger = logging.getLogger(__name__)


class SupervisorAgentHITL(SupervisorAgentA2A, HITLAgentMixin):
    """
    Supervisor Agent with both A2A and HITL capabilities.

    Features:
    - All A2A communication features
    - Human approval for agent responses
    - Policy-based approval workflow
    - Backward compatible with SupervisorAgent
    """

    def __init__(
        self,
        yelp_api_key: str,
        llm_provider: Literal["openai", "anthropic"] = "openai",
        model: str = None,
        enable_a2a: bool = True,
        enable_hitl: bool = False,  # HITL disabled by default
        agent_id: str = "supervisor"
    ):
        """
        Initialize Supervisor with A2A and HITL.

        Args:
            yelp_api_key: Yelp API key
            llm_provider: LLM provider
            model: Model name
            enable_a2a: Enable A2A communication
            enable_hitl: Enable human-in-the-loop
            agent_id: Agent identifier
        """
        # Initialize A2A supervisor
        SupervisorAgentA2A.__init__(
            self,
            yelp_api_key=yelp_api_key,
            llm_provider=llm_provider,
            model=model,
            enable_a2a=enable_a2a,
            agent_id=agent_id
        )

        # Setup HITL
        self._setup_hitl(agent_id=agent_id, enable_hitl=enable_hitl)

        logger.info(
            f"SupervisorAgentHITL initialized: "
            f"A2A={'on' if enable_a2a else 'off'}, "
            f"HITL={'on' if enable_hitl else 'off'}"
        )

    async def run_with_hitl(
        self,
        user_message: str,
        require_approval: bool = None,
        wait_for_approval: bool = False
    ) -> Dict[str, Any]:
        """
        Run query with optional HITL approval.

        Args:
            user_message: User's query
            require_approval: Force approval requirement (overrides policies)
            wait_for_approval: If True, wait for human approval (default: False - return pending status immediately)

        Returns:
            Dict with response and metadata
        """
        # Get response using A2A if enabled, otherwise traditional
        if self.enable_a2a:
            result = await self.run_with_a2a(user_message)
            response_text = result['response']
            method = result['method']
            agents_used = result.get('agents_used', [])
        else:
            response_text = await self.run(user_message)
            method = "traditional_routing"
            agents_used = []

        # If HITL disabled or not required, return immediately
        if not self.hitl_enabled and require_approval is not True:
            return {
                "response": response_text,
                "method": method,
                "agents_used": agents_used,
                "hitl_checked": False,
                "hitl_approved": None
            }

        # Check if approval required (or forced)
        logger.info("Checking if response needs human approval...")

        # Check if this type of response needs approval
        action_data = {
            "response": response_text,
            "user_query": user_message,
            "confidence": 1.0,
            "metadata": {
                "method": method,
                "agents_used": agents_used
            }
        }

        requires_approval = self.hitl_manager.should_require_approval(
            HITLActionType.AGENT_RESPONSE,
            action_data
        )

        # If no approval needed, return immediately
        if not requires_approval and require_approval is not True:
            return {
                "response": response_text,
                "method": method,
                "agents_used": agents_used,
                "hitl_checked": True,
                "hitl_approved": True,
                "hitl_decision": "auto_approved",
                "hitl_feedback": "No approval required"
            }

        # Approval is required
        if not wait_for_approval:
            # Non-blocking mode: Create request and return pending status
            hitl_request = create_hitl_request(
                action_type=HITLActionType.AGENT_RESPONSE,
                agent_id=self.agent_id,
                action_data=action_data,
                context={"agent_id": self.agent_id, "timestamp": str(time.time())},
                priority=HITLPriority.HIGH
            )

            # Add to pending queue
            self.hitl_manager._pending_requests[hitl_request.request_id] = hitl_request
            logger.info(f"HITL request {hitl_request.request_id} created - returning pending status")

            return {
                "response": response_text,
                "method": method,
                "agents_used": agents_used,
                "hitl_checked": True,
                "hitl_approved": None,  # None indicates pending
                "hitl_decision": "pending",
                "hitl_request_id": hitl_request.request_id,
                "hitl_status": "pending_approval",
                "hitl_message": "Response is pending human approval for medical information"
            }

        # Blocking mode: Wait for approval
        approval_result = await self.check_response_approval(
            response_text=response_text,
            user_query=user_message,
            confidence=1.0,
            metadata={
                "method": method,
                "agents_used": agents_used
            }
        )

        if not approval_result["approved"]:
            # Rejected by human
            logger.warning("Response rejected by human reviewer")

            return {
                "response": "I apologize, but I cannot provide that response. The system has flagged it for review.",
                "method": method,
                "agents_used": agents_used,
                "hitl_checked": True,
                "hitl_approved": False,
                "hitl_decision": approval_result["decision"].value,
                "hitl_feedback": approval_result.get("feedback")
            }

        # Use modified response if provided
        final_response = approval_result.get("response", response_text)

        return {
            "response": final_response,
            "method": method,
            "agents_used": agents_used,
            "hitl_checked": True,
            "hitl_approved": True,
            "hitl_decision": approval_result["decision"].value,
            "hitl_modified": approval_result["decision"].value == "modified",
            "hitl_feedback": approval_result.get("feedback")
        }

    async def run(self, user_message: str) -> str:
        """
        Run using traditional routing (backward compatible).
        No HITL checks in this method to maintain compatibility.
        """
        return await SupervisorAgentA2A.run(self, user_message)

    async def run_with_a2a(self, user_message: str) -> Dict[str, Any]:
        """
        Run with A2A (no HITL).
        Use run_with_hitl() for HITL approval.
        """
        return await SupervisorAgentA2A.run_with_a2a(self, user_message)

    def get_hitl_statistics(self) -> Dict[str, Any]:
        """Get HITL statistics."""
        if not self.hitl_enabled:
            return {"hitl_enabled": False}

        stats = self.hitl_manager.get_statistics()
        return {
            "hitl_enabled": True,
            **stats
        }

    def get_combined_statistics(self) -> Dict[str, Any]:
        """Get both A2A and HITL statistics."""
        return {
            "a2a": self.get_a2a_statistics() if self.enable_a2a else {"enabled": False},
            "hitl": self.get_hitl_statistics()
        }
