from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Store votes here
votes: dict[str, bool] = {}

with open("client.html", "r") as page:
    client_page = page.read()


@app.route("/")
def index():
    return render_template_string(client_page)

@app.route("/vote", methods=["POST"])
def vote():
    client_ip = request.remote_addr
    data = request.get_json(silent=True)

    if not data or "vote" not in data or not isinstance(data["vote"], bool):
        return jsonify({"error": "Invalid vote"}), 400

    votes[client_ip] = data["vote"]
    return jsonify({"status": "ok"})


@app.route("/votes")
def get_votes():
    return jsonify(votes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
