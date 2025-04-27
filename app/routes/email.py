from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, flash, g
import os
import sys
import json
import datetime
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
import logging

# Add the parent directory to sys.path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.user_service import (save_user_and_gmail_account, get_credentials_from_supabase, 
                                  get_user_profile_info, get_user_by_email)
from app.utils.session_manager import get_user_info

# Configure logging
logger = logging.getLogger(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Allow OAuth over HTTP for development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

email_bp = Blueprint('email', __name__, url_prefix='/email')

def get_user_email(credentials):
    """
    Get user email from Google API using the provided credentials
    
    Args:
        credentials: Google OAuth credentials
        
    Returns:
        User's email address or None if not available
    """
    try:
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        return user_info.get('email')
    except Exception as e:
        logger.error(f"Error getting user email: {str(e)}")
        return None

# Define all possible scopes that Google might return
SCOPES = [
    'https://mail.google.com/',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/calendar',
    'openid'
]

def build_client_config():
    """Dynamically build the Google client config from environment variables"""
    return {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "project_id": os.getenv("GOOGLE_PROJECT_ID"),
            "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
            "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URIS")]
        }
    }

@email_bp.route('/')
def email_home():
    """Display the email inbox or redirect to login if not authenticated"""
    # Check if user is logged in via session
    # if 'google_credentials' in session:
    if session.get('google_credentials') and session.get('user'):

        creds_data = session['google_credentials']
        credentials = Credentials(
            token=creds_data['token'],
            refresh_token=creds_data['refresh_token'],
            token_uri=creds_data['token_uri'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            scopes=creds_data['scopes']
        )
        
        # Check if token expired and refresh if needed
        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                # Update session with new token
                session['google_credentials']['token'] = credentials.token
                if hasattr(credentials, 'expiry'):
                    session['google_credentials']['expiry'] = credentials.expiry.isoformat()
            except Exception as e:
                logger.error(f"Error refreshing token: {str(e)}")
                return redirect(url_for('email.email_login'))
                
        # Get user profile info for display
        user_info = get_user_profile_info(credentials)
        
        # Build Gmail service for inbox display
        try:
            gmail_service = build('gmail', 'v1', credentials=credentials)
            
            # Fetch messages for inbox display
            # This is a basic implementation - will enhance with more features
            messages_result = gmail_service.users().messages().list(
                userId='me',
                maxResults=20,
                q='in:inbox'
            ).execute()
            
            # Process messages for display
            messages = []
            if 'messages' in messages_result:
                for msg in messages_result['messages']:
                    message_data = gmail_service.users().messages().get(
                        userId='me', 
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['From', 'Subject', 'Date']
                    ).execute()
                    
                    # Extract headers
                    headers = {}
                    for header in message_data.get('payload', {}).get('headers', []):
                        headers[header['name']] = header['value']
                    
                    # Add processed message to list
                    messages.append({
                        'id': msg['id'],
                        'snippet': message_data.get('snippet', ''),
                        'from': headers.get('From', ''),
                        'subject': headers.get('Subject', '(No Subject)'),
                        'date': headers.get('Date', ''),
                        'unread': 'UNREAD' in message_data.get('labelIds', [])
                    })
            
            return render_template('email/inbox.html', 
                                  user=user_info,
                                  messages=messages)
                                  
        except Exception as e:
            logger.error(f"Error accessing Gmail API: {str(e)}")
            flash("Error accessing your Gmail. Please try again.", "error")
            return redirect(url_for('email.email_login'))
    
    # Not logged in, try to get credentials from database
    if 'user' in session and session['user'].get('email'):
        # Attempt to recover credentials from Supabase
        credentials, user_data = get_credentials_from_supabase(session['user']['email'])
        
        if credentials:
            # Store credentials in session
            session['google_credentials'] = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'email': session['user']['email']
            }
            
            # Redirect back to the email home to process with new credentials
            return redirect(url_for('email.email_home'))
    
    # No valid credentials, redirect to login
    return redirect(url_for('email.email_login'))

# @email_bp.route('/login')
# def email_login():
#     """Redirect to Google OAuth2 login"""
#     client_config = build_client_config()
    
#     logger.info("Starting OAuth2 login flow")
    
#     flow = Flow.from_client_config(
#         client_config,
#         scopes=SCOPES,  # Use all possible scopes here
#         redirect_uri=url_for('email.oauth2callback', _external=True)
#     )

#     authorization_url, state = flow.authorization_url(
#         access_type='offline',
#         prompt='consent',
#         include_granted_scopes='true'  # String 'true', not boolean True
#     )

#     session['state'] = state
    
#     logger.info(f"Redirecting to authorization URL: {authorization_url}")
#     return redirect(authorization_url)

