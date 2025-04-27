import logging
import datetime
import os
import sys
from typing import Dict, Optional, Tuple, Any
from postgrest.exceptions import APIError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

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
    name: Optional[str] = None,
    picture_url: Optional[str] = None,
    history_id: Optional[int] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
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
            # Only include columns that exist in the schema
            user_data = {"email": email}
            
            # Try to include name and picture if the columns exist
            try:
                # First check if columns exist by fetching schema
                schema_check = supabase.table('users').select('*').limit(1).execute()
                columns = schema_check.data[0].keys() if schema_check.data else []
                
                if 'name' in columns and name:
                    user_data["name"] = name
                if 'picture_url' in columns and picture_url:
                    user_data["picture_url"] = picture_url
            except Exception as e:
                logger.warning(f"Could not check schema, using minimal fields: {str(e)}")
            
            user_response = supabase.table('users').insert(user_data).execute()
            user_id = user_response.data[0]['id']
        else:
            # User exists, get ID and update profile if needed
            user_id = user_response.data[0]['id']
            
            # Only update if name or picture is provided
            if name or picture_url:
                # Only include columns that exist in the schema
                user_update = {}
                
                # Try to include name and picture if the columns exist
                try:
                    # First check if columns exist by fetching schema
                    schema_check = supabase.table('users').select('*').limit(1).execute()
                    columns = schema_check.data[0].keys() if schema_check.data else []
                    
                    if 'name' in columns and name:
                        user_update["name"] = name
                    if 'picture_url' in columns and picture_url:
                        user_update["picture_url"] = picture_url
                except Exception as e:
                    logger.warning(f"Could not check schema, skipping profile update: {str(e)}")
                
                if user_update:
                    supabase.table('users').update(user_update).eq('id', user_id).execute()
        
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
        
        # Return user_id alongside success status
        return True, None, str(user_id)
    
    except APIError as e:
        logger.error(f"Supabase API error: {str(e)}")
        return False, f"Database error: {str(e)}", None
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        return False, str(e), None
    except Exception as e:
        logger.error(f"Unexpected error saving user data: {str(e)}")
        return False, f"Unexpected error: {str(e)}", None


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


def get_user_profile_info(credentials: Credentials) -> Dict[str, Any]:
    """
    Get user profile information from Google API
    
    Args:
        credentials: Google OAuth credentials
        
    Returns:
        Dictionary with user profile information (name, email, picture)
    """
    try:
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        
        return {
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'picture': user_info.get('picture')
        }
    except Exception as e:
        logger.error(f"Error getting user profile info: {str(e)}")
        return {'email': None, 'name': None, 'picture': None}


def get_user_by_email(email: str) -> Optional[Dict]:
    """
    Retrieve a user's information from Supabase by email.
    
    Args:
        email: User's email address
        
    Returns:
        User data or None if not found
    """
    try:
        supabase = get_supabase_client()
        
        user_response = supabase.table('users').select('*').eq('email', email).execute()
        
        if len(user_response.data) == 0:
            logger.info(f"User not found with email: {email}")
            return None
            
        return user_response.data[0]
        
    except Exception as e:
        logger.error(f"Error retrieving user: {str(e)}")
        return None

def get_credentials_from_supabase(email: str) -> Tuple[Optional[Credentials], Optional[Dict]]:
    """
    Get Google credentials and user data from Supabase using the user's email
    
    Args:
        email: User's email address
        
    Returns:
        Tuple of (Credentials object or None, User data or None)
    """
    try:
        gmail_account = get_gmail_account_by_user_email(email)
        user_data = get_user_by_email(email)
        
        if not gmail_account or not gmail_account.get('refresh_token'):
            return None, user_data
            
        # Create credentials object from stored data
        credentials = Credentials(
            token=gmail_account.get('access_token'),
            refresh_token=gmail_account.get('refresh_token'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            scopes=[
                'https://mail.google.com/',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
                'https://www.googleapis.com/auth/calendar.readonly',
                'https://www.googleapis.com/auth/calendar.events'
            ]
        )
        
        return credentials, user_data
        
    except Exception as e:
        logger.error(f"Error getting credentials from Supabase: {str(e)}")
        return None, None
