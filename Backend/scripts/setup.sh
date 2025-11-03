
#!/bin/bash

echo "================================"
echo "Yelp MCP LangGraph Setup"
echo "================================"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "\nCreating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "\nUpgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "\nInstalling dependencies..."
pip install -r requirements.txt

# Copy env file if it doesn't exist
if [ ! -f .env ]; then
    echo "\nCreating .env file..."
    cp .env.example .env
    echo "Please edit .env and add your API keys"
fi

echo "\n================================"
echo "Setup complete!"
echo "================================"
echo "\nNext steps:"
echo "1. Edit .env and add your YELP_API_KEY"
echo "2. (Optional) Add OPENAI_API_KEY or ANTHROPIC_API_KEY"
echo "3. Run: source venv/bin/activate"
echo "4. Run examples: python examples/basic_search.py"