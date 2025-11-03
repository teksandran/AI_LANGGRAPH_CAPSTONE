"""
Flask Web Application - Main Entry Point
Provides REST API and Web UI for Aesthetic Product Search
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import asyncio
import os
import logging
import json
import re
from dotenv import load_dotenv
from src.rag_system import get_rag_system
from src.tools import initialize_tools, search_beauty_salons, search_beauty_products
from src.langgraph_agent import BeautySearchAgent

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains on all routes

# Configure logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)
app.logger.setLevel(logging.ERROR)

# Initialize systems
rag_system = get_rag_system()
yelp_api_key = os.getenv("YELP_API_KEY")

if yelp_api_key:
    initialize_tools(yelp_api_key)


# Define product keywords for RAG search
PRODUCT_KEYWORDS = [
    'botox', 'evous', 'filler', 'dermal filler', 'hyaluronic acid',
    'retinol', 'peptide', 'serum', 'cream', 'lotion', 'moisturizer',
    'cleanser', 'toner', 'exfoliant', 'mask', 'treatment', 'product',
    'brand', 'ingredient', 'formulation', 'skincare', 'anti-aging',
    'vitamin c', 'niacinamide', 'salicylic acid', 'glycolic acid',
    'ceramide', 'collagen', 'elastin', 'antioxidant'
]

# Define service/location keywords for Yelp API search
SERVICE_KEYWORDS = [
    'salon', 'spa', 'clinic', 'doctor', 'dermatologist', 'aesthetician',
    'near me', 'in', 'location', 'appointment', 'booking', 'service',
    'treatment center', 'medical spa', 'beauty salon', 'nail salon',
    'hair salon', 'massage', 'facial', 'where', 'find', 'best',
    'recommended', 'reviews', 'rating'
]


def determine_search_type(query: str) -> str:
    """
    Determine whether to use RAG (for products) or Yelp API (for services/locations)
    based on the search query content.
    """
    query_lower = query.lower()
    
    # Count product vs service keywords
    product_score = sum(1 for keyword in PRODUCT_KEYWORDS if keyword in query_lower)
    service_score = sum(1 for keyword in SERVICE_KEYWORDS if keyword in query_lower)
    
    # Check for location patterns (city, state, zip)
    location_pattern = r'\b(in|near|at)\s+[A-Za-z\s,]+(?:CA|NY|TX|FL|IL|PA|OH|GA|NC|MI|NJ|VA|WA|AZ|MA|TN|IN|MO|MD|WI|CO|MN|SC|AL|LA|KY|OR|OK|CT|IA|MS|AR|KS|UT|NV|NM|WV|NE|ID|HI|NH|ME|MT|RI|DE|SD|ND|AK|VT|WY|DC)\b'
    has_location = bool(re.search(location_pattern, query_lower))
    
    # Decision logic
    if has_location or service_score > product_score:
        return "yelp"
    else:
        return "rag"


@app.route('/')
def home():
    """Home page"""
    return render_template('index.html')


@app.route('/api/index-products', methods=['POST'])
def index_products():
    """Index aesthetic product websites"""
    try:
        stats = asyncio.run(rag_system.index_product_websites())
        return jsonify({
            'status': 'success',
            'message': 'Products indexed successfully',
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/smart-search', methods=['POST'])
def smart_search():
    """
    Intelligent search that routes to RAG for products or Yelp API for services/locations
    """
    try:
        data = request.json
        query = data.get('query', '')
        location = data.get('location', '')
        
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Query is required'
            }), 400
        
        # Determine search type
        search_type = determine_search_type(query)
        
        if search_type == "rag":
            # Use RAG for product searches
            try:
                response = asyncio.run(rag_system.search(query))
                return jsonify({
                    'status': 'success',
                    'search_type': 'product_search',
                    'query': query,
                    'source': 'RAG',
                    'results': {
                        'answer': response,
                        'type': 'product_information'
                    }
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': f'RAG search failed: {str(e)}'
                }), 500
                
        else:  # search_type == "yelp"
            # Use Yelp API for service/location searches
            try:
                # Extract location from query if not provided separately
                if not location:
                    # Simple location extraction
                    location_match = re.search(r'\b(?:in|near|at)\s+([A-Za-z\s,]+)', query.lower())
                    if location_match:
                        location = location_match.group(1).strip()
                    else:
                        location = "San Francisco, CA"  # Default location
                
                # Determine if it's a salon or product store search
                if any(word in query.lower() for word in ['salon', 'spa', 'clinic', 'service', 'treatment']):
                    result_str = asyncio.run(search_beauty_salons(location, query, 5))
                    search_category = 'beauty_services'
                else:
                    result_str = asyncio.run(search_beauty_products(location, query, 5))
                    search_category = 'beauty_stores'
                
                result = json.loads(result_str)
                
                if 'error' in result:
                    return jsonify({
                        'status': 'error',
                        'message': result['error']
                    }), 500
                
                return jsonify({
                    'status': 'success',
                    'search_type': search_category,
                    'query': query,
                    'location': location,
                    'source': 'Yelp API',
                    'results': {
                        'businesses': result.get('businesses', []),
                        'total': result.get('total', 0),
                        'type': 'business_listings'
                    }
                })
                
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': f'Yelp search failed: {str(e)}'
                }), 500
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/search-products', methods=['POST'])
def search_products():
    """Search for aesthetic products"""
    try:
        data = request.json
        query = data.get('query', '')
        brand = data.get('brand')
        limit = data.get('limit', 5)

        if not rag_system.vector_store:
            return jsonify({
                'status': 'error',
                'message': 'Index not created. Please index products first.'
            }), 400

        results = rag_system.search_products(
            query=query,
            k=limit,
            filter_brand=brand
        )

        return jsonify({
            'status': 'success',
            'query': query,
            'results': results,
            'total': len(results)
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/search-treatments', methods=['POST'])
def search_treatments():
    """Search treatments by area"""
    try:
        data = request.json
        area = data.get('area', '')
        limit = data.get('limit', 5)

        if not rag_system.vector_store:
            return jsonify({
                'status': 'error',
                'message': 'Index not created. Please index products first.'
            }), 400

        results = rag_system.search_aesthetic_treatments(
            treatment_area=area,
            k=limit
        )

        return jsonify({
            'status': 'success',
            'treatment_area': area,
            'results': results,
            'total': len(results)
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/product-summary', methods=['GET'])
def product_summary():
    """Get summary of indexed products"""
    try:
        brand = request.args.get('brand')
        summary = rag_system.get_product_summary(brand=brand)

        return jsonify({
            'status': 'success',
            'summary': summary
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/search-type', methods=['POST'])
def get_search_type():
    """
    Test endpoint to see which search type would be used for a query
    """
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Query is required'
            }), 400
        
        search_type = determine_search_type(query)
        
        return jsonify({
            'status': 'success',
            'query': query,
            'search_type': search_type,
            'explanation': 'RAG for product searches, Yelp API for service/location searches'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'indexed': rag_system.vector_store is not None,
        'documents': len(rag_system.documents) if rag_system.documents else 0
    })


if __name__ == '__main__':
    import sys
    
    # Set UTF-8 encoding for Windows
    if sys.platform == 'win32':
        import os
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Suppress werkzeug logs
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    try:
        print("Flask API Server started at http://localhost:8080")
        print("Ready to serve React frontend requests...")
        print("Available endpoints:")
        print("- POST /api/smart-search")
        print("- POST /api/search-type")
        print("- GET /health")
        
        app.run(host='127.0.0.1', port=8080, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"Error starting Flask app: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
