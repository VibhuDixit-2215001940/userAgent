from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

WEBHOOK = "https://webhook.site/bc6a33cc-de1e-4d23-a069-20b1fc36818e"

@app.route('/receive', methods=['POST'])
def receive():
    data = request.json
    print("Received data:", data)
    try:
        r = requests.post(WEBHOOK, json=data)
        print("Forwarded to webhook:", r.status_code)
    except Exception as e:
        print("Error forwarding:", e)
    return jsonify({"status": "ok", "received": data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
