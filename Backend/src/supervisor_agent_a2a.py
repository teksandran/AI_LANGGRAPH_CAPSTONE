"""
Enhanced Supervisor Agent with A2A Communication
Maintains backward compatibility with existing routing while adding A2A capabilities.
"""

from typing import Literal, Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import asyncio
import logging
from .supervisor_agent import SupervisorAgent
from .product_agent_a2a import ProductAgentA2A
from .business_agent_a2a import BusinessAgentA2A
from .a2a_agent_mixin import A2AAgentMixin
from .a2a_protocol import (
    AgentCapability,
    A2AMessage,
    MessageType,
    create_request_message
)
from .a2a_broker import get_broker


logger = logging.getLogger(__name__)


class SupervisorAgentA2A(SupervisorAgent, A2AAgentMixin):
    """
    Supervisor Agent with A2A capabilities.

    Features:
    - Maintains backward compatibility with existing routing
    - Adds direct agent-to-agent communication
    - Enables collaborative multi-agent workflows
    - Supports both centralized (supervisor-led) and decentralized (A2A) patterns
    """

    def __init__(
        self,
        yelp_api_key: str,
        llm_provider: Literal["openai", "anthropic"] = "openai",
        model: str = None,
        enable_a2a: bool = True,
        agent_id: str = "supervisor"
    ):
        """
        Initialize Supervisor Agent with optional A2A capabilities.

        Args:
            yelp_api_key: Yelp API key
            llm_provider: LLM provider to use
            model: Model name
            enable_a2a: Enable A2A communication (default: True)
            agent_id: Unique identifier for supervisor
        """
        self.yelp_api_key = yelp_api_key
        self.enable_a2a = enable_a2a

        # Initialize LLM (don't call super().__init__ to avoid double initialization)
        if llm_provider == "openai":
            self.llm = ChatOpenAI(
                model=model or "gpt-4o-mini",
                temperature=0.3
            )
        else:
            self.llm = ChatAnthropic(
                model=model or "claude-3-5-sonnet-20241022",
                temperature=0.3
            )

        # Initialize agents with A2A capabilities if enabled
        if enable_a2a:
            self.product_agent = ProductAgentA2A(llm=self.llm, agent_id="product_agent")
            self.business_agent = BusinessAgentA2A(
                yelp_api_key=yelp_api_key,
                llm=self.llm,
                agent_id="business_agent"
            )

            # Set up A2A for supervisor
            capabilities = [
                AgentCapability(
                    name="route_query",
                    description="Route user queries to appropriate specialized agents",
                    input_schema={
                        "query": "string",
                        "user_context": "dict (optional)"
                    },
                    output_schema={
                        "response": "string",
                        "agents_used": "list"
                    },
                    examples=[
                        "What is Botox and where can I get it in NYC?",
                        "Compare Botox and Evolus"
                    ]
                ),
                AgentCapability(
                    name="coordinate_agents",
                    description="Coordinate multiple agents for complex queries",
                    input_schema={
                        "query": "string",
                        "required_agents": "list"
                    },
                    output_schema={
                        "combined_response": "string",
                        "agent_contributions": "dict"
                    }
                )
            ]

            self._setup_a2a(
                agent_id=agent_id,
                agent_type="supervisor",
                capabilities=capabilities
            )

            logger.info("SupervisorAgentA2A initialized with A2A enabled")
        else:
            # Use regular agents without A2A
            from .product_agent import ProductAgent
            from .business_agent import BusinessAgent

            self.product_agent = ProductAgent(llm=self.llm)
            self.business_agent = BusinessAgent(yelp_api_key=yelp_api_key, llm=self.llm)

            logger.info("SupervisorAgentA2A initialized without A2A (backward compatible mode)")

        # Define available workers
        self.workers = ["product_agent", "business_agent", "FINISH"]

        # Build supervisor graph (from parent class)
        self.graph = self._build_graph()

    async def run_with_a2a(self, user_message: str) -> Dict[str, Any]:
        """
        Run query using A2A communication for agent collaboration.

        This method allows agents to communicate directly and collaborate,
        rather than just being routed sequentially by the supervisor.

        Args:
            user_message: User's query

        Returns:
            Dict with response and metadata about agent interactions
        """
        if not self.enable_a2a:
            # Fall back to regular run
            response = await self.run(user_message)
            return {
                "response": response,
                "method": "traditional_routing",
                "agents_used": []
            }

        logger.info(f"Processing with A2A: {user_message}")

        # Determine if this needs product info, business info, or both
        needs_product = self._needs_product_info(user_message)
        needs_business = self._needs_business_info(user_message)

        conversation_id = f"conv_{id(user_message)}"
        agents_used = []

        try:
            if needs_product and needs_business:
                # Complex query needing collaboration
                logger.info("Query needs both product and business info - coordinating agents")

                # Get product information first
                product_response = await self.product_agent.send_request(
                    recipient="product_agent",  # Self-request to trigger processing
                    task="product_search",
                    parameters={"query": user_message},
                    context={"needs_business": True},
                    wait_for_response=True
                )

                if product_response and product_response.content.get("success"):
                    product_info = product_response.content.get("data", {}).get("formatted_response", "")
                    agents_used.append("product_agent")

                    # Extract location if present
                    location = self._extract_location(user_message)
                    if location:
                        # Now collaborate with business agent
                        business_response = await self.product_agent.handoff_to_agent(
                            recipient="business_agent",
                            task="find_providers",
                            user_message=user_message,
                            context={"product_info": product_info},
                            reason="User needs provider locations after product information",
                            conversation_id=conversation_id
                        )

                        if business_response and business_response.content.get("success"):
                            agents_used.append("business_agent")
                            combined_response = business_response.content.get("data", {}).get("response", "")
                            return {
                                "response": combined_response,
                                "method": "a2a_collaboration",
                                "agents_used": agents_used,
                                "conversation_id": conversation_id
                            }

                    # No location, just return product info
                    return {
                        "response": product_info + "\n\n💡 *Would you like to find local providers? Please specify a location.*",
                        "method": "a2a_single_agent",
                        "agents_used": agents_used,
                        "conversation_id": conversation_id
                    }

            elif needs_product:
                # Just product information
                logger.info("Query needs product info only")
                response_text = await self.product_agent.run_async(user_message)
                agents_used.append("product_agent")

                return {
                    "response": response_text,
                    "method": "a2a_single_agent",
                    "agents_used": agents_used,
                    "conversation_id": conversation_id
                }

            elif needs_business:
                # Just business search
                logger.info("Query needs business info only")
                response_text = await self.business_agent.run(user_message)
                agents_used.append("business_agent")

                return {
                    "response": response_text,
                    "method": "a2a_single_agent",
                    "agents_used": agents_used,
                    "conversation_id": conversation_id
                }

            else:
                # Unclear - use traditional routing
                logger.info("Query unclear, falling back to traditional routing")
                response = await self.run(user_message)
                return {
                    "response": response,
                    "method": "traditional_routing_fallback",
                    "agents_used": agents_used,
                    "conversation_id": conversation_id
                }

        except Exception as e:
            logger.error(f"Error in A2A processing: {e}", exc_info=True)
            # Fall back to traditional routing
            response = await self.run(user_message)
            return {
                "response": response,
                "method": "traditional_routing_error_fallback",
                "agents_used": agents_used,
                "error": str(e)
            }

    def _needs_product_info(self, query: str) -> bool:
        """Determine if query needs product information."""
        product_keywords = [
            "botox", "evolus", "jeuveau", "filler", "neurotoxin",
            "what is", "tell me about", "compare", "difference",
            "treatment", "wrinkle", "line", "cosmetic"
        ]
        return any(keyword in query.lower() for keyword in product_keywords)

    def _needs_business_info(self, query: str) -> bool:
        """Determine if query needs business/location information."""
        business_keywords = [
            "find", "where", "near", "in", "location", "provider",
            "salon", "spa", "clinic", "doctor", "appointment"
        ]
        return any(keyword in query.lower() for keyword in business_keywords)

    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location from query."""
        location_indicators = ["in ", "near ", "at ", "around "]

        for indicator in location_indicators:
            if indicator in query.lower():
                parts = query.lower().split(indicator)
                if len(parts) > 1:
                    location = parts[1].split()[0:3]  # Get next 2-3 words
                    return " ".join(location).strip(".,?!")

        return None

    def get_a2a_statistics(self) -> Dict[str, Any]:
        """Get A2A broker statistics."""
        if not self.enable_a2a:
            return {"a2a_enabled": False}

        return {
            "a2a_enabled": True,
            **self.a2a_broker.get_statistics()
        }

    async def run(self, user_message: str) -> str:
        """
        Run using traditional routing (backward compatible).
        Maintains the original SupervisorAgent behavior.
        """
        # Call parent's run method
        return await super().run(user_message)
