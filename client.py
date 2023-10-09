import requests

# Define the data to send
data_tts = {
    "user_email": "usertts@gmail.com",
    "phrase": "Notificationtts: You received an email."
}

data_stt = {
    "user_email": "userstt@gmail.com",
    "phrase": "Notificationstt: You received an email."
}

# Send data to /tts endpoint
response_tts = requests.post('http://127.0.0.1:80/tts', data=data_tts)

# Send data to /stt endpoint
response_stt = requests.post('http://127.0.0.1:80/stt', data=data_stt)

# Print the responses
print("Response from /tts endpoint:")
print(response_tts.json())
print()
print("Response from /stt endpoint:")
print(response_stt.json())