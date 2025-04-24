from flask import jsonify

def error_response(message, status_code=400):
    """
    Create a standardized error response
    
    Args:
        message (str): Error message
        status_code (int): HTTP status code
        
    Returns:
        tuple: JSON response with error message and status code
    """
    return jsonify({"success": False, "error": message}), status_code

def validate_api_key(api_key, service_name):
    """
    Validate that an API key is present
    
    Args:
        api_key (str): API key to validate
        service_name (str): Name of the service (for error message)
        
    Returns:
        bool: True if valid, raises ValueError if not
    """
    if not api_key:
        raise ValueError(f"{service_name} API key is not set in environment variables")
    return True

def format_response(data, message="Success"):
    """
    Format a standard successful response
    
    Args:
        data (dict): Data to include in response
        message (str): Success message
        
    Returns:
        dict: Formatted response
    """
    return {
        "success": True,
        "message": message,
        "data": data
    } 