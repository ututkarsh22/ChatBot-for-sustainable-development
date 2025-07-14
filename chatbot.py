import os
from flask import Flask, request, jsonify, send_from_directory, session
from dotenv import load_dotenv
import google.generativeai as genai
import uuid

# Try to load environment variables from .env file
try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {str(e)}")

# Get API key from environment variables or use a hardcoded one
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    # Hardcoded API key - using your provided key
    api_key = "AIzaSyAl2dihsCHfrrvUhjr1v_9gaxs5nkcFwtw"
    print("Using hardcoded API key")
else:
    print("Using API key from environment variables")
  
# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Configure the Gemini API
genai.configure(api_key=api_key)

# Store chat sessions
chat_sessions = {}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    session_id = request.cookies.get('session_id')
    
    if not session_id:
        session_id = str(uuid.uuid4())
    
    if not user_message:
        return jsonify({'response': 'Please provide a message', 'session_id': session_id}), 400
    
    try:
        # Define the system prompt for environmental sustainability focus
        system_prompt = """You are a Sustainability Expert Bot designed to educate users on all aspects of environmental sustainability. You have two main modes of interaction:

1. INFORMATION MODE: When users ask general questions about sustainability topics, provide clear, concise, and educational responses. Keep explanations brief (maximum 3-4 short paragraphs) and focus on the most important points. Topics include climate change, renewable energy, biodiversity, SDGs, waste management, water conservation, green technologies, sustainable agriculture, deforestation, pollution, environmental policies, circular economy, sustainable transportation, and eco-friendly lifestyles.

2. QUIZ MODE: When users specifically request a quiz or question (by using words like "quiz", "test me", "give me a question"), provide a brief quiz question. These should be structured as multiple-choice (A, B, C, D) or true/false questions, with concise explanations after the user responds.

COMPARISON FORMAT: When users ask about differences or comparisons between two or more concepts (e.g., "What's the difference between solar and wind energy?"), format your response as an HTML table with columns. Each column should have a header with the concept name, and the content should be in bullet points. For example:

<table class="comparison-table">
  <tr>
    <th>Solar Energy</th>
    <th>Wind Energy</th>
  </tr>
  <tr>
    <td>
      <ul>
        <li>Harvests energy from sunlight</li>
        <li>Works best in sunny areas</li>
        <li>No moving parts</li>
      </ul>
    </td>
    <td>
      <ul>
        <li>Harvests energy from wind</li>
        <li>Works best in windy areas</li>
        <li>Has moving turbine blades</li>
      </ul>
    </td>
  </tr>
</table>

IMPORTANT: Maintain context throughout the conversation. If you've just asked a quiz question and the user responds with an answer (like "A", "B", "C", "D", "True", or "False"), recognize it as an answer to your previous question and provide feedback on whether they were correct, along with a brief explanation.

Analyze each user message carefully to determine which mode is appropriate. If the message contains a direct question about sustainability, use INFORMATION MODE. If the message explicitly requests a quiz or question, use QUIZ MODE.

Your tone should be friendly and engaging. Prioritize brevity and clarity in all responses. Use bullet points when appropriate to organize information. Limit your responses to 150-200 words whenever possible."""

        # Get or create chat session
        if session_id not in chat_sessions:
            model = genai.GenerativeModel('gemini-1.5-flash')
            chat_sessions[session_id] = model.start_chat(history=[])
            # Add system prompt as first message
            chat_sessions[session_id].send_message(system_prompt)
        
        # Generate a response using the existing chat session
        response = chat_sessions[session_id].send_message(user_message)
        
        # Set cookie in response
        resp = jsonify({'response': response.text})
        resp.set_cookie('session_id', session_id, max_age=3600)  # 1 hour expiry
        return resp
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'response': f'Sorry, I encountered an error: {str(e)}'}), 500

if __name__ == '__main__':
    # Disable Flask's automatic loading of .env file
    app.run(debug=True, load_dotenv=False)
    