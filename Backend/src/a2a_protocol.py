"""
Agent-to-Agent (A2A) Communication Protocol
Enables direct communication between agents for collaborative task solving.
"""

from typing import Dict, Any, Optional, List, Literal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class MessageType(str, Enum):
    """Types of A2A messages."""
    REQUEST = "request"           # Request information from another agent
    RESPONSE = "response"         # Response to a request
    NOTIFICATION = "notification" # Notify another agent of information
    QUERY = "query"              # Query for agent capabilities
    HANDOFF = "handoff"          # Handoff task to another agent


class MessagePriority(str, Enum):
    """Message priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class A2AMessage:
    """
    Standard message format for agent-to-agent communication.

    Attributes:
        message_id: Unique identifier for the message
        sender: Agent ID of the sender
        recipient: Agent ID of the recipient
        message_type: Type of message (request, response, etc.)
        content: Main message content
        priority: Message priority level
        timestamp: When the message was created
        metadata: Additional metadata
        conversation_id: ID to group related messages
        reply_to: ID of message this is replying to
    """
    sender: str
    recipient: str
    message_type: MessageType
    content: Dict[str, Any]
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    conversation_id: Optional[str] = None
    reply_to: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type.value,
            "content": self.content,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "conversation_id": self.conversation_id,
            "reply_to": self.reply_to
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AMessage":
        """Create message from dictionary."""
        return cls(
            message_id=data.get("message_id", str(uuid.uuid4())),
            sender=data["sender"],
            recipient=data["recipient"],
            message_type=MessageType(data["message_type"]),
            content=data["content"],
            priority=MessagePriority(data.get("priority", "normal")),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            metadata=data.get("metadata", {}),
            conversation_id=data.get("conversation_id"),
            reply_to=data.get("reply_to")
        )


@dataclass
class AgentCapability:
    """Describes an agent's capability."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    examples: List[str] = field(default_factory=list)


@dataclass
class AgentProfile:
    """
    Profile describing an agent's capabilities and characteristics.

    Attributes:
        agent_id: Unique identifier for the agent
        agent_type: Type/role of the agent
        capabilities: List of agent capabilities
        status: Current status (active, busy, offline)
        metadata: Additional metadata
    """
    agent_id: str
    agent_type: str
    capabilities: List[AgentCapability]
    status: Literal["active", "busy", "offline"] = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle a task type."""
        return any(cap.name == task_type for cap in self.capabilities)

    def get_capability(self, name: str) -> Optional[AgentCapability]:
        """Get a specific capability by name."""
        for cap in self.capabilities:
            if cap.name == name:
                return cap
        return None


# Standard message content schemas
class RequestSchema:
    """Schema for REQUEST messages."""

    @staticmethod
    def create(
        task: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a request message content."""
        return {
            "task": task,
            "parameters": parameters,
            "context": context or {}
        }


class ResponseSchema:
    """Schema for RESPONSE messages."""

    @staticmethod
    def create(
        success: bool,
        data: Any,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a response message content."""
        return {
            "success": success,
            "data": data,
            "error": error,
            "metadata": metadata or {}
        }


class NotificationSchema:
    """Schema for NOTIFICATION messages."""

    @staticmethod
    def create(
        event: str,
        data: Dict[str, Any],
        severity: Literal["info", "warning", "error"] = "info"
    ) -> Dict[str, Any]:
        """Create a notification message content."""
        return {
            "event": event,
            "data": data,
            "severity": severity
        }


class HandoffSchema:
    """Schema for HANDOFF messages."""

    @staticmethod
    def create(
        task: str,
        context: Dict[str, Any],
        reason: str,
        user_message: str
    ) -> Dict[str, Any]:
        """Create a handoff message content."""
        return {
            "task": task,
            "context": context,
            "reason": reason,
            "user_message": user_message
        }


# Helper functions for creating common messages
def create_request_message(
    sender: str,
    recipient: str,
    task: str,
    parameters: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    conversation_id: Optional[str] = None,
    priority: MessagePriority = MessagePriority.NORMAL
) -> A2AMessage:
    """Helper to create a request message."""
    return A2AMessage(
        sender=sender,
        recipient=recipient,
        message_type=MessageType.REQUEST,
        content=RequestSchema.create(task, parameters, context),
        priority=priority,
        conversation_id=conversation_id or str(uuid.uuid4())
    )


def create_response_message(
    sender: str,
    recipient: str,
    success: bool,
    data: Any,
    reply_to: str,
    conversation_id: str,
    error: Optional[str] = None
) -> A2AMessage:
    """Helper to create a response message."""
    return A2AMessage(
        sender=sender,
        recipient=recipient,
        message_type=MessageType.RESPONSE,
        content=ResponseSchema.create(success, data, error),
        reply_to=reply_to,
        conversation_id=conversation_id
    )


def create_notification_message(
    sender: str,
    recipient: str,
    event: str,
    data: Dict[str, Any],
    severity: Literal["info", "warning", "error"] = "info"
) -> A2AMessage:
    """Helper to create a notification message."""
    return A2AMessage(
        sender=sender,
        recipient=recipient,
        message_type=MessageType.NOTIFICATION,
        content=NotificationSchema.create(event, data, severity),
        priority=MessagePriority.HIGH if severity == "error" else MessagePriority.NORMAL
    )


def create_handoff_message(
    sender: str,
    recipient: str,
    task: str,
    context: Dict[str, Any],
    reason: str,
    user_message: str,
    conversation_id: str
) -> A2AMessage:
    """Helper to create a handoff message."""
    return A2AMessage(
        sender=sender,
        recipient=recipient,
        message_type=MessageType.HANDOFF,
        content=HandoffSchema.create(task, context, reason, user_message),
        conversation_id=conversation_id,
        priority=MessagePriority.HIGH
    )
