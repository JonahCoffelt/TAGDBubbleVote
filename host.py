from flask import Flask, request, jsonify, render_template_string
from QRCodeGenerator import generate_qr_code
import socket

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

def get_local_url(port=5000):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This never actually sends packets, it just forces IP selection
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return f"http://{ip}:{port}"

# File settings
url = get_local_url()      # The link the qr code to sends users to
qr_code_name = "TeamsCode"     # The name of the image generated

print(url)

# Resolution and padding
box_size = 15                   # How many pixels go in one box
border = 3                      # How many boxes of padding it contain out the edges

# Colors                        Acceptable inputs
light_color = (255, 255, 255)   # RGB tuple: (000, 123, 255)
dark_color = "#000000"          # HEX string: "#123456" or "123456"
                                # Or any valid python color names: "white", "darkblue", etc.
# Center image
image_name = "logo.png"          # Include directory and file type (Ex: "Logos/MyPicture.png")
img_size = 2                    # How large is the center image?
correction = 4                  # 1 has the least correction and 4 has the most

generate_qr_code(url, qr_code_name, box_size, border, light_color, dark_color, image_name, img_size, correction)

app.run(host="0.0.0.0", port=5000, debug=True)