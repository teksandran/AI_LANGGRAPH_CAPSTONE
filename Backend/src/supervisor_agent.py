"""
Supervisor Agent - Coordinates between specialized sub-agents.
Routes queries to appropriate specialized agents and synthesizes responses.
"""

from typing import List, Dict, Any, Literal, Annotated, Sequence
from typing_extensions import TypedDict
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class SupervisorState(TypedDict):
    """State for the supervisor agent"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_worker: str
    final_response: str


class SupervisorAgent:
    """
    Supervisor agent that coordinates between specialized workers:
    - ProductAgent: Handles product information (Botox, Evolus)
    - BusinessAgent: Handles business search (Yelp)
    """

    def __init__(
        self,
        yelp_api_key: str,
        llm_provider: Literal["openai", "anthropic"] = "openai",
        model: str = None
    ):
        self.yelp_api_key = yelp_api_key

        # Initialize LLM
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

        # Import worker agents
        from .product_agent import ProductAgent
        from .business_agent import BusinessAgent

        # Initialize specialized workers
        self.product_agent = ProductAgent(llm=self.llm)
        self.business_agent = BusinessAgent(yelp_api_key=yelp_api_key, llm=self.llm)

        # Define available workers
        self.workers = ["product_agent", "business_agent", "FINISH"]

        # Build supervisor graph
        self.graph = self._build_graph()

    def _create_supervisor_prompt(self) -> ChatPromptTemplate:
        """Create the supervisor routing prompt."""

        system_prompt = """You are a supervisor managing two specialized agents:

1. PRODUCT_AGENT: Handles queries about aesthetic products (Botox, Evolus, Jeuveau)
   - Product information, descriptions, uses
   - Treatment areas and benefits
   - Comparisons between products

2. BUSINESS_AGENT: Handles queries about finding businesses
   - Finding salons, spas, providers
   - Business details and reviews
   - Location-based searches

Your job is to route the user's question to the appropriate agent or finish if the task is complete.

Given the conversation, decide which agent should act next, or FINISH if no more work is needed.

Workers available: {workers}

Respond with ONLY the name of the next worker (product_agent, business_agent, or FINISH)."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            ("system", "Who should act next? Respond with: product_agent, business_agent, or FINISH")
        ])

        return prompt

    def _supervisor_node(self, state: SupervisorState) -> SupervisorState:
        """Supervisor decision node - routes to appropriate worker."""

        prompt = self._create_supervisor_prompt()

        # Format the prompt with workers and messages
        formatted = prompt.format_messages(
            workers=", ".join(self.workers),
            messages=state["messages"]
        )

        # Get routing decision from LLM
        response = self.llm.invoke(formatted)
        decision = response.content.strip().lower()

        # Validate decision
        if decision not in [w.lower() for w in self.workers]:
            decision = "finish"

        return {
            "next_worker": decision,
            "messages": []
        }

    async def _product_agent_node(self, state: SupervisorState) -> SupervisorState:
        """Execute product agent."""

        # Get last user message
        user_message = None
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                user_message = msg.content
                break

        if not user_message:
            return {"messages": [AIMessage(content="No query found.")]}

        # Call product agent (ensure async compatible)
        response = await self.product_agent.run_async(user_message)

        return {
            "messages": [AIMessage(content=response, name="ProductAgent")],
            "next_worker": "finish"  # Changed from "supervisor" to "finish"
        }

    async def _business_agent_node(self, state: SupervisorState) -> SupervisorState:
        """Execute business agent."""

        # Get last user message
        user_message = None
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                user_message = msg.content
                break

        if not user_message:
            return {"messages": [AIMessage(content="No query found.")]}

        # Call business agent
        response = await self.business_agent.run(user_message)

        return {
            "messages": [AIMessage(content=response, name="BusinessAgent")],
            "next_worker": "finish"  # Changed from "supervisor" to "finish"
        }

    def _route_supervisor(self, state: SupervisorState) -> str:
        """Route based on supervisor's decision."""

        next_worker = state.get("next_worker", "finish")

        if next_worker == "product_agent":
            return "product_agent"
        elif next_worker == "business_agent":
            return "business_agent"
        else:
            return "finish"

    def _build_graph(self) -> StateGraph:
        """Build the supervisor workflow graph."""

        workflow = StateGraph(SupervisorState)

        # Add nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("product_agent", self._product_agent_node)
        workflow.add_node("business_agent", self._business_agent_node)

        # Set entry point
        workflow.set_entry_point("supervisor")

        # Add conditional routing from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self._route_supervisor,
            {
                "product_agent": "product_agent",
                "business_agent": "business_agent",
                "finish": END
            }
        )

        # Workers now route to finish node with conditional routing
        def worker_route(state: SupervisorState) -> str:
            return state.get("next_worker", "finish")

        workflow.add_conditional_edges(
            "product_agent",
            worker_route,
            {"finish": END}
        )

        workflow.add_conditional_edges(
            "business_agent",
            worker_route,
            {"finish": END}
        )

        return workflow.compile()

    async def run(self, user_message: str) -> str:
        """Run the supervisor agent with a user message."""

        initial_state = {
            "messages": [HumanMessage(content=user_message)],
            "next_worker": "",
            "final_response": ""
        }

        result = await self.graph.ainvoke(initial_state)

        # Get the last AI message
        for message in reversed(result["messages"]):
            if isinstance(message, AIMessage):
                return message.content

        return "I couldn't process that request."
