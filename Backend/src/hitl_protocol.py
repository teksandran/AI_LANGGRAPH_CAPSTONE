"""
Human-in-the-Loop (HITL) Protocol
Defines interaction patterns for human oversight and intervention in agent actions.
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class HITLActionType(str, Enum):
    """Types of actions that may require human approval."""
    AGENT_RESPONSE = "agent_response"           # Agent's response to user
    AGENT_HANDOFF = "agent_handoff"             # Handing off between agents
    API_CALL = "api_call"                       # External API calls
    DATA_RETRIEVAL = "data_retrieval"           # Retrieving sensitive data
    AGENT_COLLABORATION = "agent_collaboration" # Multi-agent collaboration
    USER_NOTIFICATION = "user_notification"     # Sending notifications to user
    CUSTOM = "custom"                           # Custom actions


class HITLDecision(str, Enum):
    """Human decisions on pending actions."""
    APPROVED = "approved"           # Approve and proceed
    REJECTED = "rejected"           # Reject and stop
    MODIFIED = "modified"           # Approve with modifications
    ESCALATED = "escalated"         # Escalate to higher authority
    NEEDS_INFO = "needs_more_info"  # Request more information
    PENDING = "pending"             # Still waiting for decision


class HITLPriority(str, Enum):
    """Priority levels for HITL requests."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class HITLRequest:
    """
    Request for human review/approval.

    Attributes:
        request_id: Unique identifier
        action_type: Type of action requiring approval
        agent_id: ID of agent requesting approval
        action_data: Data about the action
        context: Additional context
        priority: Priority level
        created_at: When request was created
        expires_at: When request expires (optional)
        metadata: Additional metadata
    """
    action_type: HITLActionType
    agent_id: str
    action_data: Dict[str, Any]
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    context: Dict[str, Any] = field(default_factory=dict)
    priority: HITLPriority = HITLPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "action_type": self.action_type.value,
            "agent_id": self.agent_id,
            "action_data": self.action_data,
            "context": self.context,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata
        }


@dataclass
class HITLResponse:
    """
    Human's response to a HITL request.

    Attributes:
        request_id: ID of request being responded to
        decision: Human's decision
        modified_data: Modified action data (if decision is MODIFIED)
        feedback: Human feedback/comments
        decided_by: Identifier of who made the decision
        decided_at: When decision was made
        metadata: Additional metadata
    """
    request_id: str
    decision: HITLDecision
    modified_data: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None
    decided_by: Optional[str] = None
    decided_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "decision": self.decision.value,
            "modified_data": self.modified_data,
            "feedback": self.feedback,
            "decided_by": self.decided_by,
            "decided_at": self.decided_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class HITLPolicy:
    """
    Policy defining when human approval is required.

    Attributes:
        name: Policy name
        description: Policy description
        action_types: Action types this policy applies to
        conditions: Conditions that trigger HITL (callable that returns bool)
        priority: Priority level for requests triggered by this policy
        timeout_seconds: Timeout for human response (None = no timeout)
        auto_decision: Decision to make if timeout expires (None = reject)
    """
    name: str
    description: str
    action_types: List[HITLActionType]
    conditions: Optional[Callable[[Dict[str, Any]], bool]] = None
    priority: HITLPriority = HITLPriority.NORMAL
    timeout_seconds: Optional[float] = None
    auto_decision: Optional[HITLDecision] = None

    def should_trigger(self, action_type: HITLActionType, action_data: Dict[str, Any]) -> bool:
        """Check if this policy should trigger for given action."""
        # Check if action type matches
        if action_type not in self.action_types:
            return False

        # If no conditions, trigger for all matching action types
        if self.conditions is None:
            return True

        # Check conditions
        try:
            return self.conditions(action_data)
        except Exception:
            # If condition check fails, err on side of caution and trigger
            return True


