from flask import jsonify

def success_response(data=None, message="Success", status_code=200):
    """Create a standardized success response"""
    response = {
        'success': True,
        'message': message,
        'data': data
    }
    return jsonify(response), status_code

def error_response(message="Error occurred", status_code=400, errors=None):
    """Create a standardized error response"""
    response = {
        'success': False,
        'message': message,
        'errors': errors
    }
    return jsonify(response), status_code

def validation_error_response(errors, message="Validation failed"):
    """Create a validation error response"""
    return error_response(message=message, status_code=422, errors=errors)