@email_bp.route('/login')
def email_login():
    """Handle Google OAuth2 login, with auto-refresh if already logged in."""
    # If already authenticated
    logger.info("Checking for existing credentials...")
    if 'google_credentials' in session:
        creds_data = session['google_credentials']
        credentials = Credentials(
            token=creds_data['token'],
            refresh_token=creds_data['refresh_token'],
            token_uri=creds_data['token_uri'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            scopes=creds_data['scopes']
        )
        
        # Check if access token expired
        if hasattr(credentials, 'expired') and credentials.expired:
            logger.info("Access token expired. Attempting to refresh...")
            try:
                credentials.refresh(Request())
                
                # Update session with new token and expiry
                session['google_credentials']['token'] = credentials.token
                if hasattr(credentials, 'expiry'):
                    session['google_credentials']['expiry'] = credentials.expiry.isoformat()
                
                logger.info("Access token refreshed successfully. Redirecting to email home.")
                return redirect(url_for('email.email_home'))
            except Exception as e:
                logger.error(f"Failed to refresh token: {str(e)}")
                # Token refresh failed, proceed to login normally

        else:
            # Token still valid
            logger.info("Already logged in with valid access token. Redirecting to email home.")
            return redirect(url_for('email.email_home'))

    # If no credentials or refresh failed, do full login
    client_config = build_client_config()
    
    logger.info("Starting fresh OAuth2 login flow")
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=url_for('email.oauth2callback', _external=True)
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        include_granted_scopes='true'
    )

    session['state'] = state
    logger.info(f"Redirecting to authorization URL: {authorization_url}")
    return redirect(authorization_url)


@email_bp.route('/oauth2callback')
def oauth2callback():
    """Handle OAuth2 callback"""
    try:
        state = session.get('state')
        if not state:
            logger.error("OAuth state not found in session")
            flash("Authentication error: Session state missing", "error")
            return redirect(url_for('email.email_home'))

        client_config = build_client_config()

        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            state=state,
            redirect_uri=url_for('email.oauth2callback', _external=True)
        )

        # Exchange authorization code for access and refresh tokens
        flow.fetch_token(authorization_response=request.url)

        credentials = flow.credentials

        # Get full user profile info from Google
        user_info = get_user_profile_info(credentials)
        user_email = user_info.get('email')
        user_name = user_info.get('name')
        user_picture = user_info.get('picture')
        
        if not user_email:
            logger.error("Could not retrieve user email from Google")
            flash("Could not verify your identity with Google", "error")
            return redirect(url_for('email.email_home'))

        # Calculate token expiry
        token_expiry = datetime.datetime.now() + datetime.timedelta(seconds=credentials.expiry.timestamp() - datetime.datetime.now().timestamp())

        try:
            # Save credentials and user profile to Supabase
            # Handle database compatibility issues - some columns may not exist yet
            result = save_user_and_gmail_account(
                email=user_email,
                gmail_address=user_email,  # Typically the same as user email
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_expiry=token_expiry,
                name=user_name,
                picture_url=user_picture
            )
            
            # Check the length of the returned tuple
            if len(result) == 3:
                success, error, user_id = result
            else:
                # Fallback for backward compatibility
                success, error = result
                user_id = None
                logger.warning("Database function returned incomplete data. Using fallback.")
        except Exception as e:
            logger.error(f"Error saving credentials: {str(e)}")
            success = False
            error = f"Error saving credentials: {str(e)}"
            user_id = None

        # Always store credentials in session for immediate use regardless of database success
        session['google_credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'email': user_email
        }
        
        # Store user info in session
        session['user'] = {
            'id': user_id,
            'email': user_email,
            'name': user_name,
            'picture': user_picture
        }
        
        # Force session save
        session.modified = True

        if not success:
            logger.error(f"Failed to save credentials to database: {error}")
            flash("Your Gmail was connected, but we couldn't save your account details.", "warning")
        else:
            logger.info(f"Successfully saved Gmail credentials for user: {user_email}")
            flash("Your Gmail account was successfully connected!", "success")

        return redirect(url_for('email.email_success'))

    except Exception as e:
        logger.error(f"Error in OAuth callback: {str(e)}")
        flash("Authentication error. Please try again.", "error")
        return redirect(url_for('email.email_home'))

@email_bp.route('/success')
def email_success():
    """Display the success page after Google authentication"""
    # You might want to test accessing Gmail API here to confirm credentials work
    return render_template('email/success.html')

@email_bp.route('/test')
def test_gmail_api():
    """Test the Gmail API connection"""
    if 'google_credentials' not in session:
        return jsonify({"error": "Not authenticated with Google"}), 401
    
    try:
        # Create credentials object from session data
        creds_data = session['google_credentials']
        credentials = Credentials(
            token=creds_data['token'],
            refresh_token=creds_data['refresh_token'],
            token_uri=creds_data['token_uri'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            scopes=creds_data['scopes']
        )
        print("Access Token:", credentials.token)
        print("Refresh Token:", credentials.refresh_token)
        print("Token URI:", credentials.token_uri)
        print("Client ID:", credentials.client_id)
        print("Client Secret:", credentials.client_secret)
        print("Scopes:", credentials.scopes)
        print("Expiry:", credentials.expiry)  # Optional, shows expiry time
        
        # Build the Gmail API service
        service = build('gmail', 'v1', credentials=credentials)
        
        # Get user profile as a test
        profile = service.users().getProfile(userId='me').execute()
        
        return jsonify({
            "success": True,
            "message": "Successfully connected to Gmail API",
            "email": profile.get('emailAddress')
        })
        
    except Exception as e:
        logger.error(f"Error testing Gmail API: {str(e)}")
        return jsonify({"error": f"Failed to connect to Gmail API: {str(e)}"}), 500

@email_bp.route('/logout')
def logout():
    """Clear the session and log out"""
    from app.utils.session_manager import clear_user_info
    clear_user_info()
    flash("You have been logged out", "info")
    return redirect(url_for('home'))

