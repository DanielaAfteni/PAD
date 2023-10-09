import requests

# URL of your Flask service
url = 'http://localhost:5000/ask'  # Change this URL to match your service's URL

# Define the question you want to ask
question = "What is the capital of France?"

# Create a JSON payload with the question
data = {
    "question": question
}

# Send a POST request to the service
response = requests.post(url, json=data)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    response_data = response.json()
    answer = response_data['answer']
    print(f"Answer: {answer}")
else:
    print(f"Error: {response.status_code} - {response.text}")
