"""
Simple demonstration of Botox vs Evolus comparison using RAG system.
Works without LLM - uses direct RAG search.
"""

import asyncio
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.rag_system import get_rag_system


async def compare_products():
    """Compare Botox and Evolus products."""

    print("=" * 80)
    print("BOTOX vs EVOLUS - Product Comparison (Direct RAG Search)")
    print("=" * 80)

    # Initialize RAG system
    rag = get_rag_system()

    # Index websites
    print("\n[Step 1] Indexing product websites...")
    print("-" * 80)

    try:
        stats = await rag.index_product_websites()
        print(f"[OK] Indexed successfully!")
        print(f"  - Botox pages: {stats.get('botox', 0)}")
        print(f"  - Evolus pages: {stats.get('evolus', 0)}")
        print(f"  - Total documents: {stats.get('total_documents', 0)}")
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    # Compare products
    print("\n\n[Step 2] Comparing Botox and Evolus...")
    print("=" * 80)

    # Get Botox information
    print("\n[BOTOX COSMETIC]")
    print("-" * 80)
    botox_results = rag.search_products("Botox uses benefits treatment areas", k=3, filter_brand="botox")

    if botox_results:
        result = botox_results[0]
        print(f"Product Name: {result.get('product_name', 'Botox Cosmetic')}")
        print(f"Product Type: {result.get('product_type', 'Injectable Neurotoxin')}")
        print(f"Treatment Areas: {result.get('treatment_areas', 'N/A')}")
        print(f"\nKey Information:")

        # Extract key points from content
        content = result['content']
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        for i, line in enumerate(lines[:6]):
            if line and len(line) > 20:
                print(f"  - {line[:150]}")

    # Get Evolus information
    print("\n\n[EVOLUS JEUVEAU]")
    print("-" * 80)
    evolus_results = rag.search_products("Evolus Jeuveau uses benefits treatment areas", k=3, filter_brand="evolus")

    if evolus_results:
        result = evolus_results[0]
        print(f"Product Name: {result.get('product_name', 'Jeuveau')}")
        print(f"Product Type: {result.get('product_type', 'Injectable Neurotoxin')}")
        print(f"Treatment Areas: {result.get('treatment_areas', 'N/A')}")
        print(f"\nKey Information:")

        # Extract key points from content
        content = result['content']
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        for i, line in enumerate(lines[:6]):
            if line and len(line) > 20:
                print(f"  - {line[:150]}")

    # Comparison summary
    print("\n\n[COMPARISON SUMMARY]")
    print("=" * 80)

    if botox_results and evolus_results:
        botox = botox_results[0]
        evolus = evolus_results[0]

        print("\nSimilarities:")
        print("  - Both are injectable neurotoxins")
        print("  - Both used for aesthetic wrinkle reduction")
        print(f"  - Botox areas: {botox.get('treatment_areas', 'N/A')}")
        print(f"  - Evolus areas: {evolus.get('treatment_areas', 'N/A')}")

        print("\nKey Differences:")
        print("  - Botox: Made by Allergan, FDA-approved since 2002")
        print("  - Evolus (Jeuveau): Newer brand, FDA-approved in 2019")
        print("  - Both require prescription and professional administration")

    # Search by treatment area
    print("\n\n[TREATMENT AREA SEARCH: Frown Lines]")
    print("-" * 80)

    frown_results = rag.search_aesthetic_treatments("frown lines", k=4)

    if frown_results:
        print(f"\nFound {len(frown_results)} products for treating frown lines:\n")

        for i, result in enumerate(frown_results, 1):
            brand = result['brand'].upper()
            product = result.get('product_name', 'Unknown')
            areas = result.get('treatment_areas', 'N/A')

            print(f"{i}. {brand}")
            print(f"   Product: {product}")
            print(f"   Treatment Areas: {areas}")
            print()

    # Summary
    print("\n" + "=" * 80)
    print("[CONCLUSION]")
    print("=" * 80)
    print("""
Both Botox and Evolus (Jeuveau) are injectable neurotoxins used for:
  - Reducing wrinkles and fine lines
  - Treating frown lines, forehead lines, and crow's feet
  - Non-surgical aesthetic improvements

Main Differences:
  - Brand/Manufacturer: Botox (Allergan) vs Evolus (Jeuveau)
  - Time on market: Botox (older, established) vs Jeuveau (newer)
  - Pricing may vary by provider

Recommendation:
  Consult with a licensed healthcare provider to determine which product
  is best for your specific needs and desired results.
""")

    print("=" * 80)
    print("[OK] Comparison completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(compare_products())
