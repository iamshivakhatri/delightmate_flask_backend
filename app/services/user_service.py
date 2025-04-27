import logging
import datetime
import os
import sys
from typing import Dict, Optional, Tuple
from postgrest.exceptions import APIError

# Add the parent directory to sys.path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils.supabase import get_supabase_client

# Configure logging
logger = logging.getLogger(__name__)

def save_user_and_gmail_account(
    email: str, 
    gmail_address: str,
    access_token: str,
    refresh_token: str, 
    token_expiry: datetime.datetime,
    history_id: Optional[int] = None
) -> Tuple[bool, Optional[str]]:
    """
    Save or update user and Gmail account information in Supabase.
    
    Args:
        email: User's email address
        gmail_address: Gmail address for OAuth (usually same as email)
        access_token: OAuth access token
        refresh_token: OAuth refresh token
        token_expiry: Token expiration datetime
        history_id: Gmail history ID (optional)
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        supabase = get_supabase_client()
        
        
        # Start a transaction by getting the connection
        # First, check if user exists
        user_response = supabase.table('users').select('id').eq('email', email).execute()
        
        if len(user_response.data) == 0:
            # User doesn't exist, create new user
            logger.info(f"Creating new user with email: {email}")
            user_response = supabase.table('users').insert({"email": email}).execute()
            user_id = user_response.data[0]['id']
        else:
            # User exists, get ID
            user_id = user_response.data[0]['id']
        
        # Check if gmail account exists for this user
        gmail_response = supabase.table('gmail_accounts').select('id').eq('user_id', user_id).execute()
        
        # Prepare account data
        gmail_data = {
            "user_id": user_id,
            "gmail_address": gmail_address,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_expiry": token_expiry.isoformat()
        }
        
        if history_id is not None:
            gmail_data["history_id"] = history_id
        
        if len(gmail_response.data) == 0:
            # Gmail account doesn't exist, create new one
            logger.info(f"Creating new Gmail account for user: {user_id}")
            supabase.table('gmail_accounts').insert(gmail_data).execute()
        else:
            # Gmail account exists, update it
            gmail_id = gmail_response.data[0]['id']
            logger.info(f"Updating Gmail account: {gmail_id} for user: {user_id}")
            supabase.table('gmail_accounts').update(gmail_data).eq('id', gmail_id).execute()
        
        return True, None
    
    except APIError as e:
        logger.error(f"Supabase API error: {str(e)}")
        return False, f"Database error: {str(e)}"
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        return False, str(e)
    except Exception as e:
        logger.error(f"Unexpected error saving user data: {str(e)}")
        return False, f"Unexpected error: {str(e)}"


def get_gmail_account_by_user_email(email: str) -> Optional[Dict]:
    """
    Retrieve a user's Gmail account information from Supabase by email.
    
    Args:
        email: User's email address
        
    Returns:
        Gmail account data or None if not found
    """
    try:
        supabase = get_supabase_client()
        
        # First, get user ID
        user_response = supabase.table('users').select('id').eq('email', email).execute()
        
        if len(user_response.data) == 0:
            logger.info(f"User not found with email: {email}")
            return None
        
        user_id = user_response.data[0]['id']
        
        # Then get Gmail account
        gmail_response = supabase.table('gmail_accounts').select('*').eq('user_id', user_id).execute()
        
        if len(gmail_response.data) == 0:
            logger.info(f"Gmail account not found for user_id: {user_id}")
            return None
            
        return gmail_response.data[0]
    
    except Exception as e:
        logger.error(f"Error retrieving Gmail account: {str(e)}")
        return None
