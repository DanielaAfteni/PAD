from flask import Flask, request, jsonify
from datetime import datetime
import threading
import time
import concurrent.futures  # Import the concurrent.futures module
import os
from dotenv import load_dotenv
import requests
import sqlite3

# connection = sqlite3.connect("config.db")
# cursor = connection.cursor()

# cursor.execute('''CREATE TABLE IF NOT EXISTS api_config (
#                     id INTEGER PRIMARY KEY,
#                     api_key TEXT
#                  )''')

# # Commit the changes and close the connection
# connection.commit()
# connection.close()

app = Flask(__name__)

user_list = []
service_status = "Healthy"  # Initial status


# Limit the number of concurrent tasks to 10
executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

def run_with_timeout(func, timeout, *args, **kwargs):
    result = None
    exception = None

    def worker():
        nonlocal result, exception
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            exception = e

    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        thread.join()  # Ensure the thread terminates
        raise TimeoutError(f"Request timed out after {timeout} seconds")

    if exception:
        raise exception

    return result

def create_new_obj(new_user_email, new_phrase, current_time):
    return {
        "user_email": new_user_email,
        "phrase": new_phrase,
        "when_received": str(current_time)
    }

@app.route('/chat', methods=['POST'])
def tts():
    if request.method == 'POST':
        new_user_email = request.form['user_email']
        new_phrase = request.form['phrase']
        new_question = request.form['question']

        current_time = datetime.now()
        
        print(new_question)
        
        
        # Set your OpenAI API key
        # api_key = "a"


        load_dotenv()
        api_key = os.environ.get('YOUR_API_KEY')

         # Retrieve the API key from the database
        # api_key = get_api_key()


        print(api_key)
        # print(type(api_key))
        # api_key = str(api_key)

        # Define the API endpoint
        api_endpoint = "https://api.openai.com/v1/chat/completions"

        # Define the prompt you want to send to the model
        prompt = new_question

        # Send a POST request to the API
        response = requests.post(
            api_endpoint,
            headers={
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
        )

        # Parse and print the response
        if response.status_code == 200:
            data = response.json()
            completions = data["choices"][0]["message"]["content"]
            print(completions)
        else:
            print("Request failed with status code:", response.status_code)

        try:
            new_obj = run_with_timeout(
                create_new_obj,
                timeout=10,  # Set a timeout of 10 seconds
                new_user_email=new_user_email,
                new_phrase=new_phrase,
                current_time=current_time
            )

            user_list.append(new_obj)
            return jsonify(user_list), 201
        except TimeoutError:
            return jsonify({"error": "Request timed out"}), 500
        
        return jsonify({}), 200


@app.route('/status', methods=['GET'])
def get_status():
    global service_status
    return jsonify({"status": service_status})

def check_health():
    global service_status
    while True:
        # Simulate some health check logic here
        # For demonstration purposes, we'll just toggle between "Healthy" and "Unhealthy"
        if service_status == "Healthy":
            service_status = "Unhealthy"
        else:
            service_status = "Healthy"
        time.sleep(10)  # Check health every 10 seconds



# def get_api_key():
#     connection = sqlite3.connect("config.db")
#     cursor = connection.cursor()

#     # Retrieve the API key from the database
#     cursor.execute("SELECT api_key FROM api_config WHERE id = 1")
#     api_key = cursor.fetchone()

#     connection.close()

#     return api_key[0] if api_key else None


# def insert_api_key(api_key):
#     connection = sqlite3.connect("config.db")
#     cursor = connection.cursor()

#     # Insert the API key into the database
#     cursor.execute("INSERT INTO api_config (api_key) VALUES (?)", (api_key,))
#     connection.commit()
#     connection.close()

# # Insert your API key into the database

# insert_api_key("a")


if __name__ == '__main__':
    # Start a thread for health checking
    health_check_thread = threading.Thread(target=check_health)
    health_check_thread.daemon = True
    health_check_thread.start()

    

    app.run(host="0.0.0.0", port=5000, debug=True)



# py tts_stt_service\tts_stt_service.py