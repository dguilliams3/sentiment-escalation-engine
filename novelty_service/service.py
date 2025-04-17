#novelty_service/app.py
from app.GPTClient import GPTClient
from agents.novelty_agent import NoveltyAgent

from flask import Flask, request, jsonify

app = Flask(__name__)
client = GPTClient()
agent = NoveltyAgent(client)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/assess_novelty", methods=["POST"])
def assess_novelty():
    data = request.get_json()
    if not data or "prior" not in data or "new" not in data:
        return jsonify({"error": "Missing 'prior' or 'new' fields"}), 400

    result = agent.assess_novelty(data["prior"], data["new"])
    return jsonify({"novel": result})
