"""
Agent-to-Agent Message Broker
Central coordinator for A2A communication with message routing and delivery.
"""

from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict
from datetime import datetime
import asyncio
import logging
from .a2a_protocol import (
    A2AMessage,
    AgentProfile,
    MessageType,
    MessagePriority
)


logger = logging.getLogger(__name__)


class A2AMessageBroker:
    """
    Message broker that routes messages between agents.
    Supports both sync and async message delivery.
    """

    def __init__(self):
        """Initialize the message broker."""
        self._agents: Dict[str, AgentProfile] = {}
        self._message_handlers: Dict[str, Callable] = {}
        self._message_queue: List[A2AMessage] = []
        self._message_history: Dict[str, List[A2AMessage]] = defaultdict(list)
        self._conversation_history: Dict[str, List[A2AMessage]] = defaultdict(list)
        self._pending_responses: Dict[str, asyncio.Future] = {}

    def register_agent(self, profile: AgentProfile, handler: Callable) -> bool:
        """
        Register an agent with the broker.

        Args:
            profile: Agent profile with capabilities
            handler: Async function to handle incoming messages
                    Should accept (message: A2AMessage) -> A2AMessage

        Returns:
            True if registration successful
        """
        if profile.agent_id in self._agents:
            logger.warning(f"Agent {profile.agent_id} already registered, updating...")

        self._agents[profile.agent_id] = profile
        self._message_handlers[profile.agent_id] = handler

        logger.info(f"Registered agent: {profile.agent_id} ({profile.agent_type})")
        return True

    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the broker."""
        if agent_id in self._agents:
            del self._agents[agent_id]
            del self._message_handlers[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")
            return True
        return False

    def get_agent_profile(self, agent_id: str) -> Optional[AgentProfile]:
        """Get an agent's profile."""
        return self._agents.get(agent_id)

    def list_agents(self) -> List[AgentProfile]:
        """List all registered agents."""
        return list(self._agents.values())

    def find_agent_by_capability(self, capability: str) -> Optional[AgentProfile]:
        """Find an agent that has a specific capability."""
        for agent in self._agents.values():
            if agent.can_handle(capability):
                return agent
        return None

    async def send_message(
        self,
        message: A2AMessage,
        wait_for_response: bool = False,
        timeout: float = 30.0
    ) -> Optional[A2AMessage]:
        """
        Send a message to an agent.

        Args:
            message: The message to send
            wait_for_response: If True, wait for response (for REQUEST messages)
            timeout: Timeout in seconds for waiting for response

        Returns:
            Response message if wait_for_response=True, else None
        """
        # Validate recipient exists
        if message.recipient not in self._agents:
            logger.error(f"Recipient agent not found: {message.recipient}")
            return None

        # Check recipient status
        recipient_profile = self._agents[message.recipient]
        if recipient_profile.status == "offline":
            logger.warning(f"Recipient agent is offline: {message.recipient}")
            return None

        # Store in history
        self._message_history[message.sender].append(message)
        self._message_history[message.recipient].append(message)

        if message.conversation_id:
            self._conversation_history[message.conversation_id].append(message)

        logger.info(
            f"Routing message {message.message_id} from {message.sender} "
            f"to {message.recipient} (type: {message.message_type})"
        )

        # Get handler
        handler = self._message_handlers.get(message.recipient)
        if not handler:
            logger.error(f"No handler for agent: {message.recipient}")
            return None

        try:
            # If waiting for response, set up future
            if wait_for_response and message.message_type == MessageType.REQUEST:
                future = asyncio.Future()
                self._pending_responses[message.message_id] = future

            # Deliver message
            response = await handler(message)

            # If we got a response and someone is waiting
            if response and message.message_id in self._pending_responses:
                self._pending_responses[message.message_id].set_result(response)

            # Wait for response if requested
            if wait_for_response and message.message_type == MessageType.REQUEST:
                if message.message_id in self._pending_responses:
                    try:
                        response = await asyncio.wait_for(
                            self._pending_responses[message.message_id],
                            timeout=timeout
                        )
                        # Clean up
                        del self._pending_responses[message.message_id]
                        return response
                    except asyncio.TimeoutError:
                        logger.error(f"Timeout waiting for response to {message.message_id}")
                        del self._pending_responses[message.message_id]
                        return None

            return response

        except Exception as e:
            logger.error(f"Error delivering message: {e}", exc_info=True)
            if message.message_id in self._pending_responses:
                del self._pending_responses[message.message_id]
            return None

    async def broadcast_message(self, message: A2AMessage, exclude: List[str] = None) -> int:
        """
        Broadcast a message to all agents (or all except excluded).

        Args:
            message: Message to broadcast (recipient will be overridden)
            exclude: List of agent IDs to exclude

        Returns:
            Number of agents message was sent to
        """
        exclude = exclude or []
        count = 0

        for agent_id in self._agents.keys():
            if agent_id not in exclude and agent_id != message.sender:
                # Create a copy with updated recipient
                broadcast_msg = A2AMessage(
                    sender=message.sender,
                    recipient=agent_id,
                    message_type=message.message_type,
                    content=message.content,
                    priority=message.priority,
                    conversation_id=message.conversation_id
                )

                await self.send_message(broadcast_msg)
                count += 1

        return count

    def get_conversation_history(self, conversation_id: str) -> List[A2AMessage]:
        """Get all messages in a conversation."""
        return self._conversation_history.get(conversation_id, [])

    def get_agent_messages(
        self,
        agent_id: str,
        limit: Optional[int] = None
    ) -> List[A2AMessage]:
        """Get messages for a specific agent."""
        messages = self._message_history.get(agent_id, [])
        if limit:
            return messages[-limit:]
        return messages

    def clear_history(self, conversation_id: Optional[str] = None):
        """Clear message history (optionally for a specific conversation)."""
        if conversation_id:
            if conversation_id in self._conversation_history:
                del self._conversation_history[conversation_id]
        else:
            self._message_history.clear()
            self._conversation_history.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """Get broker statistics."""
        total_messages = sum(len(msgs) for msgs in self._message_history.values())
        active_agents = sum(1 for a in self._agents.values() if a.status == "active")

        return {
            "total_agents": len(self._agents),
            "active_agents": active_agents,
            "total_messages": total_messages,
            "active_conversations": len(self._conversation_history),
            "pending_responses": len(self._pending_responses),
            "agents": {
                agent_id: {
                    "type": profile.agent_type,
                    "status": profile.status,
                    "message_count": len(self._message_history.get(agent_id, []))
                }
                for agent_id, profile in self._agents.items()
            }
        }


# Global broker instance (singleton pattern)
_global_broker: Optional[A2AMessageBroker] = None


def get_broker() -> A2AMessageBroker:
    """Get the global message broker instance."""
    global _global_broker
    if _global_broker is None:
        _global_broker = A2AMessageBroker()
    return _global_broker


def reset_broker():
    """Reset the global broker (useful for testing)."""
    global _global_broker
    _global_broker = None
