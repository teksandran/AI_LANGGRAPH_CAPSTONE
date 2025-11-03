from typing import Optional
import json
from langchain_core.tools import tool
from .yelp_client import YelpClient
from .config import YelpConfig, BEAUTY_CATEGORIES
from .rag_system import get_rag_system


# Initialize global client (will be set in main)
_yelp_client: Optional[YelpClient] = None


def initialize_tools(api_key: str):
    """Initialize the Yelp client for tools"""
    global _yelp_client
    config = YelpConfig(api_key=api_key)
    _yelp_client = YelpClient(config)


@tool
async def search_beauty_salons(
    location: str,
    service_type: str = "beauty salon",
    limit: int = 5
) -> str:
    """
    Search for beauty salons, spas, and beauty service providers.
    
    Args:
        location: City, state, or zip code to search in
        service_type: Type of service (hair salon, nail salon, spa, eyelash)
        limit: Maximum number of results (default 5)
    
    Returns:
        JSON string with search results
    """
    if not _yelp_client:
        return json.dumps({"error": "Yelp client not initialized"})
    
    try:
        results = await _yelp_client.search_businesses(
            term=service_type,
            location=location,
            categories=BEAUTY_CATEGORIES["salons"],
            limit=limit
        )
        
        businesses = [
            _yelp_client.format_business_result(biz)
            for biz in results.get("businesses", [])
        ]
        
        return json.dumps({
            "total": len(businesses),
            "businesses": businesses
        }, indent=2)
    
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
async def search_beauty_products(
    location: str,
    product_type: str = "beauty products",
    limit: int = 5
) -> str:
    """
    Search for stores selling beauty and aesthetics products.
    
    Args:
        location: City, state, or zip code
        product_type: Type of products (cosmetics, skincare, makeup, perfume)
        limit: Maximum number of results (default 5)
    
    Returns:
        JSON string with search results
    """
    if not _yelp_client:
        return json.dumps({"error": "Yelp client not initialized"})
    
    try:
        results = await _yelp_client.search_businesses(
            term=product_type,
            location=location,
            categories=BEAUTY_CATEGORIES["products"],
            limit=limit
        )
        
        businesses = [
            _yelp_client.format_business_result(biz)
            for biz in results.get("businesses", [])
        ]
        
        return json.dumps({
            "total": len(businesses),
            "businesses": businesses
        }, indent=2)
    
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
async def get_business_details(business_id: str) -> str:
    """
    Get detailed information about a specific business.
    
    Args:
        business_id: The Yelp business ID
    
    Returns:
        JSON string with detailed business information
    """
    if not _yelp_client:
        return json.dumps({"error": "Yelp client not initialized"})
    
    try:
        details = await _yelp_client.get_business_details(business_id)
        
        formatted = {
            "name": details.get("name"),
            "rating": details.get("rating"),
            "review_count": details.get("review_count"),
            "price": details.get("price", "N/A"),
            "phone": details.get("display_phone"),
            "address": ", ".join(details.get("location", {}).get("display_address", [])),
            "hours": details.get("hours", []),
            "photos": details.get("photos", [])[:3],
            "categories": [cat["title"] for cat in details.get("categories", [])],
            "url": details.get("url")
        }
        
        return json.dumps(formatted, indent=2)
    
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
async def get_business_reviews(business_id: str) -> str:
    """
    Get customer reviews for a specific business.
    
    Args:
        business_id: The Yelp business ID
    
    Returns:
        JSON string with customer reviews
    """
    if not _yelp_client:
        return json.dumps({"error": "Yelp client not initialized"})
    
    try:
        reviews_data = await _yelp_client.get_business_reviews(business_id)
        
        reviews = [
            {
                "rating": review.get("rating"),
                "text": review.get("text"),
                "time_created": review.get("time_created"),
                "user": review.get("user", {}).get("name")
            }
            for review in reviews_data.get("reviews", [])
        ]
        
        return json.dumps({"reviews": reviews}, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
async def index_product_websites() -> str:
    """
    Index product information from Evolus and Botox websites using RAG.
    This scrapes the websites and creates a searchable knowledge base.

    Returns:
        JSON string with indexing statistics
    """
    try:
        rag_system = get_rag_system()
        stats = await rag_system.index_product_websites()

        return json.dumps({
            "status": "success",
            "message": "Product websites indexed successfully",
            "statistics": stats
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to index websites: {str(e)}"})


@tool
async def search_product_information(
    query: str,
    brand: Optional[str] = None,
    limit: int = 5
) -> str:
    """
    Search for product information from indexed Evolus and Botox websites.

    Args:
        query: Search query (e.g., "Botox cosmetic uses", "Evolus Jeuveau")
        brand: Optional filter by brand ("evolus" or "botox")
        limit: Maximum number of results (default 5)

    Returns:
        JSON string with relevant product information
    """
    try:
        rag_system = get_rag_system()

        # Check if index exists
        if not rag_system.vector_store:
            return json.dumps({
                "error": "No product data indexed. Please run index_product_websites first."
            })

        results = rag_system.search_products(query, k=limit, filter_brand=brand)

        return json.dumps({
            "query": query,
            "brand_filter": brand,
            "total_results": len(results),
            "results": results
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}"})


@tool
async def get_indexed_products_summary(brand: Optional[str] = None) -> str:
    """
    Get a summary of indexed product information.

    Args:
        brand: Optional filter by brand ("evolus" or "botox")

    Returns:
        JSON string with summary statistics
    """
    try:
        rag_system = get_rag_system()
        summary = rag_system.get_product_summary(brand=brand)

        return json.dumps(summary, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})