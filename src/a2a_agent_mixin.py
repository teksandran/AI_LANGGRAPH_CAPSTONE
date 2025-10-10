"""
A2A Agent Mixin
Provides A2A communication capabilities to existing agents without breaking them.
"""

from typing import Optional, Dict, Any, List
import asyncio
import logging
from .a2a_protocol import (
    A2AMessage,
    AgentProfile,
    AgentCapability,
    MessageType,
    create_request_message,
    create_response_message,
    create_notification_message,
    create_handoff_message
)
from .a2a_broker import get_broker


logger = logging.getLogger(__name__)


class A2AAgentMixin:
    """
    Mixin class that adds A2A communication capabilities to agents.

    Usage:
        class MyAgent(A2AAgentMixin):
            def __init__(self, ...):
                super().__init__()
                self._setup_a2a(agent_id="my_agent", agent_type="specialist")
    """

    def _setup_a2a(
        self,
        agent_id: str,
        agent_type: str,
        capabilities: Optional[List[AgentCapability]] = None
    ):
        """
        Set up A2A communication for this agent.

        Args:
            agent_id: Unique identifier for this agent
            agent_type: Type/role of this agent
            capabilities: List of capabilities this agent has
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.a2a_broker = get_broker()

        # Create agent profile
        self.agent_profile = AgentProfile(
            agent_id=agent_id,
            agent_type=agent_type,
            capabilities=capabilities or [],
            status="active"
        )

        # Register with broker
        self.a2a_broker.register_agent(self.agent_profile, self._handle_a2a_message)
        logger.info(f"Agent {agent_id} registered for A2A communication")

    async def _handle_a2a_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """
        Handle incoming A2A messages. Override this in subclasses for custom handling.

        Args:
            message: Incoming message

        Returns:
            Response message if applicable
        """
        logger.info(
            f"Agent {self.agent_id} received {message.message_type} message "
            f"from {message.sender}"
        )

        try:
            if message.message_type == MessageType.REQUEST:
                return await self._handle_request(message)
            elif message.message_type == MessageType.HANDOFF:
                return await self._handle_handoff(message)
            elif message.message_type == MessageType.NOTIFICATION:
                await self._handle_notification(message)
                return None
            else:
                logger.warning(f"Unhandled message type: {message.message_type}")
                return None

        except Exception as e:
            logger.error(f"Error handling A2A message: {e}", exc_info=True)
            return create_response_message(
                sender=self.agent_id,
                recipient=message.sender,
                success=False,
                data=None,
                error=str(e),
                reply_to=message.message_id,
                conversation_id=message.conversation_id or ""
            )

    async def _handle_request(self, message: A2AMessage) -> A2AMessage:
        """
        Handle REQUEST messages. Override in subclass for custom behavior.

        Default: Returns error saying request type not supported
        """
        task = message.content.get("task")
        logger.info(f"Processing request: {task}")

        return create_response_message(
            sender=self.agent_id,
            recipient=message.sender,
            success=False,
            data=None,
            error=f"Request type '{task}' not supported by {self.agent_type}",
            reply_to=message.message_id,
            conversation_id=message.conversation_id or ""
        )

    async def _handle_handoff(self, message: A2AMessage) -> A2AMessage:
        """
        Handle HANDOFF messages. Override in subclass for custom behavior.

        Default: Accepts the handoff and processes the user message
        """
        content = message.content
        user_message = content.get("user_message", "")
        context = content.get("context", {})
        reason = content.get("reason", "")

        logger.info(
            f"Received handoff from {message.sender}: {reason}\n"
            f"User message: {user_message}"
        )

        # Default: Try to process the message
        # Subclasses should override this with actual logic
        return create_response_message(
            sender=self.agent_id,
            recipient=message.sender,
            success=True,
            data={"acknowledged": True, "context": context},
            reply_to=message.message_id,
            conversation_id=message.conversation_id or ""
        )

    async def _handle_notification(self, message: A2AMessage):
        """
        Handle NOTIFICATION messages. Override in subclass for custom behavior.

        Default: Just logs the notification
        """
        event = message.content.get("event")
        severity = message.content.get("severity", "info")
        logger.info(f"Notification from {message.sender}: {event} ({severity})")

    # Helper methods for sending messages

    async def send_request(
        self,
        recipient: str,
        task: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        wait_for_response: bool = True,
        timeout: float = 30.0
    ) -> Optional[A2AMessage]:
        """
        Send a request to another agent.

        Args:
            recipient: Agent ID to send request to
            task: Task to request
            parameters: Task parameters
            context: Additional context
            wait_for_response: Whether to wait for response
            timeout: Timeout in seconds

        Returns:
            Response message if wait_for_response=True
        """
        message = create_request_message(
            sender=self.agent_id,
            recipient=recipient,
            task=task,
            parameters=parameters,
            context=context
        )

        return await self.a2a_broker.send_message(
            message,
            wait_for_response=wait_for_response,
            timeout=timeout
        )

    async def send_notification(
        self,
        recipient: str,
        event: str,
        data: Dict[str, Any],
        severity: str = "info"
    ):
        """Send a notification to another agent."""
        message = create_notification_message(
            sender=self.agent_id,
            recipient=recipient,
            event=event,
            data=data,
            severity=severity  # type: ignore
        )

        await self.a2a_broker.send_message(message)

    async def handoff_to_agent(
        self,
        recipient: str,
        task: str,
        user_message: str,
        context: Dict[str, Any],
        reason: str,
        conversation_id: str
    ) -> Optional[A2AMessage]:
        """
        Hand off the current task to another agent.

        Args:
            recipient: Agent to hand off to
            task: Task description
            user_message: Original user message
            context: Context to pass along
            reason: Reason for handoff
            conversation_id: Conversation ID

        Returns:
            Response from recipient agent
        """
        message = create_handoff_message(
            sender=self.agent_id,
            recipient=recipient,
            task=task,
            context=context,
            reason=reason,
            user_message=user_message,
            conversation_id=conversation_id
        )

        return await self.a2a_broker.send_message(
            message,
            wait_for_response=True,
            timeout=30.0
        )

    async def request_agent_help(
        self,
        capability: str,
        task: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[A2AMessage]:
        """
        Request help from any agent with a specific capability.

        Args:
            capability: Required capability
            task: Task to request
            parameters: Task parameters
            context: Additional context

        Returns:
            Response from the agent
        """
        # Find agent with capability
        agent_profile = self.a2a_broker.find_agent_by_capability(capability)

        if not agent_profile:
            logger.warning(f"No agent found with capability: {capability}")
            return None

        logger.info(f"Found agent {agent_profile.agent_id} for capability {capability}")

        return await self.send_request(
            recipient=agent_profile.agent_id,
            task=task,
            parameters=parameters,
            context=context,
            wait_for_response=True
        )

    def get_available_agents(self) -> List[AgentProfile]:
        """Get list of all available agents."""
        return self.a2a_broker.list_agents()

    def get_agent_profile_by_id(self, agent_id: str) -> Optional[AgentProfile]:
        """Get profile of a specific agent."""
        return self.a2a_broker.get_agent_profile(agent_id)

    def deactivate_a2a(self):
        """Deactivate A2A communication for this agent."""
        self.agent_profile.status = "offline"
        logger.info(f"Agent {self.agent_id} deactivated from A2A communication")

    def activate_a2a(self):
        """Activate A2A communication for this agent."""
        self.agent_profile.status = "active"
        logger.info(f"Agent {self.agent_id} activated for A2A communication")
