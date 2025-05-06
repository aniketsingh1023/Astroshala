# routes/contact_routes.py
import os
import logging
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from bson import ObjectId

logger = logging.getLogger(__name__)

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/submit', methods=['POST'])
def submit_contact():
    """Handle contact form submissions"""
    try:
        # Get request data
        data = request.json
        logger.info(f"Received contact form submission: {data}")
        
        # Validate required fields
        required_fields = ['name', 'email', 'contactNumber', 'birthDate', 'birthTime', 'birthPlace']
        for field in required_fields:
            if not data.get(field):
                logger.warning(f"Missing required field: {field}")
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        # Get database connection
        mongo = current_app.extensions.get('pymongo')
        if not mongo:
            logger.error("MongoDB extension not found in Flask app")
            return jsonify({
                'success': False,
                'error': 'Database connection error'
            }), 500
        
        # Format data for MongoDB
        contact_data = {
            'name': data.get('name'),
            'email': data.get('email'),
            'contactNumber': data.get('contactNumber'),
            'birthDate': data.get('birthDate'),
            'birthTime': data.get('birthTime'),
            'birthPlace': data.get('birthPlace'),
            'message': data.get('message', ''),
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Insert directly into the default database for simplicity
        # We'll use a collection named 'contact_details'
        result = mongo.db.contact_details.insert_one(contact_data)
        logger.info(f"Contact form saved with ID: {result.inserted_id}")
        
        # Skip email notification for now to simplify debugging
        # We'll add it back once the basic functionality works
        
        return jsonify({
            'success': True,
            'message': 'Form submitted successfully',
            'id': str(result.inserted_id)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in contact form submission: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process contact form',
            'details': str(e)
        }), 500
