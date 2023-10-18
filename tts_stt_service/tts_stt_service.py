# # from flask import Flask, request, jsonify
# # import pyttsx3
# # from datetime import datetime
# # # import pyttsx3

# # # text_to_speech = pyttsx3.init()

# # # answer = input("Write your text: ")

# # # print(answer)
# # # text_to_speech.say(answer)
# # # text_to_speech.runAndWait()



# # app = Flask(__name__)

# # # user_list = [
# # #     {
# # #         "user_email": "user@gmail.com",
# # #         "phrase": "Notification: You received an email.",
# # #         "when_received": "Now"
# # #     },
# # #     {
# # #         "user_email": "user1@gmail.com",
# # #         "phrase": "Notification1: You received an email.",
# # #         "when_received": "Now"
# # #     }
# # # ]

# # user_list = []

# # @app.route('/tts', methods=['POST'])
# # def tts():
# #     if request.method == 'POST':
# #         new_user_email = request.form['user_email']
# #         new_phrase = request.form['phrase']
# #         # Get the current time
# #         current_time = datetime.now()

# #         # Get the request timestamp
# #         request_timestamp = request.headers.get('X-Request-Timestamp')

# #         if request_timestamp:
# #             # Convert the request timestamp to a datetime object
# #             request_time = datetime.fromisoformat(request_timestamp)

# #             # Calculate the time difference
# #             time_difference = current_time - request_time


# #         new_obj = {
# #             "user_email": new_user_email,
# #             "phrase": new_phrase,
# #             "when_received": str(time_difference)
# #         }

# #         user_list.append(new_obj)
# #         return jsonify(user_list), 201

# # # @app.route("/")
# # # def index():
# # #     return "Flask is working!"

# # # @app.route("/<name>")
# # # def print_name(name):
# # #     return "Hi, {}".format(name)


# # if __name__ == '__main__':
# #     app.run(host="0.0.0.0", port=80, debug=True)
# # # app.run(host="0.0.0.0", port=80)
# # # port=5001


# # # py flasktest.py
# # # Ctrl + c

# from flask import Flask, request, jsonify
# from datetime import datetime
# import threading
# import time
# from timeout_decorator import timeout

# app = Flask(__name__)

# user_list = []
# service_status = "Healthy"  # Initial status

# def run_with_timeout(func, timeout, *args, **kwargs):
#     result = None
#     exception = None

#     def worker():
#         nonlocal result, exception
#         try:
#             result = func(*args, **kwargs)
#         except Exception as e:
#             exception = e

#     thread = threading.Thread(target=worker)
#     thread.daemon = True
#     thread.start()
#     thread.join(timeout)

#     if thread.is_alive():
#         thread.join()  # Ensure the thread terminates
#         raise TimeoutError(f"Request timed out after {timeout} seconds")

#     if exception:
#         raise exception

#     return result


# def create_new_obj(new_user_email, new_phrase, current_time):
#     return {
#         "user_email": new_user_email,
#         "phrase": new_phrase,
#         "when_received": str(current_time)
#     }


# @app.route('/tts', methods=['POST'])
# def tts():
#     if request.method == 'POST':
#         new_user_email = request.form['user_email']
#         new_phrase = request.form['phrase']

#         current_time = datetime.now()

#         try:
#             new_obj = run_with_timeout(
#                 create_new_obj,
#                 timeout=10,  # Set a timeout of 10 seconds
#                 new_user_email=new_user_email,
#                 new_phrase=new_phrase,
#                 current_time=current_time
#             )

#             user_list.append(new_obj)
#             return jsonify(user_list), 201
#         except TimeoutError:
#             return jsonify({"error": "Request timed out"}), 500



# # @app.route('/tts', methods=['POST'])
# # # @timeout(10)  # Set a timeout of 10 seconds for this route
# # def tts():
# #     if request.method == 'POST':
# #         new_user_email = request.form['user_email']
# #         new_phrase = request.form['phrase']

# #         # Get the current time
# #         current_time = datetime.now()

# #         # Get the request timestamp
# #         # request_timestamp = request.headers.get('X-Request-Timestamp')

# #         # if request_timestamp:
# #         #     # Convert the request timestamp to a datetime object
# #         #     request_time = datetime.fromisoformat(request_timestamp)

# #         #     # Calculate the time difference
# #         #     time_difference = current_time - request_time

# #         new_obj = {
# #             "user_email": new_user_email,
# #             "phrase": new_phrase,
# #             "when_received": str(current_time)
# #         }

# #         user_list.append(new_obj)
# #         return jsonify(user_list), 201
# #         # else:
# #         #     return jsonify({"error": "X-Request-Timestamp header missing"}), 400

# # @app.route('/stt', methods=['POST'])
# # # @timeout(10)  # Set a timeout of 10 seconds for this route
# # def stt():
# #     if request.method == 'POST':
# #         new_user_email = request.form['user_email']
# #         new_phrase = request.form['phrase']

# #         current_time = datetime.now()

# #         new_obj = {
# #             "user_email": new_user_email,
# #             "phrase": new_phrase,
# #             "when_received": str(current_time)
# #         }

# #         user_list.append(new_obj)
# #         return jsonify(user_list), 201


# @app.route('/stt', methods=['POST'])
# # @timeout(10)  # Set a timeout of 10 seconds for this route
# def stt():
#     if request.method == 'POST':
#         new_user_email = request.form['user_email']
#         new_phrase = request.form['phrase']

#         current_time = datetime.now()

