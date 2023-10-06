# from flask import Flask, request, jsonify
# import pyttsx3
# from datetime import datetime
# # import pyttsx3

# # text_to_speech = pyttsx3.init()

# # answer = input("Write your text: ")

# # print(answer)
# # text_to_speech.say(answer)
# # text_to_speech.runAndWait()



# app = Flask(__name__)

# # user_list = [
# #     {
# #         "user_email": "user@gmail.com",
# #         "phrase": "Notification: You received an email.",
# #         "when_received": "Now"
# #     },
# #     {
# #         "user_email": "user1@gmail.com",
# #         "phrase": "Notification1: You received an email.",
# #         "when_received": "Now"
# #     }
# # ]

# user_list = []

# @app.route('/tts', methods=['POST'])
# def tts():
#     if request.method == 'POST':
#         new_user_email = request.form['user_email']
#         new_phrase = request.form['phrase']
#         # Get the current time
#         current_time = datetime.now()

#         # Get the request timestamp
#         request_timestamp = request.headers.get('X-Request-Timestamp')

#         if request_timestamp:
#             # Convert the request timestamp to a datetime object
#             request_time = datetime.fromisoformat(request_timestamp)

#             # Calculate the time difference
#             time_difference = current_time - request_time


#         new_obj = {
#             "user_email": new_user_email,
#             "phrase": new_phrase,
#             "when_received": str(time_difference)
#         }

#         user_list.append(new_obj)
#         return jsonify(user_list), 201

# # @app.route("/")
# # def index():
# #     return "Flask is working!"

# # @app.route("/<name>")
# # def print_name(name):
# #     return "Hi, {}".format(name)


# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=80, debug=True)
# # app.run(host="0.0.0.0", port=80)
# # port=5001


# # py flasktest.py
# # Ctrl + c

from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

user_list = []

@app.route('/tts', methods=['POST'])
def tts():
    if request.method == 'POST':
        new_user_email = request.form['user_email']
        new_phrase = request.form['phrase']

        # Get the current time
        current_time = datetime.now()

        # Get the request timestamp
        # request_timestamp = request.headers.get('X-Request-Timestamp')

        # if request_timestamp:
        #     # Convert the request timestamp to a datetime object
        #     request_time = datetime.fromisoformat(request_timestamp)

        #     # Calculate the time difference
        #     time_difference = current_time - request_time

        new_obj = {
            "user_email": new_user_email,
            "phrase": new_phrase,
            "when_received": str(current_time)
        }

        user_list.append(new_obj)
        return jsonify(user_list), 201
        # else:
        #     return jsonify({"error": "X-Request-Timestamp header missing"}), 400

@app.route('/stt', methods=['POST'])
def stt():
    if request.method == 'POST':
        new_user_email = request.form['user_email']
        new_phrase = request.form['phrase']

        current_time = datetime.now()

        new_obj = {
            "user_email": new_user_email,
            "phrase": new_phrase,
            "when_received": str(current_time)
        }

        user_list.append(new_obj)
        return jsonify(user_list), 201


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)