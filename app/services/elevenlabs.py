import os
import requests
import logging
import base64

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ElevenLabs API endpoint
TTS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

# Get API key from environment variables
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

# Default voice ID (can be overridden)
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # ElevenLabs Rachel voice

def generate_speech(text, voice_id=None):
    """
    Generate speech from text using ElevenLabs API
    
    Args:
        text (str): Text to convert to speech
        voice_id (str, optional): ElevenLabs voice ID to use. Defaults to Rachel voice.
        
    Returns:
        bytes: Audio data in MP3 format
    """
    if not text:
        raise ValueError("Text is required")
    
    # For development/testing without API key
    if not ELEVENLABS_API_KEY:
        logger.warning("ELEVENLABS_API_KEY is not set, using fallback TTS")
        # Return a minimal sample MP3 for testing purposes
        dummy_mp3 = base64.b64decode("SUQzAwAAAAAic1RJVDIAAABkAAAASW1wcm92aXNlZCBmYWxsYmFjayBtcDMgZmlsZQ==")
        return dummy_mp3
    
    # Use default voice if none provided
    voice_id = voice_id or DEFAULT_VOICE_ID
    
    # Setup headers with API key
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    # Setup request body
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    try:
        # Make request to ElevenLabs API
        logger.info(f"Sending TTS request for: {text[:30]}...")
        response = requests.post(
            f"{TTS_API_URL}/{voice_id}",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        # Check for errors
        response.raise_for_status()
        
        # Return the audio data
        logger.info("Successfully generated speech")
        return response.content
    
    except requests.exceptions.RequestException as e:
        logger.error(f"ElevenLabs API error: {str(e)}")
        # Return fallback audio to prevent application failure
        dummy_mp3 = base64.b64decode("SUQzAwAAAAAic1RJVDIAAABkAAAASW1wcm92aXNlZCBmYWxsYmFjayBtcDMgZmlsZQ==")
        return dummy_mp3