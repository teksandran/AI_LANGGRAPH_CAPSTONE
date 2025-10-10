"""
Enhanced example showing product search with detailed descriptions for Botox and Evolus.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_system import get_rag_system


async def main():
    """Demonstrate enhanced product search with detailed information."""

    print("=" * 80)
    print("Enhanced Product Search - Botox & Evolus")
    print("=" * 80)

    # Get RAG system instance
    rag_system = get_rag_system()

    # Step 1: Index product websites
    print("\n📦 STEP 1: Indexing product information from official websites...")
    print("-" * 80)

    try:
        stats = await rag_system.index_product_websites()
        print("✓ Indexing completed successfully!")
        print(f"  • Evolus pages scraped: {stats.get('evolus', 0)}")
        print(f"  • Botox pages scraped: {stats.get('botox', 0)}")
        print(f"  • Total documents indexed: {stats.get('total_documents', 0)}")
    except Exception as e:
        print(f"✗ Error indexing websites: {e}")
        return

    # Step 2: Search for Botox with detailed information
    print("\n\n🔍 STEP 2: Searching for 'Botox' with detailed product information...")
    print("-" * 80)

    botox_query = "Botox cosmetic uses treatment areas benefits"
    botox_results = rag_system.search_products(botox_query, k=3)

    if botox_results:
        print(f"\n📊 Found {len(botox_results)} relevant results for Botox:\n")

        for i, result in enumerate(botox_results, 1):
            print(f"{'='*80}")
            print(f"Result #{i}")
            print(f"{'='*80}")
            print(f"Brand:           {result['brand'].upper()}")
            print(f"Product Name:    {result.get('product_name', 'N/A')}")
            print(f"Product Type:    {result.get('product_type', 'N/A')}")
            print(f"Treatment Areas: {result.get('treatment_areas', 'N/A')}")
            print(f"Source:          {result['source']}")
            print(f"\n📝 Description:")
            print(f"{'-'*80}")
            # Display content with proper formatting
            content = result['content']
            if len(content) > 500:
                print(content[:500] + "...")
            else:
                print(content)
            print()
    else:
        print("  No results found for Botox")

    # Step 3: Search for Evolus/Jeuveau with detailed information
    print("\n\n🔍 STEP 3: Searching for 'Evolus Jeuveau' with detailed product information...")
    print("-" * 80)

    evolus_query = "Evolus Jeuveau aesthetic injectable treatment"
    evolus_results = rag_system.search_products(evolus_query, k=3)

    if evolus_results:
        print(f"\n📊 Found {len(evolus_results)} relevant results for Evolus:\n")

        for i, result in enumerate(evolus_results, 1):
            print(f"{'='*80}")
            print(f"Result #{i}")
            print(f"{'='*80}")
            print(f"Brand:           {result['brand'].upper()}")
            print(f"Product Name:    {result.get('product_name', 'N/A')}")
            print(f"Product Type:    {result.get('product_type', 'N/A')}")
            print(f"Treatment Areas: {result.get('treatment_areas', 'N/A')}")
            print(f"Source:          {result['source']}")
            print(f"\n📝 Description:")
            print(f"{'-'*80}")
            # Display content with proper formatting
            content = result['content']
            if len(content) > 500:
                print(content[:500] + "...")
            else:
                print(content)
            print()
    else:
        print("  No results found for Evolus")

    # Step 4: Compare products side by side
    print("\n\n⚖️  STEP 4: Comparing Botox vs Evolus...")
    print("-" * 80)

    botox_only = rag_system.search_products("neurotoxin injectable", k=2, filter_brand="botox")
    evolus_only = rag_system.search_products("neurotoxin injectable", k=2, filter_brand="evolus")

    print("\n🅱️  BOTOX Information:")
    print("=" * 80)
    if botox_only:
        for result in botox_only[:1]:
            print(f"Product Type: {result.get('product_type', 'N/A')}")
            print(f"Treatment Areas: {result.get('treatment_areas', 'N/A')}")
            print(f"\nKey Information:")
            content_lines = result['content'].split('\n')
            for line in content_lines[:5]:
                if line.strip():
                    print(f"  • {line.strip()}")

    print("\n\n🅴  EVOLUS Information:")
    print("=" * 80)
    if evolus_only:
        for result in evolus_only[:1]:
            print(f"Product Type: {result.get('product_type', 'N/A')}")
            print(f"Treatment Areas: {result.get('treatment_areas', 'N/A')}")
            print(f"\nKey Information:")
            content_lines = result['content'].split('\n')
            for line in content_lines[:5]:
                if line.strip():
                    print(f"  • {line.strip()}")

    # Step 5: Search by treatment area
    print("\n\n🎯 STEP 5: Searching by treatment area (frown lines)...")
    print("-" * 80)

    frown_results = rag_system.search_aesthetic_treatments("frown lines", k=3)

    if frown_results:
        print(f"\nFound {len(frown_results)} products for treating frown lines:\n")

        for i, result in enumerate(frown_results, 1):
            print(f"{i}. {result['brand'].upper()} - {result.get('product_name', 'N/A')}")
            print(f"   Treatment Areas: {result.get('treatment_areas', 'N/A')}")
            print(f"   Type: {result.get('product_type', 'N/A')}")
            print()

    # Step 6: Get summary statistics
    print("\n\n📈 STEP 6: Summary Statistics...")
    print("-" * 80)

    summary = rag_system.get_product_summary()
    print(f"\n✓ Indexed Data Summary:")
    print(f"  • Total documents: {summary.get('total_documents', 0)}")
    print(f"  • Product entries: {summary.get('products', 0)}")
    print(f"  • Webpage entries: {summary.get('webpages', 0)}")
    print(f"  • Brands: {', '.join(summary.get('brands', []))}")

    if summary.get('sample_products'):
        print(f"\n  Sample Products Found:")
        for product in summary['sample_products'][:5]:
            print(f"    - {product['name']} ({product['brand']})")

    print("\n" + "=" * 80)
    print("✓ Example completed!")
    print("=" * 80)
    print("\n💡 The agent can now provide detailed product information when users")
    print("   search for Botox, Evolus, or other aesthetic treatments!")


if __name__ == "__main__":
    asyncio.run(main())
