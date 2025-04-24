import os
import json
import re
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Default system message that defines agent behavior
DEFAULT_SYSTEM_MESSAGE = """
You are DelightMate, an AI assistant designed to be helpful, friendly, and efficient.
Provide concise and relevant information to the user's questions.
Always be polite and respectful. If you don't know the answer, be honest about it.
"""

def process_message(message, context=None):
    """
    Process user message with GPT-4 and return response
    
    Args:
        message (str): User's message/transcript
        context (dict, optional): Additional context like conversation history
            or user preferences
            
    Returns:
        dict: Response containing text and detected intent
    """
    if not message:
        raise ValueError("Message is required")
    
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is not set in environment variables")
    
    # Build conversation history
    messages = []
    
    # Add system message
    system_message = context.get('system_prompt', DEFAULT_SYSTEM_MESSAGE)
    messages.append({"role": "system", "content": system_message})
    
    # Add conversation history if provided
    history = context.get('history', [])
    if history:
        messages.extend(history)
    
    # Add the current user message
    messages.append({"role": "user", "content": message})
    
    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )
    
    # Extract assistant's response
    response_text = response.choices[0].message.content
    
    # Extract intent from the response text
    intent = extract_intent(response_text)
    
    # Clean the response text (remove any JSON artifacts if present)
    clean_text = clean_response_text(response_text)
    
    # Return both the text response and the detected intent
    result = {
        "text": clean_text,
        "intent": intent
    }
    
    return result

def extract_intent(response_text):
    """
    Extract intent information from the model's response
    
    The model should return intent information in JSON format like:
    {"tool": "email", "action": "compose", "params": {"recipient": "John", "subject": "Meeting"}}
    
    Args:
        response_text (str): The model's response text
        
    Returns:
        dict or None: Extracted intent if found, otherwise None
    """
    # Try to find JSON object in the response using regex
    json_pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'
    json_matches = re.findall(json_pattern, response_text)
    
    for json_str in json_matches:
        try:
            # Try to parse as JSON
            data = json.loads(json_str)
            
            # Check if this looks like a tool intent
            if isinstance(data, dict) and "tool" in data and "action" in data:
                return data
        except json.JSONDecodeError:
            continue
    
    return None

def clean_response_text(response_text):
    """
    Clean the response text by removing any JSON objects and formatting
    
    Args:
        response_text (str): The original response text
        
    Returns:
        str: Cleaned response text
    """
    # Remove JSON-like objects from the text
    clean_text = re.sub(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', '', response_text)
    
    # Remove any residual formatting artifacts
    clean_text = re.sub(r'intent:|Intent:', '', clean_text)
    clean_text = re.sub(r'```json.*?```', '', clean_text, flags=re.DOTALL)
    
    # Remove extra whitespace and newlines
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    return clean_text

def extract_actions(response_text):
    """
    Future enhancement: Parse response text to extract actions
    like scheduling events, sending emails, etc.
    """
    # This is a placeholder for future functionality
    actions = []
    return actions 