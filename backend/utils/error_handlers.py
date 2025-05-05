# utils/error_handlers.py
from flask import jsonify
from werkzeug.exceptions import HTTPException

def handle_bad_request(error):
    """
    Handle bad request errors
    """
    return jsonify({
        'error': 'Bad Request',
        'message': str(error)
    }), 400

def handle_unauthorized(error):
    """
    Handle unauthorized access errors
    """
    return jsonify({
        'error': 'Unauthorized',
        'message': str(error)
    }), 401

def handle_forbidden(error):
    """
    Handle forbidden access errors
    """
    return jsonify({
        'error': 'Forbidden',
        'message': str(error)
    }), 403

def handle_not_found(error):
    """
    Handle resource not found errors
    """
    return jsonify({
        'error': 'Not Found',
        'message': str(error)
    }), 404

def handle_server_error(error):
    """
    Handle internal server errors
    """
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500

def register_error_handlers(app):
    """
    Register error handlers for the Flask application
    """
    app.errorhandler(400)(handle_bad_request)
    app.errorhandler(401)(handle_unauthorized)
    app.errorhandler(403)(handle_forbidden)
    app.errorhandler(404)(handle_not_found)
    app.errorhandler(500)(handle_server_error)
    
    # Handle generic exceptions
    @app.errorhandler(Exception)
    def handle_exception(error):
        """
        Catch-all error handler
        """
        # Pass through HTTP errors
        if isinstance(error, HTTPException):
            return error
        
        # Log the error for server-side tracking
        app.logger.error(f"Unhandled Exception: {str(error)}")
        
        # Return a generic server error response
        return handle_server_error(error)