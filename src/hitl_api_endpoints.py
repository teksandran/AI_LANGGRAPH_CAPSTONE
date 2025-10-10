"""
HITL API Endpoints
Flask routes for human-in-the-loop approval workflow.
"""

from flask import Blueprint, request, jsonify
from typing import Optional
import logging
from .hitl_manager import get_hitl_manager
from .hitl_protocol import (
    HITLDecision,
    HITLActionType,
    HITLPriority,
    create_hitl_response,
    DefaultHITLPolicies
)


logger = logging.getLogger(__name__)

# Create blueprint for HITL endpoints
hitl_bp = Blueprint('hitl', __name__, url_prefix='/api/hitl')


@hitl_bp.route('/health', methods=['GET'])
def hitl_health():
    """Check HITL system health."""
    try:
        manager = get_hitl_manager()
        stats = manager.get_statistics()

        return jsonify({
            'status': 'healthy',
            'statistics': stats
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@hitl_bp.route('/pending', methods=['GET'])
def get_pending_requests():
    """
    Get all pending approval requests.

    Query parameters:
    - agent_id: Filter by agent ID
    - action_type: Filter by action type
    - priority: Filter by priority
    """
    try:
        manager = get_hitl_manager()

        # Get filters from query params
        agent_id = request.args.get('agent_id')
        action_type_str = request.args.get('action_type')
        priority_str = request.args.get('priority')

        action_type = (
            HITLActionType(action_type_str)
            if action_type_str
            else None
        )
        priority = (
            HITLPriority(priority_str)
            if priority_str
            else None
        )

        # Get requests
        requests = manager.get_pending_requests(
            agent_id=agent_id,
            action_type=action_type,
            priority=priority
        )

        return jsonify({
            'status': 'success',
            'count': len(requests),
            'requests': [r.to_dict() for r in requests]
        })

    except Exception as e:
        logger.error(f"Error getting pending requests: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@hitl_bp.route('/request/<request_id>', methods=['GET'])
def get_request_details(request_id: str):
    """Get details of a specific request."""
    try:
        manager = get_hitl_manager()
        req = manager.get_request(request_id)

        if not req:
            return jsonify({
                'status': 'error',
                'message': f'Request {request_id} not found'
            }), 404

        return jsonify({
            'status': 'success',
            'request': req.to_dict()
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@hitl_bp.route('/approve/<request_id>', methods=['POST'])
def approve_request(request_id: str):
    """
    Approve a pending request.

    JSON body (optional):
    - feedback: Human feedback/comments
    - decided_by: Identifier of who approved
    """
    try:
        manager = get_hitl_manager()

        # Get request
        req = manager.get_request(request_id)
        if not req:
            return jsonify({
                'status': 'error',
                'message': f'Request {request_id} not found'
            }), 404

        # Get optional data
        data = request.json or {}
        feedback = data.get('feedback')
        decided_by = data.get('decided_by', 'human')

        # Create response
        response = create_hitl_response(
            request_id=request_id,
            decision=HITLDecision.APPROVED,
            feedback=feedback,
            decided_by=decided_by
        )

        # Submit response
        success = manager.submit_response(response)

        if success:
            return jsonify({
                'status': 'success',
                'message': 'Request approved',
                'response': response.to_dict()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to submit response'
            }), 500

    except Exception as e:
        logger.error(f"Error approving request: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@hitl_bp.route('/reject/<request_id>', methods=['POST'])
def reject_request(request_id: str):
    """
    Reject a pending request.

    JSON body (optional):
    - feedback: Reason for rejection
    - decided_by: Identifier of who rejected
    """
    try:
        manager = get_hitl_manager()

        # Get request
        req = manager.get_request(request_id)
        if not req:
            return jsonify({
                'status': 'error',
                'message': f'Request {request_id} not found'
            }), 404

        # Get optional data
        data = request.json or {}
        feedback = data.get('feedback', 'Rejected by human reviewer')
        decided_by = data.get('decided_by', 'human')

        # Create response
        response = create_hitl_response(
            request_id=request_id,
            decision=HITLDecision.REJECTED,
            feedback=feedback,
            decided_by=decided_by
        )

        # Submit response
        success = manager.submit_response(response)

        if success:
            return jsonify({
                'status': 'success',
                'message': 'Request rejected',
                'response': response.to_dict()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to submit response'
            }), 500

    except Exception as e:
        logger.error(f"Error rejecting request: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@hitl_bp.route('/modify/<request_id>', methods=['POST'])
def modify_request(request_id: str):
    """
    Approve with modifications.

    JSON body (required):
    - modified_data: The modified action data
    - feedback: Explanation of modifications (optional)
    - decided_by: Identifier of who modified (optional)
    """
    try:
        manager = get_hitl_manager()

        # Get request
        req = manager.get_request(request_id)
        if not req:
            return jsonify({
                'status': 'error',
                'message': f'Request {request_id} not found'
            }), 404

        # Get modified data
        data = request.json
        if not data or 'modified_data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'modified_data is required'
            }), 400

        modified_data = data['modified_data']
        feedback = data.get('feedback', 'Modified by human reviewer')
        decided_by = data.get('decided_by', 'human')

        # Create response
        response = create_hitl_response(
            request_id=request_id,
            decision=HITLDecision.MODIFIED,
            modified_data=modified_data,
            feedback=feedback,
            decided_by=decided_by
        )

        # Submit response
        success = manager.submit_response(response)

        if success:
            return jsonify({
                'status': 'success',
                'message': 'Request approved with modifications',
                'response': response.to_dict()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to submit response'
            }), 500

    except Exception as e:
        logger.error(f"Error modifying request: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@hitl_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get HITL system statistics."""
    try:
        manager = get_hitl_manager()
        stats = manager.get_statistics()

        return jsonify({
            'status': 'success',
            'statistics': stats
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@hitl_bp.route('/history', methods=['GET'])
def get_history():
    """
    Get approval history.

    Query parameters:
    - limit: Maximum number of items to return
    - agent_id: Filter by agent ID
    """
    try:
        manager = get_hitl_manager()

        limit_str = request.args.get('limit')
        limit = int(limit_str) if limit_str else None
        agent_id = request.args.get('agent_id')

        history = manager.get_history(limit=limit, agent_id=agent_id)

        return jsonify({
            'status': 'success',
            'count': len(history),
            'history': history
        })

    except Exception as e:
        logger.error(f"Error getting history: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@hitl_bp.route('/policies', methods=['GET'])
def get_policies():
    """Get active HITL policies."""
    try:
        manager = get_hitl_manager()
        policies = manager.get_policies()

        return jsonify({
            'status': 'success',
            'count': len(policies),
            'policies': [
                {
                    'name': p.name,
                    'description': p.description,
                    'action_types': [at.value for at in p.action_types],
                    'priority': p.priority.value,
                    'timeout_seconds': p.timeout_seconds,
                    'auto_decision': p.auto_decision.value if p.auto_decision else None
                }
                for p in policies
            ]
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@hitl_bp.route('/policies', methods=['POST'])
def add_policy():
    """
    Add a new HITL policy.

    JSON body:
    - policy_name: Name of predefined policy (e.g., "always_approve_responses")
    """
    try:
        data = request.json
        if not data or 'policy_name' not in data:
            return jsonify({
                'status': 'error',
                'message': 'policy_name is required'
            }), 400

        policy_name = data['policy_name']

        # Get predefined policy
        policy_method = getattr(DefaultHITLPolicies, policy_name, None)
        if not policy_method:
            return jsonify({
                'status': 'error',
                'message': f'Unknown policy: {policy_name}'
            }), 400

        policy = policy_method()

        # Add policy
        manager = get_hitl_manager()
        manager.add_policy(policy)

        return jsonify({
            'status': 'success',
            'message': f'Policy {policy_name} added',
            'policy': {
                'name': policy.name,
                'description': policy.description
            }
        })

    except Exception as e:
        logger.error(f"Error adding policy: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@hitl_bp.route('/policies/<policy_name>', methods=['DELETE'])
def remove_policy(policy_name: str):
    """Remove a HITL policy."""
    try:
        manager = get_hitl_manager()
        success = manager.remove_policy(policy_name)

        if success:
            return jsonify({
                'status': 'success',
                'message': f'Policy {policy_name} removed'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Policy {policy_name} not found'
            }), 404

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
