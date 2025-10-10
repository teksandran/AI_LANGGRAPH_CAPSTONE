import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.langgraph_agent import BeautySearchAgent

load_dotenv()


async def main():
    """LangGraph agent examples"""
    
    # Check for required API keys
    yelp_key = os.getenv("YELP_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not yelp_key:
        print("Error: YELP_API_KEY not found in environment")
        return
    
    # Choose LLM provider based on available keys
    if openai_key:
        print("Using OpenAI GPT-4...")
        agent = BeautySearchAgent(
            yelp_api_key=yelp_key,
            llm_provider="openai"
        )
    elif anthropic_key:
        print("Using Anthropic Claude...")
        agent = BeautySearchAgent(
            yelp_api_key=yelp_key,
            llm_provider="anthropic"
        )
    else:
        print("Error: No LLM API key found (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
        return
    
    print("=" * 60)
    print("LANGGRAPH AGENT EXAMPLES")
    print("=" * 60)
    
    # Example 1: Simple search
    print("\n1. Simple beauty salon search:")
    print("-" * 60)
    response = await agent.run(
        "Find me the top-rated hair salons in San Francisco"
    )
    print(response)
    
    # Example 2: Product search
    print("\n" + "=" * 60)
    print("\n2. Beauty product search:")
    print("-" * 60)
    response = await agent.run(
        "Where can I buy high-end skincare products in Manhattan?"
    )
    print(response)
    
    # Example 3: Specific service
    print("\n" + "=" * 60)
    print("\n3. Specific service search:")
    print("-" * 60)
    response = await agent.run(
        "I need a nail salon in Chicago that's open now"
    )
    print(response)
    
    print("\n" + "=" * 60)
    print("Done!")


async def interactive_mode():
    """Interactive chat mode"""
    
    yelp_key = os.getenv("YELP_API_KEY")
    if not yelp_key:
        print("Error: YELP_API_KEY not found")
        return
    
    # Initialize agent
    llm_provider = "openai" if os.getenv("OPENAI_API_KEY") else "anthropic"
    agent = BeautySearchAgent(
        yelp_api_key=yelp_key,
        llm_provider=llm_provider
    )
    
    print("=" * 60)
    print("INTERACTIVE BEAUTY SEARCH AGENT")
    print("=" * 60)
    print("Ask me about beauty salons, spas, or product stores!")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        print("\nAgent: ", end="", flush=True)
        response = await agent.run(user_input)
        print(response + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(main())
