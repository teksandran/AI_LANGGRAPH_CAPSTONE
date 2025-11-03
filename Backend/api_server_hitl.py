"""
Flask API Server for Multi-Agent System with HITL Support
Integrates SupervisorAgent with Human-in-the-Loop approval workflow
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import os
import logging
from dotenv import load_dotenv
from src.supervisor_agent_hitl import SupervisorAgentHITL
from src.hitl_manager import get_hitl_manager
from src.hitl_protocol import DefaultHITLPolicies, HITLPolicy, HITLActionType, HITLPriority, HITLDecision
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

# Initialize HITL Manager and add selective medical policy
hitl_manager = get_hitl_manager()

# Define medical keywords for selective approval
def is_medical_query(data):
    """Check if query or response contains medical information keywords"""
    query = data.get('query', '').lower()
    response = data.get('response', '').lower()

    medical_keywords = [
        'side effects', 'side effect', 'contraindication', 'contraindicated',
        'dosage', 'dose', 'medical', 'adverse', 'reaction', 'allergy',
        'complication', 'risk', 'safety', 'warning', 'precaution',
        'injection', 'treatment', 'procedure', 'clinical', 'prescription'
    ]

    # Check if any medical keyword is present in query or response
    has_medical_content = any(keyword in query or keyword in response for keyword in medical_keywords)

    if has_medical_content:
        logger.info(f"Medical content detected in query or response - HITL approval required")

    return has_medical_content

# Create selective medical information policy
medical_policy = HITLPolicy(
    name="medical_info_approval",
    description="Require human approval only for medical information queries (side effects, dosage, etc.)",
    action_types=[HITLActionType.AGENT_RESPONSE],
    conditions=is_medical_query,
    priority=HITLPriority.HIGH,
    timeout_seconds=300.0,
    auto_decision=HITLDecision.REJECTED
)

hitl_manager.add_policy(medical_policy)
logger.info("✅ HITL Policy Active: Medical information requires human approval")

# Initialize SupervisorAgentHITL
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
        supervisor_agent = SupervisorAgentHITL(
            yelp_api_key=yelp_api_key,
            llm_provider=llm_provider,
            model="gpt-4o-mini" if llm_provider == "openai" else "claude-3-5-sonnet-20241022",
            enable_a2a=True,
            enable_hitl=True  # Enable HITL
        )
        logger.info(f"SupervisorAgentHITL initialized with {llm_provider} and HITL enabled")
    except Exception as e:
        logger.error(f"Failed to initialize SupervisorAgentHITL: {e}")


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'supervisor_agent': supervisor_agent is not None,
        'rag_indexed': rag_system.vector_store is not None,
        'llm_provider': llm_provider,
        'hitl_enabled': supervisor_agent.hitl_enabled if supervisor_agent else False,
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
    Main endpoint for querying the multi-agent system with HITL support
    Routes queries through SupervisorAgentHITL
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

        # Route through SupervisorAgentHITL with human approval workflow
        result = asyncio.run(supervisor_agent.run_with_hitl(query))

        # Calculate duration
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000

        logger.info(f"Response generated: {result.get('response', '')[:100]}...")

        # Log to LangSmith
        if is_langsmith_enabled():
            log_agent_execution(
                agent_name="SupervisorAgentHITL",
                query=query,
                response=result.get('response', ''),
                duration_ms=duration_ms,
                metadata={
                    'endpoint': '/api/query',
                    'status': 'success',
                    'hitl_approved': result.get('hitl_approved', False),
                    'agents_used': result.get('agents_used', [])
                }
            )

        response_data = {
            'status': 'success',
            'query': query,
            'response': result.get('response', ''),
            'agent_type': 'supervisor',
            'duration_ms': round(duration_ms, 2),
            'hitl_approved': result.get('hitl_approved'),
            'reviewer': result.get('reviewer'),
            'modified': result.get('modified', False),
            'agents_used': result.get('agents_used', [])
        }

        # Add HITL-specific fields if present
        if 'hitl_status' in result:
            response_data['hitl_status'] = result['hitl_status']
        if 'hitl_request_id' in result:
            response_data['hitl_request_id'] = result['hitl_request_id']
        if 'hitl_message' in result:
            response_data['hitl_message'] = result['hitl_message']
        if 'hitl_decision' in result:
            response_data['hitl_decision'] = result['hitl_decision']

        return jsonify(response_data)

    except Exception as e:
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        logger.error(f"Query processing failed: {e}", exc_info=True)

        if is_langsmith_enabled():
            log_agent_execution(
                agent_name="SupervisorAgentHITL",
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
    """Direct endpoint for product queries (bypasses supervisor)"""
    try:
        data = request.json
        query = data.get('query', '')
        brand = data.get('brand')
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

        results = rag_system.search_products(query, k=limit, filter_brand=brand)

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
    """Direct endpoint for business/location queries (bypasses supervisor)"""
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

        full_query = f"{query} in {location}" if location else query

        logger.info(f"Business query: {full_query}")

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
    """Endpoint for comparing products (e.g., Botox vs Evolus)"""
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


# ============================================
# HITL API Endpoints
# ============================================

@app.route('/api/hitl/pending', methods=['GET'])
def get_pending_hitl_requests():
    """Get all pending HITL approval requests"""
    try:
        pending_requests = hitl_manager.get_pending_requests()

        return jsonify({
            'status': 'success',
            'pending_requests': pending_requests,
            'total_pending': len(pending_requests)
        })
    except Exception as e:
        logger.error(f"Failed to get pending HITL requests: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/hitl/request/<request_id>', methods=['GET'])
def get_hitl_request(request_id):
    """Get specific HITL request details"""
    try:
        pending_requests = hitl_manager.get_pending_requests()
        request = next((r for r in pending_requests if r['request_id'] == request_id), None)

        if not request:
            return jsonify({
                'status': 'error',
                'message': 'Request not found'
            }), 404

        return jsonify({
            'status': 'success',
            **request
        })
    except Exception as e:
        logger.error(f"Failed to get HITL request: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/hitl/approve/<request_id>', methods=['POST'])
def approve_hitl_request(request_id):
    """Approve a pending HITL request"""
    try:
        data = request.json or {}
        reviewer_id = data.get('reviewer_id', 'human_reviewer')
        comments = data.get('comments', '')

        from src.hitl_protocol import HITLDecision, HITLResponse

        # Create HITL response object
        hitl_response = HITLResponse(
            request_id=request_id,
            decision=HITLDecision.APPROVED,
            decided_by=reviewer_id,
            feedback=comments
        )

        success = hitl_manager.submit_response(hitl_response)

        if success:
            return jsonify({
                'status': 'success',
                'message': 'Request approved',
                'request_id': request_id
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to approve request'
            }), 500

    except Exception as e:
        logger.error(f"Failed to approve HITL request: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/hitl/reject/<request_id>', methods=['POST'])
def reject_hitl_request(request_id):
    """Reject a pending HITL request"""
    try:
        data = request.json
        reviewer_id = data.get('reviewer_id')
        comments = data.get('comments', '')

        if not reviewer_id:
            return jsonify({
                'status': 'error',
                'message': 'reviewer_id is required'
            }), 400

        from src.hitl_protocol import HITLDecision

        success = asyncio.run(hitl_manager.submit_response(
            request_id=request_id,
            decision=HITLDecision.REJECTED,
            reviewer_id=reviewer_id,
            comments=comments
        ))

        if success:
            return jsonify({
                'status': 'success',
                'message': 'Request rejected',
                'request_id': request_id
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to reject request'
            }), 500

    except Exception as e:
        logger.error(f"Failed to reject HITL request: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/hitl/modify/<request_id>', methods=['POST'])
def modify_hitl_request(request_id):
    """Modify and approve a pending HITL request"""
    try:
        data = request.json
        reviewer_id = data.get('reviewer_id')
        modified_data = data.get('modified_data', {})
        comments = data.get('comments', '')

        if not reviewer_id:
            return jsonify({
                'status': 'error',
                'message': 'reviewer_id is required'
            }), 400

        from src.hitl_protocol import HITLDecision

        success = asyncio.run(hitl_manager.submit_response(
            request_id=request_id,
            decision=HITLDecision.MODIFIED,
            reviewer_id=reviewer_id,
            comments=comments,
            modified_data=modified_data
        ))

        if success:
            return jsonify({
                'status': 'success',
                'message': 'Request modified and approved',
                'request_id': request_id
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to modify request'
            }), 500

    except Exception as e:
        logger.error(f"Failed to modify HITL request: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/hitl/escalate/<request_id>', methods=['POST'])
def escalate_hitl_request(request_id):
    """Escalate a pending HITL request"""
    try:
        data = request.json
        reviewer_id = data.get('reviewer_id')
        comments = data.get('comments', '')

        if not reviewer_id:
            return jsonify({
                'status': 'error',
                'message': 'reviewer_id is required'
            }), 400

        from src.hitl_protocol import HITLDecision

        success = asyncio.run(hitl_manager.submit_response(
            request_id=request_id,
            decision=HITLDecision.ESCALATED,
            reviewer_id=reviewer_id,
            comments=comments
        ))

        if success:
            return jsonify({
                'status': 'success',
                'message': 'Request escalated',
                'request_id': request_id
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to escalate request'
            }), 500

    except Exception as e:
        logger.error(f"Failed to escalate HITL request: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/hitl/statistics', methods=['GET'])
def get_hitl_statistics():
    """Get HITL system statistics"""
    try:
        stats = hitl_manager.get_statistics()

        return jsonify({
            'status': 'success',
            **stats
        })
    except Exception as e:
        logger.error(f"Failed to get HITL statistics: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/hitl/history', methods=['GET'])
def get_hitl_history():
    """Get HITL approval history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = hitl_manager.get_history(limit=limit)

        return jsonify({
            'status': 'success',
            'history': history,
            'total_count': len(history)
        })
    except Exception as e:
        logger.error(f"Failed to get HITL history: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Multi-Agent API Server with HITL Support")
    print("=" * 60)
    print(f"LLM Provider: {llm_provider.upper()}")
    print(f"SupervisorAgentHITL: {'[OK] Initialized' if supervisor_agent else '[ERROR] Not initialized'}")
    print(f"HITL Enabled: {'[OK] Active' if supervisor_agent and supervisor_agent.hitl_enabled else '[OFF] Disabled'}")
    print(f"RAG System: {'[OK] Ready' if rag_system else '[ERROR] Not ready'}")
    print("=" * 60)
    print("\nAvailable API Endpoints:")
    print("  GET  /api/health              - Health check")
    print("  POST /api/index-products      - Index product websites")
    print("  POST /api/query               - Main query endpoint (with HITL)")
    print("  POST /api/product-query       - Direct product information query")
    print("  POST /api/business-query      - Direct business/location query")
    print("  POST /api/compare-products    - Compare two products")
    print("  GET  /api/rag-status          - RAG system status")
    print("\n  HITL Endpoints:")
    print("  GET  /api/hitl/pending        - Get pending approval requests")
    print("  GET  /api/hitl/request/<id>   - Get specific request")
    print("  POST /api/hitl/approve/<id>   - Approve request")
    print("  POST /api/hitl/reject/<id>    - Reject request")
    print("  POST /api/hitl/modify/<id>    - Modify and approve")
    print("  POST /api/hitl/escalate/<id>  - Escalate request")
    print("  GET  /api/hitl/statistics     - Get HITL statistics")
    print("  GET  /api/hitl/history        - Get approval history")
    print("=" * 60)

    # Print LangSmith status
    print_langsmith_status()

    print("Server starting on http://localhost:5000")
    print("HITL System Active - Human approval required for medical information")
    print("Ready for React frontend integration!\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
