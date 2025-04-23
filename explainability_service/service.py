from flask import Flask, request, jsonify
from app.GPTClient import GPTClient
from agents.explainability_agent import ExplainabilityAgent

app = Flask(__name__)
client = GPTClient()
agent = ExplainabilityAgent(client)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/explain", methods=["POST"])
def explain():
    data = request.get_json()
    if not data or "text" not in data or "sentiment" not in data:
        return jsonify({"error": "Missing 'text' or 'sentiment' fields"}), 400
    explanation = agent.explain(data["text"], data["sentiment"])
    return jsonify({"explanation": explanation}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