#         try:
#             new_obj = run_with_timeout(
#                 create_new_obj,
#                 timeout=10,  # Set a timeout of 10 seconds
#                 new_user_email=new_user_email,
#                 new_phrase=new_phrase,
#                 current_time=current_time
#             )

#             user_list.append(new_obj)
#             return jsonify(user_list), 201
#         except TimeoutError:
#             return jsonify({"error": "Request timed out"}), 500



# @app.route('/status', methods=['GET'])
# # @timeout(5)  # Set a timeout of 5 seconds for this route
# def get_status():
#     global service_status
#     return jsonify({"status": service_status})

# def check_health():
#     global service_status
#     while True:
#         # Simulate some health check logic here
#         # For demonstration purposes, we'll just toggle between "Healthy" and "Unhealthy"
#         if service_status == "Healthy":
#             service_status = "Unhealthy"
#         else:
#             service_status = "Healthy"
#         time.sleep(10)  # Check health every 10 seconds

# if __name__ == '__main__':
#     # Start a thread for health checking
#     health_check_thread = threading.Thread(target=check_health)
#     health_check_thread.daemon = True
#     health_check_thread.start()

#     app.run(host="0.0.0.0", port=80, debug=True)


from flask import Flask, request, jsonify
from datetime import datetime
import threading
import time
import concurrent.futures  # Import the concurrent.futures module
from flask import Flask, request, send_file
from gtts import gTTS
import os
import speech_recognition as sr
from pydub import AudioSegment
import grpc
import log_pb2
import log_pb2_grpc
import google.protobuf.timestamp_pb2


app = Flask(__name__)

user_list = []
service_status = "Healthy"  # Initial status
recognizer = sr.Recognizer()

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


def send_log_request(serviceName, serviceMessage):
    # Create a gRPC channel to connect to the server
    channel = grpc.insecure_channel('localhost:5297')  # Replace with the actual server address

    # Create a gRPC stub
    stub = log_pb2_grpc.NotificationStub(channel)

    current_time_seconds = int(time.time())

    # Get the current time in nanoseconds
    current_time_nanoseconds = int(time.time_ns())

    # Create a LogRequest message
    log_request = log_pb2.LogRequest(
        serviceName=serviceName,
        serviceMessage=serviceMessage,
        time= google.protobuf.timestamp_pb2.Timestamp(
            nanos=current_time_nanoseconds % 1_000_000_000,  # Ensure nanoseconds are within the valid range
            seconds=current_time_seconds
        )
    )

    # Send the LogRequest to the server
    response = stub.SaveLogToRabbit(log_request)

    # Handle the response
    if response.isSuccess:
        print("Request was successful on the port 5297.")
    else:
        print("Request failed on the port 5297.")



@app.route('/tts', methods=['POST'])
def tts():
    if request.method == 'POST':
        new_user_email = request.form['user_email']
        new_phrase = request.form['phrase']
        new_tts = request.form['tts']

        new_tts = "Text to speech: " + new_tts

        current_time = datetime.now()

        # tts = gTTS(new_tts)

        # # Define the folder where you want to save the output file
        # audio_folder_name = "audio_folder"

        # # Make sure the 'audio_folder' exists, create it if it doesn't
        # if not os.path.exists(audio_folder_name):
        #     os.mkdir(audio_folder_name)

        # # Save the generated speech as an MP3 file in the 'audio_folder'
        # output_file_path = os.path.join(audio_folder_name, 'output.mp3')
        # tts.save(output_file_path)

        # with app.app_context():
        #     send_file(output_file_path, as_attachment=True)





        

        # # Create a gTTS object
        # tts = gTTS(new_tts)
        
        # # Save the generated speech as a temporary file
        # tts.save('output.mp3')
        
        # # Send the file to the user for download
        # # send_file('output.mp3', as_attachment=True)
        # output_file_path = os.path.join(os.getcwd(), 'output.mp3')
        # with app.app_context():
        #     send_file(output_file_path, as_attachment=True)
        #     # os.remove(output_file_path)  # Delete the temporary file
        # # send_file(output_file_path, as_attachment=True)

        # # print(new_tts)

        try:
            new_obj = run_with_timeout(
                create_new_obj,
                timeout=10,  # Set a timeout of 10 seconds
                new_user_email=new_user_email,
                new_phrase=new_phrase,
                current_time=current_time
            )

            user_list.append(new_obj)
            send_log_request(new_tts, "Text to Speech Service")
            return jsonify({"response": new_tts}), 201
        except TimeoutError:
            return jsonify({"error": "Request timed out"}), 500
        
        return jsonify({}), 200

@app.route('/stt', methods=['POST'])
def stt():
    if request.method == 'POST':
        new_user_email = request.form['user_email']
        new_phrase = request.form['phrase']
        new_stt = request.form['stt']

        new_stt = "Speech to text: " + new_stt

        current_time = datetime.now()
        
        # print(new_stt)

        try:
            new_obj = run_with_timeout(
                create_new_obj,
                timeout=10,  # Set a timeout of 10 seconds
                new_user_email=new_user_email,
                new_phrase=new_phrase,
                current_time=current_time
            )

            user_list.append(new_obj)
            send_log_request(new_stt, "Speech to Text Service")
            return jsonify({"response": new_stt}), 201
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

if __name__ == '__main__':
    # Start a thread for health checking
    health_check_thread = threading.Thread(target=check_health)
    health_check_thread.daemon = True
    health_check_thread.start()

    app.run(host="0.0.0.0", port=8080, debug=True)



# py tts_stt_service\tts_stt_service.py