from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, flash
import os
import sys
import json
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import logging

# Add the parent directory to sys.path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils.session_manager import get_user_info
from app.services.user_service import get_credentials_from_supabase

# Configure logging
logger = logging.getLogger(__name__)

calendar_bp = Blueprint('calendar', __name__, url_prefix='/calendar')

@calendar_bp.route('/')
def calendar_home():
    """Display the user's calendar or redirect to email login if not authenticated"""
    user_info = get_user_info()
    
    if not user_info['is_logged_in']:
        flash("Please connect your Google account first", "warning")
        return redirect(url_for('email.email_login'))
    
    # Get credentials from session
    if 'google_credentials' in session:
        try:
            creds_data = session['google_credentials']
            credentials = Credentials(
                token=creds_data['token'],
                refresh_token=creds_data['refresh_token'],
                token_uri=creds_data['token_uri'],
                client_id=creds_data['client_id'],
                client_secret=creds_data['client_secret'],
                scopes=creds_data['scopes']
            )
            
            # Check if credentials are expired and refresh if needed
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                # Update session with new token
                session['google_credentials']['token'] = credentials.token
            
            # Build the Calendar API service
            service = build('calendar', 'v3', credentials=credentials)
            
            # Get date range for events (today + 7 days)
            now = datetime.datetime.utcnow()
            end_date = now + datetime.timedelta(days=7)
            
            # Call the Calendar API for upcoming events
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                maxResults=20,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Process calendar events for display
            processed_events = []
            for event in events:
                # Get start time
                start = event['start'].get('dateTime', event['start'].get('date'))
                
                # Convert to datetime object for formatting
                if 'T' in start:  # dateTime format with time
                    start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                else:  # all-day event
                    start_dt = datetime.datetime.strptime(start, '%Y-%m-%d')
                
                # Format for display
                if 'T' in start:
                    start_formatted = start_dt.strftime('%a, %b %d, %Y %I:%M %p')
                else:
                    start_formatted = start_dt.strftime('%a, %b %d, %Y (All day)')
                
                processed_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', '(No title)'),
                    'start': start_formatted,
                    'location': event.get('location', ''),
                    'description': event.get('description', ''),
                    'html_link': event.get('htmlLink', '')
                })
            
            return render_template('calendar/events.html', 
                                  user=user_info,
                                  events=processed_events)
                                  
        except Exception as e:
            logger.error(f"Error accessing Calendar API: {str(e)}")
            flash("Error accessing your Calendar. Please try again.", "error")
            return redirect(url_for('email.email_login'))
    
    # No credentials in session, try to get from database
    try:
        credentials, user_data = get_credentials_from_supabase(user_info['email'])
        
        if credentials:
            # Store credentials in session for future use
            session['google_credentials'] = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            # Redirect back to calendar home to use new credentials
            return redirect(url_for('calendar.calendar_home'))
        else:
            flash("Please connect your Google account first", "warning")
            return redirect(url_for('email.email_login'))
    
    except Exception as e:
        logger.error(f"Error retrieving credentials: {str(e)}")
        flash("Error accessing your account. Please try again.", "error")
        return redirect(url_for('email.email_login'))
