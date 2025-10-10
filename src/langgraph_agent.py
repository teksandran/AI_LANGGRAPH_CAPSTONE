
from typing import List, Dict, Any, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from .tools import (
    search_beauty_salons,
    search_beauty_products,
    get_business_details,
    get_business_reviews,
    index_product_websites,
    search_product_information,
    get_indexed_products_summary,
    initialize_tools
)


class AgentState(TypedDict):
    """State for the conversational agent"""
    messages: List[HumanMessage | AIMessage | SystemMessage]


class BeautySearchAgent:
    """Intelligent agent for beauty salon and product search"""
    
    def __init__(
        self,
        yelp_api_key: str,
        llm_provider: Literal["openai", "anthropic"] = "openai",
        model: str = None
    ):
        # Initialize tools
        initialize_tools(yelp_api_key)
        
        # Initialize LLM
        if llm_provider == "openai":
            self.llm = ChatOpenAI(
                model=model or "gpt-4o",
                temperature=0.7
            )
        else:
            self.llm = ChatAnthropic(
                model=model or "claude-sonnet-4-5-20250929",
                temperature=0.7
            )
        
        # Define tools
        self.tools = [
            search_beauty_salons,
            search_beauty_products,
            get_business_details,
            get_business_reviews,
            index_product_websites,
            search_product_information,
            get_indexed_products_summary
        ]
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the agent workflow graph"""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def _call_model(self, state: AgentState) -> AgentState:
        """Call the LLM with current state"""
        
        system_message = SystemMessage(content="""You are a helpful assistant specializing in beauty salons, spas, and aesthetic products including Botox and Evolus (Jeuveau).

IMPORTANT TOOL USAGE RULES:

1. PRODUCT INFORMATION QUERIES (Botox, Evolus, Jeuveau, cosmetic treatments):
   When users ask "What is X?", "Tell me about X", "Compare X and Y", or mention product names:

   Step 1: Check if data is indexed
   - Use get_indexed_products_summary() to check existing data

   Step 2: Index if needed
   - If no data exists, call index_product_websites() FIRST

   Step 3: Search for information
   - Use search_product_information(query="user's question", brand=None, limit=5)
   - For brand-specific queries, set brand="botox" or brand="evolus"

   Step 4: Provide detailed response with:
   - Product description and what it is
   - FDA-approved uses and indications
   - Treatment areas (forehead, frown lines, crow's feet)
   - Product type (injectable neurotoxin, etc.)
   - Benefits and expected results
   - Suggest finding local providers

2. BUSINESS/LOCATION QUERIES (salons, spas, providers):
   When users ask "Where can I get X?", "Find salons near me", or mention locations:
   - Use search_beauty_salons(location, service_type, limit)
   - Use get_business_details(business_id) for specific businesses
   - Use get_business_reviews(business_id) for reviews
   - Ask for location if not provided

EXAMPLES:
- "What is Botox?" → Use search_product_information(query="Botox uses benefits", limit=3)
- "Compare Botox and Evolus" → Use search_product_information twice with brand filters
- "Find Botox in NYC" → Use search_beauty_salons(location="New York, NY", service_type="botox")
- "Differences between products" → Use search_product_information with both brand names

Always provide comprehensive, accurate information from the tools.""")
        
        messages = [system_message] + state["messages"]
        response = self.llm_with_tools.invoke(messages)
        
        return {"messages": [response]}
    
    def _should_continue(self, state: AgentState) -> Literal["continue", "end"]:
        """Decide whether to continue with tools or end"""
        
        last_message = state["messages"][-1]
        
        # If there are tool calls, continue
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        
        return "end"
    
    async def run(self, user_message: str) -> str:
        """Run the agent with a user message"""
        
        initial_state = {
            "messages": [HumanMessage(content=user_message)]
        }
        
        result = await self.graph.ainvoke(initial_state)
        
        # Get the last AI message
        for message in reversed(result["messages"]):
            if isinstance(message, AIMessage):
                return message.content
        
        return "I couldn't process that request."
    
    def stream(self, user_message: str):
        """Stream the agent's response"""
        
        initial_state = {
            "messages": [HumanMessage(content=user_message)]
        }
        
        return self.graph.stream(initial_state)
