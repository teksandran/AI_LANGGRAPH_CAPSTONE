"""
Business Agent - Specialized agent for finding and managing business queries.
Handles Yelp searches for salons, spas, and beauty service providers.
"""

from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
from .yelp_client import YelpClient
from .config import YelpConfig, BEAUTY_CATEGORIES


class BusinessAgent:
    """Specialized agent for business/location queries."""

    def __init__(self, yelp_api_key: str, llm: BaseChatModel):
        self.llm = llm
        config = YelpConfig(api_key=yelp_api_key)
        self.yelp_client = YelpClient(config)

    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location from query."""
        # Simple location extraction
        location_indicators = ["in ", "near ", "at ", "around "]

        for indicator in location_indicators:
            if indicator in query.lower():
                parts = query.lower().split(indicator)
                if len(parts) > 1:
                    location = parts[1].split()[0:3]  # Get next 2-3 words
                    return " ".join(location).strip(".,?!")

        return None

    def _extract_service_type(self, query: str) -> str:
        """Extract service type from query."""
        query_lower = query.lower()

        if "botox" in query_lower or "injection" in query_lower:
            return "botox injections"
        elif "salon" in query_lower or "hair" in query_lower:
            return "hair salon"
        elif "spa" in query_lower or "massage" in query_lower:
            return "spa"
        elif "nail" in query_lower or "manicure" in query_lower:
            return "nail salon"
        elif "eyelash" in query_lower or "lash" in query_lower:
            return "eyelash salon"
        else:
            return "beauty salon"

    async def run(self, query: str) -> str:
        """Process business search query."""

        # Extract location
        location = self._extract_location(query)

        if not location:
            return "I'd be happy to help you find beauty services! Could you please specify a location? For example: 'Find Botox providers in New York' or 'Beauty salons near Los Angeles'"

        # Extract service type
        service_type = self._extract_service_type(query)

        try:
            # Search businesses
            results = await self.yelp_client.search_businesses(
                term=service_type,
                location=location,
                categories=BEAUTY_CATEGORIES.get("salons", []),
                limit=5
            )

            businesses = results.get("businesses", [])

            if not businesses:
                return f"I couldn't find any {service_type} in {location}. Try a different location or service type."

            # Format response
            response_parts = [f"**Found {len(businesses)} {service_type} in {location}:**\n"]

            for i, biz in enumerate(businesses, 1):
                name = biz.get("name", "Unknown")
                rating = biz.get("rating", "N/A")
                review_count = biz.get("review_count", 0)
                price = biz.get("price", "$$")
                address = ", ".join(biz.get("location", {}).get("display_address", []))
                phone = biz.get("display_phone", "N/A")

                response_parts.append(f"\n**{i}. {name}**")
                response_parts.append(f"   Rating: {rating} ⭐ ({review_count} reviews)")
                response_parts.append(f"   Price: {price}")
                response_parts.append(f"   Address: {address}")
                response_parts.append(f"   Phone: {phone}")

            response_parts.append("\n💡 *Would you like more details or reviews for any of these businesses?*")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Sorry, I encountered an error searching for businesses: {str(e)}"
