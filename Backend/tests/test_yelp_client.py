import pytest
from unittest.mock import AsyncMock, patch
from src.yelp_client import YelpClient
from src.config import YelpConfig


@pytest.fixture
def yelp_config():
    return YelpConfig(api_key="test_key")


@pytest.fixture
def yelp_client(yelp_config):
    return YelpClient(yelp_config)


@pytest.mark.asyncio
async def test_search_businesses(yelp_client):
    """Test business search"""
    
    mock_response = {
        "businesses": [
            {
                "id": "test-business-1",
                "name": "Test Salon",
                "rating": 4.5,
                "review_count": 100,
                "location": {"display_address": ["123 Main St", "New York, NY"]},
                "categories": [{"title": "Hair Salon"}]
            }
        ]
    }
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.raise_for_status = AsyncMock()
        
        result = await yelp_client.search_businesses(
            term="beauty salon",
            location="New York, NY"
        )
        
        assert "businesses" in result
        assert len(result["businesses"]) == 1
        assert result["businesses"][0]["name"] == "Test Salon"


@pytest.mark.asyncio
async def test_get_business_details(yelp_client):
    """Test getting business details"""
    
    mock_response = {
        "id": "test-business-1",
        "name": "Test Salon",
        "rating": 4.5,
        "display_phone": "(123) 456-7890",
        "location": {"display_address": ["123 Main St"]}
    }
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.raise_for_status = AsyncMock()
        
        result = await yelp_client.get_business_details("test-business-1")
        
        assert result["name"] == "Test Salon"
        assert result["rating"] == 4.5


def test_format_business_result(yelp_client):
    """Test business result formatting"""
    
    business = {
        "id": "test-1",
        "name": "Test Salon",
        "rating": 4.5,
        "review_count": 100,
        "price": "$",
        "location": {"display_address": ["123 Main St", "New York, NY"]},
        "categories": [{"title": "Hair Salon"}, {"title": "Spa"}],
        "url": "https://yelp.com/test"
    }
    
    formatted = yelp_client.format_business_result(business)
    
    assert formatted["name"] == "Test Salon"
    assert formatted["rating"] == 4.5
    assert formatted["price"] == "$"
    assert "Hair Salon" in formatted["categories"]
    assert "123 Main St, New York, NY" == formatted["address"]
