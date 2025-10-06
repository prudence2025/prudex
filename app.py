import os
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

# --- Configuration ---
# Map keywords to the live API endpoints that provide the data.
API_URLS_MAP = {
    "ph": "https://api.prudex.net/history/ph",
    "cod": "https://api.prudex.net/history/cod",
    "conductivity": "https://api.prudex.net/history/conductivity",
    # You can add more here later, like "bod", "tss", etc.
    # "bod": "https://api.prudex.net/history/bod",
}

# --- Initialize Flask App ---
app = Flask(__name__)
# Enable CORS to allow your frontend to make requests to this backend.
CORS(app)

# --- Initialize DeepSeek Client ---
# Load the API key from an environment variable for better security.
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

# Check if the API key is set
if not DEEPSEEK_API_KEY:
    print("FATAL ERROR: DEEPSEEK_API_KEY environment variable not set.")
    
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)

# --- Helper Functions ---
def find_relevant_api(user_query):
    """
    Identifies the relevant API URL based on keywords in the user's query.
    Returns the URL and the data type keyword.
    """
    query_lower = user_query.lower()
    for keyword, url in API_URLS_MAP.items():
        if keyword in query_lower:
            return url, keyword
    return None, None

def get_data_from_api(url):
    """
    Fetches JSON data from a URL using pandas and returns the last 20 records as a string.
    Returns None if the data cannot be fetched or parsed.
    """
    try:
        # pandas can directly read JSON from a URL into a DataFrame
        df = pd.read_json(url)
        if df.empty:
            print(f"Warning: No data returned from API at {url}")
            return None
        # Return the most recent data (tail) as context for the AI
        return df.tail(20).to_string()
    except Exception as e:
        print(f"Error fetching or parsing data from API {url}: {e}")
        return None

# --- API Endpoint ---
@app.route('/chat', methods=['POST'])
def chat():
    """
    The main chat endpoint that receives user queries and returns AI-generated answers.
    """
    data = request.json
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    if not DEEPSEEK_API_KEY:
        return jsonify({"error": "Server is not configured correctly (missing API key)."}), 500

    # 1. Identify relevant data source from the new API map
    api_url, data_type = find_relevant_api(user_message)
    
    data_context = None
    if api_url:
        data_context = get_data_from_api(api_url)

    # 2. Construct the prompt for the AI
    if data_context:
        system_prompt = f"""
        You are an intelligent data analyst for a water quality monitoring system.
        Your task is to answer the user's question based on the live data provided below.
        The data is from an API endpoint for '{data_type}'.
        Analyze the most recent trends in the data and give a clear, concise answer.
        If the data is insufficient to answer the question, state that clearly.

        Here is the most recent data:
        ---
        {data_context}
        ---
        """
    else:
        system_prompt = "You are a helpful assistant for a water quality monitoring system. The user asked a question I don't have specific data for. Please answer the user's general question clearly and concisely."

    # 3. Call the DeepSeek API
    try:
        chat_completion = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        ai_response = chat_completion.choices[0].message.content
        
        # 4. Return the AI's response
        return jsonify({"reply": ai_response})

    except Exception as e:
        error_details = str(e)
        print(f"An error occurred with the DeepSeek API. Full details: {error_details}")
        public_error_message = "Failed to get a response from the AI service. Please check the server logs for more details."
        return jsonify({"error": public_error_message}), 500
