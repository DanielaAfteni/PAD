import requests

# Define the data to send
data_chat = {
    "user_email": "userchat@gmail.com",
    "phrase": "Notificationchat: You received an email.",
    "question": "What is the capital of France?"
}

response = requests.post(url="http://127.0.0.1:5000/chat", data=data_chat)

print("Response from /chat endpoint:")
print(response.json())
