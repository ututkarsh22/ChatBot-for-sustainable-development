import os
from flask import Flask, request, jsonify, send_from_directory, session
from dotenv import load_dotenv
import google.generativeai as genai
import uuid

try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {str(e)}")


api_key = os.getenv('GEMINI_API')

if not api_key:
   raise ValueError("Missing GEMINI_API in environment variables")
  
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
    user_message = data.get('message', '').strip()
    session_id = request.cookies.get('session_id')
    
    if not session_id:
        session_id = str(uuid.uuid4())
    
    if not user_message:
        return jsonify({'response': 'Please provide a message', 'session_id': session_id}), 400

    # =========================
    # CUSTOM DEVELOPER RESPONSE
    # =========================
    trigger_phrases = [
        "who made you", "who created you", "who built you",
        "who trained you", "who developed you", "who is your creator",
        "who designed you", "who programmed you", "your developer"
    ]

    if any(phrase in user_message.lower() for phrase in trigger_phrases):
        import random
        custom_answers = [
            "I was developed by **Utkarsh Trivedi**.",
            "My creator is **Utkarsh Trivedi**.",
            "I was built and trained by **Utkarsh Trivedi**.",
            "I exist thanks to **Utkarsh Trivedi**!",
            "**Utkarsh Trivedi** is the one who made me."
        ]
        answer = random.choice(custom_answers)
        resp = jsonify({'response': answer})
        resp.set_cookie('session_id', session_id, max_age=3600)
        return resp
    # =========================

    try:
        system_prompt = """You are a Sustainability Expert Bot designed to educate users on all aspects of environmental sustainability. You have two main modes of interaction:

1. INFORMATION MODE: When users ask general questions about sustainability topics, provide clear, concise, and educational responses. Keep explanations brief (maximum 3-4 short paragraphs) and focus on the most important points. Topics include climate change, renewable energy, biodiversity, SDGs, waste management, water conservation, green technologies, sustainable agriculture, deforestation, pollution, environmental policies, circular economy, sustainable transportation, and eco-friendly lifestyles.

2. QUIZ MODE: When users specifically request a quiz or question (by using words like "quiz", "test me", "give me a question"), provide a brief quiz question. These should be structured as multiple-choice (A, B, C, D) or true/false questions, with concise explanations after the user responds.

COMPARISON FORMAT: When users ask about differences or comparisons between two or more concepts (e.g., "What's the difference between solar and wind energy?"), format your response as an HTML table with columns. Each column should have a header with the concept name, and the content should be in bullet points.

IMPORTANT: Maintain context throughout the conversation..."""

        # Get or create chat session
        if session_id not in chat_sessions:
            model = genai.GenerativeModel('gemini-2.5-flash')
            chat_sessions[session_id] = model.start_chat(history=[])
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
    