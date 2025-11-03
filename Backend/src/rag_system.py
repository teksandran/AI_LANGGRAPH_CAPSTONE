"""
RAG System for scraping and retrieving product information from websites.
Supports Evolus and Botox product pages.
"""

from typing import List, Dict, Optional, Any
import asyncio
import httpx
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import json
import re
from datetime import datetime


class ProductRAGSystem:
    """RAG system for scraping and retrieving product information."""

    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the RAG system.

        Args:
            embedding_model: HuggingFace embedding model to use
        """
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vector_store: Optional[FAISS] = None
        self.documents: List[Document] = []
        self.indexed_urls: set = set()

        # Target URLs
        self.product_urls = {
            "evolus": "https://www.evolus.com/",
            "botox": "https://www.botox.com/"
        }

    async def scrape_website(self, url: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        """
        Scrape website content recursively.

        Args:
            url: Starting URL to scrape
            max_depth: Maximum depth for recursive scraping

        Returns:
            List of scraped page data
        """
        scraped_data = []
        visited = set()

        async def scrape_page(page_url: str, depth: int = 0):
            if depth > max_depth or page_url in visited:
                return

            visited.add(page_url)

            try:
                async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                    response = await client.get(page_url, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    response.raise_for_status()

                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Remove script and style elements
                    for script in soup(["script", "style", "nav", "footer", "header"]):
                        script.decompose()

                    # Extract text content
                    text = soup.get_text(separator=' ', strip=True)
                    text = re.sub(r'\s+', ' ', text).strip()

                    # Extract metadata
                    title = soup.find('title')
                    title_text = title.get_text().strip() if title else page_url

                    meta_description = soup.find('meta', attrs={'name': 'description'})
                    description = meta_description.get('content', '') if meta_description else ''

                    # Extract product information
                    products = self._extract_product_info(soup, page_url)

                    page_data = {
                        'url': page_url,
                        'title': title_text,
                        'description': description,
                        'content': text,
                        'products': products,
                        'scraped_at': datetime.now().isoformat()
                    }

                    scraped_data.append(page_data)

                    # Find internal links for recursive scraping (limited depth)
                    if depth < max_depth:
                        base_domain = '/'.join(page_url.split('/')[:3])
                        links = soup.find_all('a', href=True)

                        for link in links[:10]:  # Limit links per page
                            href = link['href']
                            if href.startswith('/'):
                                href = base_domain + href
                            elif not href.startswith('http'):
                                continue

                            if base_domain in href and href not in visited:
                                await scrape_page(href, depth + 1)
                                await asyncio.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"Error scraping {page_url}: {str(e)}")

        await scrape_page(url)
        return scraped_data

    def _extract_product_info(self, soup: BeautifulSoup, url: str) -> List[Dict[str, str]]:
        """Extract aesthetic product-specific information from HTML."""
        products = []

        # Aesthetic keywords to identify relevant products
        aesthetic_keywords = [
            'botox', 'jeuveau', 'dysport', 'xeomin', 'daxxify',
            'wrinkle', 'fine lines', 'frown lines', 'forehead lines',
            'injectable', 'neurotoxin', 'cosmetic', 'aesthetic',
            'anti-aging', 'rejuvenation', 'facial', 'treatment',
            'glabellar lines', 'crow\'s feet', 'smoothing'
        ]

        # Look for product sections with various patterns
        product_selectors = [
            soup.find_all(['div', 'section', 'article'], class_=re.compile(r'product|item|card', re.I)),
            soup.find_all(['div', 'section'], attrs={'data-product': True}),
            soup.find_all(['div', 'section'], class_=re.compile(r'treatment|service', re.I))
        ]

        # Flatten the list
        all_sections = []
        for selector_result in product_selectors:
            all_sections.extend(selector_result)

        # Also look for content with aesthetic keywords
        for keyword in ['botox', 'jeuveau', 'injectable', 'treatment']:
            keyword_sections = soup.find_all(text=re.compile(keyword, re.I))
            for text_elem in keyword_sections[:3]:
                parent = text_elem.find_parent(['div', 'section', 'article'])
                if parent and parent not in all_sections:
                    all_sections.append(parent)

        seen_products = set()

        for section in all_sections[:20]:  # Increased limit for better coverage
            product = {}
            section_text = section.get_text(strip=True).lower()

            # Check if section contains aesthetic keywords
            has_aesthetic_content = any(keyword in section_text for keyword in aesthetic_keywords)

            if not has_aesthetic_content and len(section_text) < 50:
                continue

            # Extract product name with multiple strategies
            name_elem = (
                section.find(['h1', 'h2', 'h3', 'h4', 'h5'], class_=re.compile(r'name|title|heading|product', re.I)) or
                section.find(['h1', 'h2', 'h3', 'h4', 'h5']) or
                section.find(class_=re.compile(r'name|title', re.I))
            )

            if name_elem:
                product['name'] = name_elem.get_text(strip=True)
            else:
                # Try to extract from first sentence
                first_sentence = section_text.split('.')[0][:100]
                if any(keyword in first_sentence for keyword in aesthetic_keywords):
                    product['name'] = first_sentence.strip()

            # Extract detailed description
            desc_elems = section.find_all(['p', 'div', 'span'], class_=re.compile(r'description|detail|info|content|text', re.I))
            descriptions = []

            for desc_elem in desc_elems[:5]:
                desc_text = desc_elem.get_text(strip=True)
                if len(desc_text) > 30 and desc_text not in descriptions:
                    descriptions.append(desc_text)

            if descriptions:
                product['description'] = ' '.join(descriptions)[:1000]
            elif len(section_text) > 50:
                product['description'] = section_text[:1000]

            # Extract uses/indications
            uses_elem = section.find(text=re.compile(r'use|indication|treat|approved for', re.I))
            if uses_elem:
                uses_parent = uses_elem.find_parent(['p', 'div', 'li', 'ul'])
                if uses_parent:
                    product['uses'] = uses_parent.get_text(strip=True)[:500]

            # Extract benefits
            benefits_elem = section.find(text=re.compile(r'benefit|result|effect', re.I))
            if benefits_elem:
                benefits_parent = benefits_elem.find_parent(['p', 'div', 'li', 'ul'])
                if benefits_parent:
                    product['benefits'] = benefits_parent.get_text(strip=True)[:500]

            # Try to find price
            price_elem = section.find(['span', 'div', 'p'], class_=re.compile(r'price|cost', re.I))
            if price_elem:
                product['price'] = price_elem.get_text(strip=True)

            # Categorize product type
            product_type = 'Unknown'
            if any(term in section_text for term in ['botox', 'neurotoxin', 'injectable']):
                product_type = 'Injectable Neurotoxin'
            elif any(term in section_text for term in ['filler', 'hyaluronic']):
                product_type = 'Dermal Filler'
            elif any(term in section_text for term in ['laser', 'light therapy']):
                product_type = 'Laser Treatment'
            elif any(term in section_text for term in ['serum', 'cream', 'topical']):
                product_type = 'Topical Product'

            product['product_type'] = product_type

            # Extract areas treated
            areas = []
            area_patterns = [
                r'forehead', r'frown lines?', r'glabellar', r"crow'?s feet",
                r'brow', r'neck', r'face', r'facial', r'lip', r'cheek'
            ]
            for pattern in area_patterns:
                if re.search(pattern, section_text, re.I):
                    areas.append(pattern.replace(r'\b', '').replace('?', ''))

            if areas:
                product['treatment_areas'] = ', '.join(set(areas))

            # Only add if we have meaningful content
            if product.get('name') or (product.get('description') and len(product['description']) > 100):
                product['source_url'] = url
                product['category'] = 'Aesthetic Product'

                # Avoid duplicates
                product_key = product.get('name', product.get('description', '')[:50])
                if product_key not in seen_products:
                    seen_products.add(product_key)
                    products.append(product)

        return products

    async def index_product_websites(self) -> Dict[str, int]:
        """
        Scrape and index all configured product websites.

        Returns:
            Dictionary with indexing statistics
        """
        all_documents = []
        stats = {}

        for brand, url in self.product_urls.items():
            if url in self.indexed_urls:
                print(f"Already indexed: {url}")
                continue

            print(f"Scraping {brand}: {url}")
            scraped_data = await self.scrape_website(url, max_depth=2)

            # Convert to LangChain documents
            for page_data in scraped_data:
                # Create document for main content
                content_doc = Document(
                    page_content=page_data['content'],
                    metadata={
                        'source': page_data['url'],
                        'title': page_data['title'],
                        'description': page_data['description'],
                        'brand': brand,
                        'type': 'webpage',
                        'scraped_at': page_data['scraped_at']
                    }
                )
                all_documents.append(content_doc)

                # Create separate documents for products with enhanced metadata
                for product in page_data['products']:
                    # Build comprehensive product content
                    content_parts = [f"Product: {product.get('name', 'Unknown')}"]

                    if product.get('description'):
                        content_parts.append(f"Description: {product.get('description')}")

                    if product.get('uses'):
                        content_parts.append(f"Uses: {product.get('uses')}")

                    if product.get('benefits'):
                        content_parts.append(f"Benefits: {product.get('benefits')}")

                    if product.get('treatment_areas'):
                        content_parts.append(f"Treatment Areas: {product.get('treatment_areas')}")

                    if product.get('product_type'):
                        content_parts.append(f"Product Type: {product.get('product_type')}")

                    if product.get('price'):
                        content_parts.append(f"Price: {product.get('price')}")

                    content_parts.append(f"Brand: {brand.capitalize()}")
                    content_parts.append(f"Category: Aesthetic Improvement Product")

                    product_content = "\n".join(content_parts)

                    product_doc = Document(
                        page_content=product_content,
                        metadata={
                            'source': product.get('source_url', page_data['url']),
                            'brand': brand,
                            'type': 'product',
                            'product_name': product.get('name', 'Unknown'),
                            'product_type': product.get('product_type', 'Unknown'),
                            'category': product.get('category', 'Aesthetic Product'),
                            'treatment_areas': product.get('treatment_areas', 'N/A'),
                            'scraped_at': page_data['scraped_at']
                        }
                    )
                    all_documents.append(product_doc)

            self.indexed_urls.add(url)
            stats[brand] = len(scraped_data)

        # Split documents into chunks
        split_docs = self.text_splitter.split_documents(all_documents)
        self.documents.extend(split_docs)

        # Create or update vector store
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(split_docs, self.embeddings)
        else:
            self.vector_store.add_documents(split_docs)

        stats['total_documents'] = len(split_docs)
        stats['total_pages'] = sum(stats.values()) - stats['total_documents']

        return stats

    def search_products(self, query: str, k: int = 5, filter_brand: Optional[str] = None,
                       product_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for aesthetic product information using semantic similarity.

        Args:
            query: Search query (automatically enhanced for aesthetic context)
            k: Number of results to return
            filter_brand: Optional brand filter ('evolus' or 'botox')
            product_type: Optional product type filter ('Injectable Neurotoxin', 'Dermal Filler', etc.)

        Returns:
            List of relevant aesthetic products with detailed metadata
        """
        if not self.vector_store:
            return []

        # Enhance query with aesthetic context if not already present
        aesthetic_terms = ['aesthetic', 'cosmetic', 'wrinkle', 'treatment', 'injectable']
        if not any(term in query.lower() for term in aesthetic_terms):
            enhanced_query = f"{query} aesthetic improvement cosmetic treatment"
        else:
            enhanced_query = query

        # Perform similarity search with higher k for better filtering
        docs = self.vector_store.similarity_search(enhanced_query, k=k*3)

        # Prioritize product documents over general webpage content
        product_docs = [doc for doc in docs if doc.metadata.get('type') == 'product']
        other_docs = [doc for doc in docs if doc.metadata.get('type') != 'product']

        # Combine with products first
        docs = product_docs + other_docs

        # Apply filters
        if filter_brand:
            docs = [doc for doc in docs if doc.metadata.get('brand') == filter_brand]

        if product_type:
            docs = [doc for doc in docs if doc.metadata.get('product_type') == product_type]

        # Format results with rich metadata
        results = []
        for doc in docs[:k]:
            result = {
                'content': doc.page_content,
                'metadata': doc.metadata,
                'source': doc.metadata.get('source', 'Unknown'),
                'brand': doc.metadata.get('brand', 'Unknown'),
                'type': doc.metadata.get('type', 'Unknown'),
                'product_name': doc.metadata.get('product_name', 'N/A'),
                'product_type': doc.metadata.get('product_type', 'N/A'),
                'treatment_areas': doc.metadata.get('treatment_areas', 'N/A'),
                'category': doc.metadata.get('category', 'N/A')
            }
            results.append(result)

        return results

    def search_aesthetic_treatments(self, treatment_area: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for aesthetic treatments by target area (forehead, frown lines, etc.).

        Args:
            treatment_area: The area to be treated (e.g., 'forehead', 'crow\'s feet')
            k: Number of results to return

        Returns:
            List of relevant aesthetic treatment products
        """
        query = f"aesthetic treatment for {treatment_area} wrinkles fine lines improvement"
        return self.search_products(query, k=k)

    def get_product_summary(self, brand: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a summary of indexed products.

        Args:
            brand: Optional brand filter

        Returns:
            Summary statistics
        """
        if not self.documents:
            return {'error': 'No documents indexed'}

        filtered_docs = self.documents
        if brand:
            filtered_docs = [doc for doc in self.documents if doc.metadata.get('brand') == brand]

        products = [doc for doc in filtered_docs if doc.metadata.get('type') == 'product']
        webpages = [doc for doc in filtered_docs if doc.metadata.get('type') == 'webpage']

        summary = {
            'total_documents': len(filtered_docs),
            'products': len(products),
            'webpages': len(webpages),
            'brands': list(set(doc.metadata.get('brand', 'Unknown') for doc in filtered_docs)),
            'indexed_urls': list(self.indexed_urls)
        }

        if products:
            summary['sample_products'] = [
                {
                    'name': doc.metadata.get('product_name', 'Unknown'),
                    'brand': doc.metadata.get('brand', 'Unknown'),
                    'source': doc.metadata.get('source', 'Unknown')
                }
                for doc in products[:5]
            ]

        return summary

    def save_index(self, path: str = "./product_index"):
        """Save the vector store to disk."""
        if self.vector_store:
            self.vector_store.save_local(path)

    def load_index(self, path: str = "./product_index"):
        """Load the vector store from disk."""
        try:
            self.vector_store = FAISS.load_local(
                path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            print(f"Error loading index: {e}")


# Global RAG system instance
_rag_system: Optional[ProductRAGSystem] = None


def get_rag_system() -> ProductRAGSystem:
    """Get or create the global RAG system instance."""
    global _rag_system
    if _rag_system is None:
        _rag_system = ProductRAGSystem()
    return _rag_system
