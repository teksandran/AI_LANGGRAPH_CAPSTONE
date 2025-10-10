import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.langgraph_agent import BeautySearchAgent


@pytest.fixture
def mock_openai():
    with patch("src.langgraph_agent.ChatOpenAI") as mock:
        instance = MagicMock()
        mock.return_value = instance
        yield instance


@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent initialization"""
    
    with patch("src.langgraph_agent.initialize_tools"):
        with patch("src.langgraph_agent.ChatOpenAI") as mock_llm:
            agent = BeautySearchAgent(
                yelp_api_key="test_key",
                llm_provider="openai"
            )
            
            assert agent.llm is not None
            assert agent.graph is not None
            assert len(agent.tools) == 4


@pytest.mark.asyncio
async def test_agent_should_continue():
    """Test should_continue decision logic"""
    
    with patch("src.langgraph_agent.initialize_tools"):
        with patch("src.langgraph_agent.ChatOpenAI"):
            agent = BeautySearchAgent(
                yelp_api_key="test_key",
                llm_provider="openai"
            )
            
            # Test with tool calls
            state_with_tools = {
                "messages": [
                    MagicMock(tool_calls=[{"name": "search"}])
                ]
            }
            assert agent._should_continue(state_with_tools) == "continue"
            
            # Test without tool calls
            state_no_tools = {
                "messages": [
                    MagicMock(tool_calls=[])
                ]
            }
            assert agent._should_continue(state_no_tools) == "end"
