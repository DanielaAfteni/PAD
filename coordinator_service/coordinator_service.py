from flask import Flask, request, jsonify
import requests
import threading

app = Flask(__name__)

# Server URLs
chat_gpt_url = "http://gpt1:5000"
user_service_url = "http://user_service:6000"

# Helper function for asynchronous request
def async_request(url, data):
    def _make_request():
        requests.get(url, json=data)

    thread = threading.Thread(target=_make_request)
    thread.start()

# Endpoint for creating a user
@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()

    # Step 1: Asynchronous requests to check connection health
    async_request(f"{chat_gpt_url}/get_connection", {})
    async_request(f"{user_service_url}/get_connection", {})

    # Step 2: Synchronous request to save data
    data_user = {"email": data['email'], "name": data['name']}
    data_chat_gpt = {"name": data['name'], "name_appearance": data['name_appearance']}
    response_user_service = requests.post(f"{user_service_url}/create", json=data_user)
    response_chat_gpt = requests.post(f"{chat_gpt_url}/create", json=data_chat_gpt)

    # Check if any connection health check failed
    if response_user_service.status_code != 200 or response_chat_gpt.status_code != 200:
        # Undo changes by sending a request to user_service and chat_gpt_service to remove the user
        undo_data_user = {"email": data['email'], "name": data['name']}
        undo_data_chat_gpt = {"name": data['name'], "name_appearance": data['name_appearance']}

        # Undo in user_service
        requests.delete(f"{user_service_url}/undo", json=undo_data_user)
        
        # Undo in chat_gpt_service
        requests.delete(f"{chat_gpt_url}/undo", json=undo_data_chat_gpt)

        return jsonify({"status": "error", "message": "Connection health check failed. Changes undone."}), 500

    return jsonify({"status": "success", "message": "User created successfully."})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6001, debug=True)
