from flask import Flask, request, jsonify, send_from_directory
import os
import openai
from dotenv import load_dotenv
from flask_cors import CORS
import asyncio

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Check if the API key is loaded correctly
if not api_key:
    raise ValueError("OpenAI API key not found. Please ensure 'OPENAI_API_KEY' is set in your .env file.")

# Initialize OpenAI client
client = openai.AsyncOpenAI(api_key=api_key)

# Initialize Flask app and enable CORS for frontend interaction
app = Flask(__name__, static_folder='climategpt', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Endpoint for GPT analysis
@app.route('/api/gpt', methods=['POST'])
async def gpt_analysis():
    try:
        # Print statement to check if the function is triggered
        print("GPT Analysis function called.")

        # Get the JSON data from the request
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request, JSON data expected"}), 400

        user_message = data.get('message')
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        print(f"Received message: {user_message}")

        # Call OpenAI GPT model using the correct API method
        print("Calling OpenAI API...")
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # Adjust to the appropriate model you have access to
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
        )

        # Access the 'content' property directly
        reply = response.choices[0].message.content
        print(f"Received reply from OpenAI: {reply}")
        return jsonify({"reply": reply})  # Return the response as JSON

    except openai.BadRequestError as e:
        # Handle OpenAI API errors gracefully
        print(f"OpenAI API error: {e}")
        return jsonify({"error": "OpenAI API error, please try again later."}), 500

    except Exception as e:
        # Handle general errors
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred, please try again."}), 500

# Serve the frontend files
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_file(path):
    return send_from_directory(app.static_folder, path)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
