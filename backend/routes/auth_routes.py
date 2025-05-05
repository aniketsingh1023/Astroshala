# routes/auth_routes.py
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from utils.validators import validate_registration, validate_login
import jwt
import datetime
import os
from email_service import EmailService
import secrets
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)
email_service = EmailService()

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    
    # Log the signup attempt
    logger.info(f"Signup attempt for email: {data.get('email', 'unknown')}")
    
    # Validate input
    validation_error = validate_registration(data)
    if validation_error:
        logger.warning(f"Validation error during signup: {validation_error}")
        return jsonify({'error': validation_error}), 400
    
    # Check if user already exists
    try:
        existing_user = User.find_by_email(data['email'])
        if existing_user:
            logger.info(f"Signup attempt for existing user: {data['email']}")
            return jsonify({'error': 'User already exists'}), 409
    except Exception as e:
        logger.error(f"Error checking for existing user: {str(e)}")
        return jsonify({'error': 'Internal server error during user check'}), 500
    
    try:
        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        verification_expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        
        # Create user with unverified status
        hashed_password = generate_password_hash(data['password'])
        new_user = User(
            email=data['email'],
            password=hashed_password,
            name=data.get('name', ''),
            verification_token=verification_token,
            verification_expiry=verification_expiry,
            is_verified=False
        )
        user_id = new_user.save()
        
        if not user_id:
            logger.error(f"Failed to save new user: {data['email']}")
            return jsonify({'error': 'Failed to create user'}), 500
        
        # Get frontend URL from environment
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        
        # Construct verification URL - make sure it goes to the verify-email page
        verification_url = f"{frontend_url}/auth/verify-email?token={verification_token}"
        logger.info(f"Verification URL created: {verification_url}")
        
        # Send verification email
        email_sent = email_service.send_verification_email(
            data['email'],
            data.get('name', 'User'),
            verification_url
        )
        
        logger.info(f"Email sending result for {data['email']}: {'Success' if email_sent else 'Failed'}")
        
        return jsonify({
            'message': 'Registration successful. Please check your email for verification.',
            'email_sent': email_sent,
            'user_id': user_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error during signup process: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    token = request.json.get('token')
    
    if not token:
        logger.warning("Verification attempt without token")
        return jsonify({'error': 'Verification token is required'}), 400
    
    try:
        # Find user by verification token
        logger.info(f"Searching for user with verification token: {token[:10]}...")
        user = User.find_by_verification_token(token)
        
        if not user:
            logger.warning(f"Invalid verification token: {token[:10]}...")
            return jsonify({'error': 'Invalid verification token'}), 400
        
        # Check if token has expired
        current_time = datetime.datetime.utcnow()
        if current_time > user.get('verification_expiry', current_time):
            logger.warning(f"Expired token for user: {user.get('email')}")
            return jsonify({'error': 'Verification token has expired'}), 400
        
        # Update user verification status
        logger.info(f"Verifying email for user: {user.get('email')}")
        success = User.verify_email(user['_id'])
        
        if not success:
            logger.error(f"Failed to update verification status for user: {user.get('email')}")
            return jsonify({'error': 'Failed to verify email'}), 500
        
        return jsonify({'message': 'Email verified successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error during email verification: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    
    # Validate input
    validation_error = validate_login(data)
    if validation_error:
        return jsonify({'error': validation_error}), 400
    
    try:
        # Find user
        user = User.find_by_email(data['email'])
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if email is verified
        if not user.get('is_verified', False):
            return jsonify({'error': 'Please verify your email before logging in'}), 401
        
        # Check password
        if not check_password_hash(user['password'], data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Get JWT secret
        jwt_secret = os.getenv('JWT_SECRET')
        if not jwt_secret:
            logger.error("JWT_SECRET environment variable is not set")
            return jsonify({'error': 'Configuration error. Please contact support.'}), 500
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': str(user['_id']),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, jwt_secret, algorithm='HS256')
        
        # Check if the token is a bytes object and convert to string if needed
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        
        return jsonify({
            'token': token,
            'user_id': str(user['_id']),
            'name': user.get('name', ''),
            'email': user['email'],
            'has_birth_details': bool(user.get('birth_details', {}))
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    email = request.json.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        user = User.find_by_email(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        if user.get('is_verified', False):
            return jsonify({'error': 'Email is already verified'}), 400
        
        # Generate new verification token
        verification_token = secrets.token_urlsafe(32)
        verification_expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        
        # Update user verification token
        token_updated = User.update_verification_token(
            user['_id'],
            verification_token,
            verification_expiry
        )
        
        if not token_updated:
            logger.error(f"Failed to update verification token for user: {email}")
            return jsonify({'error': 'Failed to generate new verification token'}), 500
        
        # Get frontend URL from environment
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        
        # Construct verification URL
        verification_url = f"{frontend_url}/auth/verify-email?token={verification_token}"
        
        # Send new verification email
        email_sent = email_service.send_verification_email(
            email,
            user.get('name', 'User'),
            verification_url
        )
        
        logger.info(f"Resend verification email to {email}: {'Success' if email_sent else 'Failed'}")
        
        return jsonify({
            'message': 'Verification email resent successfully',
            'email_sent': email_sent
        }), 200
        
    except Exception as e:
        logger.error(f"Error resending verification email: {str(e)}")
        return jsonify({'error': str(e)}), 500