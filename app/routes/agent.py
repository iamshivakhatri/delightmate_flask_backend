from flask import Blueprint, request, jsonify
from services.chat_agent import process_message
from utils.helpers import error_response

bp = Blueprint('agent', __name__, url_prefix='/api')

@bp.route('/agent', methods=['POST'])
def agent_interaction():
    """Send user message to GPT-4 agent and get response"""
    data = request.get_json()
    
    if not data or 'transcript' not in data:
        return error_response("No transcript provided", 400)
    
    transcript = data['transcript']
    context = data.get('context', {})  # Optional context data
    
    try:
        # Process the message with GPT agent
        response = process_message(transcript, context)
        
        return jsonify({
            "success": True,
            "response": response['text'],
            "actions": response.get('actions', [])
        })
    except Exception as e:
        return error_response(f"Error processing message: {str(e)}", 500) 