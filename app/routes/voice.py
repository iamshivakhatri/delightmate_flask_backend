from flask import Blueprint, request, jsonify, Response
from services.whisper import transcribe_audio
from services.elevenlabs import generate_speech
from utils.helpers import error_response
import io

bp = Blueprint('voice', __name__, url_prefix='/api')

@bp.route('/stt', methods=['POST'])
def speech_to_text():
    """Convert speech to text using OpenAI Whisper API"""
    if 'audio' not in request.files:
        return error_response("No audio file provided", 400)
    
    audio_file = request.files['audio']
    
    if audio_file.filename == '':
        return error_response("Empty audio file", 400)
    
    try:
        transcript = transcribe_audio(audio_file)
        return jsonify({"success": True, "transcript": transcript})
    except Exception as e:
        return error_response(f"Error transcribing audio: {str(e)}", 500)

@bp.route('/tts', methods=['POST'])
def text_to_speech():
    """Convert text to speech using ElevenLabs API"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return error_response("No text provided", 400)
    
    text = data['text']
    voice_id = data.get('voice_id', None)  # Optional voice ID
    
    try:
        audio_data = generate_speech(text, voice_id)
        
        # Return audio as a stream
        return Response(
            io.BytesIO(audio_data),
            mimetype='audio/mpeg',
            headers={"Content-Disposition": "attachment;filename=speech.mp3"}
        )
    except Exception as e:
        return error_response(f"Error generating speech: {str(e)}", 500) 