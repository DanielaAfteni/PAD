# # # # # from flask import Flask, request, jsonify
# # # # # import openai
# # # # # import os
# # # # # from dotenv import load_dotenv

# # # # # app = Flask(__name__)

# # # # # # load_dotenv()
# # # # # # Replace 'YOUR_API_KEY' with your actual OpenAI API key
# # # # # openai.api_key = "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"


# # # # # @app.route('/chat', methods=['POST'])
# # # # # def chat():
# # # # #     # Get the user's question from the request
# # # # #     user_input = request.json.get('question', '')
# # # # #     print(user_input)

# # # # #     # Make a request to ChatGPT
# # # # #     response = openai.Completion.create(
# # # # #         engine="text-davinci-002",
# # # # #         prompt=f"Answer the following question: {user_input}",
# # # # #         max_tokens=50  # Adjust this based on your requirements
# # # # #     )

# # # # #     # Extract the response from ChatGPT
# # # # #     bot_response = response.choices[0].text.strip()

# # # # #     return jsonify({"response": bot_response})

# # # # # if __name__ == '__main__':
# # # # #     app.run(debug=True)

# # # # from flask import Flask, request, jsonify
# # # # import openai

# # # # # Replace 'YOUR_API_KEY' with your actual GPT-3 API key
# # # # api_key = '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'

# # # # # Initialize Flask
# # # # app = Flask(__name__)

# # # # # Initialize the OpenAI API client
# # # # openai.api_key = api_key

# # # # # Define an endpoint for asking questions
# # # # @app.route('/ask', methods=['POST'])
# # # # def ask_question():
# # # #     try:
# # # #         # Get the question from the request data
# # # #         data = request.json
# # # #         question = data['question']

# # # #         # Define a prompt for GPT-3
# # # #         prompt = f"Answer the following question:\n{question}\nAnswer:"

# # # #         # Generate a response from GPT-3
# # # #         response = openai.Completion.create(
# # # #             engine="davinci",
# # # #             prompt=prompt,
# # # #             max_tokens=100  # You can adjust this as needed
# # # #         )

# # # #         # Extract the answer from the response
# # # #         answer = response.choices[0].text.strip()

# # # #         # Return the answer as a JSON response
# # # #         return jsonify({'answer': answer})

# # # #     except Exception as e:
# # # #         return jsonify({'error': str(e)}), 500

# # # # if __name__ == '__main__':
# # # #     app.run(debug=True)



# # # import requests
# # # import json

# # # # Set your OpenAI API key
# # # api_key = "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"

# # # # Define the API endpoint
# # # api_endpoint = "https://api.openai.com/v1/engines/davinci-codex/completions/"

# # # # Define the prompt you want to send to the model
# # # prompt = "Translate the following English text to French:"

# # # # Define the maximum number of tokens in the response
# # # max_tokens = 50

# # # # Send a POST request to the API
# # # response = requests.post(
# # #     api_endpoint,
# # #     headers={
# # #         "Authorization": f"Bearer {api_key}",
# # #         "Content-Type": "application/json",
# # #     },
# # #     json={
# # #         "prompt": prompt,
# # #         "max_tokens": max_tokens,
# # #     },
# # # )

# # # # Parse and print the response
# # # if response.status_code == 200:
# # #     data = response.json()
# # #     completions = data["choices"][0]["text"]
# # #     print(completions)
# # # else:
# # #     print("Request failed with status code:", response.status_code)



# # import openai

# # openai.api_key = "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"
# # model_engine = "gpt-3.5-turbo" 

# # response = openai.ChatCompletion.create(
# #     model='gpt-3.5-turbo',
# #     messages=[
# #         {"role": "system", "content": "You are a helpful assistant."},
# #         {"role": "user", "content": "Hello, ChatGPT!"},
# #     ])

# # message = response.choices[0]['message']
# # print("{}: {}".format(message['role'], message['content']))


# import openai 
# openai.api_key = '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'
# messages = [ {"role": "system", "content":  
#               "You are a intelligent assistant."} ] 
# while True: 
#     message = input("User : ") 
#     if message: 
#         messages.append( 
#             {"role": "user", "content": message}, 
#         ) 
#         chat = openai.ChatCompletion.create( 
#             model="gpt-3.5-turbo", messages=messages 
#         ) 
#     reply = chat.choices[0].message.content 
#     print(f"ChatGPT: {reply}") 
#     messages.append({"role": "assistant", "content": reply}) 


import requests
import json

# Set your OpenAI API key
api_key = "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"

# Define the API endpoint
api_endpoint = "https://api.openai.com/v1/chat/completions"

# Define the prompt you want to send to the model
prompt = "Translate the following English text to French:"

# Define the maximum number of tokens in the response
max_tokens = 50

# Send a POST request to the API
response = requests.post(
    api_endpoint,
    headers={
        "Authorization": f"Bearer {api_key}",
    },
    json={
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Who won the first world cup"}],
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




