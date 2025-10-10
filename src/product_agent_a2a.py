"""
Enhanced Product Agent with A2A Communication
Extends ProductAgent with agent-to-agent communication capabilities.
"""

from typing import Optional, Dict, Any
from langchain_core.language_models.chat_models import BaseChatModel
from .product_agent import ProductAgent
from .a2a_agent_mixin import A2AAgentMixin
from .a2a_protocol import (
    A2AMessage,
    AgentCapability,
    MessageType,
    create_response_message
)
import logging


logger = logging.getLogger(__name__)


class ProductAgentA2A(ProductAgent, A2AAgentMixin):
    """
    Product Agent with A2A capabilities.
    Can communicate with other agents and handle inter-agent requests.
    """

    def __init__(self, llm: BaseChatModel, agent_id: str = "product_agent"):
        """
        Initialize Product Agent with A2A capabilities.

        Args:
            llm: Language model for processing
            agent_id: Unique identifier for this agent
        """
        # Initialize base ProductAgent
        ProductAgent.__init__(self, llm)

        # Define capabilities
        capabilities = [
            AgentCapability(
                name="product_search",
                description="Search for aesthetic product information (Botox, Evolus)",
                input_schema={
                    "query": "string",
                    "brand": "string (optional)",
                    "limit": "int (optional)"
                },
                output_schema={
                    "products": "list",
                    "formatted_response": "string"
                },
                examples=[
                    "What is Botox?",
                    "Tell me about Evolus Jeuveau",
                    "Compare Botox and Evolus"
                ]
            ),
            AgentCapability(
                name="product_comparison",
                description="Compare two or more aesthetic products",
                input_schema={
                    "products": "list of product names",
                    "criteria": "list of comparison criteria (optional)"
                },
                output_schema={
                    "comparison": "dict",
                    "summary": "string"
                },
                examples=[
                    "Compare Botox vs Evolus",
                    "What are the differences between Botox and Jeuveau?"
                ]
            ),
            AgentCapability(
                name="treatment_info",
                description="Provide information about treatment areas and uses",
                input_schema={
                    "treatment_area": "string",
                    "product": "string (optional)"
                },
                output_schema={
                    "information": "string",
                    "recommended_products": "list"
                },
                examples=[
                    "What treatments are available for forehead lines?",
                    "Tell me about crow's feet treatment"
                ]
            )
        ]

        # Set up A2A communication
        self._setup_a2a(
            agent_id=agent_id,
            agent_type="product_specialist",
            capabilities=capabilities
        )

        logger.info(f"ProductAgentA2A initialized with ID: {agent_id}")

    async def _handle_request(self, message: A2AMessage) -> A2AMessage:
        """
        Handle A2A request messages.
        Processes requests from other agents for product information.
        """
        task = message.content.get("task")
        parameters = message.content.get("parameters", {})
        context = message.content.get("context", {})

        logger.info(f"ProductAgent handling request: {task}")

        try:
            if task == "product_search":
                # Handle product search request
                query = parameters.get("query", "")
                brand = parameters.get("brand")
                limit = parameters.get("limit", 3)

                # Use existing search functionality
                results = self.rag_system.search_products(query, k=limit, filter_brand=brand)

                # Format response
                response_text = await self.run_async(query)

                return create_response_message(
                    sender=self.agent_id,
                    recipient=message.sender,
                    success=True,
                    data={
                        "results": results,
                        "formatted_response": response_text,
                        "query": query
                    },
                    reply_to=message.message_id,
                    conversation_id=message.conversation_id or ""
                )

            elif task == "product_comparison":
                # Handle product comparison request
                products = parameters.get("products", [])
                query = f"Compare {' vs '.join(products)}"

                response_text = await self.run_async(query)

                return create_response_message(
                    sender=self.agent_id,
                    recipient=message.sender,
                    success=True,
                    data={
                        "comparison": response_text,
                        "products": products
                    },
                    reply_to=message.message_id,
                    conversation_id=message.conversation_id or ""
                )

            elif task == "treatment_info":
                # Handle treatment information request
                treatment_area = parameters.get("treatment_area", "")
                product = parameters.get("product")

                if not self.rag_system.vector_store:
                    await self._ensure_indexed()

                # Search for treatment information
                results = self.rag_system.search_aesthetic_treatments(
                    treatment_area=treatment_area,
                    k=3
                )

                return create_response_message(
                    sender=self.agent_id,
                    recipient=message.sender,
                    success=True,
                    data={
                        "treatment_area": treatment_area,
                        "results": results,
                        "count": len(results)
                    },
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
        Accepts product-related queries handed off by the supervisor or business agent.
        """
        content = message.content
        user_message = content.get("user_message", "")
        context = content.get("context", {})
        reason = content.get("reason", "")

        logger.info(
            f"ProductAgent received handoff from {message.sender}\n"
            f"Reason: {reason}\n"
            f"User query: {user_message}"
        )

        try:
            # Process the user message using existing logic
            response_text = await self.run_async(user_message)

            # Check if we need to hand off to BusinessAgent for location search
            if self._needs_business_agent(user_message, context):
                logger.info("ProductAgent detected need for business search, will suggest handoff")
                response_text += "\n\n💡 Would you like me to help you find local providers for these treatments?"

            return create_response_message(
                sender=self.agent_id,
                recipient=message.sender,
                success=True,
                data={
                    "response": response_text,
                    "handled": True,
                    "needs_followup": self._needs_business_agent(user_message, context)
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

    def _needs_business_agent(self, query: str, context: Dict[str, Any]) -> bool:
        """Check if query needs business agent help."""
        location_keywords = ["near", "in", "find", "location", "where", "provider", "clinic"]
        return any(keyword in query.lower() for keyword in location_keywords)

    async def collaborate_with_business_agent(
        self,
        user_message: str,
        product_info: str,
        conversation_id: str
    ) -> Optional[str]:
        """
        Collaborate with BusinessAgent to provide complete response.

        Args:
            user_message: Original user message
            product_info: Product information gathered
            conversation_id: Conversation ID

        Returns:
            Combined response from both agents
        """
        try:
            # Send request to business agent
            response = await self.handoff_to_agent(
                recipient="business_agent",
                task="find_providers",
                user_message=user_message,
                context={"product_info": product_info},
                reason="User needs provider locations after product information",
                conversation_id=conversation_id
            )

            if response and response.content.get("success"):
                business_response = response.content.get("data", {}).get("response", "")
                return f"{product_info}\n\n{business_response}"

            return product_info

        except Exception as e:
            logger.error(f"Error collaborating with business agent: {e}")
            return product_info
