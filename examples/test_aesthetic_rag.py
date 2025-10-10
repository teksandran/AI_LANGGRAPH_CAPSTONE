"""
Test script for aesthetic product RAG system.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_system import get_rag_system


async def main():
    """Test aesthetic product RAG functionality."""

    print("=" * 70)
    print("AESTHETIC PRODUCT RAG SYSTEM TEST")
    print("=" * 70)

    rag_system = get_rag_system()

    # Step 1: Index websites
    print("\n[1/5] Indexing Evolus and Botox product websites...")
    print("-" * 70)

    try:
        stats = await rag_system.index_product_websites()
        print(f"✓ Indexing completed!")
        print(f"  • Evolus pages: {stats.get('evolus', 0)}")
        print(f"  • Botox pages: {stats.get('botox', 0)}")
        print(f"  • Total documents: {stats.get('total_documents', 0)}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Step 2: Get summary
    print("\n[2/5] Summary of indexed aesthetic products...")
    print("-" * 70)

    summary = rag_system.get_product_summary()
    print(f"  • Total documents: {summary.get('total_documents', 0)}")
    print(f"  • Aesthetic products: {summary.get('products', 0)}")
    print(f"  • Brands: {', '.join(summary.get('brands', []))}")

    if summary.get('sample_products'):
        print(f"\n  Sample Products:")
        for product in summary['sample_products']:
            print(f"    → {product['name']} ({product['brand'].upper()})")

    # Step 3: Test aesthetic product searches
    print("\n[3/5] Testing aesthetic product searches...")
    print("-" * 70)

    test_queries = [
        ("wrinkle reduction", "General wrinkle treatment"),
        ("forehead lines treatment", "Forehead-specific treatment"),
        ("botox cosmetic", "Botox products"),
        ("injectable neurotoxin", "Injectable treatments")
    ]

    for query, description in test_queries:
        print(f"\n  Query: '{query}' ({description})")
        results = rag_system.search_products(query, k=3)

        if results:
            print(f"  ✓ Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n    Result #{i}:")
                print(f"      • Product: {result.get('product_name', 'N/A')}")
                print(f"      • Brand: {result.get('brand', 'N/A').upper()}")
                print(f"      • Type: {result.get('product_type', 'N/A')}")
                print(f"      • Areas: {result.get('treatment_areas', 'N/A')}")
                print(f"      • Preview: {result['content'][:120]}...")
        else:
            print(f"  ✗ No results found")

    # Step 4: Test treatment area search
    print("\n[4/5] Testing treatment area-specific searches...")
    print("-" * 70)

    treatment_areas = ["forehead", "frown lines", "crow's feet"]

    for area in treatment_areas:
        print(f"\n  Treatment Area: '{area}'")
        results = rag_system.search_aesthetic_treatments(area, k=2)

        if results:
            print(f"  ✓ Found {len(results)} treatment options:")
            for i, result in enumerate(results, 1):
                product_name = result.get('product_name', 'N/A')
                brand = result.get('brand', 'N/A').upper()
                print(f"    {i}. {product_name} ({brand})")
        else:
            print(f"  ✗ No treatments found")

    # Step 5: Test brand filtering
    print("\n[5/5] Testing brand-specific searches...")
    print("-" * 70)

    for brand in ['botox', 'evolus']:
        print(f"\n  Brand: {brand.upper()}")
        results = rag_system.search_products(
            "aesthetic improvement products",
            k=3,
            filter_brand=brand
        )

        if results:
            print(f"  ✓ Found {len(results)} {brand.upper()} products:")
            for i, result in enumerate(results, 1):
                product_name = result.get('product_name', 'N/A')
                product_type = result.get('product_type', 'N/A')
                print(f"    {i}. {product_name} - {product_type}")
        else:
            print(f"  ✗ No products found for {brand}")

    # Final summary
    print("\n" + "=" * 70)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\nThe RAG system is now ready to provide aesthetic product information.")
    print("You can search for:")
    print("  • Specific products (Botox, Jeuveau)")
    print("  • Treatment types (wrinkle reduction, line smoothing)")
    print("  • Target areas (forehead, frown lines, crow's feet)")
    print("  • Brand-specific products (Evolus or Botox)")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
