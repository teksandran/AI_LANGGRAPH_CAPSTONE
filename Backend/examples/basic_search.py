
import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.yelp_client import YelpClient
from src.config import YelpConfig, BEAUTY_CATEGORIES

load_dotenv()


async def main():
    """Basic search examples"""
    
    # Initialize client
    config = YelpConfig.from_env()
    client = YelpClient(config)
    
    print("=" * 60)
    print("BASIC YELP SEARCH EXAMPLES")
    print("=" * 60)
    
    # Example 1: Search beauty salons
    print("\n1. Searching for beauty salons in New York...")
    salon_results = await client.search_businesses(
        term="beauty salon",
        location="New York, NY",
        categories=BEAUTY_CATEGORIES["salons"],
        limit=3
    )
    
    for biz in salon_results.get("businesses", []):
        print(f"\n   {biz['name']}")
        print(f"   Rating: {biz.get('rating')} ⭐ ({biz.get('review_count')} reviews)")
        print(f"   Price: {biz.get('price', 'N/A')}")
        print(f"   Address: {', '.join(biz['location']['display_address'])}")
    
    # Example 2: Search beauty products
    print("\n" + "=" * 60)
    print("\n2. Searching for beauty product stores in Los Angeles...")
    results = await client.search_businesses(
        term="cosmetics",
        location="Los Angeles, CA",
        categories=BEAUTY_CATEGORIES["products"],
        limit=3
    )
    
    for biz in results.get("businesses", []):
        print(f"\n   {biz['name']}")
        print(f"   Rating: {biz.get('rating')} ⭐")
        print(f"   Categories: {', '.join([c['title'] for c in biz.get('categories', [])])}")
    
    # Example 3: Get business details
    if salon_results.get("businesses"):
        business_id = salon_results["businesses"][0]["id"]
        business_name = salon_results["businesses"][0]["name"]
        print("\n" + "=" * 60)
        print(f"\n3. Getting details for {business_name}...")
        
        try:
            details = await client.get_business_details(business_id)
            
            print(f"   Phone: {details.get('display_phone')}")
            print(f"   Hours: {'Open' if details.get('hours') else 'Hours not available'}")
            if details.get('photos'):
                print(f"   Photos available: {len(details.get('photos'))}")
        except Exception as e:
            print(f"   Error getting details: {e}")
        
        # Example 4: Get reviews (Note: Reviews endpoint may not be available with all API plans)
        print("\n" + "=" * 60)
        print(f"\n4. Attempting to get reviews for {business_name}...")
        
        # Check if business has reviews before attempting to fetch them
        review_count = salon_results["businesses"][0].get("review_count", 0)
        print(f"   Business shows {review_count} reviews available")
        
        if review_count > 0:
            try:
                reviews = await client.get_business_reviews(business_id)
                
                if reviews.get("reviews"):
                    for i, review in enumerate(reviews.get("reviews", []), 1):
                        print(f"\n   Review {i}:")
                        print(f"   Rating: {review['rating']} ⭐")
                        print(f"   {review['text'][:100]}...")
                else:
                    print("   No reviews returned from API")
            except Exception as e:
                print(f"   Reviews endpoint not accessible: {type(e).__name__}")
                print("   Note: The Yelp Fusion API reviews endpoint may require a different access level")
                print("   or may not be available with all API plans.")
        else:
            print(f"   This business has no reviews to display")
    
    print("\n" + "=" * 60)
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())

