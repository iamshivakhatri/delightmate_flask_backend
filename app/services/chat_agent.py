import os
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
        dict: Response containing text and optional actions
    """
    if not message:
        raise ValueError("Message is required")
    
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is not set in environment variables")
    
    # Build conversation history
    messages = []
    
    # Add system message
    system_message = context.get('system_message', DEFAULT_SYSTEM_MESSAGE)
    messages.append({"role": "system", "content": system_message})
    
    # Add conversation history if provided
    history = context.get('history', [])
    if history:
        messages.extend(history)
    
    # Add the current user message
    messages.append({"role": "user", "content": message})
    
    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4-turbo", 
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )
    
    # Extract assistant's response
    response_text = response.choices[0].message.content
    
    # Parse any actions - more complex parsing can be implemented here
    # For now, we'll just return the text response
    result = {
        "text": response_text,
        "actions": []  # Future: Extract actions from response
    }
    
    return result

def extract_actions(response_text):
    """
    Future enhancement: Parse response text to extract actions
    like scheduling events, sending emails, etc.
    """
    # This is a placeholder for future functionality
    actions = []
    return actions 