"""
Enhanced Business Agent with A2A Communication
Extends BusinessAgent with agent-to-agent communication capabilities.
"""

from typing import Optional, Dict, Any
from langchain_core.language_models.chat_models import BaseChatModel
from .business_agent import BusinessAgent
from .a2a_agent_mixin import A2AAgentMixin
from .a2a_protocol import (
    A2AMessage,
    AgentCapability,
    MessageType,
    create_response_message
)
import logging


logger = logging.getLogger(__name__)


class BusinessAgentA2A(BusinessAgent, A2AAgentMixin):
    """
    Business Agent with A2A capabilities.
    Can communicate with other agents and handle inter-agent requests.
    """

    def __init__(
        self,
        yelp_api_key: str,
        llm: BaseChatModel,
        agent_id: str = "business_agent"
    ):
        """
        Initialize Business Agent with A2A capabilities.

        Args:
            yelp_api_key: Yelp API key
            llm: Language model for processing
            agent_id: Unique identifier for this agent
        """
        # Initialize base BusinessAgent
        BusinessAgent.__init__(self, yelp_api_key, llm)

        # Define capabilities
        capabilities = [
            AgentCapability(
                name="business_search",
                description="Search for beauty salons, spas, and service providers",
                input_schema={
                    "query": "string",
                    "location": "string",
                    "service_type": "string (optional)",
                    "limit": "int (optional)"
                },
                output_schema={
                    "businesses": "list",
                    "formatted_response": "string"
                },
                examples=[
                    "Find Botox providers in New York",
                    "Beauty salons near Los Angeles",
                    "Spas in San Francisco"
                ]
            ),
            AgentCapability(
                name="find_providers",
                description="Find providers for specific treatments",
                input_schema={
                    "treatment": "string",
                    "location": "string",
                    "limit": "int (optional)"
                },
                output_schema={
                    "providers": "list",
                    "count": "int"
                },
                examples=[
                    "Find Botox providers in Miami",
                    "Where can I get Jeuveau in Chicago?"
                ]
            ),
            AgentCapability(
                name="business_details",
                description="Get detailed information about a specific business",
                input_schema={
                    "business_id": "string"
                },
                output_schema={
                    "business": "dict",
                    "reviews": "list"
                },
                examples=[
                    "Tell me more about [business name]",
                    "Get reviews for [business]"
                ]
            )
        ]

        # Set up A2A communication
        self._setup_a2a(
            agent_id=agent_id,
            agent_type="business_specialist",
            capabilities=capabilities
        )

        logger.info(f"BusinessAgentA2A initialized with ID: {agent_id}")

    async def _handle_request(self, message: A2AMessage) -> A2AMessage:
        """
        Handle A2A request messages.
        Processes requests from other agents for business information.
        """
        task = message.content.get("task")
        parameters = message.content.get("parameters", {})
        context = message.content.get("context", {})

        logger.info(f"BusinessAgent handling request: {task}")

        try:
            if task == "business_search":
                # Handle business search request
                query = parameters.get("query", "")
                location = parameters.get("location", "")
                service_type = parameters.get("service_type")
                limit = parameters.get("limit", 5)

                # Build full query
                full_query = f"{service_type or query} in {location}" if location else query

                # Use existing search functionality
                response_text = await self.run(full_query)

                return create_response_message(
                    sender=self.agent_id,
                    recipient=message.sender,
                    success=True,
                    data={
                        "response": response_text,
                        "query": query,
                        "location": location
                    },
                    reply_to=message.message_id,
                    conversation_id=message.conversation_id or ""
                )

            elif task == "find_providers":
                # Handle provider search request
                treatment = parameters.get("treatment", "")
                location = parameters.get("location", "")
                limit = parameters.get("limit", 5)

                # Extract product from context if available
                product_info = context.get("product_info", "")

                # Build query
                query = f"{treatment} providers in {location}"

                response_text = await self.run(query)

                # Add context from product agent if available
                if product_info:
                    response_text = f"Based on the product information:\n{product_info}\n\n{response_text}"

                return create_response_message(
                    sender=self.agent_id,
                    recipient=message.sender,
                    success=True,
                    data={
                        "response": response_text,
                        "treatment": treatment,
                        "location": location
                    },
                    reply_to=message.message_id,
                    conversation_id=message.conversation_id or ""
                )

            elif task == "business_details":
                # Handle business details request
                business_id = parameters.get("business_id")

                # This would require additional Yelp API calls
                # For now, return a placeholder
                return create_response_message(
                    sender=self.agent_id,
                    recipient=message.sender,
                    success=False,
                    data=None,
                    error="Business details not yet implemented",
                    reply_to=message.message_id,
                    conversation_id=message.conversation_id or ""
                )

            else:
                # Unknown task, call parent handler
                return await super()._handle_request(message)

        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            return create_response_message(
                sender=self.agent_id,
                recipient=message.sender,
                success=False,
                data=None,
                error=str(e),
                reply_to=message.message_id,
                conversation_id=message.conversation_id or ""
            )

    async def _handle_handoff(self, message: A2AMessage) -> A2AMessage:
        """
        Handle task handoffs from other agents.
        Accepts business/location queries handed off by the supervisor or product agent.
        """
        content = message.content
        user_message = content.get("user_message", "")
        context = content.get("context", {})
        reason = content.get("reason", "")

        logger.info(
            f"BusinessAgent received handoff from {message.sender}\n"
            f"Reason: {reason}\n"
            f"User query: {user_message}"
        )

        try:
            # Process the user message using existing logic
            response_text = await self.run(user_message)

            # Check if product information is in context
            product_info = context.get("product_info")
            if product_info:
                # Combine product info with business results
                response_text = f"**Product Information:**\n{product_info}\n\n**Local Providers:**\n{response_text}"

            return create_response_message(
                sender=self.agent_id,
                recipient=message.sender,
                success=True,
                data={
                    "response": response_text,
                    "handled": True
                },
                reply_to=message.message_id,
                conversation_id=message.conversation_id or ""
            )

        except Exception as e:
            logger.error(f"Error handling handoff: {e}", exc_info=True)
            return create_response_message(
                sender=self.agent_id,
                recipient=message.sender,
                success=False,
                data=None,
                error=str(e),
                reply_to=message.message_id,
                conversation_id=message.conversation_id or ""
            )

    async def collaborate_with_product_agent(
        self,
        user_message: str,
        location: str,
        conversation_id: str
    ) -> Optional[str]:
        """
        Collaborate with ProductAgent to provide complete response.

        Args:
            user_message: Original user message
            location: Location for business search
            conversation_id: Conversation ID

        Returns:
            Combined response from both agents
        """
        try:
            # First get product information
            product_response = await self.send_request(
                recipient="product_agent",
                task="product_search",
                parameters={"query": user_message},
                context={"needs_location": True},
                wait_for_response=True
            )

            if product_response and product_response.content.get("success"):
                product_info = product_response.content.get("data", {}).get("formatted_response", "")

                # Then get business results
                business_query = f"{user_message} in {location}"
                business_response = await self.run(business_query)

                # Combine responses
                return f"**Product Information:**\n{product_info}\n\n**Local Providers:**\n{business_response}"

            # If no product info, just return business results
            return await self.run(user_message)

        except Exception as e:
            logger.error(f"Error collaborating with product agent: {e}")
            return await self.run(user_message)
