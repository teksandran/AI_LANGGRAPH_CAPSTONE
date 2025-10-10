"""
HITL Agent Mixin
Provides Human-in-the-Loop capabilities to agents.
"""

from typing import Optional, Dict, Any
import asyncio
import logging
from .hitl_protocol import (
    HITLActionType,
    HITLDecision,
    create_hitl_request
)
from .hitl_manager import get_hitl_manager


logger = logging.getLogger(__name__)


class HITLAgentMixin:
    """
    Mixin class that adds HITL capabilities to agents.

    Usage:
        class MyAgent(HITLAgentMixin):
            def __init__(self):
                super().__init__()
                self._setup_hitl(agent_id="my_agent")
    """

    def _setup_hitl(self, agent_id: str, enable_hitl: bool = True):
        """
        Set up HITL for this agent.

        Args:
            agent_id: Unique identifier for this agent
            enable_hitl: Whether to enable HITL (default: True)
        """
        self.agent_id = agent_id
        self.hitl_enabled = enable_hitl
        self.hitl_manager = get_hitl_manager()

        logger.info(
            f"Agent {agent_id} HITL {'enabled' if enable_hitl else 'disabled'}"
        )

    async def request_human_approval(
        self,
        action_type: HITLActionType,
        action_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[float] = None,
        bypass_check: bool = False
    ) -> Dict[str, Any]:
        """
        Request human approval for an action.

        Args:
            action_type: Type of action
            action_data: Data about the action
            context: Additional context
            timeout_seconds: Timeout for response
            bypass_check: If True, skip policy check and always request

        Returns:
            Dict with:
            - approved: bool
            - decision: HITLDecision
            - modified_data: Optional modified data
            - feedback: Optional human feedback
        """
        # If HITL disabled, auto-approve
        if not self.hitl_enabled:
            return {
                "approved": True,
                "decision": HITLDecision.APPROVED,
                "modified_data": None,
                "feedback": "HITL disabled - auto-approved"
            }

        # Check if approval required
        if not bypass_check:
            requires_approval = self.hitl_manager.should_require_approval(
                action_type,
                action_data
            )

            if not requires_approval:
                return {
                    "approved": True,
                    "decision": HITLDecision.APPROVED,
                    "modified_data": None,
                    "feedback": "No policy required approval"
                }

        # Request approval
        logger.info(
            f"Agent {self.agent_id} requesting approval for {action_type.value}"
        )

        response = await self.hitl_manager.request_approval(
            action_type=action_type,
            agent_id=self.agent_id,
            action_data=action_data,
            context=context,
            timeout_seconds=timeout_seconds
        )

        # Process response
        approved = response.decision in [
            HITLDecision.APPROVED,
            HITLDecision.MODIFIED
        ]

        return {
            "approved": approved,
            "decision": response.decision,
            "modified_data": response.modified_data,
            "feedback": response.feedback
        }

    async def check_response_approval(
        self,
        response_text: str,
        user_query: str,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check if agent response needs human approval.

        Args:
            response_text: The response agent wants to send
            user_query: Original user query
            confidence: Confidence score (0-1)
            metadata: Additional metadata

        Returns:
            Approval result with possibly modified response
        """
        action_data = {
            "response": response_text,
            "user_query": user_query,
            "confidence": confidence,
            "metadata": metadata or {}
        }

        context = {
            "agent_id": self.agent_id,
            "timestamp": str(asyncio.get_event_loop().time())
        }

        result = await self.request_human_approval(
            action_type=HITLActionType.AGENT_RESPONSE,
            action_data=action_data,
            context=context
        )

        # If modified, use the modified response
        if result["decision"] == HITLDecision.MODIFIED and result["modified_data"]:
            result["response"] = result["modified_data"].get(
                "response",
                response_text
            )
        else:
            result["response"] = response_text

        return result

    async def check_api_call_approval(
        self,
        api_name: str,
        parameters: Dict[str, Any],
        sensitive: bool = False
    ) -> Dict[str, Any]:
        """
        Check if API call needs human approval.

        Args:
            api_name: Name of API being called
            parameters: API parameters
            sensitive: Whether this is a sensitive API call

        Returns:
            Approval result
        """
        action_data = {
            "api_name": api_name,
            "parameters": parameters,
            "sensitive": sensitive
        }

        return await self.request_human_approval(
            action_type=HITLActionType.API_CALL,
            action_data=action_data
        )

    async def check_collaboration_approval(
        self,
        target_agent: str,
        collaboration_type: str,
        data_to_share: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if agent collaboration needs approval.

        Args:
            target_agent: Agent to collaborate with
            collaboration_type: Type of collaboration
            data_to_share: Data being shared

        Returns:
            Approval result
        """
        action_data = {
            "target_agent": target_agent,
            "collaboration_type": collaboration_type,
            "data_to_share": data_to_share
        }

        return await self.request_human_approval(
            action_type=HITLActionType.AGENT_COLLABORATION,
            action_data=action_data
        )

    async def execute_with_approval(
        self,
        action_type: HITLActionType,
        action_function,
        action_data: Dict[str, Any],
        on_rejected=None
    ):
        """
        Execute an action with human approval.

        Args:
            action_type: Type of action
            action_function: Async function to execute if approved
            action_data: Data about the action
            on_rejected: Function to call if rejected

        Returns:
            Result of action_function if approved, else None
        """
        # Request approval
        approval = await self.request_human_approval(
            action_type=action_type,
            action_data=action_data
        )

        if approval["approved"]:
            logger.info(f"Action {action_type.value} approved, executing...")

            # Use modified data if provided
            if approval["modified_data"]:
                action_data.update(approval["modified_data"])

            # Execute the action
            if asyncio.iscoroutinefunction(action_function):
                return await action_function(action_data)
            else:
                return action_function(action_data)

        else:
            logger.info(
                f"Action {action_type.value} rejected: {approval['feedback']}"
            )

            if on_rejected:
                if asyncio.iscoroutinefunction(on_rejected):
                    await on_rejected(approval)
                else:
                    on_rejected(approval)

            return None

    def enable_hitl(self):
        """Enable HITL for this agent."""
        self.hitl_enabled = True
        logger.info(f"HITL enabled for agent {self.agent_id}")

    def disable_hitl(self):
        """Disable HITL for this agent."""
        self.hitl_enabled = False
        logger.info(f"HITL disabled for agent {self.agent_id}")

    def is_hitl_enabled(self) -> bool:
        """Check if HITL is enabled."""
        return self.hitl_enabled
