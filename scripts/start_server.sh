
#!/bin/bash

echo "================================"
echo "Starting Yelp MCP Server"
echo "================================"

# Activate virtual environment
source venv/bin/activate

# Check for API key
if [ -z "$YELP_API_KEY" ]; then
    echo "Error: YELP_API_KEY not set"
    echo "Please set it in .env file or export it"
    exit 1
fi

# Start server
echo "Starting MCP server..."
python examples/mcp_server_example.py