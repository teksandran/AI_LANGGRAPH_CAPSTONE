"""
Flask API Server for Multi-Agent System
Integrates SupervisorAgent, ProductAgent, and BusinessAgent
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import os
import logging
from dotenv import load_dotenv
from src.supervisor_agent import SupervisorAgent
from src.rag_system import get_rag_system
from src.langsmith_config import print_langsmith_status, is_langsmith_enabled, log_agent_execution
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React integration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize RAG system
rag_system = get_rag_system()

# Initialize SupervisorAgent
yelp_api_key = os.getenv("YELP_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

if not yelp_api_key:
    logger.error("YELP_API_KEY not found in environment variables")

# Choose LLM provider based on available API keys
llm_provider = "openai" if openai_api_key else "anthropic"
supervisor_agent = None

if yelp_api_key and (openai_api_key or anthropic_api_key):
    try:
        supervisor_agent = SupervisorAgent(
            yelp_api_key=yelp_api_key,
            llm_provider=llm_provider,
            model="gpt-4o-mini" if llm_provider == "openai" else "claude-3-5-sonnet-20241022"
        )
        logger.info(f"SupervisorAgent initialized with {llm_provider}")
    except Exception as e:
        logger.error(f"Failed to initialize SupervisorAgent: {e}")


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'supervisor_agent': supervisor_agent is not None,
        'rag_indexed': rag_system.vector_store is not None,
        'llm_provider': llm_provider,
        'agents': {
            'supervisor': supervisor_agent is not None,
            'product_agent': supervisor_agent is not None,
            'business_agent': supervisor_agent is not None
        }
    })


@app.route('/api/index-products', methods=['POST'])
def index_products():
    """Index product websites (Botox, Evolus) into RAG system"""
    try:
        logger.info("Starting product indexing...")
        stats = asyncio.run(rag_system.index_product_websites())
        logger.info(f"Indexing complete: {stats}")

        return jsonify({
            'status': 'success',
            'message': 'Products indexed successfully',
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Product indexing failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/query', methods=['POST'])
def query_agent():
    """
    Main endpoint for querying the multi-agent system
    Routes queries through SupervisorAgent to appropriate specialized agents
    """
    if not supervisor_agent:
        return jsonify({
            'status': 'error',
            'message': 'SupervisorAgent not initialized. Check API keys.'
        }), 500

    start_time = datetime.now()

    try:
        data = request.json
        query = data.get('query', '')

        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Query is required'
            }), 400

        logger.info(f"Received query: {query}")

        # Route through SupervisorAgent (LangSmith will auto-trace LangChain calls)
        response = asyncio.run(supervisor_agent.run(query))

        # Calculate duration
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000

        logger.info(f"Response generated: {response[:100]}...")

        # Log to LangSmith (custom logging)
        if is_langsmith_enabled():
            log_agent_execution(
                agent_name="SupervisorAgent",
                query=query,
                response=response,
                duration_ms=duration_ms,
                metadata={
                    'endpoint': '/api/query',
                    'status': 'success',
                    'response_length': len(response)
                }
            )

        return jsonify({
            'status': 'success',
            'query': query,
            'response': response,
            'agent_type': 'supervisor',
            'duration_ms': round(duration_ms, 2)
        })

    except Exception as e:
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        logger.error(f"Query processing failed: {e}", exc_info=True)

        # Log error to LangSmith
        if is_langsmith_enabled():
            log_agent_execution(
                agent_name="SupervisorAgent",
                query=query if 'query' in locals() else 'unknown',
                response=None,
                duration_ms=duration_ms,
                metadata={
                    'endpoint': '/api/query',
                    'status': 'error',
                    'error': str(e)
                }
            )

        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/product-query', methods=['POST'])
def product_query():
    """
    Direct endpoint for product queries (bypasses supervisor)
    Queries ProductAgent directly via RAG system
    """
    try:
        data = request.json
        query = data.get('query', '')
        brand = data.get('brand')  # Optional: 'botox' or 'evolus'
        limit = data.get('limit', 3)

        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Query is required'
            }), 400

        if not rag_system.vector_store:
            return jsonify({
                'status': 'error',
                'message': 'RAG system not indexed. Please call /api/index-products first'
            }), 400

        logger.info(f"Product query: {query}, brand: {brand}")

        # Search using RAG
        results = rag_system.search_products(query, k=limit, filter_brand=brand)

        # Format response
        formatted_results = []
        for result in results:
            formatted_results.append({
                'product_name': result.get('product_name', 'N/A'),
                'brand': result.get('brand', 'Unknown'),
                'product_type': result.get('product_type', 'N/A'),
                'treatment_areas': result.get('treatment_areas', 'N/A'),
                'content': result.get('content', ''),
                'source': result.get('source', '')
            })

        return jsonify({
            'status': 'success',
            'query': query,
            'brand_filter': brand,
            'results': formatted_results,
            'total': len(formatted_results),
            'agent_type': 'product'
        })

    except Exception as e:
        logger.error(f"Product query failed: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/business-query', methods=['POST'])
def business_query():
    """
    Direct endpoint for business/location queries (bypasses supervisor)
    Queries BusinessAgent directly via Yelp API
    """
    if not supervisor_agent:
        return jsonify({
            'status': 'error',
            'message': 'Business agent not initialized. Check YELP_API_KEY.'
        }), 500

    try:
        data = request.json
        query = data.get('query', '')
        location = data.get('location', '')

        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Query is required'
            }), 400

        # Construct query with location if provided
        full_query = f"{query} in {location}" if location else query

        logger.info(f"Business query: {full_query}")

        # Use BusinessAgent directly
        response = asyncio.run(supervisor_agent.business_agent.run(full_query))

        return jsonify({
            'status': 'success',
            'query': query,
            'location': location,
            'response': response,
            'agent_type': 'business'
        })

    except Exception as e:
        logger.error(f"Business query failed: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/compare-products', methods=['POST'])
def compare_products():
    """
    Endpoint for comparing products (e.g., Botox vs Evolus)
    """
    try:
        data = request.json
        product1 = data.get('product1', 'botox')
        product2 = data.get('product2', 'evolus')

        if not rag_system.vector_store:
            return jsonify({
                'status': 'error',
                'message': 'RAG system not indexed. Please call /api/index-products first'
            }), 400

        logger.info(f"Comparing {product1} vs {product2}")

        # Search for both products
        results1 = rag_system.search_products(product1, k=2, filter_brand=product1.lower())
        results2 = rag_system.search_products(product2, k=2, filter_brand=product2.lower())

        comparison = {
            product1: [],
            product2: []
        }

        for result in results1:
            comparison[product1].append({
                'product_name': result.get('product_name', 'N/A'),
                'product_type': result.get('product_type', 'N/A'),
                'treatment_areas': result.get('treatment_areas', 'N/A'),
                'content': result.get('content', '')[:300]
            })

        for result in results2:
            comparison[product2].append({
                'product_name': result.get('product_name', 'N/A'),
                'product_type': result.get('product_type', 'N/A'),
                'treatment_areas': result.get('treatment_areas', 'N/A'),
                'content': result.get('content', '')[:300]
            })

        return jsonify({
            'status': 'success',
            'comparison': comparison,
            'agent_type': 'product'
        })

    except Exception as e:
        logger.error(f"Product comparison failed: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/rag-status', methods=['GET'])
def rag_status():
    """Get RAG system status and statistics"""
    try:
        summary = rag_system.get_product_summary()

        return jsonify({
            'status': 'success',
            'indexed': rag_system.vector_store is not None,
            'summary': summary
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Multi-Agent API Server")
    print("=" * 60)
    print(f"LLM Provider: {llm_provider.upper()}")
    print(f"SupervisorAgent: {'[OK] Initialized' if supervisor_agent else '[ERROR] Not initialized'}")
    print(f"RAG System: {'[OK] Ready' if rag_system else '[ERROR] Not ready'}")
    print("=" * 60)
    print("\nAvailable API Endpoints:")
    print("  GET  /api/health              - Health check")
    print("  POST /api/index-products      - Index product websites")
    print("  POST /api/query               - Main query endpoint (routes to appropriate agent)")
    print("  POST /api/product-query       - Direct product information query")
    print("  POST /api/business-query      - Direct business/location query")
    print("  POST /api/compare-products    - Compare two products")
    print("  GET  /api/rag-status          - RAG system status")
    print("=" * 60)

    # Print LangSmith status
    print_langsmith_status()

    print("Server starting on http://localhost:5000")
    print("Ready for React frontend integration!\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
