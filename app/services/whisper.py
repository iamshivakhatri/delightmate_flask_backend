import os
import tempfile
import logging
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client with API key
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

def transcribe_audio(audio_file):
    """
    Transcribe audio using OpenAI's Whisper API
    
    Args:
        audio_file: Audio file object (from Flask's request.files)
        
    Returns:
        str: Transcribed text
    """
    if not audio_file:
        logger.error("No audio file provided")
        return None
    
    # Check if OpenAI API key is set
    if not api_key:
        logger.warning("OPENAI_API_KEY not set - returning mock transcription")
        return "This is a test transcription because the OpenAI API key is not configured."
    
    # Create a temporary file to save the audio
    temp_file = None
    try:
        # Create a temporary file with .webm extension
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
        temp_file.close()
        
        # Save the audio to the temporary file
        audio_file.save(temp_file.name)
        
        logger.info(f"Starting transcription of audio file")
        
        # Open the file in binary mode for the Whisper API
        with open(temp_file.name, "rb") as audio:
            # Use advanced parameters for better accuracy
            # - Lower temperature for more predictable results
            # - Add a prompt to provide context
            # - Request verbose_json to get more detailed response data
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                temperature=0.3,  # Lower temperature for more predictable results
                language="en",    # Explicitly set language to English
                prompt="This is a conversation with a voice assistant.",  # Context hint
                response_format="text"  # Just return the text
            )
        
        # Extract the transcript text from the response
        transcription = response
        logger.info(f"Transcription successful: {transcription[:50]}...")
        return transcription
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return None
        
    finally:
        # Clean up the temporary file
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
            logger.debug("Temporary audio file deleted") 