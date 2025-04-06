from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env if available

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # or replace with your key as a string

def get_gemini_response(prompt):
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-001:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(url, headers=headers, params=params, json=data)

    if response.status_code == 200:
        reply = response.json()
        try:
            return reply["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "No valid response received from Gemini."
    else:
        return f"Error: {response.status_code} - {response.text}"

@app.route("/get-recommendation", methods=["GET"])
def get_recommendation():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Please provide a query parameter"}), 400

    result = get_gemini_response(query)
    return jsonify({"recommendation": result})

if __name__ == "__main__":
    app.run(debug=True)
