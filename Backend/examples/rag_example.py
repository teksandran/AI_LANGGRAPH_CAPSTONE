"""
Example usage of the RAG system for product information retrieval.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_system import get_rag_system


async def main():
    """Demonstrate RAG system usage."""

    print("=" * 60)
    print("Product RAG System Example")
    print("=" * 60)

    # Get RAG system instance
    rag_system = get_rag_system()

    # Step 1: Index product websites
    print("\n1. Indexing Evolus and Botox websites...")
    print("-" * 60)

    try:
        stats = await rag_system.index_product_websites()
        print(f"✓ Indexing completed successfully!")
        print(f"  - Evolus pages scraped: {stats.get('evolus', 0)}")
        print(f"  - Botox pages scraped: {stats.get('botox', 0)}")
        print(f"  - Total documents indexed: {stats.get('total_documents', 0)}")
    except Exception as e:
        print(f"✗ Error indexing websites: {e}")
        return

    # Step 2: Get summary of indexed data
    print("\n2. Getting summary of indexed products...")
    print("-" * 60)

    summary = rag_system.get_product_summary()
    print(f"✓ Summary:")
    print(f"  - Total documents: {summary.get('total_documents', 0)}")
    print(f"  - Products found: {summary.get('products', 0)}")
    print(f"  - Webpages indexed: {summary.get('webpages', 0)}")
    print(f"  - Brands: {', '.join(summary.get('brands', []))}")

    if summary.get('sample_products'):
        print(f"\n  Sample products:")
        for product in summary['sample_products']:
            print(f"    - {product['name']} ({product['brand']})")

    # Step 3: Search for product information
    print("\n3. Searching for product information...")
    print("-" * 60)

    queries = [
        "What is Botox used for?",
        "Evolus Jeuveau products",
        "cosmetic wrinkle treatment"
    ]

    for query in queries:
        print(f"\nQuery: '{query}'")
        results = rag_system.search_products(query, k=3)

        if results:
            print(f"  Found {len(results)} relevant results:")
            for i, result in enumerate(results[:2], 1):
                print(f"\n  Result {i}:")
                print(f"    Brand: {result['brand']}")
                print(f"    Type: {result['type']}")
                print(f"    Source: {result['source']}")
                print(f"    Content preview: {result['content'][:150]}...")
        else:
            print("  No results found")

    # Step 4: Search with brand filter
    print("\n4. Searching with brand filter...")
    print("-" * 60)

    print("\nQuery: 'aesthetic treatments' (Botox only)")
    results = rag_system.search_products("aesthetic treatments", k=3, filter_brand="botox")
    print(f"  Found {len(results)} results from Botox brand")

    print("\nQuery: 'wrinkle reduction' (Evolus only)")
    results = rag_system.search_products("wrinkle reduction", k=3, filter_brand="evolus")
    print(f"  Found {len(results)} results from Evolus brand")

    # Step 5: Save index for future use
    print("\n5. Saving index to disk...")
    print("-" * 60)

    try:
        rag_system.save_index("./product_index")
        print("✓ Index saved successfully to './product_index'")
        print("  You can load it later with: rag_system.load_index('./product_index')")
    except Exception as e:
        print(f"✗ Error saving index: {e}")

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
