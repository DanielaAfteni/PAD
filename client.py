import requests

# Define the data to send
data_tts = {
    "user_email": "usertts@gmail.com",
    "phrase": "Notificationtts: You received an email.",
    "tts": "We are thrilled to announce the grand opening of our new flagship store this Saturday, October 14th! Join us for an exciting day of exclusive discounts, giveaways, and refreshments. Don't miss this opportunity to discover our latest products and experience top-notch customer service. See you there!"
}

data_stt = {
    "user_email": "userstt@gmail.com",
    "phrase": "Notificationstt: You received an email.", 
    "stt": "Join us for an unforgettable evening of music and entertainment! Our live concert featuring talented artists from around the world will leave you mesmerized. Save the date and get ready to be swept away by the magic of music."
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