import os
from supabase import create_client
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

def get_supabase_client():
    """
    Create and return a Supabase client using environment variables
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    
    if not url or not key:
        logger.error("SUPABASE_URL or SUPABASE_KEY environment variables are not set")
        raise ValueError("Supabase credentials not configured. Please set SUPABASE_URL and SUPABASE_KEY environment variables")
    
    return create_client(url, key)
