
from typing import List, Dict, Any
import json
from mcp.server import Server
from mcp.types import Tool, TextContent
from .yelp_client import YelpClient
from .config import YelpConfig, BEAUTY_CATEGORIES


class YelpMCPServer:
    """MCP Server for Yelp API integration"""
    
    def __init__(self, api_key: str):
        self.config = YelpConfig(api_key=api_key)
        self.client = YelpClient(self.config)
        self.server = self._create_server()
    
    def _create_server(self) -> Server:
        """Create and configure MCP server"""
        server = Server("yelp-beauty-server")
        
        @server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available Yelp tools"""
            return [
                Tool(
                    name="search_beauty_salons",
                    description="Search for beauty salons, spas, and beauty services",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City, state, or zip code"
                            },
                            "service_type": {
                                "type": "string",
                                "description": "Type of service (hair salon, nail salon, spa)",
                                "default": "beauty salon"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of results (max 50)",
                                "default": 10
                            },
                            "price": {
                                "type": "string",
                                "description": "Price range: 1, 2, 3, 4"
                            },
                            "open_now": {
                                "type": "boolean",
                                "description": "Only show currently open businesses",
                                "default": False
                            }
                        },
                        "required": ["location"]
                    }
                ),
                Tool(
                    name="search_beauty_products",
                    description="Search for beauty and aesthetics product stores",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City, state, or zip code"
                            },
                            "product_type": {
                                "type": "string",
                                "description": "Type (cosmetics, skincare, makeup)",
                                "default": "beauty products"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of results",
                                "default": 10
                            }
                        },
                        "required": ["location"]
                    }
                ),
                Tool(
                    name="get_salon_details",
                    description="Get detailed information about a business",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "business_id": {
                                "type": "string",
                                "description": "Yelp business ID"
                            }
                        },
                        "required": ["business_id"]
                    }
                ),
                Tool(
                    name="get_salon_reviews",
                    description="Get customer reviews for a business",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "business_id": {
                                "type": "string",
                                "description": "Yelp business ID"
                            }
                        },
                        "required": ["business_id"]
                    }
                )
            ]
        
        @server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "search_beauty_salons":
                    result = await self.client.search_businesses(
                        term=arguments.get("service_type", "beauty salon"),
                        location=arguments["location"],
                        categories=BEAUTY_CATEGORIES["salons"],
                        limit=arguments.get("limit", 10),
                        price=arguments.get("price"),
                        open_now=arguments.get("open_now", False)
                    )
                    
                elif name == "search_beauty_products":
                    result = await self.client.search_businesses(
                        term=arguments.get("product_type", "beauty products"),
                        location=arguments["location"],
                        categories=BEAUTY_CATEGORIES["products"],
                        limit=arguments.get("limit", 10)
                    )
                    
                elif name == "get_salon_details":
                    result = await self.client.get_business_details(
                        arguments["business_id"]
                    )
                    
                elif name == "get_salon_reviews":
                    result = await self.client.get_business_reviews(
                        arguments["business_id"]
                    )
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
        
        return server
    
    async def run(self):
        """Run the MCP server"""
        import mcp.server.stdio
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )