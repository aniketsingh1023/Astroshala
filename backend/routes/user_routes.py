# routes/user_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
import logging
import traceback

logger = logging.getLogger(__name__)
user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get the current user's profile"""
    try:
        logger.info("Profile information requested")
        
        # Get current user ID from JWT
        current_user_id = get_jwt_identity()
        logger.info(f"Fetching profile for user ID: {current_user_id}")
        
        # Find user by ID
        user = User.find_by_id(current_user_id)
        
        if not user:
            logger.warning(f"User not found: {current_user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        # Return user profile without sensitive information
        profile = {
            'email': user.get('email', ''),
            'name': user.get('name', ''),
            'birth_details': user.get('birth_details', {}),
            'is_verified': user.get('is_verified', False),
            'created_at': user.get('created_at', '')
        }
        
        logger.info(f"Profile successfully retrieved for {user.get('email')}")
        return jsonify(profile), 200
        
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Failed to retrieve profile', 'details': str(e)}), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update the current user's profile"""
    try:
        logger.info("Profile update requested")
        
        # Get current user ID from JWT
        current_user_id = get_jwt_identity()
        logger.info(f"Updating profile for user ID: {current_user_id}")
        
        # Get request data
        data = request.json or {}
        
        # Validate input
        allowed_fields = ['name', 'birth_details']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            logger.warning("No valid fields to update")
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Update user profile
        success = User.update_profile(current_user_id, update_data)
        
        if not success:
            logger.error(f"Failed to update profile for user ID: {current_user_id}")
            return jsonify({'error': 'Failed to update profile'}), 500
        
        logger.info(f"Profile successfully updated for user ID: {current_user_id}")
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500

@user_bp.route('/birth-details', methods=['POST'])
@jwt_required()
def set_birth_details():
    """Set the user's birth details"""
    try:
        logger.info("Birth details update requested")
        
        # Get current user ID from JWT
        current_user_id = get_jwt_identity()
        logger.info(f"Setting birth details for user ID: {current_user_id}")
        
        # Get request data
        data = request.json or {}
        
        # Validate required fields
        required_fields = ['date', 'time', 'place']
        if not all(field in data for field in required_fields):
            logger.warning("Missing required birth details fields")
            return jsonify({
                'error': 'Missing required fields', 
                'required': required_fields
            }), 400
        
        # Update birth details
        birth_details = {
            'date': data.get('date'),
            'time': data.get('time'),
            'place': data.get('place'),
            'latitude': data.get('latitude', '0'),
            'longitude': data.get('longitude', '0')
        }
        
        success = User.update_birth_details(current_user_id, birth_details)
        
        if not success:
            logger.error(f"Failed to update birth details for user ID: {current_user_id}")
            return jsonify({'error': 'Failed to update birth details'}), 500
        
        logger.info(f"Birth details successfully updated for user ID: {current_user_id}")
        return jsonify({
            'message': 'Birth details updated successfully',
            'birth_details': birth_details
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating birth details: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Failed to update birth details', 'details': str(e)}), 500