# Pre-defined policies
class DefaultHITLPolicies:
    """Common HITL policies that can be used out of the box."""

    @staticmethod
    def always_approve_responses() -> HITLPolicy:
        """Policy: Always require approval for agent responses."""
        return HITLPolicy(
            name="always_approve_responses",
            description="Require human approval for all agent responses",
            action_types=[HITLActionType.AGENT_RESPONSE],
            conditions=None,
            priority=HITLPriority.NORMAL,
            timeout_seconds=300.0,  # 5 minutes
            auto_decision=HITLDecision.APPROVED
        )

    @staticmethod
    def approve_high_confidence() -> HITLPolicy:
        """Policy: Require approval only for low-confidence responses."""
        def low_confidence(data: Dict[str, Any]) -> bool:
            confidence = data.get("confidence", 1.0)
            return confidence < 0.7

        return HITLPolicy(
            name="approve_low_confidence",
            description="Require approval when agent confidence is < 70%",
            action_types=[HITLActionType.AGENT_RESPONSE],
            conditions=low_confidence,
            priority=HITLPriority.HIGH,
            timeout_seconds=180.0,
            auto_decision=HITLDecision.REJECTED
        )

    @staticmethod
    def approve_api_calls() -> HITLPolicy:
        """Policy: Require approval for external API calls."""
        return HITLPolicy(
            name="approve_api_calls",
            description="Require approval for all external API calls",
            action_types=[HITLActionType.API_CALL],
            conditions=None,
            priority=HITLPriority.HIGH,
            timeout_seconds=60.0,
            auto_decision=HITLDecision.REJECTED
        )

    @staticmethod
    def approve_sensitive_data() -> HITLPolicy:
        """Policy: Require approval for sensitive data access."""
        def is_sensitive(data: Dict[str, Any]) -> bool:
            sensitive_keywords = ["personal", "private", "confidential", "password", "key"]
            query = str(data.get("query", "")).lower()
            return any(keyword in query for keyword in sensitive_keywords)

        return HITLPolicy(
            name="approve_sensitive_data",
            description="Require approval for sensitive data access",
            action_types=[HITLActionType.DATA_RETRIEVAL],
            conditions=is_sensitive,
            priority=HITLPriority.CRITICAL,
            timeout_seconds=120.0,
            auto_decision=HITLDecision.REJECTED
        )

    @staticmethod
    def approve_multi_agent() -> HITLPolicy:
        """Policy: Require approval for multi-agent collaboration."""
        return HITLPolicy(
            name="approve_multi_agent",
            description="Require approval when multiple agents collaborate",
            action_types=[HITLActionType.AGENT_COLLABORATION],
            conditions=None,
            priority=HITLPriority.NORMAL,
            timeout_seconds=180.0,
            auto_decision=HITLDecision.APPROVED
        )

    @staticmethod
    def no_approval() -> HITLPolicy:
        """Policy: Never require approval (for testing/development)."""
        return HITLPolicy(
            name="no_approval",
            description="No approval required (autonomous mode)",
            action_types=list(HITLActionType),
            conditions=lambda data: False,  # Never triggers
            priority=HITLPriority.LOW
        )


# Helper functions
def create_hitl_request(
    action_type: HITLActionType,
    agent_id: str,
    action_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    priority: HITLPriority = HITLPriority.NORMAL,
    timeout_seconds: Optional[float] = None
) -> HITLRequest:
    """Helper to create a HITL request."""
    request = HITLRequest(
        action_type=action_type,
        agent_id=agent_id,
        action_data=action_data,
        context=context or {},
        priority=priority
    )

    if timeout_seconds:
        from datetime import timedelta
        request.expires_at = datetime.now() + timedelta(seconds=timeout_seconds)

    return request


def create_hitl_response(
    request_id: str,
    decision: HITLDecision,
    modified_data: Optional[Dict[str, Any]] = None,
    feedback: Optional[str] = None,
    decided_by: Optional[str] = None
) -> HITLResponse:
    """Helper to create a HITL response."""
    return HITLResponse(
        request_id=request_id,
        decision=decision,
        modified_data=modified_data,
        feedback=feedback,
        decided_by=decided_by
    )
