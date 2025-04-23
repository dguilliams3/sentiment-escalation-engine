from flask import Flask, request, jsonify
from app.GPTClient import GPTClient
from agents.sentiment_agent import SentimentAgent

app = Flask(__name__)
client = GPTClient()
agent = SentimentAgent(client)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/classify_sentiment", methods=["POST"])
def classify_sentiment():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field"}), 400
    sentiment = agent.classify(data["text"])
    return jsonify({"sentiment": sentiment}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
