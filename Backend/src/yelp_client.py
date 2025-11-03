
from typing import Dict, Any, Optional, List
import httpx
from .config import YelpConfig


class YelpClient:
    """Client for interacting with Yelp Fusion API"""
    
    def __init__(self, config: YelpConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "accept": "application/json"
        }
    
    async def search_businesses(
        self,
        term: str,
        location: str,
        categories: Optional[str] = None,
        limit: int = 10,
        price: Optional[str] = None,
        open_now: bool = False,
        sort_by: str = "best_match"
    ) -> Dict[str, Any]:
        """
        Search for businesses on Yelp
        
        Args:
            term: Search term (e.g., "beauty salon")
            location: Location to search (city, state, or zip)
            categories: Comma-separated category filters
            limit: Number of results (max 50)
            price: Price filter (1, 2, 3, 4 for $, $$, $$$, $$$$)
            open_now: Filter for currently open businesses
            sort_by: Sort results by best_match, rating, review_count, or distance
        
        Returns:
            Dictionary containing search results
        """
        params = {
            "term": term,
            "location": location,
            "limit": min(limit, 50),
            "sort_by": sort_by,
            "open_now": open_now
        }
        
        if categories:
            params["categories"] = categories
        if price:
            params["price"] = price
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.config.base_url}/businesses/search",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    async def get_business_details(self, business_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific business
        
        Args:
            business_id: Yelp business ID
        
        Returns:
            Dictionary containing business details
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.config.base_url}/businesses/{business_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_business_reviews(
        self,
        business_id: str,
        locale: str = "en_US",
        limit: int = 3
    ) -> Dict[str, Any]:
        """
        Get reviews for a specific business
        
        Args:
            business_id: Yelp business ID
            locale: Locale for reviews
            limit: Number of reviews to return (max 3)
        
        Returns:
            Dictionary containing reviews
        """
        params = {
            "locale": locale,
            "limit": min(limit, 3)
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.config.base_url}/businesses/{business_id}/reviews",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    def format_business_result(self, business: Dict[str, Any]) -> Dict[str, Any]:
        """Format a business result for display"""
        return {
            "id": business.get("id"),
            "name": business.get("name"),
            "rating": business.get("rating"),
            "review_count": business.get("review_count"),
            "price": business.get("price", "N/A"),
            "phone": business.get("phone", "N/A"),
            "address": ", ".join(business.get("location", {}).get("display_address", [])),
            "categories": [cat["title"] for cat in business.get("categories", [])],
            "url": business.get("url"),
            "image_url": business.get("image_url"),
        }