#!/usr/bin/env python3
"""
Simple test Flask app to verify endpoints work
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Test Flask App Running"})

@app.route('/api/smart-search', methods=['POST'])
def smart_search():
    """Test smart search endpoint"""
    data = request.json
    query = data.get('query', '')
    
    return jsonify({
        'status': 'success',
        'query': query,
        'message': 'Smart search endpoint is working!',
        'test': True
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'test': True})

if __name__ == '__main__':
    print("🚀 Test Flask Server started at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)