
import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.mcp_server import YelpMCPServer

load_dotenv()


async def main():
    """Start the MCP server"""
    
    api_key = os.getenv("YELP_API_KEY")
    if not api_key:
        print("Error: YELP_API_KEY not found in environment")
        return
    
    print("=" * 60)
    print("STARTING YELP MCP SERVER")
    print("=" * 60)
    print("\nThe server will communicate via stdio (standard input/output)")
    print("Connect this server to Claude Desktop or other MCP clients\n")
    
    server = YelpMCPServer(api_key)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())

