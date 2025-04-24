from flask import Blueprint, request, jsonify
from services.chat_agent import process_message
from utils.helpers import error_response

bp = Blueprint('agent', __name__, url_prefix='/api')

@bp.route('/agent', methods=['POST'])
def agent_interaction():
    """Send user message to GPT-4 agent and get response with intent detection"""
    data = request.get_json()
    
    if not data or 'transcript' not in data:
        return error_response("No transcript provided", 400)
    
    transcript = data['transcript']
    
    # Get system prompt if provided, otherwise will use default
    system_prompt = data.get('system_prompt')
    
    # Create context object with system prompt
    context = {
        'system_prompt': system_prompt
    }
    
    try:
        # Process the message with GPT agent
        response = process_message(transcript, context)
        
        # Return the response text and detected intent
        return jsonify({
            "success": True,
            "response": response['text'],
            "intent": response['intent']
        })
    except Exception as e:
        return error_response(f"Error processing message: {str(e)}", 500) 