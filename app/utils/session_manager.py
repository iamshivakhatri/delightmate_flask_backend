import logging
from typing import Dict, Optional, Any
from flask import session

from app.services.user_service import get_user_by_email

# Configure logging
logger = logging.getLogger(__name__)

def get_user_info() -> Dict[str, Any]:
    """
    Get user information from session or database
    
    Returns:
        User information dictionary
    """
    # Start with an empty user info object
    user_info = {
        'is_logged_in': False,
        'id': None,
        'email': None,
        'name': None,
        'picture': None
    }
    
    # First try to get from session
    if 'user' in session:
        user_info['is_logged_in'] = True
        user_info['id'] = session['user'].get('id')
        user_info['email'] = session['user'].get('email')
        user_info['name'] = session['user'].get('name')
        user_info['picture'] = session['user'].get('picture')
        
        # If we're missing any info but have email, try to get from database
        if user_info['email'] and (not user_info['name'] or not user_info['picture']):
            try:
                db_user = get_user_by_email(user_info['email'])
                if db_user:
                    # Update session with DB data
                    if not user_info['id']:
                        user_info['id'] = db_user.get('id')
                        session['user']['id'] = db_user.get('id')
                    
                    if not user_info['name'] and db_user.get('name'):
                        user_info['name'] = db_user.get('name')
                        session['user']['name'] = db_user.get('name')
                        
                    if not user_info['picture'] and db_user.get('picture_url'):
                        user_info['picture'] = db_user.get('picture_url')
                        session['user']['picture'] = db_user.get('picture_url')
            except Exception as e:
                logger.error(f"Error retrieving user data from database: {str(e)}")
    
    return user_info

def store_user_info(user_data: Dict[str, Any]) -> None:
    """
    Store user information in session
    
    Args:
        user_data: User information to store
    """
    session['user'] = {
        'id': user_data.get('id'),
        'email': user_data.get('email'),
        'name': user_data.get('name'),
        'picture': user_data.get('picture')
    }
    
def clear_user_info() -> None:
    """
    Clear user information from session
    """
    if 'user' in session:
        del session['user']
    
    if 'google_credentials' in session:
        del session['google_credentials']
