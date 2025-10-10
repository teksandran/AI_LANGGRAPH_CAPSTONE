
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="yelp-mcp-langgraph",
    version="0.1.0",
    author="Your Name",
    description="Yelp MCP Server with LangGraph for beauty salon and product search",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "httpx>=0.27.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.7.0",
        "mcp>=0.9.0",
        "langgraph>=0.2.0",
        "langchain>=0.3.0",
        "langchain-core>=0.3.0",
    ],
    extras_require={
        "openai": ["langchain-openai>=0.2.0"],
        "anthropic": ["langchain-anthropic>=0.2.0"],
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
            "black>=24.0.0",
            "ruff>=0.4.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)