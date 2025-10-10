import asyncio
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv
import httpx

load_dotenv()

async def test_yelp():
    api_key = os.getenv("YELP_API_KEY")
    
    if not api_key:
        print("❌ YELP_API_KEY not found in .env file!")
        return
    
    print("✅ API key found")
    print("Testing Yelp API connection...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json"
    }
    
    params = {
        "term": "beauty salon",
        "location": "New York, NY",
        "limit": 3
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://api.yelp.com/v3/businesses/search",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"\n✅ SUCCESS! Found {len(data['businesses'])} businesses:")
            for biz in data['businesses']:
                print(f"  - {biz['name']} ({biz['rating']}⭐)")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_yelp())