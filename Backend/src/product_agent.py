"""
Product Agent - Specialized agent for handling product information queries.
Handles Botox, Evolus, and other aesthetic product information using RAG.
"""

import asyncio
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
from .rag_system import get_rag_system


class ProductAgent:
    """Specialized agent for product information queries."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.rag_system = get_rag_system()
        self._indexed = False

    async def _ensure_indexed(self):
        """Ensure product data is indexed."""
        if not self._indexed and not self.rag_system.vector_store:
            try:
                await self.rag_system.index_product_websites()
                self._indexed = True
            except Exception as e:
                print(f"Warning: Could not index products: {e}")

    async def run_async(self, query: str) -> str:
        """Process product information query (async version)."""
        # Ensure data is indexed
        await self._ensure_indexed()

        # Check if indexed
        if not self.rag_system.vector_store:
            return "Product information is not available. Please try again later."

        # Search for product information
        results = self.rag_system.search_products(query, k=3)

        if not results:
            return "I couldn't find specific information about that product. Could you rephrase your question?"

        # Format results
        response_parts = []

        # Check if this is a comparison query
        if "compare" in query.lower() or "difference" in query.lower() or "vs" in query.lower():
            # Get both brands
            botox_results = self.rag_system.search_products(query, k=2, filter_brand="botox")
            evolus_results = self.rag_system.search_products(query, k=2, filter_brand="evolus")

            response_parts.append("**Product Comparison:**\n")

            if botox_results:
                response_parts.append("\n**BOTOX:**")
                result = botox_results[0]
                response_parts.append(f"- Type: {result.get('product_type', 'Injectable Neurotoxin')}")
                response_parts.append(f"- Treatment Areas: {result.get('treatment_areas', 'Face, forehead, frown lines')}")
                content = result['content'][:300]
                response_parts.append(f"- Info: {content}...")

            if evolus_results:
                response_parts.append("\n**EVOLUS (Jeuveau):**")
                result = evolus_results[0]
                response_parts.append(f"- Type: {result.get('product_type', 'Injectable Neurotoxin')}")
                response_parts.append(f"- Treatment Areas: {result.get('treatment_areas', 'Face, frown lines')}")
                content = result['content'][:300]
                response_parts.append(f"- Info: {content}...")

            response_parts.append("\n**Key Similarities:**")
            response_parts.append("- Both are FDA-approved injectable neurotoxins")
            response_parts.append("- Both treat wrinkles and fine lines")
            response_parts.append("- Both require professional administration")

        else:
            # Single product query
            result = results[0]
            brand = result.get('brand', 'Unknown').upper()
            product_name = result.get('product_name', brand)
            product_type = result.get('product_type', 'Aesthetic Product')
            areas = result.get('treatment_areas', 'Various facial areas')

            response_parts.append(f"**{brand} ({product_name})**\n")
            response_parts.append(f"**Type:** {product_type}")
            response_parts.append(f"**Treatment Areas:** {areas}\n")

            # Extract key information from content
            content = result['content']
            lines = [line.strip() for line in content.split('\n') if line.strip() and len(line.strip()) > 30]

            response_parts.append("**Key Information:**")
            for line in lines[:5]:
                if any(keyword in line.lower() for keyword in ['use', 'benefit', 'treatment', 'approved', 'indication']):
                    response_parts.append(f"- {line[:200]}")

        return "\n".join(response_parts)

    def run(self, query: str) -> str:
        """Process product information query (sync version)."""
        # Ensure data is indexed (run async in sync context)
        try:
            asyncio.get_running_loop()
            # Already in async context
            pass
        except RuntimeError:
            # Not in async context, run sync
            asyncio.run(self._ensure_indexed())

        # Check if indexed
        if not self.rag_system.vector_store:
            return "Product information is not available. Please try again later."

        # Search for product information
        results = self.rag_system.search_products(query, k=3)

        if not results:
            return "I couldn't find specific information about that product. Could you rephrase your question?"

        # Format results
        response_parts = []

        # Check if this is a comparison query
        if "compare" in query.lower() or "difference" in query.lower() or "vs" in query.lower():
            # Get both brands
            botox_results = self.rag_system.search_products(query, k=2, filter_brand="botox")
            evolus_results = self.rag_system.search_products(query, k=2, filter_brand="evolus")

            response_parts.append("**Product Comparison:**\n")

            if botox_results:
                response_parts.append("\n**BOTOX:**")
                result = botox_results[0]
                response_parts.append(f"- Type: {result.get('product_type', 'Injectable Neurotoxin')}")
                response_parts.append(f"- Treatment Areas: {result.get('treatment_areas', 'Face, forehead, frown lines')}")
                content = result['content'][:300]
                response_parts.append(f"- Info: {content}...")

            if evolus_results:
                response_parts.append("\n**EVOLUS (Jeuveau):**")
                result = evolus_results[0]
                response_parts.append(f"- Type: {result.get('product_type', 'Injectable Neurotoxin')}")
                response_parts.append(f"- Treatment Areas: {result.get('treatment_areas', 'Face, frown lines')}")
                content = result['content'][:300]
                response_parts.append(f"- Info: {content}...")

            response_parts.append("\n**Key Similarities:**")
            response_parts.append("- Both are FDA-approved injectable neurotoxins")
            response_parts.append("- Both treat wrinkles and fine lines")
            response_parts.append("- Both require professional administration")

        else:
            # Single product query
            result = results[0]
            brand = result.get('brand', 'Unknown').upper()
            product_name = result.get('product_name', brand)
            product_type = result.get('product_type', 'Aesthetic Product')
            areas = result.get('treatment_areas', 'Various facial areas')

            response_parts.append(f"**{brand} ({product_name})**\n")
            response_parts.append(f"**Type:** {product_type}")
            response_parts.append(f"**Treatment Areas:** {areas}\n")

            # Extract key information from content
            content = result['content']
            lines = [line.strip() for line in content.split('\n') if line.strip() and len(line.strip()) > 30]

            response_parts.append("**Key Information:**")
            for line in lines[:5]:
                if any(keyword in line.lower() for keyword in ['use', 'benefit', 'treatment', 'approved', 'indication']):
                    response_parts.append(f"- {line[:200]}")

        return "\n".join(response_parts)
